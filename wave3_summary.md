# Wave 3 — S001-F-004 Implementation Summary

**Requirement:** Disable anonymization service via config flag with user-facing notice
**Status:** implemented
**Tests:** 7 / 7 passed
**Date:** 2026-04-28

---

## What was changed

### `backend/config.py`
Added three new feature-flag constants in a new `Feature Flags` section, using the
existing `get_bool_env` helper:

```python
ENABLE_ANONYMIZATION: bool  = get_bool_env('ENABLE_ANONYMIZATION', False)
ENABLE_DOCUMENT_SEARCH: bool = get_bool_env('ENABLE_DOCUMENT_SEARCH', False)
ENABLE_UPLOAD: bool          = get_bool_env('ENABLE_UPLOAD', False)
```

`ENABLE_DOCUMENT_SEARCH` and `ENABLE_UPLOAD` are placed here now (they are
documented in `.env.example` from S001-D-001) so F-005 and F-006 can import
them without touching config again.

---

### `backend/api/chat.py`

**Import change** — adds `ENABLE_ANONYMIZATION` alongside the existing
`ENABLE_CHAT_HISTORY` import, plus two module-level string constants that mirror
the frontend i18n keys:

```python
ANONYMIZATION_DISABLED_MESSAGE_DE = (
    "Die Anonymisierungsfunktion ist in dieser Demo-Umgebung noch nicht verfügbar."
)
ANONYMIZATION_DISABLED_MESSAGE_EN = (
    "The anonymization feature is not yet available in this demo environment."
)
```

**`handle_anonymization`** — a guard block is inserted at the very top of the
function body, before any file-path extraction:

```python
if not ENABLE_ANONYMIZATION:
    language = message.get("language", "de")
    disabled_msg = (
        ANONYMIZATION_DISABLED_MESSAGE_DE if language == "de"
        else ANONYMIZATION_DISABLED_MESSAGE_EN
    )
    await websocket.send_json({
        "type": "anonymization_complete",
        "success": False,
        "error": "feature_disabled",
        "message": disabled_msg,
        "timestamp": None,
    })
    return
```

The rest of the existing function (file-path validation, format check,
`anonymize_document` call, render registration, chat messages) is untouched.

**`chat_health_check`** — the JSON response now includes an `"anonymization"` key:

```python
"anonymization": "enabled" if ENABLE_ANONYMIZATION else "disabled",
```

This satisfies TC-05: operators and the frontend can query `GET /api/chat/health`
to learn the flag state without inferring it from a failed anonymization attempt.

---

### `backend/services/anonymization_service.py`

**`check_service_health`** — an early-return guard is added at the top of the
method. When `ENABLE_ANONYMIZATION` is false the method returns immediately with
`{"status": "disabled"}` and makes no outbound TCP connection:

```python
from backend.config import ENABLE_ANONYMIZATION
if not ENABLE_ANONYMIZATION:
    return {"status": "disabled"}
# ... existing aiohttp health-check logic unchanged ...
```

The import is local (inside the method) to avoid a circular-import risk at module
load time. The return type annotation is loosened from `bool` to bare (no
annotation) to accommodate both the dict and bool return paths; no external
callers existed so there is no breakage.

---

### `src/i18n/locales/de.json`
Added a new top-level `"anonymization"` section:

```json
"anonymization": {
  "notImplemented": "Die Anonymisierungsfunktion ist in dieser Demo-Umgebung noch nicht verfügbar."
}
```

---

### `src/i18n/locales/en.json`
Same section, English translation:

```json
"anonymization": {
  "notImplemented": "The anonymization feature is not yet available in this demo environment."
}
```

---

### `src/types/websocket.ts` *(scope override)*
Added `message?: string` to `AnonymizationResponse`:

```typescript
message?: string;
```

This field carries the backend-provided localized string when
`error === "feature_disabled"`. Without it the TypeScript compiler would reject
the access in `AppContext.tsx`. No existing callers are affected.

---

### `src/contexts/AppContext.tsx` *(scope override — approved)*
The `anonymization_complete` handler gained a new `else if` branch before the
existing destructive-toast fallback:

```typescript
} else if (anonResponse.error === 'feature_disabled') {
  toast({
    title: anonResponse.message || i18n.t('anonymization.notImplemented'),
  });
} else {
  toast({
    title: 'Anonymization Failed',
    description: anonResponse.error || 'Unknown error occurred',
    variant: 'destructive',
  });
}
```

When the feature is disabled the UI shows a neutral info toast (no `variant:
'destructive'`) whose text is the localized message delivered by the backend.
All other error paths still render the red error toast as before.

---

## Test files created

| File | What it asserts |
|---|---|
| `TC-S001-F-004-01.py` | `handle_anonymization` with `ENABLE_ANONYMIZATION=false` sends exactly one `anonymization_complete` message with `success=false`, `error="feature_disabled"`, and a German `message` field. |
| `TC-S001-F-004-02.py` | Under the same disabled condition, `anonymize_document` is never called (no outbound traffic). |
| `TC-S001-F-004-03.py` | Both locale files contain `anonymization.notImplemented` with the exact required strings. |
| `TC-S001-F-004-04.py` | With `ENABLE_ANONYMIZATION=true`, `handle_anonymization` proceeds past the guard and calls `anonymize_document` exactly once. |
| `TC-S001-F-004-05.py` | `GET /api/chat/health` returns `"anonymization": "disabled"` when flag is false and `"anonymization": "enabled"` when true. |

