To run the full stack (LiteLLM proxy + app), use the umbrella scripts created by S001-NFR-005. The standard sequence is three commands from the repo root:

  # 1. (one-time / idempotent) generate .env and litellm/.env with matching tokens
  bash temp/setup-env.sh

  # 2. bring up the LiteLLM proxy on :4000 (gitignored litellm/ subproject)
  bash temp/up-proxy.sh

  # 3. bring up the app stack — backend on :8000, frontend nginx on :3000
  bash temp/up.sh

  Then open http://localhost:3000.

  Tear-down

  bash temp/down.sh           # stop backend + frontend
  bash temp/down-proxy.sh     # stop the LiteLLM proxy
  # add --volumes to temp/down.sh for a full reset (drops named volumes)

  Lifecycle helpers cheat sheet

  ┌──────────────────────────────────────────────┬────────────────────────────────────────────────────────┐
  │                     What                     │                        Command                         │
  ├──────────────────────────────────────────────┼────────────────────────────────────────────────────────┤
  │ Generate env files                           │ bash temp/setup-env.sh                                 │
  ├──────────────────────────────────────────────┼────────────────────────────────────────────────────────┤
  │ Start LiteLLM proxy                          │ bash temp/up-proxy.sh                                  │
  ├──────────────────────────────────────────────┼────────────────────────────────────────────────────────┤
  │ Stop LiteLLM proxy                           │ bash temp/down-proxy.sh                                │
  ├──────────────────────────────────────────────┼────────────────────────────────────────────────────────┤
  │ Start app stack (backend + frontend)         │ bash temp/up.sh                                        │
  ├──────────────────────────────────────────────┼────────────────────────────────────────────────────────┤
  │ Stop app stack                               │ bash temp/down.sh                                      │
  ├──────────────────────────────────────────────┼────────────────────────────────────────────────────────┤
  │ Full reset (incl. volumes)                   │ bash temp/down.sh --volumes && bash temp/down-proxy.sh │
  ├──────────────────────────────────────────────┼────────────────────────────────────────────────────────┤
  │ End-to-end smoke test (real chat round-trip) │ backend/venv/bin/python3 temp/verify-e2e.py            │
  └──────────────────────────────────────────────┴────────────────────────────────────────────────────────┘

  The README's ## Quickstart (Docker — recommended) section (line 46) has the same flow with prereqs (Docker engine ≥ 24, host Ollama with gemma3:12b pulled).

  ▎ Note: there is no single "run everything" command in sprint 1 — up-proxy.sh and up.sh are intentionally separate because the LiteLLM proxy lives in a gitignored
  ▎ subproject (litellm/) with its own compose file, and in production (BDOP/k8s) the proxy is provided externally and not deployed by us. If you want a one-liner for
  ▎ daily dev convenience, you can chain them: bash temp/setup-env.sh && bash temp/up-proxy.sh && bash temp/up.sh.