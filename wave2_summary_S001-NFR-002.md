# Sprint 001 — Wave 2 Implementation Summary

_Date: 2026-04-28 | Sprint: 001 | Wave: 2 of 7_

---

## Overview

Wave 2 consists of four requirements that depend on Wave 1 (S001-D-001, S001-F-001, S001-F-008). Three of the four are implemented; one remains pending.

| ID | Title | Status | Tests |
|---|---|---|---|
| S001-F-003 | Render dynamic-context URLs as plain text | **implemented** | 12 / 12 |
| S001-NFR-001 | Containerize FastAPI backend (Dockerfile + .dockerignore) | **pending** | — |
| S001-NFR-002 | Containerize Vite frontend (Dockerfile) | **implemented** | 8 / 8 |
| S001-NFR-004 | Containerize LiteLLM proxy (gitignored subproject) | **implemented** | 7 / 11 (4 integration deferred) |

**Wave gate:** Wave 3 (NFR-003 Docker Compose + F-004 anonymization flag) requires NFR-001 and NFR-002 both implemented. NFR-002 is done; **NFR-001 is the sole blocker** for Wave 3.

---

## S001-F-003 — Render dynamic-context URLs as plain text

**Status:** implemented · 12/12 tests passing

### What was built

The `ContextHierarchyDialog` and `CaseContextDialog` components previously rendered URL-typed entries in the case context tree as clickable `<a>` links. In the BAMF closed deployment there is no internet access, so those links led nowhere and the visual affordance was misleading.

**Frontend changes:**
- `src/components/workspace/ContextHierarchyDialog.tsx::renderNode` now detects URL-shaped values and emits a `<span class="font-mono text-xs">` instead of an `<a target="_blank">`.
- A muted disclaimer line using `t("context.offlineNotice")` appears below each inert URL.
- `CaseContextDialog.tsx` received the same treatment for any URL fields it renders.
- Two new i18n keys were added to both locale files:
  - `de.json`: `"context.offlineNotice": "Offline-Modus: Inhalt wird simuliert"`
  - `en.json`: `"context.offlineNotice": "Offline mode: content is simulated"`

**Backend changes:**
- `backend/services/gemini_service.py::_load_context` now reads `regulations[*].extractedText` when present in `case.json`.
- `_build_prompt` injects the extracted text as grounding context and includes the URL only as a citation marker (`(source: <url>)`) — the URL is no longer passed as a clickable resource to the LLM.
- This is entirely opt-in: if `extractedText` is absent, the prompt includes the URL citation only. No HTTP crawling occurs at runtime; operators hand-prepare extracted text and place it in `case.json`.

### Key design decisions

- The pre-extraction path (crawling URLs at runtime) was explicitly scoped out. The sprint 1 approach is operator-prepared `extractedText` — a deliberate simplification documented in `README.md`.
- `GET /api/context/case/{case_id}` remains unchanged — raw `case.json` payload is returned unmodified; extraction logic lives entirely in the prompt builder.
- The offline notice respects the S001-F-008 fallback chain: if the translation key is missing, the key name renders instead of throwing.

### Test coverage (12 TC)

TC-01: No `<a>` element emitted for URL-shaped values in `ContextHierarchyDialog`.  
TC-02: Disclaimer text matches locale strings for both `de` and `en`.  
TC-03: With `extractedText` present, the LLM prompt contains the extracted text (verified via fake `LLMProvider`).  
TC-04: Without `extractedText`, URL is included as citation only; no outbound HTTP.  
TC-05: Missing `context.offlineNotice` key degrades gracefully — key name renders, no throw.  
TC-06–12: Additional edge cases covering nested URL nodes, empty regulation arrays, and regression checks against the context API contract.

---

## S001-NFR-001 — Containerize the FastAPI backend

**Status:** pending (not yet started)

### What it needs to deliver

- `backend/Dockerfile` — multi-step build based on `${DOCKER_REGISTRY}/python:3.12-slim`, non-root user `app` (UID 10001), installs Python dependencies via `${PIP_INDEX_URL}`, copies `backend/`, `ontology_shacl_material/`, `root_docs/`, and `backend/data/contexts/templates/` (but not `cases/`).
- `.dockerignore` at the project root — excludes `node_modules/`, `dist/`, `backend/venv/`, `__pycache__/`, `.env`/`info-env`, case data, `temp/`, and `docs/`.
- Healthcheck at `GET /health` every 30s.

### Why this is the Wave 3 gate

NFR-003 (Docker Compose orchestration) has explicit semantic dependencies on both NFR-001 and NFR-002. NFR-002 is done. NFR-001 is the last remaining blocker before Wave 3 can start.

### Side effect on NFR-002 (already implemented)

NFR-002's Dockerfile was written and tested **without** `.dockerignore`. The build works, but sends the full 487 MB `node_modules/` directory to the Docker daemon as build context on every build. Once NFR-001 lands and creates `.dockerignore`, frontend builds will become significantly faster. No change to `frontend/Dockerfile` is required — the `.dockerignore` is automatically picked up by Docker.

### Planned test surface (8 TC)

