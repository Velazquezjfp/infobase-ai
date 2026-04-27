# MCP Knowledge-Graph — Forensic Q&A and Corrected Diagnosis

**Companion to:** `mcp-improvement-proposal.md`.
**Status:** This document **corrects** parts of the original proposal that
were based on the build agent's self-reported framing. After reading the MCP
server source and the on-disk evidence directly, the actual root cause is
different from (and simpler than) what the original proposal claimed. The
priority list still holds in spirit; the "in-memory vs disk" framing does
not.

**Evidence used:**
- MCP source: `~/clients/personal/mcp-services/KG/linux-kg/Local-KnowledgeGraph/knowledge_graph_mcp_custom_path.py`
- On-disk graph: `docs/code-graph/code-graph.json` (1,190 entities, 1,503 relations)
- HTML viz: `docs/code-graph/graph_visualization.html` (embeds 800 nodes, 0 links)
- Backup chain: `docs/code-graph/backups/*.bak` (6 snapshots from build)
- Agent memory: `.claude/agent-memory/code-graph-builder/mcp-quirks.md`
- Live MCP probes done while writing this doc

---

## 0. Executive correction

The original proposal said the MCP holds an in-memory cache that diverges
from disk. **That was wrong.** Reading the source confirms:

> Every MCP tool calls `read_graph_file()` at its entry point. There is no
> persistent in-memory cache. The "divergence" was caused by a single
> schema mismatch that makes `read_graph_file()` silently return an empty
> graph for the on-disk file.

The actual root cause is one bug in 6 lines of code:

```python
class Relation(BaseModel):
    from_: str          # <-- field name, no alias
    to: str
    relationType: str
```

…combined with this fall-back in `read_graph_file()`:

```python
except (json.JSONDecodeError, ValueError):
    return KnowledgeGraph()    # ValidationError IS a ValueError → swallowed
```

The disk file uses `"from"` as the JSON key (because that's the natural
JSON-RPC field name). The model expects `"from_"`. With
`model_config = {"extra": "ignore"}`, Pydantic silently drops `"from"`,
then fails because required field `"from_"` is missing. The exception is a
`ValidationError`, which is a `ValueError`, which is caught and converted
to "empty graph". So MCP reads the file, sees nothing, and proceeds.

I reproduced this directly:

```
Disk -> entities: 1190, relations: 1503
ValidationError (1503 errors). First 2:
  {'type': 'missing', 'loc': ('relations', 0, 'from_'), 'msg': 'Field required',
   'input': {'from': 'backend/api/admin.py', ...}}
After renaming 'from' -> 'from_': 1190 entities, 1503 relations
```

This single bug explains:
- Why the HTML viz captured a degraded state.
- Why "390 entities went missing."
- Why `set_graph_path` "doesn't reload from disk" (it actually does — the
  disk just looks empty due to the schema mismatch).
- Why the agent built a Python extractor and wrote disk directly: it was
  routing around an MCP that couldn't see its own files.

The rest of this document goes block-by-block through your questions with
the evidence I could verify, and explicitly marks the questions I can't
answer because I delegated the build and don't have the raw trace.

---

## Block 1 — Write-loss mechanism

> ~390 entities never landed. Concurrent writes? Transport timeouts?
> Something else?

**Verified facts:**
- The disk file currently has **1,190 entities and 1,503 relations**. So
  nothing is "missing on disk."
- The HTML viz on disk embeds **800 nodes and 0 links**. The "390 missing"
  was about the HTML, not about the canonical graph.
