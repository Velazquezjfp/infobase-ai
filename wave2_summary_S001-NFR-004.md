# Wave 2 Implementation Summary — S001-NFR-004

**Requirement:** Containerize the LiteLLM proxy as a self-contained `litellm/` subproject (gitignored)
**Sprint:** 001
**Wave:** 2
**Status:** implemented
**Implemented at:** 2026-04-28

---

## What was built

A fully self-contained LiteLLM proxy subproject at the repo root, intentionally gitignored so no local secrets or config ever enter version control. The proxy is the front door for all `LLM_BACKEND=internal` calls going forward — it sits between the FastAPI backend and the local Ollama instance, presenting an OpenAI-compatible REST surface on port 4000.

---

## Files created (all inside `litellm/`, gitignored)

| File | Purpose |
|------|---------|
| `litellm/Dockerfile` | Thin wrapper over `ghcr.io/berriai/litellm:v1.81.9-stable`. Copies `config.yaml` to `/app/config.yaml` and sets the entry-point command `litellm --config /app/config.yaml --port 4000 --num_workers 1`. |
| `litellm/config.yaml` | Declares one model entry: `model_name: gemma3:12b`, `litellm_params.model: ollama_chat/gemma3:12b`, `litellm_params.api_base: os.environ/LITELLM_OLLAMA_HOST`, `model_info.supports_function_calling: true`. Master key read from `os.environ/LITELLM_MASTER_KEY`. |
| `litellm/docker-compose.yml` | Single `litellm` service. Port `4000:4000`, `env_file: .env`, `extra_hosts: host.docker.internal:host-gateway` (Linux Ollama reach), healthcheck on `GET /health/liveliness`. |
| `litellm/.env.example` | Documents `LITELLM_MASTER_KEY` (default `sk-bamf-local-dev-key`), `LITELLM_OLLAMA_HOST` (default `http://host.docker.internal:11434`), `LITELLM_OLLAMA_MODEL` (default `gemma3:12b`). The operator copies this to `litellm/.env`. |
| `litellm/README.md` | Three lifecycle commands (build / up -d / logs -f). Model-swap procedure (requires editing both `config.yaml` and `.env` because `os.environ/` substitution does not apply to `litellm_params.model`). Full `LITELLM_MASTER_KEY ↔ LITELLM_TOKEN` consistency table. Host-run vs. containerised backend connectivity matrix. |

---

## Files modified (tracked)

### `.gitignore`
Added entry `litellm/` so the entire subproject directory — including any `.env` with real credentials — is excluded from version control.

### `.env.example`
- `LLM_BACKEND` flipped from `external` → `internal` (the proxy now ships alongside the requirement; the safe default is the internal path)
- `# Default:` comment updated to match
- `LITELLM_PROXY_URL=http://localhost:4000` was already correct from wave 1 (S001-F-001); no change needed there
- All `# 🔒` markers and `# introduced by S001-` tags preserved

### `README.md`
Added **"Local LiteLLM proxy"** section (after Quick Start, before Technology Stack) covering:
- First-time setup (copy `.env.example`, edit keys, build & start)
- Three lifecycle commands
- Pointer to `litellm/README.md` for full detail
- Regeneration instructions for fresh-checkout machines

### `backend/services/llm_provider.py` — `_build_provider()`
Added a fail-fast precondition: when `LLM_BACKEND=internal` and `LITELLM_PROXY_URL` is empty or blank, raises:

```
ValueError: LITELLM_PROXY_URL is required when LLM_BACKEND=internal —
start the LiteLLM container per S001-NFR-004 or set LLM_BACKEND=external
```

The check fires **before** any `LiteLLMProvider` is instantiated, so `litellm.acompletion` is never reached. This converts the old silent "provider unhealthy at first request" failure into an early, debuggable startup error — as documented in the wave-1 F-001 implementer report.

---

## Env vars introduced

These live in `litellm/.env` (gitignored), **not** in the root `.env`:

| Var | Default | Purpose |
|-----|---------|---------|
| `LITELLM_MASTER_KEY` | `sk-bamf-local-dev-key` | Token the proxy enforces on all inbound requests. Must equal `LITELLM_TOKEN` in root `.env`. |
| `LITELLM_OLLAMA_HOST` | `http://host.docker.internal:11434` | URL of the Ollama instance. Injected into `config.yaml` via `os.environ/`. |
| `LITELLM_OLLAMA_MODEL` | `gemma3:12b` | Used to document the default in `.env.example`; changing it also requires editing `config.yaml` (see model-swap caveat below). |

---

## Model-swap caveat

`os.environ/` substitution works in LiteLLM config for `api_base` and `master_key` but **not** for the model string in `litellm_params.model`. To swap from `gemma3:12b` to another Ollama model the operator must:

