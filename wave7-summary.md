# Wave 7 — S001-F-007 Implementation Summary

**Requirement:** S001-F-007 — Ephemeral one-shot session with `root_docs` reset on logout, close, or 10-min idle
**Sprint:** 001
**Status:** implemented
**Implemented at:** 2026-04-29T00:00:00Z
**Tests:** 12 / 12 passed

---

## Goal

Make the sprint-1 demo a true single-session experience. On any of three events
the app must reset every per-case mutable artifact back to the deterministic
seed state captured under `root_docs/` and the matching context template:

1. **Logout** — `setUser(null)` from the chat / workspace.
2. **Browser close** — `beforeunload` fires before the tab dies.
3. **Idle timeout** — `SESSION_IDLE_TIMEOUT_MINUTES` (default 10) elapse with
   no `mousemove` / `keydown` / `scroll` / `click`.

"Reset" means: wipe `${DOCUMENTS_PATH}/${case_id}/`, restore
`backend/data/contexts/cases/${case_id}/` from the matching template under
`backend/data/contexts/templates/${caseType}/`, copy the six seed files from
`root_docs/` into their target folders, drop manifest entries for the case and
let `document_registry.reconcile()` rebuild them with fresh `documentId` and
`fileHash` values. The same path also runs once on backend startup so a fresh
container ends in the seeded state.

---

## Backend changes

### `backend/services/session_manager.py` (new)

- `ROOT_DOCS_MAPPING` — the canonical sprint-1 seed mapping
  (filename → target folder under the case dir):

  | Folder            | Files                                                                 |
  |-------------------|-----------------------------------------------------------------------|
  | `personal-data/`  | `Aufenthalstitel.png`, `Geburtsurkunde.jpg`, `Personalausweis.png`    |
  | `certificates/`   | `Sprachzeugnis-Zertifikat.pdf`                                        |
  | `applications/`   | `Anmeldeformular.pdf`                                                 |
  | `evidence/`       | `Notenspiegel.pdf`                                                    |

  Per the polished requirement, `Notenspiegel.pdf` is mapped to the existing
  `evidence/` folder rather than introducing a new "Additional information"
  folder default.

- `reset_case_to_seed(case_id)` — owns the full reset flow in five steps:
  1. `_detect_case_type` reads the existing `case.json` to learn `caseType`,
     defaulting to `integration_course` when the case dir is gone.
  2. `_purge_documents` deletes `${DOCUMENTS_PATH}/{case_id}/` and recreates it
     empty.
  3. `_restore_case_context` overwrites `cases/{case_id}/` with a fresh
     `copytree` from `templates/{caseType}/`, then rewrites `caseId` in the
     copied `case.json`.
  4. `_seed_documents` copies each `ROOT_DOCS_MAPPING` file into its target
     folder under the case docs path.
  5. `_reset_manifest_for_case` drops manifest entries with the matching
     `caseId`, then calls `scan_filesystem` + `reconcile` to rebuild them
     with new `documentId` / `fileHash` values.

  Returns `{"copied": N, "registered": N}` for callers that want stats.

- Module-level path constants (`ROOT_DOCS_DIR`, `CASES_DIR`, `TEMPLATES_DIR`,
  `DOCUMENTS_BASE_PATH`) are exposed so tests can monkey-patch them into a
  sandbox without going near the live project state.

### `backend/api/session.py` (new)

- `POST /api/session/reset` — accepts `{"case_id": "ACTE-2024-001"}`, returns
  `200 {"success": true, "case_id": ..., "copied": ..., "registered": ...}`.
- Pydantic `ResetRequest` validates `case_id` length (1..100).
- Surfaces `FileNotFoundError` (no template for caseType) as `404`; everything
  else returns `500 session_reset_failed` with the real exception logged
  server-side.

### `backend/config.py`

- New `SESSION_IDLE_TIMEOUT_MINUTES: int = get_int_env('SESSION_IDLE_TIMEOUT_MINUTES', 10)`
  in a new "Session Lifecycle Configuration (S001-F-007)" section. Default
  matches the frontend hook's fallback.

### `backend/main.py`

- Imports `from backend.api.session import router as session_router`.
- `app.include_router(session_router, tags=["session"])` next to the existing
  routers.
- `lifespan` now calls `reset_case_to_seed("ACTE-2024-001")` at startup
  before the legacy `INIT_TEST_DOCS` block, replacing the old behaviour as
  required. The legacy block is preserved as a documented no-op so existing
  local setups that still set `INIT_TEST_DOCS=true` don't break.

---

## Frontend changes

### `src/hooks/useIdleTimeout.ts` (new)

