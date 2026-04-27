# MCP fix — verification report

This document records the before/after state after the patch landed in
`knowledge_graph_mcp_custom_path.py` and the agent definitions for
`BO-code-graph-builder-updater` and `BO-project-grammar-builder` were
updated. The full plan is at `~/.claude/plans/polished-gliding-stream.md`.
The original diagnosis is in `docs-deprecated/code-graph/mcp-qa.md`.

## TL;DR

The patch landed cleanly. The next code-graph build ran end-to-end
through MCP (no direct disk writes), produced a complete HTML
visualization, and shows monotonic backup growth. The
`from`/`from_` schema bug is fixed; `read_graph_file` now bubbles
errors instead of silently returning empty.

## Patch surface

### MCP source — `knowledge_graph_mcp_custom_path.py`

| Block | Change | Effect |
|---|---|---|
| A1 | `Relation.from_ = Field(alias="from")` + `populate_by_name=True` | Pydantic accepts both `"from"` and `"from_"` from JSON-RPC; emits `"from"` to disk (alias). |
| A2 | `save_graph` rewrites: `auto_generate_html=False` default, atomic `os.replace`, `by_alias=True` dump, `ensure_ascii=False` | Writes are torn-write-safe and Unicode-safe. HTML regen no longer thrashes on every batch. |
| A3 | Typo fixes at lines 1419 + 1493 (`r.to_` → `r.to`) | `advanced_search` and `generate_report` no longer hit `AttributeError` once bare except is removed. |
| A4 | `read_graph_file` shim (`from_` → `from`) + remove `except (json.JSONDecodeError, ValueError): return KnowledgeGraph()` | Old-format `.bak` files still load. Corrupt files now raise instead of silently producing empty. |
| A5 | All 19 `"message": str(e)` → `f"{type(e).__name__}: {e}"` | Tools surface error type so callers can distinguish `JSONDecodeError` vs `ValidationError` vs generic. |
| A6 | `restore_graph` migrated to Pydantic v2 (`model_validate`, `model_dump_json(by_alias=True)`) + same shim | Restore round-trips with current on-disk format. |
| B1 | New `reload_graph(path?)` tool | Explicit preflight + post-swap verification. |
| B2 | New `validate_graph` tool | Orphan / duplicate-name / self-loop check; capped at 50 per list. |
| B3 | `_log_call` helper + JSONL log to `<graph_dir>/mcp.log.jsonl` | Per-call audit trail (tool, status, ms, in/out counts). Wired into `reload_graph` and `validate_graph`; existing tools can be wired later. |

### Agent definitions

- **BO-code-graph-builder-updater.md** — added Step 0.5 (MCP preflight: write sentinel, `reload_graph`, assert count, delete, switch path), an MCP contract section (no direct disk writes; `"from"` is the wire format; reads are always fresh from disk; errors are loud), and Step 6 expanded to call `reload_graph`/`validate_graph`/`generate_html_visualization` at end-of-build. `generate_html_visualization` and the two new tools added to the allowed-tools list. The "advanced_search bug" quirk note removed (fixed in A3).
- **BO-project-grammar-builder.md** — added Phase 4.5 (regex compile preflight). Every pattern in every grammar file is `re.compile`-checked before write; bad patterns abort emission with file/group/pattern/error.

### Project artifacts

- `docs/` archived to `docs-deprecated/` for comparison.
- `.claude/agent-memory/code-graph-builder/` deleted (the `mcp-quirks.md` it contained encoded the wrong rule "use `from` not `from_`").
- Grammar-builder memory at `.claude/agent-memory/project-grammar-builder/` preserved (Context7 reference IDs + version anchors still valid).

### Tests

- `test_relation_alias.py` written. Six cases (load canonical, round-trip, accept `"from"`, accept `"from_"`, corrupt file errors loudly, old-format `.bak` shim). All 14 sub-assertions pass.
- Existing `test_custom_path.py` and `test_kg.py` continue to pass — no regressions.

## Before / after — verification numbers

| Check | Before (`docs-deprecated/`) | After (`docs/`) | Pass condition |
|---|---:|---:|---|
| `code-graph.json` entities | 1190 | 1057 | within 15% (grammar drift OK) |
| `code-graph.json` relations | 1503 | 1211 | within 25% (grammar drift OK) |
| `"from"` keys in JSON | 1503 | 1211 | matches relation count |
| `"from_"` keys in JSON | 0 | 0 | zero |
| HTML viz nodes | **800** (incomplete — 67% of disk) | **1057** (matches disk) | new == disk |
| HTML viz links | **0** (incomplete) | **1211** (matches disk) | new == disk |
| Backup chain progression | **thrashed**: 33 → 155 → 348968 → 37776 → 73318 → 348968 | **monotonic**: 208258 → 232368 → 257604 → 281309 → 304660 → 330842 → 338942 → 351047 → 361100 → 371246 | strictly non-decreasing |
| `validate_graph` issues | 15 (12 orphans + 1 duplicate + 2 self-loops) | 1 (1 duplicate, the same shadcn `use-toast.ts::toast` name collision) | issues_count drops |
| `mcp.log.jsonl` | absent | present, 2 lines from probe | exists, contains valid JSON |
| Agent bypassed MCP for canonical write | yes (recovery write at end) | **no** | sub-agent confirmed in report |

The 1190 → 1057 entity drop and 1503 → 1211 relation drop are explained
by grammar drift between the old and new builds (the new
grammar-builder run produced slightly different pattern groups, and the
new code-graph-builder run excluded `docs-v1/` properly — see the open
follow-ups below). Both are within the expected drift envelope.