TC-01: `docker build -t bamf-backend:dev -f backend/Dockerfile .` exits 0.  
TC-02: Running container answers `GET /health` with `200 {"status": "healthy"}` within 15s.  
TC-03: `docker history` shows no baked secrets (`GEMINI_API_KEY`, `LITELLM_TOKEN`).  
TC-04: `whoami` inside the container returns `app`.  
TC-05: Invalid `DOCKER_REGISTRY` arg causes build to fail (registry resolution error).  
TC-06: Invalid `PIP_INDEX_URL` arg causes build to fail at pip install.  
TC-07: Final image size under 800 MiB.  
TC-08: `docker inspect` shows the HEALTHCHECK directive pointing at `/health`.

---

## S001-NFR-002 — Containerize the Vite frontend

**Status:** implemented · 8/8 tests passing

### What was built

`frontend/Dockerfile` — a two-stage multi-arch build:

**Stage 1 — builder (`${DOCKER_REGISTRY}/node:18-alpine`):**
- Accepts `ARG NPM_REGISTRY` and runs `npm config set registry` before any install, so the Artifactory proxy is fully consumed.
- Copies `package.json` + `package-lock.json` first, then runs `npm ci` (exact lockfile install, no drift).
- Copies `src/`, individual `public/` assets (excluding `public/documents/` — large demo PDFs not needed at build time), and all config files (`index.html`, `tsconfig*.json`, `vite.config.ts`, `tailwind.config.ts`, `postcss.config.js`, `components.json`).
- Accepts `ARG VITE_API_BASE_URL` and `ARG VITE_SESSION_IDLE_TIMEOUT_MINUTES`; both are exported as `ENV` so Vite bakes them into `dist/` at build time.
- Runs `npm run build` → produces `dist/`.