1. Edit `litellm/config.yaml` → change `ollama_chat/gemma3:12b`
2. Edit `litellm/.env` → change `LITELLM_OLLAMA_MODEL`
3. Edit root `.env` → change `LITELLM_MODEL`
4. Rebuild and restart the container

This is documented in `litellm/README.md` and covered by TC-07's structural assertions.

---

## Tests written — `docs/tests/S001-NFR-004/`

| File | Type | What it checks |
|------|------|---------------|
| `TC-S001-NFR-004-01.py` | Unit | `litellm/` is in `.gitignore`; `git check-ignore` exits 0 for `litellm/Dockerfile`; `git status` does not list it. |
| `TC-S001-NFR-004-02.py` | Integration | `docker compose -f litellm/docker-compose.yml build` exits 0. |
| `TC-S001-NFR-004-03.py` | Integration | `GET /health/liveliness` returns 200 within 30s of `docker compose up -d`. |
| `TC-S001-NFR-004-04.py` | Integration | `GET /v1/models` with master key returns `gemma3:12b` in `data[].id`. |
| `TC-S001-NFR-004-05.py` | Integration | `POST /v1/chat/completions` returns 200 with non-empty `choices[0].message.content`. |
| `TC-S001-NFR-004-06.py` | Integration | Same endpoint without `Authorization` header returns 401. |
| `TC-S001-NFR-004-07.py` | Unit | `config.yaml` uses `os.environ/LITELLM_OLLAMA_HOST`; `.env.example` documents `LITELLM_OLLAMA_MODEL=gemma3:12b`; `README.md` documents swap procedure. |
| `TC-S001-NFR-004-08.py` | Integration | Backend `POST /api/admin/generate-field` returns 200 through the **real** proxy (no mock) — closes the integration gap from wave 1 F-001. |
| `TC-S001-NFR-004-09.py` | Unit | `get_provider()` raises `ValueError` with message containing `LITELLM_PROXY_URL` and `S001-NFR-004` when URL is empty/blank; `litellm.acompletion` is never called. |
| `TC-S001-NFR-004-10.py` | Unit | `.env.example` has `LLM_BACKEND=internal`, `LITELLM_PROXY_URL=http://localhost:4000`, all `# 🔒` markers, all `# introduced by S001-` tags. |
| `TC-S001-NFR-004-11.py` | Unit | All F-001 scenarios still pass after the precondition is added (fresh_modules sets `LITELLM_PROXY_URL` explicitly, bypassing the fail-fast branch). |

### Test run results

```
pytest docs/tests/S001-NFR-004/ (unit subset: TC-01, TC-07, TC-09, TC-10, TC-11)
15 passed, 0 failed

pytest docs/tests/S001-F-001/ (regression)
7 passed, 0 failed
```

Integration tests (TC-02 through TC-08, `@pytest.mark.integration`) require a live Docker daemon and Ollama with `gemma3:12b` pulled. They were not run in this session.

---

## Design decisions

**Why hard-code `ollama_chat/gemma3:12b` in `config.yaml` instead of using env var substitution?**
LiteLLM's `os.environ/` syntax resolves env vars for secret/URL fields but not for model strings. Using a literal keeps `config.yaml` readable and the validation AC unambiguous. The model swap procedure is explicitly documented.

**Why `v1.81.9-stable` as the pinned tag?**
This is the stable tag cited in the requirement text. The `main-stable` floating tag was rejected to prevent silent upstream changes breaking a known-good configuration.

**Why the fail-fast in `_build_provider()` rather than `LiteLLMProvider.__init__()`?**
The precondition must fire before any provider object is constructed, so `litellm.acompletion` is provably unreachable. Placing it in `__init__` would still create the object partially. `_build_provider` is the correct chokepoint.

---

## What the operator must do before first use

```bash
# 1. Copy and edit the env template
cp litellm/.env.example litellm/.env
# set LITELLM_MASTER_KEY to a secret string

# 2. Set the same key in the root .env
#    LITELLM_TOKEN=<same string>
#    LLM_BACKEND=internal           (now the default)
#    LITELLM_PROXY_URL=http://localhost:4000

# 3. Start Ollama and pull the model
ollama pull gemma3:12b

# 4. Build and start the proxy
docker compose -f litellm/docker-compose.yml build
docker compose -f litellm/docker-compose.yml up -d

# 5. Verify
curl -s http://localhost:4000/health/liveliness
```

---

## Next steps / handoff notes

- TC-02 through TC-08 (integration tests) should be run once the Docker environment is available.
- Wave 3 (`S001-NFR-003`) depends on NFR-004 being complete — it reads `LITELLM_OLLAMA_MODEL` (created here) and can now assume the proxy exists.
- `S001-F-002` (optional Ollama dev container) also depends on `LITELLM_OLLAMA_MODEL` — that requirement can now proceed.
- Run `/update-code-graph` (backend/services/llm_provider.py changed) and `/env-doc-update` (new env vars + LLM_BACKEND default change) before continuing.
