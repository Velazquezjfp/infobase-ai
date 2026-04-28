# S001-NFR-001 — Implementation Summary

_Date: 2026-04-28 | Sprint: 001 | Wave: 2 of 7_

**Status:** implemented · 8 / 8 tests passing

---

## What was built

### `backend/Dockerfile`

A single-stage build based on `${DOCKER_REGISTRY}/python:3.12-slim` targeting `linux/amd64`.

Key characteristics:

| Aspect | Detail |
|---|---|
| Base image | `${DOCKER_REGISTRY}/python:3.12-slim` (ARG default: `docker.io`) |
| Python version | 3.12 |
| Non-root user | `app` (UID/GID 10001) — created by `groupadd`/`useradd`, no home directory |
| Pip index | `${PIP_INDEX_URL}` (ARG default: `https://pypi.org/simple`) |
| WORKDIR | `/app` |
| Documents path | `ENV DOCUMENTS_PATH=/var/app/documents` (volume-mounted at runtime by NFR-003) |
| Exposed port | `$BACKEND_PORT` (ARG default: `8000`) |
| Healthcheck | `curl -f http://localhost:8000/health` every 30s, 5s timeout, 15s start-period, 3 retries |
| CMD | `uvicorn backend.main:app --host 0.0.0.0 --port 8000` (exec form) |

**Layer order for cache efficiency:**

1. System packages (`apt-get install curl`) — almost never changes
2. User creation — almost never changes
3. `COPY backend/requirements.txt` + `RUN pip install` — cache busted only when dependencies change
4. `COPY --chown=app:app backend/ ...` — cache busted on code changes
5. `COPY --chown=app:app ontology_shacl_material/ ...`
6. `COPY --chown=app:app root_docs/ ...`

All application files are owned by `app:app` via `--chown`. The pip install runs as root (system-wide packages) before `USER app` is set; the `USER app` directive precedes `EXPOSE`, `HEALTHCHECK`, and `CMD`.

**What the image contains:**

- `backend/` — full Python application (venv excluded by `.dockerignore`; `data/contexts/cases/ACTE-*` excluded by `.dockerignore`, leaving `cases/` empty)
- `backend/data/contexts/templates/` — included as part of `backend/` COPY; required by `create_case_from_template`
- `ontology_shacl_material/` — SHACL/Turtle ontology files for integration course validation
- `root_docs/` — six seed documents used by the S001-F-007 seed-reset flow

**What the image does NOT contain:**

- `backend/venv/` — excluded by `.dockerignore`
- `backend/data/contexts/cases/ACTE-*` — case data excluded; `cases/` directory is present but empty
- `node_modules/`, `dist/`, `temp/` — excluded by `.dockerignore`
- `.env`, `info-env` — secrets never baked in; passed at runtime via `docker-compose env_file`
- `docs/` tree — excluded by `.dockerignore`; build artifacts not needed at runtime

### `.dockerignore` (project root)

```
.git/
node_modules/
dist/
backend/venv/
**/__pycache__/
**/.pytest_cache/
**/.mypy_cache/
*.env
info-env
backend/data/contexts/cases/ACTE-*
public/documents/ACTE-*
temp/
bamf-dev/
docs/code-graph/backups/
docs/
```

This file is shared by both `backend/Dockerfile` and `frontend/Dockerfile`. The NFR-002 frontend build previously sent the entire 487 MB `node_modules/` directory to the Docker daemon on every build because `.dockerignore` didn't exist yet. Now that it exists, frontend builds will be significantly faster.

---

## Notable discoveries and decisions

### 1. `requirements.txt` had three stale version pins (scope override)

`requirements.txt` is listed as `affected_surface.reads` in the requirement. However, the pip install failed immediately with `ResolutionImpossible` because three pins were out of date relative to what `litellm==1.83.14` actually requires:

| Package | requirements.txt (old) | Actual venv / litellm requirement |
|---|---|---|
| `python-dotenv` | `1.0.0` | `1.2.2` |
| `aiohttp` | `3.9.1` | `3.13.4` |
| `pydantic` | `2.5.2` | `2.12.5` |

All three were already at the correct version in the `backend/venv/` (likely upgraded in place after `litellm` was first installed). The requirements file had simply never been re-pinned. Fixed with explicit user approval. The next re-polish of the requirement should move `requirements.txt` to `affected_surface.modifies`.

### 2. Default `LLM_BACKEND=internal` prevents the server from booting without a proxy

`GeminiService` is instantiated at module import time in `backend/api/chat.py`. The `llm_provider.get_provider()` fail-fast guard (added by S001-NFR-004) raises `ValueError` if `LLM_BACKEND=internal` and `LITELLM_PROXY_URL` is unset — causing uvicorn to exit with code 1 during `config.load()`.