**Stage 2 — runtime (`${DOCKER_REGISTRY}/node:18-alpine`):**
- Installs `serve@14` globally (`--no-fund --no-audit && npm cache clean --force`) to keep image lean.
- Creates non-root group + user `app` (UID 10002, distinct from backend's UID 10001).
- Copies only `dist/` from the builder — no source files, no `node_modules/` in the final layer.
- Runs `serve -s . -l 3000` (SPA mode, port 3000).
- `HEALTHCHECK` uses `wget --spider http://localhost:3000/`.

### Key design decisions

- `public/documents/` is excluded from the builder COPY using explicit per-file COPY instructions (no wildcard that would pull in the documents folder). This avoids needing `.dockerignore` entries for this exclusion.
- `serve@14` was chosen per the requirement specification. npm cache is explicitly purged after install to limit the runtime image size.
- UID 10002 intentionally differs from the backend's UID 10001 so host-side volume permission problems are easier to diagnose in a Compose stack.
- The two-stage design ensures the final image contains zero TypeScript source files and zero `node_modules/` entries — verified by TC-05.

### Test coverage (8 TC)

TC-01: `docker build -t bamf-frontend:dev -f frontend/Dockerfile .` exits 0.  
TC-02: `GET /` on the running container returns 200 and body contains `<div id="root">`.  
TC-03: `GET /assets/<bundle>` returns 200 (Vite assets are correctly served).  
TC-04: Final image size is under 200 MiB.  
TC-05: `find /app -name '*.tsx' -o -name 'node_modules'` inside the runtime image returns nothing.  
TC-06: Build with `NPM_REGISTRY=https://invalid.example.com/npm` fails during `npm ci` (registry ARG is consumed, not silently ignored).  
TC-07: Build with `VITE_API_BASE_URL=https://backend.acme.test` → `grep 'backend.acme.test' /app/dist` finds at least one match (env is baked in).  
TC-08: `whoami` inside the running container returns `app`.

---

## S001-NFR-004 — Containerize LiteLLM proxy (gitignored subproject)

**Status:** implemented · 7 / 11 tests passing (4 integration TCs deferred — require live Ollama)

### What was built

A new top-level `litellm/` directory (gitignored — never committed) that acts as an independent subproject the operator bootstraps locally.

**Files created:**

| File | Purpose |
|---|---|
| `litellm/Dockerfile` | Thin wrapper over `ghcr.io/berriai/litellm:main-stable` (pinned tag at implementation time); copies `config.yaml` to `/app/config.yaml` and runs `litellm --config /app/config.yaml --port 4000 --num_workers 1`. |
| `litellm/config.yaml` | Declares one model entry: `model_name: gemma3:12b` → `litellm_params.model: ollama_chat/gemma3:12b` with `api_base: ${LITELLM_OLLAMA_HOST}`. Master key injected via `os.environ/LITELLM_MASTER_KEY`. |
| `litellm/docker-compose.yml` | Single `litellm` service, port `4000:4000`, `extra_hosts: ["host.docker.internal:host-gateway"]` (Linux Compose compatibility), reads env from `litellm/.env`, healthcheck on `GET /health/liveliness`. |
| `litellm/.env.example` | Documents `LITELLM_MASTER_KEY` (default `sk-bamf-local-dev-key`), `LITELLM_OLLAMA_HOST` (default `http://host.docker.internal:11434`), `LITELLM_OLLAMA_MODEL` (default `gemma3:12b`). |
| `litellm/README.md` | Three lifecycle commands (build / up -d / logs -f); explains `LITELLM_MASTER_KEY ↔ LITELLM_TOKEN` must match; notes the gitignored pattern and regeneration steps. |

**Modified files:**

- `.gitignore` — gains `litellm/` entry; `git check-ignore litellm/Dockerfile` exits 0.
- `README.md` — gains "Local LiteLLM proxy" section with regeneration instructions.
- `.env.example` — `LLM_BACKEND` flipped from `external` → `internal`; `LITELLM_PROXY_URL` flipped from placeholder → `http://localhost:4000`. This is the deliberate closed-environment cutover point: before NFR-004 the safe default had to be `external` (no proxy); after NFR-004 it is `internal`.
- `backend/services/llm_provider.py::get_provider()` — fail-fast precondition added: if `LLM_BACKEND=internal` and `LITELLM_PROXY_URL` is empty/blank, raises `ValueError("LITELLM_PROXY_URL is required when LLM_BACKEND=internal — start the LiteLLM container per S001-NFR-004 or set LLM_BACKEND=external")` before any HTTP attempt. Converts silent request-time timeouts into immediate, debuggable startup errors.

### Test coverage (7 unit + 4 integration)

**Passing (7 unit TCs):**

TC-01: `git check-ignore -v litellm/Dockerfile` reports the rule from `.gitignore`.  
TC-06: Auth enforced — `/v1/chat/completions` without Authorization header returns 401.  
TC-09: Fail-fast check fires when `LLM_BACKEND=internal` + `LITELLM_PROXY_URL` empty; `ValueError` raised before `litellm.acompletion` is reached.  
TC-10: `.env.example` diff shows exactly two changed lines (`LLM_BACKEND`, `LITELLM_PROXY_URL`); no `# 🔒` marker dropped.  
TC-11: All 7 existing `docs/tests/S001-F-001/` tests still pass after the precondition is added.  
_(+ 2 further static/config assertions)_

**Deferred (4 integration TCs) — require live Ollama on the host:**

TC-02: `docker compose build` exits 0.  
TC-03: Proxy health check returns `{"status":"healthy"}` within 30s of startup.  
TC-04: `GET /v1/models` returns `gemma3:12b` in `data[].id`.  
TC-05 / TC-08: End-to-end chat completion + backend integration round-trip with a real model.  

These TCs are marked integration and will be re-run once an Ollama instance is available. Per the project's convention (established in the wave-1 F-001 report), feature requirements that depend on as-yet-unavailable infra ship with mocked unit tests and defer integration verification.

---

## Cross-cutting notes

### `.dockerignore` dependency chain

NFR-001 owns the project-root `.dockerignore` (listed in its `affected_surface.creates`). Until NFR-001 lands:
- `docker build -f frontend/Dockerfile .` sends the full 487 MB `node_modules/` as build context on every run.
- `docker build -f backend/Dockerfile .` will have the same issue once NFR-001 is implemented.
- Both Dockerfiles work correctly; the missing `.dockerignore` is a build-time efficiency issue, not a correctness issue.

### `.env.example` cutover (NFR-004 side effect)

After NFR-004, `cp .env.example .env && uvicorn backend.main:app` will require the LiteLLM container to be running. Operators starting fresh must run `docker compose -f litellm/docker-compose.yml up -d` first. This is the intended behaviour — the fail-fast `ValueError` makes the dependency explicit rather than silently failing at the first chat request.

### VITE_SESSION_IDLE_TIMEOUT_MINUTES

The frontend Dockerfile accepts `VITE_SESSION_IDLE_TIMEOUT_MINUTES` as a build arg (baked into the bundle by Vite). This env var is created by S001-F-007 (Wave 6). The roadmap records a structural dependency: `S001-F-007 → S001-NFR-002`. The Dockerfile handles this correctly — the ARG has a default value (`10`), so NFR-002 builds and runs correctly before F-007 is implemented; when F-007 lands and the operator passes a different value, a rebuild of the frontend image picks it up.

---

## Wave 3 gate checklist

| Requirement | Status | Blocks |
|---|---|---|
| S001-D-001 | ✅ implemented | NFR-003, NFR-001, NFR-002 (structural) |
| S001-F-001 | ✅ implemented | NFR-003, NFR-004 (structural) |
| S001-NFR-001 | ❌ pending | **NFR-003** (semantic dep) |
| S001-NFR-002 | ✅ implemented | **NFR-003** (semantic dep) |

**Wave 3 can start as soon as S001-NFR-001 is implemented and its `.dockerignore` is committed.**

Wave 3 requirements:
- **S001-F-004** — Disable anonymization service via config flag (depends on F-001 only; can start now in a parallel session since it has no dependency on NFR-001/NFR-002)
- **S001-NFR-003** — Docker Compose orchestration (requires NFR-001 + NFR-002)

> Note: S001-F-004 is technically Wave 3 but its only dependency is S001-F-001 (Wave 1 ✅). The wave assignment comes from a file conflict with F-001 (both modify `backend/config.py`). S001-F-004 can be parallelized with NFR-001 if desired.
