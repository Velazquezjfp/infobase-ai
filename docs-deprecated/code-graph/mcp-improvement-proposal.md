# Knowledge-Graph MCP — Diagnosis & Improvement Proposal

**Audience:** an AI (or engineer) tasked with extending the
`knowledge-graph-custom-path` MCP server and the `BO-code-graph-builder-updater`
agent that drives it.
**Source data:** observations from a full code-graph rebuild on the
`bamf-acte-companion` codebase (153 files, 1,190 entities, 1,503 relations).
**Status:** the rebuild "succeeded" by the agent's own metrics, yet the
visualization output is incomplete and the graph is missing classes of
relations that downstream agents (impact analysis, doc generation, requirement
grounding) depend on. This document explains why and ranks fixes by impact.

---

## 1. TL;DR — Where the rot is

| Symptom | Layer | Diagnosis |
|---|---|---|
| HTML visualization missing nodes/edges | **MCP, not viz** | `generate_html_visualization` reads from MCP in-memory state, which only held ~800 of 1,190 emitted entities. Disk file is complete. |
| ~33% of emitted entities never reached MCP cache | **MCP** | `create_entities` accepts large batches but silently truncates / drops on partial failure. No partial-success error returned. |
| `set_graph_path` doesn't reload from disk | **MCP** | The path setter only changes where future writes land; it does not hydrate state from the file. So sessions diverge from disk silently. |
| Zero `calls_endpoint`, `calls`, `renders`, `uses_selector` relations | **Extraction** | Regex grammars cannot resolve template-literal URLs, JSX render trees, function-call edges, or DOM selectors. Agent silently dropped them. |
| One bad regex in `css.json` (`\s-:`) silently skipped | **Grammar tooling** | Grammar files are not validated at load time. Bad patterns disappear from the build with no error. |
| `extends` to unresolved target dropped (1 case) | **Resolver** | Forward references and out-of-batch symbols have no lazy-bind step. |

**Net effect:** the graph on disk is *partly* correct, the graph in memory is
*more* incomplete, and the visualization shows the latter. Downstream
consumers (impact analysis, requirement grounding, API/DB doc generators) are
operating on a degraded view of the codebase.

---

## 2. The visualization is a symptom, not the disease

The user reported the HTML viz "doesn't load all dependencies." That is true,
but it is not a viz bug. The chain is:

```
disk (code-graph.json, 1190 entities, complete)
   |
   |  set_graph_path()  -- DOES NOT RELOAD --
   v
MCP in-memory state (~800 entities, stale/partial)
   |
   v
generate_html_visualization()  -- reads in-memory --
   |
   v
graph_visualization.html  (under-populated)
```

Two independent bugs combine here:

1. **Partial writes during build.** The build agent's `create_entities` calls
   succeeded by HTTP/MCP exit code but ~390 entities never landed. No error,
   no log, no replay. This is the dominant data-loss vector.
2. **No reload-from-disk.** Even after a clean rebuild that *did* complete on
   disk, a fresh MCP session pointed at the file via `set_graph_path` does
   not hydrate. So later tool calls (viz, search, statistics) work against
   whatever happened to be in memory.

**Either bug alone would degrade the viz. Both together explain the gap.**

---

## 3. Concrete pain points the build agent hit

These came up during the build and are recoverable signals for what to fix:

1. **Silent batch truncation.** Batches of 10–15 files emitted N entities but
   `get_statistics` reported < N after each push. No `create_entities` call
   returned an error. Agent worked around by keeping its own canonical JSON
   on disk and treating MCP as a write-through cache.
2. **`set_graph_path` is misleading.** Its name implies it points the tool at
   a graph; it actually only redirects future writes. A new agent session
   starting against an existing graph file has to re-emit everything to make
   the cache match. This pattern wastes work and risks duplication.
3. **No idempotent upsert.** `create_entities` is name-keyed but does not
   surface "already exists" cleanly; the agent has to defensively de-dupe
   client-side.
4. **No provenance.** When an observation like `imports:react` lands on a
   file entity, there is no way to know which grammar pattern, which line, or
   which build run produced it. Debugging extraction gaps is guesswork.
5. **Template-literal URLs lose specificity.** `${apiBase}/api/chat/clear/${id}`
   becomes a string blob; the `endpoint` entity it should bind to never
   gets a `calls_endpoint` edge. This is the single biggest reason
   frontend↔backend coupling is invisible in the graph.