---

## Scope overrides

Two files outside `affected_surface` were edited with explicit user approval:

- **`src/contexts/AppContext.tsx`** — required to satisfy TC-03 (info toast vs.
  destructive error toast). The acceptance criterion implies frontend behaviour
  change; the polished requirement's `affected_surface` omitted this file.
- **`src/types/websocket.ts`** — a strictly necessary companion to the
  `AppContext` change: TypeScript would not compile `anonResponse.message` access
  without the new field in `AnonymizationResponse`.

Recommendation: re-polish S001-F-004 (or note in the sprint retro) to add both
files to `affected_surface.modifies` so future impact analysis is accurate.

---

## Behaviour after this wave

| Condition | `handle_anonymization` | `check_service_health` | `GET /api/chat/health` | Frontend toast |
|---|---|---|---|---|
| `ENABLE_ANONYMIZATION=false` (default) | Returns `feature_disabled` immediately, no service call | Returns `{"status": "disabled"}`, no HTTP request | `"anonymization": "disabled"` | Neutral info toast with localized message |
| `ENABLE_ANONYMIZATION=true` | Full existing flow unchanged | Full existing HTTP probe unchanged | `"anonymization": "enabled"` | Existing success/failure toasts unchanged |

---

---

# Wave 3 — S001-NFR-003 Implementation Summary

**Requirement:** Docker Compose orchestration for backend + frontend with persistent volumes
**Status:** implemented
**Tests:** 11 passed, 4 skipped (environment-dependent), 0 failed
**Date:** 2026-04-28

---

## What was changed

### `docker-compose.yml` *(new file)*

Compose v3.9 file at the project root. Key structure:

- **`services.backend`**: builds from `backend/Dockerfile`; loads all runtime vars via `env_file: [".env"]`; exposes `${BACKEND_PORT:-8000}:8000`; mounts three named volumes; healthcheck (`curl /health`, interval 30s, timeout 5s, retries 3, start_period 15s); resource limits (2 CPU / 2 GB, informational on `docker compose up`, enforced on Swarm); `restart: unless-stopped`.
- **`services.frontend`**: builds from `frontend/Dockerfile`; exposes `${FRONTEND_PORT:-3000}:3000`; `depends_on.backend.condition: service_healthy` so the frontend container waits for the backend health check to flip green; resource limits (1 CPU / 1 GB); `restart: unless-stopped`.
- **`services.ollama`**: behind `profiles: ["ollama"]`; pulls `ollama/ollama:latest`; mounts `ollama-data`; not started unless `--profile ollama` is passed.
- **Named volumes**: `documents-data` (`/var/app/documents`), `cases-data` (`/app/backend/data/contexts/cases`), `manifest-data` (`/app/backend/data`), `ollama-data`.

Build args use `${VAR:-default}` fallbacks for `DOCKER_REGISTRY`, `PIP_INDEX_URL`, and `NPM_REGISTRY` so the file works in environments where those vars are unset (safe dev defaults; the requirement's general rule is "only fallbacks via `${VAR:-default}` for safe dev defaults").

---

### `README.md` *(modified)*

Added a `## Quickstart` section before the existing `## Quick Start` section. Describes the Docker Compose path: copy `.env.example` → `.env`, edit `LITELLM_TOKEN` or `GEMINI_API_KEY`, `docker compose up -d`, browse to `http://localhost:3000`. Includes a note that `deploy.resources.limits` is informational under `docker compose up` and is only enforced on Docker Swarm.

---

## Test files created

| File | What it asserts |
|---|---|
| `TC-S001-NFR-003-01.py` | `docker compose config` exits 0; normalized output contains `backend` and `frontend`; source file declares `version: "3.9"`. |
| `TC-S001-NFR-003-02.py` | Both services reach `healthy` state within 90 s after `docker compose up -d --build`. Skips with an informative message when `.env` lacks LLM configuration (the 4-skip set). |
| `TC-S001-NFR-003-03.py` | Creating a folder, restarting the backend container, and re-querying confirms `cases-data` volume persists data. Skips if backend not healthy. |
| `TC-S001-NFR-003-04.py` | `LOG_LEVEL` from `.env` appears inside the running backend container via `docker compose exec backend env`. Skips if backend not healthy. |
| `TC-S001-NFR-003-05.py` | Frontend returns HTTP 200 on `http://localhost:3000`. Skips if frontend not healthy. |
| `TC-S001-NFR-003-06.py` | `docker-compose.yml` contains no Google API key, OpenAI-style key, or Bearer token patterns. |
| `TC-S001-NFR-003-07.py` | `docker compose ps` without `--profile ollama` does not list an `ollama` service. |
| `TC-S001-NFR-003-08.py` | `frontend.depends_on.backend.condition` is `service_healthy` (checked against parsed YAML). |

---

## Notes

- The 4 skipped tests (TC-02, TC-03, TC-04, TC-05) require the stack to start healthy. The stack needs `.env` to have either `LLM_BACKEND=external` (Gemini key only) or `LLM_BACKEND=internal` with `LITELLM_PROXY_URL`/`LITELLM_TOKEN`. Adding `LLM_BACKEND=external` to `.env` unblocks all four.
- `docker compose config` emits a warning that `version` is obsolete (modern Compose v2.x treats it as informational). The file keeps the `version: "3.9"` literal as required; TC-01 checks the raw file rather than the normalized output.