The acceptance criterion's smoke-test one-liner (`-e GEMINI_API_KEY=dummy`) therefore does **not** start the server by itself. TC-02 and the `running_container` fixture both pass `LLM_BACKEND=external` as an additional env var. The `/health` endpoint has no LLM dependency; this is the correct smoke-test mode.

**Production behaviour is unchanged:** the `docker-compose.yml` (NFR-003) will override `LLM_BACKEND=internal` and provide `LITELLM_PROXY_URL` via `env_file`, so the real deployment path is unaffected.

The requirement's acceptance criterion should be amended to note that `LLM_BACKEND=external` is needed for the one-container smoke test, or the docker-compose (NFR-003) should be used for full stack validation.

### 3. Curl must be explicitly installed

`python:3.12-slim` does not ship with `curl` or `wget`. The HEALTHCHECK uses `curl -f http://localhost:8000/health`. A `RUN apt-get install -y --no-install-recommends curl` step (followed by `rm -rf /var/lib/apt/lists/*`) was added before the user-creation step. This adds approximately 2 MB to the image and keeps curl available for the health daemon.

### 4. Final image size

`docker inspect --format '{{.Size}}'` reported the image at approximately **630 MB**, well under the 800 MiB limit. The dominant contributor is `litellm==1.83.14` and its transitive dependencies (openai SDK, anthropic SDK, httpx, etc.). The slim base and `--no-cache-dir` pip flag kept the overhead minimal.

---

## Test coverage (8 TC)

All tests live in `docs/tests/S001-NFR-001/`. A session-scoped `docker_build` fixture in `conftest.py` builds the image once per pytest session and tears it down on exit.

| TC | Description | Mechanism | Result |
|---|---|---|---|
| TC-01 | `docker build` exits 0 | `docker_build` fixture returncode assertion | ✅ pass |
| TC-02 | Container answers `/health` with `200 {"status":"healthy"}` | `running_container` fixture polls up to 30s; `urllib.request` check | ✅ pass |
| TC-03 | No secrets baked into layers | `docker history --no-trunc`; asserts `GEMINI_API_KEY=` and `LITELLM_TOKEN=` absent | ✅ pass |
| TC-04 | Container default user is `app` | `docker run --rm ... whoami` | ✅ pass |
| TC-05 | Invalid `DOCKER_REGISTRY` causes build failure | `docker build --no-cache --build-arg DOCKER_REGISTRY=invalid.registry.example.com` → returncode != 0 | ✅ pass |
| TC-06 | Invalid `PIP_INDEX_URL` causes pip failure | `docker build --no-cache --build-arg PIP_INDEX_URL=https://invalid.example.com/pypi/simple` → returncode != 0 | ✅ pass |
| TC-07 | Image under 800 MiB | `docker inspect --format '{{.Size}}'`; asserts `< 800 * 1024**2` bytes | ✅ pass (~630 MiB) |
| TC-08 | HEALTHCHECK directive present and references `/health` | `docker inspect --format '{{.Config.Healthcheck.Test}}'`; string contains `/health` | ✅ pass |

TC-05 and TC-06 use `--no-cache` and pull no layers from cache (they test the ARG substitution path, not cached layers). They are the slowest tests (~8s each). The remaining 6 tests re-use the session-cached image and complete in under 5s total.

---

## Side effects on other requirements

### NFR-002 (frontend Dockerfile) — build context now efficient

Before this requirement landed, `docker build -f frontend/Dockerfile .` was transferring `node_modules/` (487 MB) to the Docker daemon on every build. Now that `.dockerignore` exists at the project root, the frontend build context is minimal. No change to `frontend/Dockerfile` is needed.

### NFR-003 (Docker Compose) — Wave 3 gate now clear

S001-NFR-003 has explicit semantic dependencies on both NFR-001 and NFR-002. NFR-002 was already implemented. With NFR-001 now done, the Wave 3 gate is fully cleared and NFR-003 can be implemented in the next session.

---

## Wave 3 gate status (updated)

| Requirement | Status | Blocks |
|---|---|---|
| S001-D-001 | ✅ implemented | NFR-003, NFR-001, NFR-002 |
| S001-F-001 | ✅ implemented | NFR-003, NFR-004 |
| S001-NFR-001 | ✅ **implemented** | **NFR-003** |
| S001-NFR-002 | ✅ implemented | **NFR-003** |

**Wave 3 is now unblocked.** Next requirements in execution order:

- **S001-NFR-003** — Docker Compose orchestration (all dependencies satisfied)
- **S001-F-004** — Disable anonymization service via config flag (only depends on F-001; can run in parallel with NFR-003)