6. **JSX is opaque.** `<UserCard user={u} />` should produce a `renders`
   edge from the parent component to `UserCard` and ideally a prop-flow edge.
   Regex cannot do this without false positives. There are 199 components in
   this codebase and **zero** `renders` relations.
7. **Grammar regex compile errors are silently swallowed.** A bad
   `tailwind_directives` pattern (`\s-:` is an invalid character range in
   Python `re`) was dropped during extraction. The build still reported
   success. Grammar quality has no feedback loop.
8. **Unresolved `extends` targets are dropped, not deferred.** Forward
   references (B extends A where A is in a not-yet-scanned file) are
   silently lost. Should be queued and resolved in a second pass.
9. **No filtering/layering in viz.** A 1,190-node force-directed graph is
   unreadable even when complete. The viz needs domain filters
   (frontend-only, API-surface-only, single-feature subgraph).

---

## 4. Capability gaps (what regex + current MCP fundamentally cannot do)

These are not bugs — they are ceiling effects. Fixing them requires new
tooling, not patches.

| Gap | What it blocks | Required capability |
|---|---|---|
| No call graph (function → function) | Impact analysis, dead-code detection, refactor safety | AST-level extraction for Python and TS/TSX |
| No JSX render tree | Frontend impact analysis, prop-flow tracking | TSX AST parser (e.g. ts-morph, swc, babel) |
| No template-literal URL resolution | Frontend↔backend coupling, API consumer tracking | Limited dataflow: track string-typed const assignments and template substitutions |
| No semantic search | "find anything related to authentication" | Embedding index per entity; top-K nearest by vector similarity |
| No declarative graph query | "all functions in module X reachable from endpoint Y" | Cypher-like or Datalog-like query layer |
| No diff between two graph snapshots | Incremental update verification, drift detection | Snapshot diff tool (added/removed/modified) |
| No centrality / cluster metrics | Identifying hot spots, refactor candidates | Graph-algorithm tools (PageRank, betweenness, Louvain) |

---

## 5. Proposed MCP tools (priority-ranked)

### Tier 1 — Correctness (must-have; ship first)

#### 5.1 `reload_graph`
Force MCP to read its current path's JSON file and replace in-memory state.
Optional: make `set_graph_path` reload by default with `reload=true`.

```jsonc
{
  "name": "reload_graph",
  "args": { "from_path": "string?", "validate": "boolean = true" },
  "returns": { "entities_loaded": "int", "relations_loaded": "int", "warnings": "string[]" }
}
```

**Acceptance:** after `reload_graph`, `get_statistics` matches the on-disk
file byte-for-byte (same entity count, same relation count, same observation
count).

#### 5.2 `bulk_upsert_entities` / `bulk_upsert_relations`
Atomic, idempotent, with explicit per-row success/failure return. Replace
the silently-truncating `create_entities`.

```jsonc
{
  "name": "bulk_upsert_entities",
  "args": {
    "entities": [{ "name": "...", "type": "...", "observations": ["..."] }],
    "on_conflict": "merge | replace | skip"
  },
  "returns": {
    "inserted": "int",
    "updated": "int",
    "skipped": "int",
    "failed": [{ "name": "...", "reason": "..." }]
  }
}
```

**Acceptance:** zero silent drops; client can detect partial failure
deterministically.

#### 5.3 `validate_graph`
On-demand consistency check. Reports orphan relations (target missing),
self-loops, duplicate-named entities of different types, broken `extends`,
and observations exceeding size limits.

**Acceptance:** running validate → fixing reported issues → running validate
should converge to zero issues.

#### 5.4 Grammar pre-flight validation (build-side, not MCP)
Add a step in the agent that compiles every regex in every grammar file
before the scan. Bad patterns abort the build with the file, group, and
pattern that failed.

**Acceptance:** the `\s-:` bug is caught before any file is scanned.

---

### Tier 2 — Coverage ceiling (lifts what the graph can express)

#### 5.5 AST-based extractors (replace regex for structural constructs)
Add language-specific extractors that emit:
- Python: function-call edges, decorator argument values, FastAPI router
  binding (decorator → endpoint name resolution), Pydantic field types.
- TypeScript: function-call edges, JSX render edges, hook-call edges,
  `extends`/`implements` resolution, type alias references.

Regex grammars are kept for the simple cases (imports, top-level decls)
and serve as a fast-path. AST is invoked when the regex pass marks an
entity as "needs structural detail."

