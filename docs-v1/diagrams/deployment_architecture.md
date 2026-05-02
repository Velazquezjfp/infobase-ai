# Deployment Architecture — BAMF ACTE Companion

> Companion to [`deployment_architecture.mmd`](./deployment_architecture.mmd). Reading order: glance at the diagram first, then come back here for details.
>
> Scope: how the demo runs locally on a Linux/WSL2 host (Docker Compose) and how the same image set deploys to Kubernetes (BDOP). Source-of-truth requirement: [`docs/requirements/sprint-001/S001-NFR-005.md`](../../docs/requirements/sprint-001/S001-NFR-005.md).

---

## 1. The promise — single host port

The operator opens **one URL** and gets the entire application:

```
http://localhost:3000
```

Behind that one port lives:
- the React SPA (Vite-built, served as static files by nginx),
- all `/api/*` HTTP endpoints (proxied to the FastAPI backend),
- the `/ws/chat/{case_id}` WebSocket (proxied with proper Upgrade headers),
- all `/root_docs/*` and `/documents/*` PDF assets (also proxied to the backend).

This is **single-origin**: the browser never sees `:8000`, never has to do CORS, and there are zero hardcoded `localhost`-style URLs in the SPA bundle. Production deployments (BDOP/k8s) point the same image at a different backend host by changing two env vars on the frontend pod (`BACKEND_HOST`, `BACKEND_PORT`).

---

## 2. Container inventory

Three primary containers run today (plus an optional fourth):

