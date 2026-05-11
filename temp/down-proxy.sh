#!/usr/bin/env bash
# S001-NFR-005 Phase 5 — tear down the LiteLLM proxy container.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo "==> down-proxy.sh"
docker compose -f litellm/docker-compose.yml down 2>&1 | tail -5
echo "==> done"
