#!/usr/bin/env bash
#
# S001-NFR-005 Phase 6 — bring up the application stack (backend + frontend).
# Optional: ENABLE_OLLAMA_CONTAINER=true also starts the in-compose Ollama service.
#
# Run AFTER `temp/setup-env.sh` (creates .env / litellm/.env)
# and AFTER `temp/up-proxy.sh` (LiteLLM proxy on :4000).
#

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> up.sh"

if [ ! -f .env ]; then
    echo "  ✗ .env missing — run temp/setup-env.sh first" >&2
    exit 1
fi

# Source .env so we can read flags like ENABLE_OLLAMA_CONTAINER + ports
set -a; . .env; set +a

PROFILES_FLAG=()
if [ "${ENABLE_OLLAMA_CONTAINER:-false}" = "true" ]; then
    PROFILES_FLAG=(--profile ollama)
    echo "  • ENABLE_OLLAMA_CONTAINER=true → adding --profile ollama"
fi

BACKEND_PORT_LOCAL="${BACKEND_PORT:-8000}"
FRONTEND_PORT_LOCAL="${FRONTEND_PORT:-3000}"

# Quick proxy reachability check (informational; not fatal — operator may bring it
# up after this script).
if ! curl -sf -m 2 http://localhost:4000/health/liveliness >/dev/null 2>&1; then
    echo "  ! warning: LiteLLM proxy not responding on :4000 — backend chat will 5xx until it's up"
    echo "    bring it up with: bash temp/up-proxy.sh"
fi

echo "  • building + starting backend, frontend ${PROFILES_FLAG[*]:-}…"
docker compose up -d --build "${PROFILES_FLAG[@]}" 2>&1 | tail -10

echo "  • polling backend health (max 90s)…"
for i in $(seq 1 90); do
    # docker compose ps --format json emits one JSON object per line.
    # Each backend object includes "Service":"backend" and "Health":"healthy".
    HEALTH=$(docker compose ps --format json 2>/dev/null \
             | grep '"Service":"backend"' \
             | grep -c '"Health":"healthy"' || true)
    if [ "$HEALTH" = "1" ]; then
        echo "  ✓ backend healthy after ${i}s"
        break
    fi
    if [ "$i" -eq 90 ]; then
        echo "  ✗ backend did not become healthy within 90s"
        docker compose logs --tail=30 backend 2>&1
        exit 2
    fi
    sleep 1
done

echo "  • probing http://localhost:${BACKEND_PORT_LOCAL}/health …"
if ! curl -sf "http://localhost:${BACKEND_PORT_LOCAL}/health" >/dev/null; then
    echo "  ✗ backend /health unreachable from host"
    exit 3
fi
echo "  ✓ backend /health 200"

echo "  • probing http://localhost:${FRONTEND_PORT_LOCAL}/ …"
if ! curl -sf "http://localhost:${FRONTEND_PORT_LOCAL}/" >/dev/null; then
    echo "  ✗ frontend unreachable from host"
    exit 4
fi
echo "  ✓ frontend / 200"

echo ""
echo "==> done."
echo "   open http://localhost:${FRONTEND_PORT_LOCAL}/ in your browser"
echo "   logs: docker compose logs -f backend frontend"
echo "   tear down: bash temp/down.sh"
