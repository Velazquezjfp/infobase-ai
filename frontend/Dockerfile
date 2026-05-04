# S001-NFR-005 Phase 1.5 — frontend container is now an nginx reverse proxy.
# Stage 1 (builder) is unchanged from NFR-002; only Stage 2 changes.
#
# Global ARG is available to all FROM instructions.
ARG DOCKER_REGISTRY=docker.io

# ---- Stage 1: builder ----
FROM ${DOCKER_REGISTRY}/node:20-alpine AS builder

WORKDIR /app

ARG NPM_REGISTRY=https://registry.npmjs.org
RUN npm config set registry "${NPM_REGISTRY}" && \
    npm config set strict-ssl false

COPY package.json package-lock.json ./

# S001-NFR-005 diagnostic mode (closed-environment Artifactory).
# Replaced strict `npm ci` with `npm install --verbose` to:
#   1) bypass `npm ci`'s lockfile strictness, which combined with mirror
#      quirks reproducibly triggers npm 10.x's "Exit handler never called!"
#      bug (https://github.com/npm/cli/issues/7657 and similar);
#   2) skip the audit + funding endpoints that some Artifactory virtual
#      repos don't proxy correctly (404 → trips the same exit-handler bug);
#   3) prefer-offline so cached metadata is reused when available;
#   4) legacy-peer-deps to allow lockfile↔mirror version drift to resolve;
#   5) maximum verbose output so any future failure surfaces the actual
#      cause (specific package, HTTP status, tarball integrity, etc.)
#      instead of vanishing into npm's broken error reporter.
# On failure, dump npm's own debug log file (the one referenced in the
# error message) so the build output contains all available diagnostics,
# AND propagate exit 1 so buildah stops the build instead of silently
# continuing past the failure.
RUN npm install \
        --verbose \
        --no-audit \
        --no-fund \
        --prefer-offline \
        --legacy-peer-deps \
    || { \
        echo "==================================================="; \
        echo "  npm install FAILED — dumping all available logs"; \
        echo "==================================================="; \
        echo "--- /root/.npm/_logs/ contents ---"; \
        ls -la /root/.npm/_logs/ 2>/dev/null || echo "(directory missing)"; \
        echo "--- last 500 lines of every debug log ---"; \
        for f in /root/.npm/_logs/*-debug-0.log; do \
            [ -f "$f" ] || continue; \
            echo "--- $f ---"; \
            tail -500 "$f"; \
        done; \
        echo "--- npm config ---"; \
        npm config list -l 2>/dev/null || true; \
        echo "==================================================="; \
        exit 1; \
    }

# Copy source files; public/documents/ is intentionally excluded (large demo PDFs).
COPY src/ ./src/
COPY public/favicon.ico public/placeholder.svg public/robots.txt ./public/
COPY index.html vite.config.ts tailwind.config.ts postcss.config.js components.json ./
COPY tsconfig*.json ./

# Vite bakes these into the bundle at build time.
# Default is now empty: the SPA emits relative URLs (`/api/...`, `/ws/...`)
# and the frontend container's nginx forwards to the backend.
ARG VITE_API_BASE_URL=
ARG VITE_SESSION_IDLE_TIMEOUT_MINUTES=10
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_SESSION_IDLE_TIMEOUT_MINUTES=${VITE_SESSION_IDLE_TIMEOUT_MINUTES}

RUN npm run build

# ---- Stage 2: nginx runtime (reverse proxy) ----
FROM ${DOCKER_REGISTRY}/nginxinc/nginx-unprivileged:1.27-alpine

# nginx-unprivileged runs as user `nginx` (uid 101); built-in entrypoint does
# envsubst on /etc/nginx/templates/*.template at start; output goes to
# /etc/nginx/conf.d/<name>.conf which is included by the default nginx.conf.

COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf.template /etc/nginx/templates/default.conf.template

# Defaults that work under docker-compose's default bridge network.
# k8s Deployment overrides these via env (e.g. backend.bamf.svc.cluster.local).
ENV BACKEND_HOST=backend \
    BACKEND_PORT=8000

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -q --spider http://127.0.0.1:3000/ || exit 1
# Note: 127.0.0.1 (IPv4 explicit) — busybox wget in Alpine tries IPv6 first
# and doesn't fall back, so `localhost` would attempt ::1 and fail because
# nginx in this image listens on 0.0.0.0 only.

# Inherit upstream image's CMD (`nginx -g "daemon off;"`); entrypoint chain
# runs the envsubst pass first.
