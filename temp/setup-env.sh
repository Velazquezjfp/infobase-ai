#!/usr/bin/env bash
#
# S001-NFR-005 Phase 1 — generate .env and litellm/.env from templates with consistent token.
# Idempotent: re-running is a no-op once both files exist (>=1024 bytes).
# Override the shared token via env: LITELLM_KEY=<my-secret> bash temp/setup-env.sh
#

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

LITELLM_KEY="${LITELLM_KEY:-sk-bamf-local-dev-key}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

echo "==> setup-env.sh in $ROOT"
echo "    using LITELLM token: <hidden, sha256=$(printf %s "$LITELLM_KEY" | sha256sum | cut -c1-8)…>"

# ---------- root .env ----------
need_root_init=false
if [ ! -f .env ]; then
    need_root_init=true
elif [ "$(wc -c < .env)" -lt 1024 ]; then
    echo "    .env is smaller than 1024 bytes (stub)."
    need_root_init=true
fi

if $need_root_init; then
    if [ -f .env ]; then
        cp .env ".env.bak.$TIMESTAMP"
        echo "  • backed up existing .env to .env.bak.$TIMESTAMP"
    fi
    cp .env.example .env
    if grep -q "^LITELLM_TOKEN=" .env; then
        sed -i.tmp "s|^LITELLM_TOKEN=.*$|LITELLM_TOKEN=${LITELLM_KEY}|" .env
        rm -f .env.tmp
        echo "  • created .env from .env.example, set LITELLM_TOKEN"
    else
        echo "  ! WARNING: .env.example has no LITELLM_TOKEN= line; manual edit needed"
    fi
else
    echo "  • .env exists (>=1024 bytes); preserving"
fi

# ---------- litellm/.env ----------
if [ ! -f litellm/.env ]; then
    if [ ! -f litellm/.env.example ]; then
        echo "  ! ERROR: litellm/.env.example missing — has the litellm/ subproject been created?" >&2
        exit 2
    fi
    cp litellm/.env.example litellm/.env
    if grep -q "^LITELLM_MASTER_KEY=" litellm/.env; then
        sed -i.tmp "s|^LITELLM_MASTER_KEY=.*$|LITELLM_MASTER_KEY=${LITELLM_KEY}|" litellm/.env
        rm -f litellm/.env.tmp
        echo "  • created litellm/.env from template, set LITELLM_MASTER_KEY"
    else
        echo "  ! WARNING: litellm/.env.example has no LITELLM_MASTER_KEY= line; manual edit needed"
    fi
else
    echo "  • litellm/.env exists; preserving"
fi

# ---------- consistency check ----------
ROOT_TOKEN_HASH=$(awk -F= '/^LITELLM_TOKEN=/{print $2; exit}' .env | sha256sum | awk '{print $1}')
LITELLM_KEY_HASH=$(awk -F= '/^LITELLM_MASTER_KEY=/{print $2; exit}' litellm/.env | sha256sum | awk '{print $1}')

if [ "$ROOT_TOKEN_HASH" = "$LITELLM_KEY_HASH" ]; then
    echo "  ✓ tokens match (sha256=${ROOT_TOKEN_HASH:0:8}…)"
else
    echo "  ✗ TOKENS DO NOT MATCH" >&2
    echo "    .env LITELLM_TOKEN sha256:        ${ROOT_TOKEN_HASH:0:8}…" >&2
    echo "    litellm/.env LITELLM_MASTER_KEY:  ${LITELLM_KEY_HASH:0:8}…" >&2
    echo "    fix manually or rerun with LITELLM_KEY=<same-value> bash temp/setup-env.sh" >&2
    exit 1
fi

echo "==> done. Next: bash temp/up-proxy.sh && bash temp/up.sh"