- Backup chain (chronological mtimes):

  | Time     | File size  | Entities | Relations | Likely cause                                 |
  |----------|-----------:|---------:|----------:|----------------------------------------------|
  | 22:59:54 | 33 B       | 0        | 0         | First touch — `set_graph_path` to new file   |
  | 23:04:03 | 155 B      | 1        | 0         | Agent wrote a `_probe_` entity to test       |
  | 23:08:07 | 348,968 B  | **1190** | **1503**  | Agent wrote full graph **directly via Python** |
  | 23:11:36 | 37,776 B   | 200      | 0         | MCP `create_entities` clobbered file         |
  | 23:15:42 | 73,318 B   | 400      | 0         | MCP `create_entities` clobbered again        |
  | 23:15:42 | (HTML)     | 800      | 0         | HTML auto-regen captured a later batch       |
  | 23:16:05 | 348,968 B  | **1190** | **1503**  | Agent wrote full graph back directly (recovery) |

  This is not write contention. It is the **schema bug** in action: every
  MCP write reads the disk, sees empty (due to validation failure), adds
  the new batch, and saves a file that is now strictly smaller than what
  was on disk before. The agent recovered by writing the canonical graph
  back at the end.

**Concurrent writes / overlapping calls:** I cannot answer with
certainty — the build was a delegated sub-agent and I don't have its raw
tool-call timeline. But:
- `ps -ef` shows a single MCP process (PID 6760). One server, one writer.
- No other agent sessions ran during the build.
- The Pydantic model rejects the on-disk schema, so even strictly serial
  writes would have produced the observed pattern. **You don't need
  concurrency to explain this.**