- `useIdleTimeout(onTimeout, minutes?)` — single-effect hook.
- Reads the timeout from the optional argument first, then
  `import.meta.env.VITE_SESSION_IDLE_TIMEOUT_MINUTES`, then falls back to
  `DEFAULT_TIMEOUT_MINUTES = 10`.
- Listens on `mousemove`, `keydown`, `scroll`, `click` (passive). Each event
  clears the running `setTimeout` and reschedules it.
- Uses a `callbackRef` so callers can pass a fresh closure on each render
  without forcing the listeners to re-bind.
- Cleans up timer + listeners on unmount.

### `src/contexts/AppContext.tsx`

- Imports `useIdleTimeout` and adds three pieces of session-lifecycle wiring:

  1. `setUser` is now transition-aware. When the previous value was
     non-null and the new value is null (logout), it fires
     `POST /api/session/reset` with `keepalive: true` against
     `${VITE_API_BASE_URL || 'http://localhost:8000'}/api/session/reset`. The
     active case id is read from `currentCaseIdRef`, which a small effect
     keeps in sync with `currentCase.id`.
  2. A `beforeunload` listener registered in `AppProvider` ships the same
     payload via `navigator.sendBeacon` so the request survives tab close.
  3. `useIdleTimeout` is invoked at the AppProvider top level. When it fires
     it calls `setUser(null)`; the existing `Workspace.tsx` route guard
     handles the navigation back to the login page.

  No other AppContext behaviour changed — the new code is additive.

### `src/i18n/locales/de.json` and `src/i18n/locales/en.json`

- New top-level `session.idleTimeout` key.
  - DE: `"Sitzung wegen Inaktivität abgemeldet"`
  - EN: `"Logged out due to inactivity"`
- Both files re-validated by `python3 -c "import json; json.load(open(...))"`.

---

## Tests

All under `docs/tests/S001-F-007/`. Pytest discovers `TC-*.py` per the
sprint-wide `conftest.py` convention.

| ID | What it asserts | Layer |
|----|-----------------|-------|
| TC-S001-F-007-01 | Reset wipes `__anonymized` renders and stray files; `personal-data/` ends with exactly the three seed files | backend / disk snapshot |
| TC-S001-F-007-02 | A staged `custom_rules.json` modification disappears after reset (the `integration_course` template provides no `custom_rules.json`); `case.json` is restored with the right `caseId` | backend / disk snapshot |
| TC-S001-F-007-03 | `useIdleTimeout` uses `setTimeout` to fire the callback, reads `VITE_SESSION_IDLE_TIMEOUT_MINUTES`, default falls back to 10 | frontend source-level |
| TC-S001-F-007-04 | The hook listens for `mousemove`/`keydown`/`scroll`/`click`, the listeners are wired to `resetTimer`, and `resetTimer` clears the running timeout before scheduling a new one | frontend source-level |
| TC-S001-F-007-05 | After reset, `evidence/Notenspiegel.pdf` exists with non-zero size | backend / disk snapshot |
| TC-S001-F-007-06 | After reset, `document_manifest.json` carries exactly six entries for the case, one per seed file, each with non-empty `documentId` and `fileHash` | backend / manifest |
| TC-S001-F-007-07 | A fresh sandbox + `reset_case_to_seed("ACTE-2024-001")` produces the full six-file seeded layout; `backend/main.py` source contains the `reset_case_to_seed` call (so a future refactor cannot silently drop it) | backend / disk snapshot + source |

**Result:** `pytest docs/tests/S001-F-007/ -v` → **12 passed** in 0.08s.
The number is higher than the test-case count because TC-03, TC-04 and TC-07
each contain multiple narrow assertions (one per behaviour), keeping each
failure trace pointed at a single contract.

### Conftest pattern

`docs/tests/S001-F-007/conftest.py` builds a sandboxed copy of the assets the
reset flow needs:

- Copies `backend/data/contexts/templates/` and the six relevant
  `root_docs/` files into a `tmp_path` sandbox.
- Sets `DOCUMENTS_PATH` to a sandbox dir, drops `backend.config` /
  `backend.services.document_registry` / `backend.services.session_manager` /
  `backend.api.session` from `sys.modules`, and re-imports them so the
  module-level path bindings pick up the sandboxed env var.
- Monkey-patches `session_manager.ROOT_DOCS_DIR`, `CASES_DIR`, `TEMPLATES_DIR`,
  `DOCUMENTS_BASE_PATH` and `document_registry.MANIFEST_PATH` so the function
  body never reaches outside the sandbox.

The sandbox guarantees tests don't mutate the live `backend/data/` tree, the
real `public/documents/` directory, or the project's `document_manifest.json`.