**Acceptance:** at least 80% of `calls` edges that a human reviewer would
expect appear in the graph for sample modules.

#### 5.6 Template-literal URL resolution
A small dataflow pass: for each `fetch(`url`)` or `axios.get(...)` site,
walk back the variable bindings of any `${...}` substitution within
the file. If they resolve to constants or imported constants, render the
URL to a pattern (e.g. `/api/chat/clear/:id`) and emit `calls_endpoint`.

**Acceptance:** the existing `${apiBase}/api/chat/...` family of URLs
in `AIChatInterface.tsx` produces `calls_endpoint` edges to the
corresponding backend endpoints.

#### 5.7 `semantic_search`
Vector-embed each entity's name + observations on insert. Expose top-K
nearest by cosine similarity to a query string or to another entity.

```jsonc
{
  "name": "semantic_search",
  "args": {
    "query": "string OR { entity_name: string }",
    "k": "int = 10",
    "filter": { "type": "string?", "min_score": "float?" }
  },
  "returns": [{ "name": "...", "type": "...", "score": "float" }]
}
```

**Why this is a force multiplier:** today, finding "everything related to
chat history" requires the agent to grep observations for
"chat|conversation|history" and union manually. With embeddings, one query
returns ranked candidates and the agent spends its context on synthesis,
not search.

**Implementation note:** use a small local model
(e.g. `all-MiniLM-L6-v2`) by default; allow override via env var. Embeddings
recomputed only on insert/update, not on read.

**Acceptance:** for 10 hand-labeled (query → expected entity) pairs,
top-5 recall is ≥ 80%.

#### 5.8 `attach_embedding` / `attach_summary`
Allow an external pipeline (e.g. an LLM-driven enricher) to attach a
natural-language summary or a custom embedding to any entity. This makes
the graph a substrate for AI-augmented documentation, not just static
extraction.

---

### Tier 3 — Query power & visualization

#### 5.9 `neighborhood`
Return the k-hop subgraph around a seed entity, optionally filtered by
relation types and entity types.

```jsonc
{
  "name": "neighborhood",
  "args": {
    "seed": "string | string[]",
    "depth": "int = 1",
    "include_relations": "string[]?",
    "include_types": "string[]?",
    "max_nodes": "int = 200"
  },
  "returns": { "entities": "...", "relations": "..." }
}
```

**Acceptance:** "show me everything within 2 hops of `AIChatInterface`"
returns a bounded, focused subgraph the viz can render legibly.

#### 5.10 `graph_query` (declarative DSL)
A Cypher-subset or Datalog-subset query language. Even a small one is
transformative:

```cypher
MATCH (f:function)-[:calls]->(g:function)
WHERE g.name = 'process_chat_message'
RETURN f.name
```

**Acceptance:** five canonical queries (callers-of, callees-of,
endpoints-touched-by-feature, components-rendering-X, env-vars-read-by-module)
are expressible in <5 lines each.

#### 5.11 `diff_graphs`
Compare two graph snapshots (file paths or named snapshots), return
added/removed/modified entities and relations. Foundation for incremental
updates and for sprint-impact analysis.

**Acceptance:** the existing `update-code-graph` skill can use this to
verify its incremental output matches a full rebuild ± expected drift.

#### 5.12 Layered visualization
The HTML viz takes a `view` parameter that pre-filters before layout:
- `view=api-surface`: endpoints + their direct callers/callees
- `view=frontend`: components + their renders/uses_selector edges
- `view=feature:<name>`: results of `semantic_search` expanded by
  `neighborhood`
- `view=full` (default): current behavior, but with degree-based
  clustering and collapse-by-folder for >300 nodes

**Acceptance:** no view renders >500 nodes by default; user can drill in.

---

### Tier 4 — Analytics

#### 5.13 `compute_centrality`
PageRank, betweenness, in/out degree. Identifies hub modules and
refactoring hot-spots.

#### 5.14 `detect_clusters` (already exists — extend)
Add Louvain / Leiden community detection in addition to whatever is
currently used. Tag each entity with its cluster ID for viz coloring.

#### 5.15 `cycle_check`
Find cycles in the import or call graph. Most have legitimate reasons; a
few are bugs in waiting.

---

## 6. Non-functional requirements

