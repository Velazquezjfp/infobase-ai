# Implementation Summary — S001-F-005
## Disable IDIRS document-search and RAG via config flag with user-facing notice

### What was built

A feature flag `ENABLE_DOCUMENT_SEARCH` (default `false`) gates the two IDIRS proxy endpoints. When the flag is off, both endpoints return `503` with a structured error body before opening any outbound TCP connection to IDIRS. The frontend detects that specific error shape and renders a localized notice instead of a generic error string.

---

### Backend changes

**`backend/config.py`** — already contained `ENABLE_DOCUMENT_SEARCH = get_bool_env('ENABLE_DOCUMENT_SEARCH', False)` from prior sprint work. No changes needed.

**`backend/api/idirs.py`**
- Added `from fastapi.responses import JSONResponse` and `ENABLE_DOCUMENT_SEARCH` to imports.
- Added `ErrorResponse` Pydantic model (`error: str`, `detail: str`).
- Added early-return guard at the top of both `idirs_search` and `idirs_rag`:
  ```python
  if not ENABLE_DOCUMENT_SEARCH:
      return JSONResponse(
          status_code=503,
          content={
              "error": "feature_disabled",
              "detail": "Die Dokumentsuche ist in dieser Demo-Umgebung noch nicht verfügbar.",
          },
      )
  ```
  The existing proxy code paths are untouched downstream of the guard.

**`backend/api/search.py`**
- Added `ENABLE_DOCUMENT_SEARCH` import from `backend.config`.
- Added `"document_search": "enabled" if ENABLE_DOCUMENT_SEARCH else "disabled"` to the `GET /api/search/health` response body.

---

### Frontend changes

**`src/i18n/locales/de.json`**
- Added `documentSearch.notImplemented`: `"Die Dokumentsuche ist in dieser Demo-Umgebung noch nicht verfügbar."`

**`src/i18n/locales/en.json`**
- Added `documentSearch.notImplemented`: `"The document search feature is not yet available in this demo environment."`

**`src/components/workspace/AIChatInterface.tsx`**
- Updated the `!response.ok` handler in both the `/Dokumentsuche` (search) and `/Dokumente-abfragen` (RAG) branches of `processSearchCommand`:
  ```ts
  const msg = errData.error === 'feature_disabled'
    ? t('documentSearch.notImplemented')
    : `${t('documentSearch.searchError')}: ${errData.detail || response.statusText}`;
  addChatMessage({ role: 'assistant', content: msg });
  ```
  When the backend returns `error: "feature_disabled"`, the localized `notImplemented` string is shown; all other errors fall through to the existing generic error path.

---

### Tests

Location: `docs/tests/S001-F-005/`

| File | Test | Result |
|------|------|--------|
| `TC-S001-F-005-01.py` | `POST /api/idirs/search` with flag off → 503 + `feature_disabled` | PASS |
| `TC-S001-F-005-02.py` | `POST /api/idirs/rag` with flag off → 503 + `feature_disabled` | PASS |
| `TC-S001-F-005-03.py` | No outbound `httpx.AsyncClient` call when flag off | PASS |
| `TC-S001-F-005-04.py` | `documentSearch.notImplemented` key present in both locale files | PASS (2 assertions) |
| `TC-S001-F-005-05.py` | Flag on + mocked IDIRS 200 → upstream payload returned verbatim | PASS |
| `TC-S001-F-005-06.py` | `GET /api/search/health` reports `document_search: disabled/enabled` | PASS (2 assertions) |

**Total: 8 / 8 passed**

---

### Scope notes

- `.env.example` was not modified — owned by S001-D-001 per the requirement's affected_surface.
- `backend/config.py` required no changes; the constant was already present from prior sprint work.
- No outbound connection is opened when the flag is off — verified by TC-03 via `patch.object` on the `httpx` module reference inside `idirs.py`.