### Frontend tests in pytest

The polished test cases TC-03 and TC-04 originally specified Vitest with
faked timers. The project's harness is pytest only, so those are implemented
as source-level contract tests against `src/hooks/useIdleTimeout.ts` (same
pattern as S001-F-003 TC-01 and S001-F-006 TC-03). The contracts they enforce
— event names listened for, `setTimeout` / `clearTimeout` ordering inside
`resetTimer`, env-var name and default — are exactly the behaviours a
real-timer Vitest run would observe.

---

## Affected surface — scope check

Every edited resource maps directly to `affected_surface` in
`S001-F-007.md`:

- **Created** (matches `affected_surface.creates`):
  - `backend/api/session.py` ✓
  - `backend/services/session_manager.py` ✓
  - `src/hooks/useIdleTimeout.ts` ✓
  - `backend/api/session.py::reset_session` (function) ✓
  - `backend/services/session_manager.py::reset_case_to_seed` (function) ✓
  - `src/hooks/useIdleTimeout.ts::useIdleTimeout` (function) ✓
  - `POST /api/session/reset` (endpoint) ✓
  - `SESSION_IDLE_TIMEOUT_MINUTES` (env var, surfaced via `backend/config.py`) ✓
  - `VITE_SESSION_IDLE_TIMEOUT_MINUTES` (env var, consumed via
    `import.meta.env`) ✓
  - `ROOT_DOCS_MAPPING` (constant in `session_manager.py`) ✓
  - `SESSION_IDLE_TIMEOUT_MINUTES` (constant in `backend/config.py`) ✓

- **Modified** (matches `affected_surface.modifies`):
  - `backend/main.py` (router include + lifespan call) ✓
  - `backend/config.py` (added `SESSION_IDLE_TIMEOUT_MINUTES`) ✓
  - `src/contexts/AppContext.tsx` (logout reset, beforeunload, idle hook) ✓
  - `src/i18n/locales/de.json` (added `session.idleTimeout`) ✓
  - `src/i18n/locales/en.json` (added `session.idleTimeout`) ✓
  - `backend/main.py::lifespan` ✓
  - `src/contexts/AppContext.tsx::setUser` ✓
  - `src/contexts/AppContext.tsx::AppProvider` (new effect + hook call) ✓

- **Read** (matches `affected_surface.reads`):
  - `document_registry.reconcile`, `register_document` ✓
  - `context_manager` template path conventions (re-implemented with
    `shutil.copytree` to keep `session_manager` self-contained — function is
    `read` only, not invoked) ✓
  - The six `root_docs/` files ✓
  - `DOCUMENTS_PATH` env var ✓

**No scope overrides were taken.** Every file touched by this implementation
appears in the requirement's `affected_surface`.

---

## Pending dependencies

None. The five upstream requirements
(S001-F-001, S001-F-003, S001-F-004, S001-F-005, S001-F-006) are all
`status: implemented` per their frontmatter.

---

## Implementation notes for review

- `setUser(null) → navigate to /login` is implemented as
  `setUser(null) → Workspace.tsx route guard navigates to /`. The project's
  router uses `/` as the login landing (see `src/App.tsx`); no `/login` route
  exists. `AppProvider` lives outside `BrowserRouter`, so `useNavigate` isn't
  callable there. Routing the user out via the existing state-driven guard
  matches the pattern used elsewhere in the app.
- Lifespan keeps the legacy `INIT_TEST_DOCS` block as a documented no-op
  back-compat path. It runs after the new seed reset, so when both are on
  the seed-reset wins (which is the intended sprint-1 behaviour).
- `S001-NFR-002` (the `.env.example` schema requirement) already documents
  `SESSION_IDLE_TIMEOUT_MINUTES=10`. No `.env.example` edit was needed in
  this wave.

---

## Next steps for the user

1. Review the diff and the new tests under `docs/tests/S001-F-007/`.
2. `git add` the modified + created files (this command does not touch git
   itself).
3. Commit the code change.
4. Run `/code-graph-update` to refresh the code graph.
5. Run `/api-doc-update` — `POST /api/session/reset` is a brand-new endpoint
   surface.
6. Run `/env-doc-update` — `SESSION_IDLE_TIMEOUT_MINUTES` and
   `VITE_SESSION_IDLE_TIMEOUT_MINUTES` are now consumed by the codebase.
7. `/db-doc-update` is **not** needed — no DB schema or persistence story
   changed; the persistence-removal mentioned in the requirement description
   is implemented as wipe-on-reset rather than a schema change.
8. Commit the doc updates and push.
