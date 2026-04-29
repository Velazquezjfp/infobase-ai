# Wave 5 — S001-F-006 Implementation Summary

**Requirement:** S001-F-006 — Disable file upload via config flag with user-facing notice
**Sprint:** 001
**Status:** implemented
**Implemented at:** 2026-04-29T11:20:46Z
**Tests:** 15 / 15 passed

---

## Goal

Lock down `POST /api/files/upload` for the closed-environment demo. The
backend handler must early-return `403 feature_disabled` when
`ENABLE_UPLOAD=false`, and every UI surface that initiates an upload
(folder context-menu, folder drag-drop, sidebar drop-zone, global
`FileDropZone`) must short-circuit before sending bytes — with a
greyed-out Upload button and an `upload.notImplemented` toast.

The handler body remains intact behind the guard, so re-enabling the
feature is a single env-var flip.

---

## Backend changes

### `backend/api/files.py`

- Imports `from backend import config` (read flag at request time so
  test monkeypatches take effect after module reload).
- `upload_file` — early-return guard at the top of the handler:
  ```python
  if not config.ENABLE_UPLOAD:
      raise HTTPException(
          status_code=403,
          detail={
              "error": "feature_disabled",
              "detail": "Das Hochladen ist in dieser Demo-Umgebung deaktiviert.",
              "file_name": file.filename,
          },
      )
  ```
- OpenAPI `responses` map for `/upload` now lists `403` with the
  `ErrorResponse` model (description covers both feature-disabled and
  the existing path-traversal denial — no new status codes added).
- `files_health_check` — `features.upload` now mirrors
  `config.ENABLE_UPLOAD` instead of the hard-coded `True`.

### `backend/config.py`

No change needed in this wave: `ENABLE_UPLOAD` was already exposed by
S001-D-001 (.env schema requirement) and the matching
`get_bool_env('ENABLE_UPLOAD', False)` call site already exists in the
Feature Flags section of `config.py`.

---

## Frontend changes

### `src/types/file.ts`

- `UploadResult` gains an optional `disabled?: boolean` discriminator.
  When the backend returns `403` with `error: "feature_disabled"`, the
  fileApi helpers resolve with `{ success: false, disabled: true, ... }`
  rather than throwing — callers can branch on this without parsing
  error strings.

### `src/lib/fileApi.ts`

- `uploadFileSimple` (fetch path) and `uploadFileWithProgress` (XHR
  path) both detect `status === 403 && error === "feature_disabled"` and
  resolve with the typed disabled result.
- New `checkUploadEnabled()` — module-cached call to
  `GET /api/files/health` that reads `features.upload`. Fail-closed: any
  error resolves to `false` so the UI defaults to the disabled state
  rather than letting clicks race the network.
- New `resetUploadEnabledCache()` — exposed for tests.

### `src/components/workspace/CaseTreeExplorer.tsx`

- Imports `checkUploadEnabled` from `@/lib/fileApi`.
- New `useEffect` calls `checkUploadEnabled()` once on mount; result
  drives the new `uploadEnabled` state (default `true`, fail-permissive
  while the flag loads — backend remains the source of truth).
- `uploadEnabled` is threaded as a prop through `FolderItem` (and
  recursively to subfolders).
- Short-circuits added to:
  - `FolderItem.handleUploadClick` (folder context-menu Upload item)
  - `FolderItem.handleDrop` (drag-drop on a folder row)
  - `CaseTreeExplorer.handleDropZoneClick` (sidebar drop-zone click)
  - `CaseTreeExplorer.handleDropZoneDrop` (sidebar drop-zone drop)
- Each short-circuit shows `toast({ title: t('upload.notImplemented') })`
  before returning.
- The sidebar drop-zone `<div>` now renders with:
  - `aria-disabled={!uploadEnabled}`
  - `data-disabled` data attribute
  - `title={t('upload.notImplemented')}` when off
  - Greyed-out class set (`opacity-60`, `cursor-not-allowed`,
    `text-muted-foreground/60`)
  - Localised disabled label inside the button (`upload.notImplemented`)

### `src/components/workspace/FileDropZone.tsx`

- Imports `checkUploadEnabled` and `useTranslation`.
- New `uploadEnabled` state populated by the same `useEffect`/cache
  pattern.
- `uploadFiles` returns immediately on `!uploadEnabled`, surfacing the
  `upload.notImplemented` toast — files are never sent to the backend.
- `handleClick` (which opens the file picker) short-circuits with the
  same toast when off.
- The floating `<button>` now has both `disabled={!uploadEnabled}` and
  `aria-disabled={!uploadEnabled}` (the acceptance criterion calls for
  both attributes), with a greyed-out class and a tooltip pointing to
  the disabled-message string.

