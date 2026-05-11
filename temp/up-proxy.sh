#!/usr/bin/env bash
#
# S001-NFR-005 Phase 5 — bring up the LiteLLM proxy container.
# Asserts host Ollama is reachable, builds the proxy image, starts it, polls health.
#
# Exit codes:
#   0 — proxy healthy
#   1 — host Ollama unreachable / model missing
#   2 — proxy failed to become healthy within timeout
#

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> up-proxy.sh"

# Source .env so the substitution-defaults are visible to compose
if [ -f .env ]; then set -a; . .env; set +a; fi

OLLAMA_MODEL="${LITELLM_OLLAMA_MODEL:-gemma3:12b}"
OLLAMA_HOST="${LITELLM_OLLAMA_HOST:-http://host.docker.internal:11434}"
# For host-side check: replace docker hostname with localhost
OLLAMA_HOST_LOCAL="${OLLAMA_HOST/host.docker.internal/localhost}"

echo "  • checking host Ollama at $OLLAMA_HOST_LOCAL …"
if ! curl -sf "${OLLAMA_HOST_LOCAL}/api/tags" >/tmp/_ollama-tags.json 2>/dev/null; then
    echo "  ✗ Ollama daemon unreachable at $OLLAMA_HOST_LOCAL"
    echo "    start it with: ollama serve  (or systemctl start ollama)"
    exit 1
fi

# grep-based model check (avoids jq dependency on the host)
if ! grep -q "\"name\":\"${OLLAMA_MODEL}\"" /tmp/_ollama-tags.json; then
    echo "  ✗ model $OLLAMA_MODEL not pulled on host Ollama"
    echo "    pull it with: ollama pull $OLLAMA_MODEL"
    rm -f /tmp/_ollama-tags.json
    exit 1
fi
echo "  ✓ host Ollama serves $OLLAMA_MODEL"
rm -f /tmp/_ollama-tags.json

echo "  • building litellm image…"
docker compose -f litellm/docker-compose.yml build 2>&1 | tail -5

echo "  • starting litellm container…"
docker compose -f litellm/docker-compose.yml up -d 2>&1 | tail -5

echo "  • polling http://localhost:4000/health/liveliness (max 60s)…"
for i in $(seq 1 60); do
    if curl -sf http://localhost:4000/health/liveliness >/dev/null 2>&1; then
        echo "  ✓ proxy healthy after ${i}s"
        echo ""
        echo "==> done. Test it:"
        echo "   set -a; . litellm/.env; set +a"
        echo "   curl -sf -H \"Authorization: Bearer \$LITELLM_MASTER_KEY\" http://localhost:4000/v1/models | jq"
        exit 0
    fi
    sleep 1
done

echo "  ✗ proxy did not become healthy within 60s"
echo "  recent logs:"
docker compose -f litellm/docker-compose.yml logs --tail=30 2>&1
exit 2
