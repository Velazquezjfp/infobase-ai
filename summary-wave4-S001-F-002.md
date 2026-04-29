# Implementation Summary — S001-F-002
## Optional local Ollama dev container behind a Compose flag

**Date:** 2026-04-29
**Status:** Implemented — 13/13 tests passing

---

## What was done

### 1. `docker-compose.yml` — patched the existing `ollama` service block

The `ollama` service already existed (skeleton added by S001-NFR-003) but had two gaps:

- **Removed host port binding.** The service had `ports: ["11434:11434"]`, which would conflict with a host-installed Ollama running on port 11434. The binding was removed entirely; port 11434 is now only reachable on the internal Compose bridge network (via `http://ollama:11434`).
- **Added model-pull entrypoint.** A shell entrypoint was added that starts `ollama serve` in the background, polls until the API is ready, pulls `${LITELLM_OLLAMA_MODEL:-gemma3:12b}`, then waits on the server process. This covers first-run population of the `ollama-data` volume and is a no-op on subsequent starts (Ollama skips pulls for already-present models).

```yaml
ollama:
  image: "${DOCKER_REGISTRY:-docker.io}/ollama/ollama:latest"
  profiles:
    - ollama
  volumes:
    - ollama-data:/root/.ollama
  entrypoint:
    - /bin/sh
    - -c
    - "ollama serve & OLLAMA_PID=$!; until ollama list >/dev/null 2>&1; do sleep 1; done; ollama pull ${LITELLM_OLLAMA_MODEL:-gemma3:12b}; wait $OLLAMA_PID"
  restart: unless-stopped
```

### 2. `README.md` — added "Local LLM development" section

Inserted after the existing "Local LiteLLM Proxy" section. Documents both operator paths:

- **Path A (default):** Host-installed Ollama — operator already has Ollama on the host with `gemma3:12b` pre-installed; just run `docker compose up -d`.
- **Path B:** Compose-managed Ollama — use `docker compose --profile ollama up -d` for machines without a local Ollama (CI, fresh developer laptops). Documents: no host port conflict, volume persistence, model switching via `LITELLM_OLLAMA_MODEL`.

### 3. `.env.example` — no change needed

`ENABLE_OLLAMA_CONTAINER=false` was already present and correctly documented (added by a prior requirement).

---

## Files changed

| File | Change |
|------|--------|
| `docker-compose.yml` | Removed host port binding; added model-pull entrypoint |
| `README.md` | Added "Local LLM development" section |
| `docs/requirements/sprint-001/S001-F-002.md` | Updated frontmatter: `status: implemented`, test counts |

## Files created

| File | Purpose |
|------|---------|
| `docs/tests/S001-F-002/conftest.py` | Shared fixtures: `_compose()` helper, `compose_config` and `compose_config_no_profile` session fixtures |
| `docs/tests/S001-F-002/TC-S001-F-002-01.py` | Profile off: compose file declares `profiles: [ollama]`; default config has backend+frontend only |
| `docs/tests/S001-F-002/TC-S001-F-002-02.py` | Profile on: `docker compose --profile ollama config` includes the ollama service |
| `docs/tests/S001-F-002/TC-S001-F-002-03.py` | Entrypoint: compose file contains `ollama serve`, `ollama pull`, and `LITELLM_OLLAMA_MODEL:-gemma3:12b` |
| `docs/tests/S001-F-002/TC-S001-F-002-04.py` | Volume: `ollama-data` declared top-level and mounted at `/root/.ollama` |
| `docs/tests/S001-F-002/TC-S001-F-002-05.py` | No host binding; `ENABLE_OLLAMA_CONTAINER` in `.env.example`; README has the new section and `--profile ollama` |

---

## Test results

```
13 passed, 0 failed
```

TC-01 through TC-02 are static-analysis tests (parse `docker-compose.yml` and run `docker compose config`).
TC-03 through TC-05 verify the compose file structure via text/regex inspection.
TC-02/TC-04/TC-05 (docker-dependent runtime tests — actual container spin-up) are not run in the static suite; they require `docker compose --profile ollama up` and are documented in the requirement as integration-level scenarios.

---

## Acceptance criteria coverage

| Criterion | Status |
|-----------|--------|
| `ollama` service with `profiles: ["ollama"]` | Verified by TC-01, TC-02 |
| Image references `${DOCKER_REGISTRY}/ollama/ollama:latest` | Verified by TC-02 config output |
| `ollama-data` volume declared + mounted at `/root/.ollama` | Verified by TC-04 |
| Entrypoint runs `ollama pull ${LITELLM_OLLAMA_MODEL:-gemma3:12b}` | Verified by TC-03 |
| Default `docker compose up` does not start ollama | Verified by TC-01 (profile gate), TC-02 (normalized config) |
| README has "Local LLM development" section (two paths) | Verified by TC-05 |
| `ENABLE_OLLAMA_CONTAINER` in `.env.example` with default `false` | Verified by TC-05 |