| Service     | Image                                                    | Size     | Listens on                | Network                    |
|-------------|----------------------------------------------------------|----------|----------------------------|----------------------------|
| frontend    | `bamf-acte-companion-frontend:latest`                    | 50.4 MB  | `:3000` (HTTP/1.1, gzip)   | `bamf-acte-companion_default` (bridge) |
| backend     | `bamf-acte-companion-backend:latest`                     | 400 MB   | `:8000` (HTTP/1.1 + WS)    | `bamf-acte-companion_default` (bridge) |
| litellm     | `litellm-litellm:latest`                                 | 1.87 GB  | `:4000` (host network)     | **host** (shares host's netns) |
| ollama (opt)| `ollama/ollama:latest`                                   | varies   | `:11434` (compose net only)| `bamf-acte-companion_default` (bridge) |

Container build bases:

| Stage                 | FROM image                                       | Why                                              |
|-----------------------|--------------------------------------------------|--------------------------------------------------|
| frontend stage 1      | `node:18-alpine`                                 | `npm run build` produces `dist/`                 |
| frontend stage 2      | `nginxinc/nginx-unprivileged:1.27-alpine`        | non-root nginx, built-in envsubst entrypoint     |
| backend               | `python:3.12-slim`                               | FastAPI + uvicorn + LiteLLM SDK + websockets     |
| litellm               | `ghcr.io/berriai/litellm:v1.81.9-stable`         | upstream proxy with `prod_entrypoint.sh`         |

---

## 3. Per-container detail

### 3.1 `frontend` — nginx reverse proxy

The frontend container is the **only entry point** into the system from the operator's browser. It serves the SPA's static assets and forwards every dynamic request to the backend over Docker's internal bridge network.

**Build:**
- Stage 1 builds the SPA with `npm run build` (Vite). Critical build arg: `VITE_API_BASE_URL=` (empty) — the SPA emits relative URLs, no `localhost` baked in.
- Stage 2 copies `dist/` to `/usr/share/nginx/html/` and `frontend/nginx.conf.template` to `/etc/nginx/templates/default.conf.template`.

**Run-time templating:** the upstream `nginx-unprivileged` image runs `envsubst` on `*.template` files at container start. Two env vars get substituted:
- `BACKEND_HOST` (default `backend`)
- `BACKEND_PORT` (default `8000`)

In Compose those defaults Just Work because Docker's bridge network resolves `backend` to the backend container. In Kubernetes, override these in the Deployment to point at `backend.<namespace>.svc.cluster.local:8000`.

**nginx config — key directives:**

```nginx
upstream backend {
    server ${BACKEND_HOST}:${BACKEND_PORT};
    keepalive 16;
}

server {
    listen 3000;
    root /usr/share/nginx/html;

    gzip on;                                 # text/css/js/json
    gzip_min_length 1024;

    location / { try_files $uri $uri/ /index.html; }   # SPA fallback

    location /api/ {                                    # HTTP API
        proxy_pass http://backend;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_read_timeout 300s;
    }

    location /ws/ {                                     # WebSocket chat
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade    $http_upgrade;
        proxy_set_header Connection $connection_upgrade;   # via map block
        proxy_read_timeout 3600s;                            # cold model loads
    }

    location /root_docs/  { proxy_pass http://backend; }   # backend StaticFiles
    location /documents/  { proxy_pass http://backend; }   # backend StaticFiles
}
```

**Healthcheck:** `wget -q --spider http://127.0.0.1:3000/` (IPv4-explicit; alpine busybox wget doesn't fall back from IPv6).

### 3.2 `backend` — FastAPI + WebSocket + LLM provider

The backend is a FastAPI app run by `uvicorn` with no reverse proxy of its own — it relies on the frontend container's nginx.

**HTTP routers** (`backend/main.py:196-206`):

| Router          | Mount prefix                  | Notes                                    |
|-----------------|-------------------------------|------------------------------------------|
| `chat_router`   | (none — see below)            | Owns the `/ws/chat/{case_id}` WebSocket  |
| `admin_router`  | (none, routes are `/api/admin/*`) | Field generation, config endpoints |
| `files_router`  | `/api/files/*`                | Upload/list (gated by `ENABLE_UPLOAD`)   |
| `documents_router` | `/api/documents/*`         | Document tree, list, parse-email         |
| `context_router` | `/api/context/*`             | Case context (S5-011)                    |
| `search_router` | `/api/search/*`               | Semantic search (S5-003)                 |
| `validation_router` | `/api/validation/*`       | Case validation                          |
| `custom_context_router` | `/api/custom-context/*` | User custom rules (S5-017)            |
| `folders_router` | `/api/folders/*`             | Folder management                        |
| `idirs_router`  | `/api/idirs/*`                | IDIRS hybrid search & RAG (gated by `ENABLE_DOCUMENT_SEARCH`) |
| `session_router`| `/api/session/*`              | Ephemeral session lifecycle (S001-F-007) |

**Static-file mounts** (`backend/main.py:188-194`):

| Path           | Filesystem source                          | Notes                                |
|----------------|--------------------------------------------|--------------------------------------|
| `/root_docs/*` | `root_docs/` (baked into image)            | Source demo PDFs                     |
| `/documents/*` | `${DOCUMENTS_PATH}` = `/var/app/documents` | Mounted volume; uploaded case files  |

**Top-level endpoints:** `GET /health` (used by Docker healthcheck), `GET /` (basic info).

**WebSocket protocol** (`backend/api/chat.py:104+`):
- URL: `ws://<host>/ws/chat/{case_id}?language={de|en}`
- Frames in: `{"type":"chat","content":"…","caseId":"…"}` (also `anonymize`, `translate`)
- Frames out (streaming mode): many `chat_chunk{is_complete:false}` then one terminal `chat_chunk{is_complete:true,content:""}`
- Frames out (non-streaming): single `chat_response{content:"…"}`
- Welcome frame: `{"type":"system","content":"Connected to AI assistant for Akte-…"}`
- Error frame: `{"type":"error","message":"…"}`

**State** (important for k8s):
- `manager = ConnectionManager()` is a module-level singleton.
- `active_connections: Dict[case_id, WebSocket]` is per-process in-memory.
- **k8s deployment must set `replicas: 1` for backend.** Multi-replica chat would require Redis pub/sub or sticky sessions.

**Container-correct overrides** (compose `services.backend.environment`):
- `LITELLM_PROXY_URL=http://host.docker.internal:4000` (replaces the `.env`'s `localhost:4000` — wrong inside a container)
- `DOCUMENTS_PATH=/var/app/documents` (replaces the `.env`'s `public/documents` — that path is outside the volume mount, so files would be lost on container recreate)

**Healthcheck:** `curl -f http://localhost:8000/health`. Resource limits: 2 CPU / 2 GB.

### 3.3 `litellm` — OpenAI-compatible proxy

A thin wrapper on `ghcr.io/berriai/litellm:v1.81.9-stable` that copies `litellm/config.yaml` and runs the proxy on port 4000.

**Why it's separate from the umbrella compose:**
- `litellm/` is a gitignored subproject (per S001-NFR-004) so local secrets never get committed.
- Lifecycle is independent of the app stack — operator can restart the proxy without touching backend/frontend.
- In Kubernetes the local container is **dropped entirely**; the BDOP-managed proxy URL replaces it via `LITELLM_PROXY_URL` env on the backend pod.

**Networking choice — `network_mode: host`:**

Default Docker bridge would require the host's Ollama daemon to bind to `0.0.0.0:11434` (or at least the docker0 interface) so the proxy can reach it via `host.docker.internal:host-gateway`. That is a security-relevant host config change. Instead, the litellm container runs in the **host's network namespace** so the proxy reaches Ollama at plain `localhost:11434` (the same loopback Ollama actually binds to).

Side effects of host networking:
- `ports: ["4000:4000"]` is **not used** (the container's :4000 IS the host's :4000).
- `extra_hosts: ["host.docker.internal:host-gateway"]` is ignored.
- `LITELLM_OLLAMA_HOST=http://localhost:11434` (was `host.docker.internal:11434` in the bridge variant).

**Auth:** `Authorization: Bearer <LITELLM_MASTER_KEY>` enforced on every request. `LITELLM_TOKEN` (set in root `.env`) MUST equal `LITELLM_MASTER_KEY` (set in `litellm/.env`). `temp/setup-env.sh` enforces this and verifies via sha256.

**Healthcheck:** `curl -sf http://localhost:4000/health/liveliness`. Note: the `/health/liveliness` endpoint returns `"I'm alive!"` (LiteLLM convention; not the literal word "healthy"). Some legacy NFR-004 tests assert on the wrong string — known stale assertion, not a runtime defect.

### 3.4 `ollama` (optional, profile-gated)

When `docker compose --profile ollama up -d` is used, an in-compose Ollama container starts with the `ollama/ollama:latest` image. It binds NO host ports (avoids collision with a host-installed Ollama), mounts `ollama-data` for model weights, and pulls `${LITELLM_OLLAMA_MODEL:-gemma3:12b}` on start.

The flag `ENABLE_OLLAMA_CONTAINER` in `.env.example` is an intent flag the operator sets to `true`; `temp/up.sh` reads it and translates it into `--profile ollama` because Compose v3.9 cannot conditionally activate profiles from env vars.

In sprint 1 the demo defaults to **using the host's Ollama daemon** (no in-compose Ollama). The optional path exists for fresh laptops / CI.

---

## 4. Routing table — full URL → handler map

What the browser sends → who handles it → where the data ends up.

| Browser URL                                 | nginx location  | Forwarded to                     | Final handler                           |
|---------------------------------------------|-----------------|----------------------------------|-----------------------------------------|
| `http://localhost:3000/`                    | `location /`    | (none — static)                  | nginx serves `index.html`               |
| `http://localhost:3000/assets/index-*.js`   | `location /`    | (none — static)                  | nginx serves the JS bundle (gzipped)    |
| `http://localhost:3000/api/documents/all`   | `location /api/`| `http://backend:8000/api/documents/all` | FastAPI `documents_router`         |
| `http://localhost:3000/api/admin/health`    | `location /api/`| `http://backend:8000/api/admin/health`  | FastAPI `admin_router`             |
| `ws://localhost:3000/ws/chat/ACTE-2024-001` | `location /ws/` | `http://backend:8000/ws/chat/ACTE-2024-001` (WS Upgrade) | FastAPI `chat_router` |
| `http://localhost:3000/root_docs/foo.pdf`   | `location /root_docs/` | `http://backend:8000/root_docs/foo.pdf` | FastAPI `StaticFiles` mount       |
| `http://localhost:3000/documents/ACTE-…/Anmeldeformular.pdf` | `location /documents/` | `http://backend:8000/documents/...` | FastAPI `StaticFiles` mount |

> The routing in nginx uses `proxy_pass http://backend;` (no trailing slash), so the full request URI is forwarded. `proxy_pass http://backend/;` would strip the location prefix — wrong for our paths.

---

## 5. Communication flows — the four hops

### Hop 1 — browser → frontend container (`:3000`)

- HTTP/1.1 (no HTTP/2 advertised in sprint 1; that's a later hardening step).
- Static content served from `/usr/share/nginx/html/` with gzip on.
- WS Upgrade for `/ws/*` paths.

### Hop 2 — frontend container → backend container (`backend:8000`)

- Protocol: HTTP/1.1, plus WebSocket Upgrade.
- DNS: Docker bridge `bamf-acte-companion_default` resolves `backend` to `172.22.0.2`.
- Headers preserved: `Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`.
- Idempotent retry: not configured (sprint 1).
- Long-lived connection idle timeout: 3600 s for `/ws/`, 300 s for `/api/`, 60 s for `/{root_docs,documents}/`.

### Hop 3 — backend container → LiteLLM proxy (`host.docker.internal:4000`)

- Protocol: HTTP/1.1 (LiteLLM SDK uses `aiohttp`).
- DNS: `host.docker.internal` resolves to `172.22.0.1` (the bridge gateway) thanks to `extra_hosts: ["host.docker.internal:host-gateway"]` on the backend service.
- Header: `Authorization: Bearer ${LITELLM_TOKEN}`.
- Endpoints used: `POST /v1/chat/completions`.

### Hop 4 — LiteLLM proxy → host Ollama (`localhost:11434`)

- Protocol: HTTP/1.1 (Ollama API, OpenAI-shaped).
- DNS: `localhost` resolves to the host loopback because of `network_mode: host` (proxy is in host's netns, not Docker's bridge).
- Endpoint: `POST /api/generate` with model `ollama_chat/gemma3:12b`.

---

## 6. Volumes & persistent state

Three named volumes carry the application's persistent state. In Kubernetes these become PVCs.

| Volume name                              | Mount path inside container          | What it holds                              | Owner          |
|------------------------------------------|--------------------------------------|--------------------------------------------|----------------|
| `bamf-acte-companion_documents-data`     | `/var/app/documents`                 | Uploaded case files (when `ENABLE_UPLOAD=true`) | `app:app` (10001:10001) |
| `bamf-acte-companion_cases-data`         | `/app/backend/data/contexts/cases`   | Per-case state, custom-context rules        | `app:app` (10001:10001) |
| `bamf-acte-companion_manifest-data`      | `/app/backend/data`                  | `document_manifest.json` (idempotency / scan reconciliation) | `app:app` (10001:10001) |
| `bamf-acte-companion_ollama-data` (opt.) | `/root/.ollama` (only when `--profile ollama`) | Ollama model weights                  | (per Ollama image) |

On first init, named volumes copy the seed contents from the image's path. The backend Dockerfile pre-creates the mount points with `app:app` ownership specifically so the volumes don't default to `root:root` (which would block writes by the non-root user).

---

## 7. Environment variables — who reads what

| Variable                       | Read by                                      | Default value (sprint 1)               | Notes                                            |
|--------------------------------|----------------------------------------------|----------------------------------------|--------------------------------------------------|
| `BACKEND_HOST` / `BACKEND_PORT` | frontend container (envsubst on nginx tmpl) | `backend` / `8000`                     | k8s overrides to repoint the upstream            |
| `LITELLM_PROXY_URL`            | backend (`llm_provider.py`)                  | `http://host.docker.internal:4000` (compose), `http://localhost:4000` (host-run), BDOP-provided URL (k8s) | Container-run override comes from compose `environment:`, not `.env` |
| `LITELLM_TOKEN`                | backend (Bearer token)                       | `sk-bamf-local-dev-key`                | Must equal `LITELLM_MASTER_KEY` in `litellm/.env` |
| `LITELLM_MODEL`                | backend (model name to send)                 | `gemma3:12b`                           | LiteLLM proxy must serve a model with the same `model_name` |
| `LITELLM_MASTER_KEY`           | litellm container (auth enforce)             | `sk-bamf-local-dev-key`                | The proxy's master token                          |
| `LITELLM_OLLAMA_HOST`          | litellm container (config.yaml `os.environ/`) | `http://localhost:11434`              | Where the proxy routes Ollama traffic; `localhost` because of host networking |
| `LITELLM_OLLAMA_MODEL`         | optional Ollama container (entrypoint)        | `gemma3:12b`                          | Model the in-compose Ollama pulls on start        |
| `LLM_BACKEND`                  | backend (`get_provider()`)                   | `internal`                             | `internal` = LiteLLM, `external` = Gemini direct  |
| `GEMINI_API_KEY`               | backend (only if `LLM_BACKEND=external`)     | (not set in closed-environment demo)   | Replaces LiteLLM in the external path             |
| `DOCUMENTS_PATH`               | backend (StaticFiles mount + uploads)        | `/var/app/documents` (compose override) | The compose `environment:` block overrides the `.env.example` value `public/documents` |
| `ENABLE_ANONYMIZATION` / `_DOCUMENT_SEARCH` / `_UPLOAD` | backend feature gates       | `false` / `false` / `false`            | Sprint-1 disabled-feature notices                  |
| `SESSION_IDLE_TIMEOUT_MINUTES` | backend (idle reset) + SPA (build-time)      | `10`                                   | Ephemeral one-shot session                         |
| `BACKEND_PORT` / `FRONTEND_PORT` | compose host-port mapping                  | `8000` / `3000`                        | Demoed on host as `localhost:${PORT}`             |
| `DOCKER_REGISTRY`              | both Dockerfiles                             | `docker.io`                            | Override to point at Artifactory in BDOP          |
| `NPM_REGISTRY`                 | frontend Dockerfile                          | `https://registry.npmjs.org/`          | Same — Artifactory in BDOP                         |
| `PIP_INDEX_URL`                | backend Dockerfile                           | `https://pypi.org/simple`              | Same — Artifactory in BDOP                         |
| `INIT_TEST_DOCS`               | backend startup                              | `false`                                | When `true`, auto-loads the demo case             |
| `LOG_LEVEL`                    | backend (logging)                            | `INFO`                                 |                                                  |

---

## 8. Healthchecks & resource limits

| Service     | Healthcheck command                              | Interval | Resource limits     |
|-------------|--------------------------------------------------|----------|---------------------|
| frontend    | `wget -q --spider http://127.0.0.1:3000/`        | 30 s     | 1 CPU / 1024 MB     |
| backend     | `curl -f http://localhost:8000/health`           | 30 s     | 2 CPU / 2048 MB     |
| litellm     | `curl -sf http://localhost:4000/health/liveliness` | 10 s   | (uncapped in sprint 1) |
| ollama (opt)| (none in compose — relies on `ollama list` loop) | n/a      | (uncapped) |

> Compose's `deploy.resources.limits` is informational under `docker compose up`; it's enforced under Swarm and translates directly to k8s `resources.{requests,limits}`.

---

## 9. Operator lifecycle — the umbrella scripts

All under `temp/` (gitignored). Run from the repository root.

| Script                  | What it does                                                                 |
|-------------------------|------------------------------------------------------------------------------|
| `temp/setup-env.sh`     | Idempotent: creates `.env` and `litellm/.env` from templates with matching tokens (`LITELLM_TOKEN == LITELLM_MASTER_KEY`); backs up stub `.env` files |
| `temp/up-proxy.sh`      | Verifies host Ollama serves `gemma3:12b`, then `docker compose -f litellm/docker-compose.yml build && up -d`, polls `/health/liveliness` |
| `temp/down-proxy.sh`    | `docker compose -f litellm/docker-compose.yml down`                          |
| `temp/up.sh`            | Reads `ENABLE_OLLAMA_CONTAINER` to optionally add `--profile ollama`, then `docker compose up -d --build`, polls backend health, then host probes |
| `temp/down.sh`          | `docker compose down` (with optional `--volumes` for full reset)             |
| `temp/verify-e2e.py`    | Python WS test driver: connects via both `:3000` (proxied) and `:8000` (direct), sends a chat prompt, asserts a non-empty response |

**Standard bring-up:**
```bash
bash temp/setup-env.sh
bash temp/up-proxy.sh
bash temp/up.sh
# now: open http://localhost:3000
```

**Standard tear-down:**
```bash
bash temp/down.sh
bash temp/down-proxy.sh
```

---

## 10. From local Compose to Kubernetes (BDOP) — what stays, what changes

### What stays the same
- The same `frontend` and `backend` images deploy to k8s without modification.
- The nginx reverse-proxy pattern (frontend = single origin) translates 1:1 to a k8s `Service` exposing `:3000` and an `Ingress` mapping a public hostname.
- Resource limits are already aligned with k8s `resources.{requests,limits}` semantics.
- The backend's container-run `environment:` overrides (`LITELLM_PROXY_URL`, `DOCUMENTS_PATH`) become identical entries on the Deployment.

### What changes
- **The `litellm/` subproject is dropped.** BDOP provides a managed LiteLLM proxy URL; the backend just consumes `LITELLM_PROXY_URL=https://litellm.bdop.internal:4000` and the rest works.
- **The named volumes become PVCs.** Same mount points (`/var/app/documents`, `/app/backend/data/contexts/cases`, `/app/backend/data`).
- **`extra_hosts: host-gateway` becomes irrelevant.** k8s pod networking already provides Service DNS for any pod the backend needs to reach.
- **`network_mode: host` does not exist** on the litellm container in k8s — it's dropped along with the local proxy.
- **Frontend nginx upstream** is overridden via Deployment env: `BACKEND_HOST=backend.<namespace>.svc.cluster.local`, `BACKEND_PORT=8000`. No image rebuild needed.
- **Backend `services.backend.ports`** (host-mapped `:8000`) is dropped — the backend Service is `ClusterIP`-only; only the frontend is exposed via Ingress.
- **`replicas: 1` on the backend Deployment is mandatory** (in-memory `ConnectionManager`).
- **Registry overrides** (`DOCKER_REGISTRY`, `NPM_REGISTRY`, `PIP_INDEX_URL`) point at the BDOP Artifactory.

### What's still out of scope for sprint 1 (post-sprint follow-ups)
- Writing the actual k8s manifests (Deployment / Service / Ingress / ConfigMap / PVC).
- Backend `CORS_ALLOW_ORIGINS` configurability — currently hardcoded localhost list in `backend/main.py:166-180`. Single-origin proxy makes CORS moot for the proxied path; production with arbitrary public hostnames needs env-driven origins.
- PDF.js worker is loaded from `unpkg.com` — won't work in closed-environment k8s; should be vendored to `public/`.
- Multi-replica chat (Redis pub/sub or sticky sessions) — required only if scaling the demo beyond 1 backend pod.

---

## 11. Quick reference — health probe URLs

While the stack is up, the operator can verify each layer:

```bash
# Frontend (single-origin entry)
curl -sf http://localhost:3000/                    # SPA HTML
curl -sf http://localhost:3000/api/documents/all   # proxies to backend
curl -sI -H "Accept-Encoding: gzip" http://localhost:3000/   # gzip headers

# Backend (direct, kept exposed for sprint-1 dev only)
curl -sf http://localhost:8000/health

# LiteLLM proxy
curl -sf http://localhost:4000/health/liveliness
set -a; . litellm/.env; set +a
curl -sf -H "Authorization: Bearer $LITELLM_MASTER_KEY" http://localhost:4000/v1/models

# Host Ollama
curl -sf http://localhost:11434/api/tags

# End-to-end WebSocket chat
backend/venv/bin/python3 temp/verify-e2e.py
```

---

## 12. Key file references

- **Architecture spec:** [`docs/requirements/sprint-001/S001-NFR-005.md`](../../docs/requirements/sprint-001/S001-NFR-005.md)
- **Compose:** [`docker-compose.yml`](../../docker-compose.yml)
- **Backend Dockerfile:** [`backend/Dockerfile`](../../backend/Dockerfile)
- **Frontend Dockerfile:** [`frontend/Dockerfile`](../../frontend/Dockerfile)
- **Frontend nginx template:** [`frontend/nginx.conf.template`](../../frontend/nginx.conf.template)
- **LiteLLM compose (gitignored):** `litellm/docker-compose.yml` (regen instructions in `litellm/README.md`)
- **Env schema:** [`.env.example`](../../.env.example)
- **API client (single source of URL truth):** [`src/lib/apiConfig.ts`](../../src/lib/apiConfig.ts)
- **Chat WebSocket handler:** [`backend/api/chat.py`](../../backend/api/chat.py)
- **LLM provider abstraction:** [`backend/services/llm_provider.py`](../../backend/services/llm_provider.py)