**Transport timeouts:** No evidence in the trace I can see (HTTP/JSON-RPC
errors would have surfaced in the agent's report). The schema bug alone
suffices.

**`{"status": "success", "added": N}`:** Looking at `create_entities`
(line 774–808), even when the disk read returns empty, the response
returns `"added": len(new_entities)` — which is the count of *new* entities
added relative to **the empty in-memory graph**, not relative to what was
on disk. So responses always look successful even when the operation has
just truncated the file.

**Maximum batch size / payload limits:** Per agent memory:
> "Pasting big JSON payloads inline to `create_entities` is expensive —
> the MCP echoes every entity back. For a ~1200-entity graph, budget for
> six 200-entity batches (~25 KB in, ~25 KB out each). Bigger batches
> (400 entities ~50 KB) also work."

So batches up to ~400 entities work. No transport-level limit was hit.
The pain was throughput (large echo) and the silent clobber, not size.

**Could `get_statistics` numbers change between consecutive calls without
mutations?** Yes if the disk changes, no otherwise — there's no cache to
go stale.

**Could the on-disk count decrease between two reads?** Yes — every
`save_graph()` overwrites the file (no atomic temp+rename), and with the
schema bug, every save can reduce the on-disk count.

---

## Block 2 — HTML generation as hidden cost

> Auto-HTML on every save is a major hidden cost. Need data.

**Verified facts:**
- `save_graph` (line 132–159) **always** regenerates the HTML when there
  are entities present. There is no toggle from outside. The internal
  call `_generate_html_visualization_internal(graph, file_path)` rebuilds
  the entire D3 payload by iterating every entity and every relation.
- The HTML on disk is **236 KB**, embeds 800 nodes and 0 links. So per
  save, the cost is "iterate graph, build node and link dicts, format a
  ~250 KB string template, write file." For 800 entities this is
  sub-second on modern hardware. For 10–50k entities it would become
  noticeable.
- Worse than the wall time: **every save invalidates the HTML semantics.**
  The HTML reflects whatever the in-progress build state was at that
  moment, not the canonical end state. Anyone opening the HTML mid-build
  (or after a build that ended via the agent's direct-write recovery)
  sees a stale snapshot.

**Browser behavior on the actual HTML file:** I haven't tested in a
browser from this session. But: 800 nodes in D3 force layout is heavy but
typically renders in a few seconds. 1,190 nodes (the canonical count)
would render but be visually unusable without filtering. >5,000 nodes will
hang the browser.

**Pauses / hangs during the build:** Cannot answer from this session —
delegated to a sub-agent. The likely culprits if any: the inline echo of
each batch in JSON-RPC responses, plus the auto-HTML regen on every save.
Together those make each `create_entities(N=400)` call do O(graph_size)
work per call.

**Specific recommendation:**
- Make HTML auto-generation **opt-in** via an `auto_generate_html` flag on
  the request, defaulting to `False`. Add an explicit
  `generate_html_visualization` tool (already exists at line 1875) that
  the agent can call once at the end.
- Or: regenerate the HTML only if the graph entity count changed by >N%
  since the last regen.

---

## Block 3 — The "in-memory state" claim

> I read the source and don't see a persistent in-memory cache — every
> tool call reads from disk fresh. Want to verify.

**You are correct. The original proposal was wrong on this point.**

**Source-level confirmation:**

```python
# Line 91 — the only "memory" is a single global string:
_custom_graph_path = None
```

Every tool entry point follows the same pattern:

```python
@mcp.tool()
def get_statistics() -> Dict[str, Any]:
    try:
        graph = read_graph_file()        # <-- always fresh from disk
        ...
```

`read_graph_file()` opens the file every time, parses with Pydantic, and
returns a fresh `KnowledgeGraph` object. There is no module-level graph
state.

**`set_graph_path` does not reload:** True, but for a different reason
than I claimed. It doesn't need to reload — it just updates
`_custom_graph_path`, and the next tool call will hit the new path via
`read_graph_file()`. The reason it *appears* not to reload is because the
file at the new path **fails validation** and is treated as empty.

**Concrete trace I just ran (Sat 2026-04-27, in this session):**

```
1. get_current_graph_path()
   → /home/javiervel/.knowledge_graph/graph.json  (default, unrelated graph)

2. get_statistics()
   → 7 entities (FastMCP/gcloud blueprint stuff, persisted from a prior session)

3. set_graph_path("/home/.../docs/code-graph/code-graph.json")
   → success

4. get_statistics()
   → 0 entities, 0 relations    ← APPARENT DIVERGENCE

5. search_nodes({"query": "AIChatInterface"})
   → matchCount: 0              ← entity exists in disk file, MCP can't see it

6. Manual reproduction with the same Pydantic models against the disk file:
   → ValidationError, 1503 errors, all "missing required field 'from_'"
   → After renaming 'from' → 'from_' in memory, model_validate succeeds
     and returns 1190 entities and 1503 relations.
```

So:
- Step 4's "0 entities" is not because MCP failed to load — it's because
  it loaded, hit `ValidationError`, fell to the bare `except` clause, and
  returned `KnowledgeGraph()` (empty).
- The disk file is correct; the model is incompatible with it.

**Where the agent's `from`-vs-`from_` note came from:** The agent memory
file (`mcp-quirks.md`) claims:
> "Relation key must be `from` not `from_`. The python JSON dump default
> of `from_` for the `from` keyword will cause pydantic validation errors
> at the MCP layer."

This is the **opposite** of what Pydantic actually does in this codebase.
Pydantic v2 with `from_: str` and no alias **rejects `from` and accepts
`from_`**. I verified this directly:

```
Accepts {'from_': 'A'}: YES
Accepts {'from':  'A'}: NO (ValidationError)
```

So the agent's note is wrong. The agent likely tried both, got mixed
results (perhaps because it was sometimes writing the file directly with
`"from"` and sometimes through MCP with `"from_"`), and locked in the
wrong rule. The disk file ended up with `"from"` because it was written
directly by the extractor's own `json.dump`, not by MCP's `save_graph`.

**This entire situation is a 30-line fix.** See Block 8 for the patch.

---

## Block 4 — Grammar pipeline

> How does the build agent consume the grammar JSON? What happens on
> regex compile failure?

**Cannot fully verify — the extractor script (`/tmp/extract_graph.py`)
was deleted after the build.** What I can say:

- Grammars in `docs/bamf-acte-companion_grammars/{python,typescript,css,turtle}.json`
  are well-formed JSON. Each contains a `patterns` dictionary keyed by
  semantic group (e.g. `react_components`, `api_endpoints`).
- The build agent's report named the bad regex: `tailwind_directives` in
  `css.json`, with `\s-:` inside a character class — Python's `re` rejects
  this with `re.error: bad character range`.
- Inspecting `css.json` confirms: the pattern `r'@apply\s+([\w\s-:/[\]]+)'`
  has `[\w\s-:/[\]]` where `s-:` reads as "characters in range from `s`
  to `:`," which is invalid because `s` (0x73) is greater than `:` (0x3a).
- The agent reported the build still completed with 0% parse failures and
  the bad pattern was "skipped." This implies the extractor wraps each
  `re.compile` in try/except and silently drops bad patterns, then continues.
  That is a reasonable but **error-hiding** policy. It should fail loud
  on grammar load, not silently at extract time.

**Were grammars Context7-enriched?** Yes. The grammar-builder report listed
Context7 as fetched for all JS/Python frameworks. SHACL/OWL were marked
unavailable. None of the consumed grammar files have a
`context7_status: "unavailable"` mark on a pattern that was actually used.

**Number of grammar files / patterns:**
- 4 grammar files (python, typescript, css, turtle)
- ~44 pattern groups across them (per the grammar-builder report)
- I did not count individual regex literals across files, but it's on
  the order of 100–150 patterns total.

---

## Block 5 — Extraction completeness

> Zero `renders` edges, missing `calls_endpoint`, dropped `extends`,
> verify the entity-type breakdown.

**Verified directly from the disk file:**

```
Total entities: 1190
  function:  520
  class:     213
  component: 199
  file:      153
  constant:   49
  endpoint:   36
  selector:   12
  env_var:     8

Total relations: 1503
  defines:  1029
  imports:   298
  contains:  148
  reads_env:  18
  extends:    10
```

**Confirms:**
- `imports` + `defines` + `contains` = 1,475 of 1,503 (98%). Bridges
  (`calls`, `calls_endpoint`, `renders`, `uses_selector`,
  `queries_table`) are zero. This is the regex ceiling.
- 199 components × 0 `renders` edges = no frontend render tree.
- 36 endpoints × 0 `calls_endpoint` edges = no frontend↔backend coupling.
- 18 `reads_env` for 8 env_vars = avg 2.25 readers per env var (reasonable).

**Zero `renders` was extraction-not-attempted, not extraction-failed.**
The TypeScript grammar's `react_components` pattern group exists
(I see it referenced in the grammar-builder report's typescript.json
groups list). But it identifies *which entities are components* — it does
not extract render edges. Render-edge extraction would require parsing
the JSX `<Foo prop={x} />` syntax inside a component body, which the
grammar doesn't have a pattern for, and which regex cannot do reliably.

**`calls_endpoint`:** The agent's notes say frontend fetches use
template-literal URLs (`` `${apiBase}/api/chat/clear/${id}` ``) that don't
statically resolve. The grammar likely has `fetch(...)` patterns; their
matches were stored as `api_call:<literal>` observations on the file
entity rather than as relations. So extraction *attempted* it and degraded
to observation-only.

**Dropped `extends`:** I haven't pinpointed which exact pair was dropped;
identifying it would require reproducing the extractor. The MCP-side
`create_relations` (line 822–840) does enforce both endpoints to exist
and silently drops relations whose endpoints are missing
(`missing_entities` is built but only logged in the response, not
persisted as a deferred-resolution queue). Forward references die there.

---

## Block 6 — Concurrency and process model

**Verified:**
- `ps -ef | grep mcp` during this session shows **one** MCP process
  (PID 6760), running since 10:40 today. The MCP did not restart between
  the build and now.
- No other agent sessions or scripts wrote to the graph file during the
  build window. The only writers were the build sub-agent (sometimes via
  MCP, sometimes via direct `json.dump` to disk) and MCP's own
  `save_graph` triggered by the agent's calls.
- `set_graph_path` was called at least once during the build (the agent
  set it before its first `create_entities` call). I cannot determine
  whether it was called multiple times — likely once.

**No concurrency exists.** The race-condition framing is not what's
happening here.

---

## Block 7 — Scale calibration

**`bamf-acte-companion` ended at 1,190 entities / 1,503 relations on a
codebase of 153 in-scope files.** That's ~7.8 entities/file, ~9.8
relations/file — low because the relations are dominated by
`defines`/`imports` and lack any call or render edges.

**With AST extraction added,** my estimate:

| What gets added                               | Multiplier (est.) |
|-----------------------------------------------|------------------:|
| Function-call edges (`calls`)                 | +500–1,500 relations  |
| JSX render edges (`renders`)                  | +400–1,000 relations  |
| Resolved `calls_endpoint` from template URLs  | +30–100 relations     |
| Hook-use edges (`useState`, `useEffect`, …)   | +200–500 relations    |
| Pydantic field types as type-ref edges        | +100–300 relations    |

**Realistic post-AST scale for this project:** 1,200–1,500 entities and
**3,000–5,000 relations**. So a 2–3× multiplier on relations, 1× on
entities. Not 10×.

**Other client codebases:** I have no visibility. Open question —
worth checking other repos before designing the v2 size envelope.

**Have any reached >5,000 entities?** Not in this codebase. I cannot
speak for others.

**Sizing recommendation for v2:** Design for graphs of 5,000–20,000
entities and 20,000–100,000 relations. Every operation should be O(log N)
or O(N) in graph size, not O(N²). The current MCP's per-call
`read_graph_file → parse JSON → linear scan` is fine up to ~5k entities
on disk; beyond that you'll want either lazy parsing or an indexed store.

---

## Block 8 — Path forward

> Single biggest friction. One new tool you'd want first. Read-from-disk
> vs in-memory. AST stack preference.

### 8.1 Single biggest friction

**The schema bug + silent ValidationError-as-empty fall-back.** Every
other pain point I named in the original proposal was a symptom of this.
Once a single tool call fails to parse the file, every subsequent write
operation truncates it. The build was unwinnable until the agent
side-stepped MCP entirely.

### 8.2 One new tool, before any AST work

Not from the original list. The most valuable single change is to **make
the existing tools actually work on existing files**:

```python
# Line 117 — current
def read_graph_file() -> KnowledgeGraph:
    file_path = get_graph_file_path()
    if not file_path.exists():
        return KnowledgeGraph()
    with open(file_path, "r") as f:
        try:
            data = json.load(f)
            graph = KnowledgeGraph.model_validate(data)
            graph._name_index = {e.name.lower(): i for i, e in enumerate(graph.entities)}
            return graph
        except (json.JSONDecodeError, ValueError):
            return KnowledgeGraph()        # <-- silent failure here
```

```python
# Proposed
def read_graph_file() -> KnowledgeGraph:
    file_path = get_graph_file_path()
    if not file_path.exists():
        return KnowledgeGraph()
    with open(file_path, "r") as f:
        data = json.load(f)        # let JSONDecodeError surface
    # Normalize legacy 'from' → 'from_' before validation
    for r in data.get("relations", []):
        if "from" in r and "from_" not in r:
            r["from_"] = r.pop("from")
    graph = KnowledgeGraph.model_validate(data)   # let ValidationError surface
    graph._name_index = {e.name.lower(): i for i, e in enumerate(graph.entities)}
    return graph
```

And on the model:

```python
class Relation(BaseModel):
    from_: str = Field(alias="from")
    to: str
    relationType: str
    model_config = {"populate_by_name": True}
```

This:
- Accepts both `"from"` and `"from_"` from incoming requests.
- When dumping, emits `"from"` (per alias), matching what's already on disk
  and matching the JSON-RPC field name everywhere else.
- Stops swallowing validation errors. **If the file is corrupt, fail loud.**

That single PR (~30 lines including tests) fixes the visualization bug,
the silent truncation, and the agent's need to bypass MCP for the canonical
write. Everything else in the original proposal is real but downstream of
this.

If after that you want one **new** tool, I'd pick:

**`reload_graph(path?)` → `{entities, relations, warnings[]}`.** Even
though every tool already reads fresh from disk, an explicit reload tool
serves two purposes: (a) lets the agent verify the path it just set is
parseable, surfacing errors *before* it starts writing batches; (b) gives
a clear signal to humans about what state MCP sees. Currently the only
way to check is to call `get_statistics` and infer. Make it explicit.

### 8.3 Read-from-disk vs in-memory cache

**Keep read-from-disk for now.** Reasons:
- The current model is correct, just brittle around schema. Fix the
  brittleness, keep the simplicity.
- File size for this codebase is 348 KB. Even at 5× (post-AST) it's under
  2 MB. JSON-parsing 2 MB is sub-100ms.
- An in-memory cache forces invalidation logic, which is the harder
  problem.
- Atomic writes (write-temp-then-rename) plus an OS-level lock during
  save are sufficient for safety.

**Reconsider when:**
- Graph crosses ~50k entities (parse cost begins to matter).
- You need sub-100ms `neighborhood`/`semantic_search` queries on hot paths.
  At that point switch to a process-resident in-memory model with explicit
  reload, not a JSON-on-every-call model.

The original proposal's framing ("MCP holds in-memory state separate from
disk") was wrong. I retract that part.

### 8.4 AST stack — tree-sitter vs language-native

**Recommendation: language-native, in two repos.**

- **TypeScript/TSX:** use `ts-morph` (built on the TypeScript compiler
  API). Stronger semantics than tree-sitter — you get type information,
  resolved imports, JSX attribute types, and the same module-resolution
  semantics the editor uses. Run as a Node sidecar, expose a tiny stdin/stdout
  protocol for the Python MCP to call into. Or rewrite the relevant MCP
  tools in TS.
- **Python:** use the stdlib `ast` module + `astroid` for cross-module
  resolution if needed. Free, mature, deterministic.

Tree-sitter is right when you have a long tail of languages to support
(Go, Rust, Ruby, Java, etc.). For a Python+TS shop, you spend more time
fighting tree-sitter's loose semantics than you save in setup time. The
"broad language support" win is hypothetical; the "weak semantics" cost
is real (e.g., tree-sitter cannot tell you what type a JSX prop is, so
prop-flow extraction stays heuristic).

**Cost-aware order:**
1. Python `ast` extraction first — stdlib, single import, immediate
   payoff (call graph + decorator arg resolution + Pydantic type extraction).
2. TS-morph integration second — needs a sidecar process and a JSON-RPC
   thin layer, but gives you the JSX render tree and resolved
   template-URL endpoint binding. **Highest impact** for this codebase.
3. Tree-sitter as a fall-back for any future language only after both
   above are stable.

### 8.5 Fork or patch?

**Patch.** The `from`-alias fix + a few of the proposal's P0 items
(observability, validate_graph, optional auto-HTML, atomic writes) are a
1–2 day surface change. The MCP's design is sound; it just has bugs.

Fork (or build a new MCP) **only if** you commit to AST extraction and
semantic search as core features. Those are different code, a different
performance envelope, and arguably a different name (e.g.
`code-graph-mcp` instead of generic `knowledge-graph-mcp`). At that point
the existing MCP becomes a "general KG store" alongside the new
"code-aware KG store," and the new one inherits little from the old.

---

## Block 9 — Things missed

### 9.1 Backup-pruning hides build evidence

`save_graph` keeps only the last 10 `.bak` files. A long build can churn
through more than that and prune the early evidence, making post-mortems
harder. For diagnostic builds it would be useful to either disable pruning
or move it to a `cleanup_backups` tool.

### 9.2 Auto-HTML on every write made the build act like a leaky abstraction

The agent had no way to opt out. So every batch insert paid the
visualization cost AND produced a partial HTML. By the time the build
finished, the HTML on disk reflected the last MCP-driven save, not the
canonical end state. That's the "viz looks broken" complaint — it was
right, just for a different reason than I claimed.

### 9.3 The agent's workaround introduced its own issues

To work around the silent-clobber, the agent wrote the canonical graph
file directly via Python and ran MCP only for ingestion attempts. This:
- Made the MCP's HTML reflect a stale partial state (the last MCP save).
- Burned ~3× the work — extractor wrote disk, then MCP read disk (saw
  empty), then MCP wrote disk (truncated), and the agent had to write
  disk again to recover.
- Left a `from`-vs-`from_` myth in the agent memory file that will
  mislead the next builder agent unless we correct it.

I'd suggest correcting the agent memory file to reflect the actual
behavior:
- "The MCP rejects `from` and accepts `from_` in incoming requests."
  (Opposite of what's currently written.)
- "MCP's `read_graph_file` swallows `ValidationError` as empty graph.
  Until the schema is fixed, never write the canonical file directly
  with `from` — MCP will overwrite it with an empty graph on the next
  mutation."

### 9.4 No build-side preflight

The build agent did not check whether MCP could parse a known-good file
at the start. A 5-line preflight (write a sentinel, set path, re-read,
assert nonzero entity count) would have caught the schema bug in the
first 30 seconds of the build instead of at hour 1.

### 9.5 `endpoint` entities have no path information attached

Endpoint entities are named like `backend/api/chat.py::clear_chat` (file
+ function), not `POST /api/chat/clear/{id}` (HTTP method + URL pattern).
This means the graph cannot be queried by route. The route information
exists in the source (FastAPI `@router.post("/...")`) but the grammar
extracts it as an observation, not as the entity name. Fixing this is a
build-agent change, not an MCP change.

---

## Synthesis — the actually-corrected priority list

**P0 — One PR, ~30 LOC + tests, fixes the visualization gap and the
silent clobber:**
1. Add `Field(alias="from")` and `populate_by_name=True` to `Relation`.
2. Stop swallowing `ValidationError` in `read_graph_file`. Bubble up.
3. Add legacy normalization (`"from"` → `"from_"`) so existing files load.
4. Make `save_graph(auto_generate_html=False)` the default; add an
   `auto_html` kwarg the build agent can opt into at the end of the build.
5. Atomic write: write to `<file>.tmp`, then rename. Removes torn-write
   risk during interrupted builds.

**P1 — A second small PR, ~200 LOC + tests, agent ergonomics:**
1. `reload_graph` tool — explicit path verification.
2. `validate_graph` tool — orphan relations, missing endpoints, duplicate
   names.
3. Structured logging to `mcp.log.jsonl` per call (tool name, args sketch,
   timing, in/out cardinality, errors).
4. Replace the bare `except: return empty` everywhere with explicit error
   responses.

**P2 — A real feature push: semantic + structural extraction.** Pick this
*only after* P0/P1 land and a clean rebuild proves the agent can drive
MCP straight through (no direct-write workaround).
1. Python AST extractor: function-call edges, decorator arg resolution.
2. TS-morph sidecar: JSX render edges, template-URL → endpoint binding.
3. Embedding-on-insert + `semantic_search`. Local model, computed once
   per entity, stored in graph as `_embedding` (excluded from default
   serialization).

**P3 — Power tools for AI consumers:**
1. `neighborhood(seed, depth)` — bounded subgraph extraction.
2. `graph_query` — Cypher-subset DSL.
3. `diff_graphs` — snapshot comparison.

**P4 — Analytics:**
1. Centrality / cluster / cycle detection.
2. Layered visualization with view filters.

---

## What I would tell the next agent reading this

> **The MCP is not buggy in the way the original proposal said.** It is
> simple and read-fresh-from-disk and that is fine. There is one schema
> mismatch on the `from`/`from_` field that, combined with one bare
> `except` clause, makes every read of a canonical graph file return
> empty. Fix that one bug and the MCP becomes usable as-is. After that
> one PR, decide whether you want to *extend* it (add semantic search,
> AST extraction) — and if so, that is a net-new effort, not a fork.
>
> Do not write the canonical graph file directly to disk and expect MCP
> to read it correctly until the schema bug is fixed. The temptation to
> do so (it works, you "see" the file with the right contents) was the
> single biggest source of confusion in this build.