## Backup chain — qualitative comparison

Old build (broken-state):

```
33 B       → empty  (initial set_graph_path created empty file)
155 B      → 1 entity probe
348968 B   → 1190/1503 (agent wrote disk DIRECTLY, bypassing MCP)
37776 B    → 200/0    (MCP create_entities clobbered after read-empty due to schema bug)
73318 B    → 400/0    (next batch, same pattern)
348968 B   → 1190/1503 (agent recovered by writing disk directly at end)
```

The 348968 → 37776 → 73318 oscillation is the schema-bug fingerprint:
every `save_graph` saw an empty in-memory state (because `read_graph_file`
swallowed `ValidationError`) and overwrote the disk file with just the
current batch.

New build (post-fix):

```
208258 B   → batch 1 landed
232368 B   → +24 KB
257604 B   → +25 KB
281309 B   → +24 KB
304660 B   → +23 KB
330842 B   → +26 KB
338942 B   → +8 KB  (relation chunk)
351047 B   → +12 KB
361100 B   → +10 KB
371246 B   → +10 KB
```

Strictly increasing. Each batch adds entities/relations to a graph
that's already there. This is the expected behavior.

## Open follow-ups

Surfaced by the sub-agent during the build but not in scope for this fix
session.

### 1. `backup_graph` MCP tool errors out
> `TypeError: 'dumps_kwargs' keyword arguments are no longer supported`

This is a Pydantic v2 deprecation. The current implementation passes
`dumps_kwargs` to a v1-style `.json(...)` method that's gone in v2. Fix
is the same pattern we used in A6 for `restore_graph`: replace
`backup_graph.<deprecated dump>(...)` with
`model_dump_json(by_alias=True, indent=2, exclude={'_name_index'})`.
Roughly 3-line change at the relevant tool body. Defer to next fix
session unless the user needs the tool now.

### 2. `create_relations` rejects payloads above ~150 relations per call
The sub-agent reports a Pydantic `ValidationError` masquerading as
`Input should be a valid dictionary` when the `relations` array is
large. The agent worked around it by chunking into 75-relation batches.
Could be a request-size cap, a Pydantic v2 quirk with long string
arrays, or an MCP transport limit. Worth investigating — current chunk
size is fine but understanding the boundary helps future builds.

### 3. Pattern groups not yet in the dispatch table
The agent definition's Step 2 dispatch table omits some pattern groups
that the regenerated grammars include:

- Python: `decorators`, `type_aliases`
- TypeScript: `enums`, `zod_schemas`, `react_routes` (treated as
  observations only — `hooks` was correctly merged into `function`)
- CSS: `css_custom_properties`, `keyframes`, `media_queries`,
  `tailwind_directives`
- Turtle: `datatype_declarations`, `ontology_declarations`

Currently silently skipped per the rule "anything not in this table
goes into observations." Worth a follow-up review of the table — at
minimum, decorator-aware observations on functions and a clear policy
for `enums` / `zod_schemas` would lift the relation count.

### 4. Sub-agent tool-set freezing
When the parent harness disconnects the MCP, sub-agents launched while
the disconnect window is in effect inherit a tool set without MCP
tools. After reconnect, already-launched sub-agents still don't see
them (their tool set is frozen at spawn). The build sub-agent reported
`generate_html_visualization` was not in its tool set — that was
because of timing, not a missing allowlist entry. Mitigation: invoke
sub-agents only when MCP is confirmed live (probe via `reload_graph`
in the parent before spawning).

### 5. JSONL logging is wired only into the new tools
`_log_call` was added module-level. It's wired into `reload_graph` and
`validate_graph`. Wiring it into the seven mutating tools would give a
complete audit trail per build. ~5–10 lines per tool, mechanical.
Defer to next session unless logging gaps become a problem.

### 6. The `_pydantic_extra` warning in `KnowledgeGraph`
Cosmetic; not addressed. Pydantic emits a deprecation warning on
private attributes. Fixable later.

## What this proves

1. The Pydantic alias + shim + loud-error trio fixes the silent-empty
   failure mode that caused the `docs-deprecated/` thrashing.
2. The atomic write + opt-in HTML keeps mid-build state from leaking
   into the canonical artifact.
3. The Step 0.5 preflight + MCP contract in the agent definition kept
   the sub-agent from re-introducing the "write disk directly to
   recover" anti-pattern.
4. The `validate_graph` integrity report (15 → 1 issues) reflects a
   build that is also semantically cleaner — the orphan extends to
   stdlib classes (`TypedDict`, `Enum`, `NamedTuple`, `ABC`,
   `DocumentProcessor`) and self-referential imports were artifacts of
   the previous extractor run and don't appear in the new build.

## Next-session candidates (in priority order)

1. **Fix `backup_graph` Pydantic v2 issue** (3 lines, pattern proven by A6).
2. **Investigate the `create_relations` ~150-row ceiling** (one repro test
   + decide if it's transport, parsing, or a Pydantic v2 quirk).
3. **Wire `_log_call` into the seven mutating tools** (~50 lines total).
4. **Extend Step 2 dispatch table** to cover decorators and zod schemas.

Bigger items from `mcp-improvement-proposal.md` (semantic_search,
AST extraction, `neighborhood`, `graph_query`) remain deferred and
sized appropriately given that this whole fix touched ~150 lines of
the MCP source.