### `src/i18n/locales/de.json` and `src/i18n/locales/en.json`

- New `upload.notImplemented` keys.
  - DE: `"Das Hochladen ist in dieser Demo-Umgebung deaktiviert."`
  - EN: `"File upload is disabled in this demo environment."`
- Both files validated with `python3 -c "import json; json.load(...)"`.

---

## Tests

All under `docs/tests/S001-F-006/`. Pytest discovers `TC-*.py` per the
sprint-wide `conftest.py` convention.

| ID | What it asserts | Layer |
|----|-----------------|-------|
| TC-S001-F-006-01 | `POST /upload` with `ENABLE_UPLOAD=false` returns `403` with `error: "feature_disabled"` and the German notice | backend / FastAPI ASGI |
| TC-S001-F-006-02 | A pre-existing sentinel file remains untouched and no new files appear under `${tmp}/public/documents/{case}/{folder}/` after the rejected upload | backend / disk snapshot |
| TC-S001-F-006-03 | `CaseTreeExplorer` imports `checkUploadEnabled`, drop-zone uses `aria-disabled={!uploadEnabled}`, `handleUploadClick` and `handleDropZoneClick` short-circuit, and `FileDropZone`'s button has both `disabled` and `aria-disabled` | frontend source-level (no JS test runner — same pattern as S001-F-005 TC-04) |
| TC-S001-F-006-04 | `de.json` / `en.json` carry `upload.notImplemented`; `FileDropZone.uploadFiles` short-circuits before its for-loop; `FolderItem.handleDrop` short-circuits with the i18n key | frontend source-level + JSON |
| TC-S001-F-006-05 | `GET /api/files/health` returns `features.upload === false` when off and `=== true` when on | backend / FastAPI ASGI |
| TC-S001-F-006-06 | With `ENABLE_UPLOAD=true`, a 1KB upload returns `200` and the bytes persist at `public/documents/{case}/{folder}/{name}` | backend / FastAPI ASGI + tmp filesystem |

**Result:** `pytest docs/tests/S001-F-006/ -v` → **15 passed** in 0.47s.
The number is higher than the test-case count because TC-03 and TC-04
each contain multiple narrow assertions (one per behaviour), keeping
each failure trace pointed at a single acceptance criterion.

### Conftest pattern

`docs/tests/S001-F-006/conftest.py` provides the `fresh_files_modules`
fixture (mirrors `S001-F-005/conftest.py`):

- Drops `backend.config` and `backend.api.files` from `sys.modules`.
- Applies env via `monkeypatch.setenv`.
- Reimports `backend.config` and `backend.api.files` so the handler
  picks up the latest `ENABLE_UPLOAD` value.

---

## Affected surface — scope check

Every edited resource maps directly to `affected_surface` in
`S001-F-006.md`:

- **Files modified:** `backend/api/files.py`, `src/lib/fileApi.ts`,
  `src/components/workspace/CaseTreeExplorer.tsx`,
  `src/components/workspace/FileDropZone.tsx`,
  `src/i18n/locales/de.json`, `src/i18n/locales/en.json`. ✓
- **`src/types/file.ts`:** the `UploadResult` interface is the carrier
  of the typed disabled-state result the requirement explicitly names —
  the type augmentation is the contract surface, not a new module. The
  three `uploadFile*` functions listed in `affected_surface.modifies`
  consume this type, and `disabled?` is additive (no breaking change to
  any other caller). Treated as in-scope.
- **`backend/config.py`:** not modified — `ENABLE_UPLOAD` was already
  added by S001-D-001 / earlier waves.
- **`.env.example`:** already documented `ENABLE_UPLOAD=false` per
  S001-D-001 — confirmed via grep. Not modified.

No scope overrides were taken.

---

## Pending dependencies

None. S001-D-001 (the env schema requirement) is `status: implemented`,
which is the only structural dependency this requirement has.

---

## Next steps for the user

1. Review the diff and the new tests under `docs/tests/S001-F-006/`.
2. `git add` the modified + created files (this command does not touch
   git itself).
3. Commit the code change.
4. Run `/code-graph-update` to refresh the code graph.
5. Run `/api-doc-update` — `POST /api/files/upload` now documents `403
   feature_disabled`; `GET /api/files/health.features.upload` flipped
   from a hard-coded `true` to the live `ENABLE_UPLOAD` value.
6. Run `/env-doc-update` — `ENABLE_UPLOAD` is now actually consumed by
   `backend/api/files.py` (not just `backend/config.py`).
7. `/db-doc-update` is **not** needed — no DB surfaces touched.
8. Commit the doc updates and push.