| NFR | Target |
|---|---|
| **Persistence** | Write-through to disk on every mutation, atomic rename. `reload_graph` must be O(seconds) for graphs up to 50k entities. |
| **Determinism** | Same input files + same grammars → byte-identical graph file. Sort entities by name, observations by insertion order, relations by (from, type, to). |
| **Idempotency** | Re-running a build over an unchanged tree produces the same graph and zero log warnings. |
| **Observability** | Every tool call logs to a structured file (`mcp.log.jsonl`): tool name, args summary, timing, in/out cardinality, errors. |
| **Concurrency** | At least one writer at a time (file lock). Readers always consistent (no torn reads of relations referencing deleted entities). |
| **Error contract** | No silent drops anywhere. Partial failure is always reported per row. |
| **Performance** | Sub-second response for `search_nodes`, `neighborhood(depth=2)`, `get_statistics` on graphs up to 50k entities. Bulk upsert of 10k entities in <5s. |
| **Schema enforcement** | Reject entities with unknown types unless registered. Allow declaring custom types per project (config file). |

---

## 7. Priority-ordered roadmap

| Tier | Items | Justification |
|---|---|---|
| **P0 — Correctness** | 5.1 reload_graph · 5.2 bulk_upsert_* · 5.3 validate_graph · 5.4 grammar regex preflight · NFR observability | Without these, every other improvement builds on quicksand. The viz bug, the silent drops, and the silently-skipped grammars all live here. |
| **P1 — Coverage** | 5.5 AST extractors · 5.6 template-URL resolution · 5.7 semantic_search | Lifts what the graph can *express*. Semantic search alone changes how every downstream agent works. |
| **P2 — Query/Viz** | 5.9 neighborhood · 5.10 graph_query DSL · 5.11 diff_graphs · 5.12 layered viz | Makes the graph *useful* to a human and to LLM consumers. |
| **P3 — Analytics** | 5.13 centrality · 5.14 clusters · 5.15 cycles · 5.8 attach_embedding/summary | Nice-to-have. Defer until P0–P2 are solid. |

---

## 8. What NOT to do (scope discipline for the implementer)

- **Do not** rewrite the regex grammars to try to capture call graphs or
  JSX trees. They will get worse, not better. AST is the right answer.
- **Do not** push embedding generation into the agent runtime. It belongs
  in the MCP server's insert path so it happens once, not per query.
- **Do not** introduce a database (Neo4j, Postgres, DuckDB) until P0/P1
  are done in-memory + JSON. The performance ceiling for 10k–50k entities
  is fine in-process. A DB adds operational weight that is not yet
  justified.
- **Do not** ship Cypher full — a five-clause subset is enough for 95% of
  consumer queries.
- **Do not** wire the agent to call the same tool sequentially when
  `bulk_upsert` is available. Round-trip cost dominates at this scale.

---

## 9. Acceptance criteria for "the bamf-acte-companion graph is healthy"

Concrete checks to run after the improvements land:

1. `reload_graph` followed by `get_statistics` returns 1,190 entities and
   1,503 relations (current canonical numbers; will grow).
2. `generate_html_visualization` produces an HTML that includes every
   node in `code-graph.json`.
3. `semantic_search("chat history persistence")` returns
   `AIChatInterface.tsx`, the chat router, and the chat models in the top 5.
4. `neighborhood(seed="POST /api/chat", depth=2)` returns the
   frontend caller (`AIChatInterface`), the FastAPI router, the service
   class, and the Pydantic request/response models — i.e. the full
   end-to-end slice of one feature.
5. AST extraction emits ≥ 1 `renders` edge for at least 80% of
   non-leaf React components in `src/components/`.
6. Template-URL resolution emits a `calls_endpoint` edge for every
   `${apiBase}/api/...` site in `AIChatInterface.tsx`.
7. Running a full rebuild twice in a row produces byte-identical
   `code-graph.json` files.
8. `validate_graph` reports zero issues on a clean build.

---

## 10. One paragraph for the implementer

> The MCP today is a thin in-memory store with file persistence bolted on,
> driven by a regex-only extractor. It loses data on the write path, can't
> rehydrate from disk, has no error contract, and has no semantic layer.
> Fix the write path first (P0), then lift the extractor's ceiling with AST
> + template-URL resolution and add semantic search (P1), then make the
> graph queryable and viewable (P2). Don't introduce a database until
> P0–P2 are stable. The single most valuable new capability for AI
> consumers of this graph is `semantic_search` — invest in it once
> correctness is solid.
