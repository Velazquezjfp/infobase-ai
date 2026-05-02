# Wave 7 — S001-F-009 Implementation Summary

**Requirement:** S001-F-009 — Resolve documented anti-patterns in API and environment surfaces
**Sprint:** 001
**Status:** implemented
**Implemented at:** 2026-04-29T16:15:58Z
**Tests:** 17 / 17 passed

---

## What this requirement resolved

Three duplications/inconsistencies the current-state docs flagged before the closed-environment deployment:

1. **Duplicate Vite env vars** — six modules read `VITE_API_URL`, four read `VITE_API_BASE_URL`, both with the same fallback. Consolidated to a single canonical name `VITE_API_BASE_URL`, sourced once from `src/lib/apiConfig.ts`.
2. **Duplicate `ErrorResponse` schema** — defined separately in `backend/api/admin.py` and `backend/api/files.py`. Moved the canonical `ErrorResponse` to `backend/api/_shared.py`; `files.py` extends it with `FileErrorResponse(ErrorResponse)` adding `file_name`.
3. **Misleading `gemini_initialized` health-check field** — closed-environment deployments may run on LiteLLM, so the name implies the wrong backend. Added a sibling `llm_backend` field populated from `get_provider().__class__.__name__` (or `"unconfigured"`). `gemini_initialized` is preserved unchanged for backward compatibility.

---

## Files

### Created
- `src/lib/apiConfig.ts` — `export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"`
- `backend/api/_shared.py` — canonical `ErrorResponse` and `FileErrorResponse`
- `docs/tests/S001-F-009/conftest.py`
- `docs/tests/S001-F-009/TC-S001-F-009-01.py` through `TC-S001-F-009-06.py`

### Modified

**Frontend (migrated to import `API_BASE_URL` from `@/lib/apiConfig`):**
- `src/components/workspace/AdminConfigPanel.tsx`
- `src/components/workspace/AIChatInterface.tsx`
- `src/components/workspace/CaseContextDialog.tsx`
- `src/components/workspace/CaseTreeExplorer.tsx`
- `src/components/workspace/ContextHierarchyDialog.tsx`
- `src/components/workspace/SubmitCaseDialog.tsx`
- `src/components/workspace/DocumentViewer.tsx`
- `src/lib/adminApi.ts`
- `src/lib/fileApi.ts`
- `src/contexts/AppContext.tsx`

**Backend:**
- `backend/api/admin.py` — removed local `ErrorResponse`; imports from `_shared`
- `backend/api/files.py` — removed local error class; `responses=` decls now reference `FileErrorResponse`
- `backend/api/chat.py` — adds `llm_backend` to `GET /api/chat/health`
- `backend/api/search.py` — adds `llm_backend` to `GET /api/search/health`
- `backend/api/validation.py` — adds `llm_backend` to `GET /api/validation/health`; also fixed a pre-existing bug where the handler referenced `service._gemini_service` (the attribute is `_provider` after the S001-F-001 refactor)

**Requirement frontmatter:**
- `docs/requirements/sprint-001/S001-F-009.md` — set `status: implemented`, added `implemented_at`, `tests_passed_at`, `tests_total`, `tests_passed`, `tests_failed`

### Notes on scope
- `src/components/workspace/FormViewer.tsx` was listed in `affected_surface.modifies` but uses relative URLs only (no `VITE_API_*` reference), so no change was needed.
- The validation-health attribute fix (`_gemini_service` → `_provider`) was an in-scope correction on a file already in `affected_surface.modifies`; without it, `TC-S001-F-009-04` for the validation endpoint cannot pass.

---

## Acceptance-criterion checklist

| Criterion | Status |
|---|---|
| `src/lib/apiConfig.ts` exists and exports `API_BASE_URL` | done |
| `git grep VITE_API_URL` in `src/` returns zero matches | verified by TC-01 |
| `git grep "import.meta.env.VITE_API_BASE_URL"` returns exactly one match | verified by TC-01 |
| `backend/api/_shared.py` exports `ErrorResponse` and `FileErrorResponse(ErrorResponse)` | done |
| `admin.py` and `files.py` import shared models; local definitions removed | verified by TC-03/TC-05 |
| `responses=` declarations reference shared types; OpenAPI shows single `ErrorResponse` schema | verified by TC-03 |
| `/api/chat/health`, `/api/search/health`, `/api/validation/health` include `llm_backend` field | verified by TC-04 |
| `gemini_initialized` field preserved as a boolean on the same endpoints | verified by TC-04/TC-06 |
| Frontend health-badge contract preserved (no rename of `gemini_initialized`) | verified by TC-06 |

---

## Test results

```
docs/tests/S001-F-009/TC-S001-F-009-01.py  PASS  (2 tests)
docs/tests/S001-F-009/TC-S001-F-009-02.py  PASS  (3 tests)
docs/tests/S001-F-009/TC-S001-F-009-03.py  PASS  (3 tests)
docs/tests/S001-F-009/TC-S001-F-009-04.py  PASS  (3 tests)
docs/tests/S001-F-009/TC-S001-F-009-05.py  PASS  (3 tests)
docs/tests/S001-F-009/TC-S001-F-009-06.py  PASS  (3 tests)

Total: 17 passed, 0 failed
Run with: python3 -m pytest docs/tests/S001-F-009/ -v
```

---

## Next steps (handled outside this command)

1. Review the diff and the new tests under `docs/tests/S001-F-009/`.
2. `git add` modified + created files; commit.
3. `/code-graph-update`.
4. `/api-doc-update` — captures the consolidated `ErrorResponse` schema and the new `llm_backend` health field across three endpoints.
5. `/env-doc-update` — captures removal of `VITE_API_URL` and the consolidation note on `VITE_API_BASE_URL`.
6. Commit doc updates and push.

DB docs are unaffected — no schema changes in this requirement.
