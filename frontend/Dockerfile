# Global ARG is available to all FROM instructions.
ARG DOCKER_REGISTRY=docker.io

# ---- Stage 1: builder ----
FROM ${DOCKER_REGISTRY}/node:18-alpine AS builder

WORKDIR /app

ARG NPM_REGISTRY=https://registry.npmjs.org
RUN npm config set registry "${NPM_REGISTRY}"

COPY package.json package-lock.json ./
RUN npm ci

# Copy source files; public/documents/ is intentionally excluded (large demo PDFs).
COPY src/ ./src/
COPY public/favicon.ico public/placeholder.svg public/robots.txt ./public/
COPY index.html vite.config.ts tailwind.config.ts postcss.config.js components.json ./
COPY tsconfig*.json ./

# Vite bakes these into the bundle at build time.
ARG VITE_API_BASE_URL=http://localhost:8000
ARG VITE_SESSION_IDLE_TIMEOUT_MINUTES=10
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_SESSION_IDLE_TIMEOUT_MINUTES=${VITE_SESSION_IDLE_TIMEOUT_MINUTES}

RUN npm run build

# ---- Stage 2: runtime ----
FROM ${DOCKER_REGISTRY}/node:18-alpine

RUN npm install -g serve@14 --no-fund --no-audit && npm cache clean --force

# UID 10002 — differs from backend's 10001.
RUN addgroup -g 10002 -S app && adduser -u 10002 -S -G app app

COPY --from=builder /app/dist /app/dist

WORKDIR /app/dist

USER app

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -q --spider http://localhost:3000/ || exit 1

CMD ["serve", "-s", ".", "-l", "3000"]
