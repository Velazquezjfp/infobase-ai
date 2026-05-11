#!/usr/bin/env bash
# S001-NFR-005 Phase 6 — tear down the application stack.
# Pass --volumes to also drop the named volumes (full reset).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo "==> down.sh"
docker compose --profile ollama down "$@" 2>&1 | tail -10
echo "==> done"
