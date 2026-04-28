# Sprint 001 — Execution Roadmap

_Generated from `_dep-graph.json`. Do not edit manually — regenerate with `/sprint-roadmap-update 001` when requirements change._

**Summary:** 14 requirements across 7 waves. 20 file conflicts auto-resolved. 3 requirements already implemented (S001-D-001, S001-F-001, S001-F-008).

## Wave 1 — Foundational

_These requirements have no pending dependencies and can execute in parallel sessions._

- **S001-D-001** — Centralized .env schema for closed-environment deployment (data, **implemented**)
  - Affected: creates 6, reads 9
  - File: `docs/requirements/sprint-001/S001-D-001.md`

- **S001-F-001** — Pluggable LLM backend with LiteLLM proxy and Gemini fallback (functional, **implemented**)
  - Affected: creates 13, modifies 15, reads 2
  - File: `docs/requirements/sprint-001/S001-F-001.md`

- **S001-F-008** — German-first localization with graceful missing-translation fallback (functional, **implemented**)
  - Affected: creates 1, modifies 2, reads 3
  - File: `docs/requirements/sprint-001/S001-F-008.md`

## Wave 2 — Feature

_Runs after Wave 1 completes._

- **S001-F-003** — Render dynamic-context URLs as plain text in the closed environment (functional)
  - Depends on: S001-F-001
  - Affected: modifies 8, reads 2
  - File: `docs/requirements/sprint-001/S001-F-003.md`

- **S001-NFR-001** — Containerize the FastAPI backend with Artifactory-friendly Dockerfile (non-functional)
  - Depends on: S001-D-001
  - Affected: creates 2, reads 14
  - File: `docs/requirements/sprint-001/S001-NFR-001.md`

- **S001-NFR-002** — Containerize the Vite frontend with Artifactory-friendly Dockerfile (non-functional)
  - Depends on: S001-D-001
  - Affected: creates 1, reads 11
  - File: `docs/requirements/sprint-001/S001-NFR-002.md`

- **S001-NFR-004** — Containerize the LiteLLM proxy as a self-contained litellm/ subproject (gitignored) (non-functional)
  - Depends on: S001-D-001, S001-F-001
  - Affected: creates 3, modifies 5, reads 4
  - File: `docs/requirements/sprint-001/S001-NFR-004.md`

## Wave 3 — Feature

_Runs after Wave 2 completes._

- **S001-F-004** — Disable anonymization service via config flag with user-facing notice (functional)
  - Depends on: S001-F-001
  - Affected: creates 2, modifies 6, reads 4
  - File: `docs/requirements/sprint-001/S001-F-004.md`

- **S001-NFR-003** — Docker Compose orchestration for backend + frontend with persistent volumes (non-functional)
  - Depends on: S001-D-001, S001-F-001, S001-NFR-001, S001-NFR-002
  - Affected: creates 1, modifies 1, reads 21
  - File: `docs/requirements/sprint-001/S001-NFR-003.md`

## Wave 4 — Feature

_Runs after Wave 3 completes._

- **S001-F-002** — Optional local Ollama dev container behind a Compose flag (functional)
  - Depends on: S001-D-001, S001-NFR-003, S001-NFR-004
  - Affected: creates 1, modifies 2, reads 2
  - File: `docs/requirements/sprint-001/S001-F-002.md`

- **S001-F-005** — Disable IDIRS document-search and RAG via config flag with user-facing notice (functional)
  - Depends on: S001-F-001, S001-F-003, S001-F-004
  - Affected: creates 2, modifies 11, reads 2
  - File: `docs/requirements/sprint-001/S001-F-005.md`

## Wave 5 — Feature

_Runs after Wave 4 completes._

- **S001-F-006** — Disable file upload via config flag with user-facing notice (functional)
  - Depends on: S001-F-001, S001-F-003, S001-F-004, S001-F-005
  - Affected: creates 2, modifies 16
  - File: `docs/requirements/sprint-001/S001-F-006.md`

## Wave 6 — Feature

_Runs after Wave 5 completes._

- **S001-F-007** — Ephemeral one-shot session with root_docs reset on logout, close, or 10-min idle (functional)
  - Depends on: S001-F-001, S001-F-003, S001-F-004, S001-F-005, S001-F-006
  - Affected: creates 11, modifies 8, reads 7
  - File: `docs/requirements/sprint-001/S001-F-007.md`

## Wave 7 — Feature

_Runs after Wave 6 completes._

- **S001-F-009** — Resolve documented anti-patterns in API and environment surfaces (functional)
  - Depends on: S001-D-001, S001-F-003, S001-F-004, S001-F-005, S001-F-006, S001-F-007
  - Affected: creates 5, modifies 20, deletes 1
  - File: `docs/requirements/sprint-001/S001-F-009.md`

## Dependency edges

### Semantic (from requirement text)

- **S001-NFR-001** → **S001-NFR-003** — S001-NFR-003 declares a semantic dependency on S001-NFR-001
- **S001-NFR-002** → **S001-NFR-003** — S001-NFR-003 declares a semantic dependency on S001-NFR-002
- **S001-NFR-003** → **S001-F-002** — S001-F-002 declares a semantic dependency on S001-NFR-003

### Structural (from affected_surface)

- **S001-D-001** → **S001-F-002** — S001-F-002 reads env_var 'docker_registry' which S001-D-001 creates
- **S001-D-001** → **S001-F-009** — S001-F-009 deletes env_var 'vite_api_url' which S001-D-001 reads — delete after reads
- **S001-D-001** → **S001-NFR-001** — S001-NFR-001 reads env_var 'docker_registry' which S001-D-001 creates
- **S001-D-001** → **S001-NFR-002** — S001-NFR-002 reads env_var 'docker_registry' which S001-D-001 creates
- **S001-D-001** → **S001-NFR-003** — S001-NFR-003 reads file '.env.example' which S001-D-001 creates
- **S001-D-001** → **S001-NFR-004** — S001-NFR-004 modifies file '.env.example' which S001-D-001 creates
- **S001-F-001** → **S001-NFR-003** — S001-NFR-003 reads env_var 'llm_backend' which S001-F-001 creates
- **S001-F-001** → **S001-NFR-004** — S001-NFR-004 reads env_var 'litellm_proxy_url' which S001-F-001 creates
- **S001-F-004** → **S001-NFR-003** — S001-NFR-003 reads env_var 'enable_anonymization' which S001-F-004 creates
- **S001-F-005** → **S001-NFR-003** — S001-NFR-003 reads env_var 'enable_document_search' which S001-F-005 creates
- **S001-F-006** → **S001-NFR-003** — S001-NFR-003 reads env_var 'enable_upload' which S001-F-006 creates
- **S001-F-007** → **S001-NFR-002** — S001-NFR-002 reads env_var 'vite_session_idle_timeout_minutes' which S001-F-007 creates
- **S001-F-007** → **S001-NFR-003** — S001-NFR-003 reads env_var 'session_idle_timeout_minutes' which S001-F-007 creates
- **S001-NFR-004** → **S001-F-002** — S001-F-002 reads env_var 'litellm_ollama_model' which S001-NFR-004 creates

### Conflicts (auto-resolved)

- **S001-F-001** → **S001-F-003** — both modify file 'backend/services/gemini_service.py' — S001-F-003 deferred to avoid parallel-edit collision
- **S001-F-001** → **S001-F-004** — both modify file 'backend/config.py' — S001-F-004 deferred to avoid parallel-edit collision
- **S001-F-001** → **S001-F-005** — both modify file 'backend/config.py' — S001-F-005 deferred to avoid parallel-edit collision
- **S001-F-001** → **S001-F-006** — both modify file 'backend/config.py' — S001-F-006 deferred to avoid parallel-edit collision
- **S001-F-001** → **S001-F-007** — both modify file 'backend/config.py' — S001-F-007 deferred to avoid parallel-edit collision
- **S001-F-003** → **S001-F-004** — both modify file 'src/i18n/locales/de.json' — S001-F-004 deferred to avoid parallel-edit collision
- **S001-F-003** → **S001-F-005** — both modify file 'src/i18n/locales/de.json' — S001-F-005 deferred to avoid parallel-edit collision
- **S001-F-003** → **S001-F-006** — both modify file 'src/i18n/locales/de.json' — S001-F-006 deferred to avoid parallel-edit collision
- **S001-F-003** → **S001-F-007** — both modify file 'src/i18n/locales/de.json' — S001-F-007 deferred to avoid parallel-edit collision
- **S001-F-003** → **S001-F-009** — both modify file 'src/components/workspace/contexthierarchydialog.tsx' — S001-F-009 deferred to avoid parallel-edit collision
- **S001-F-004** → **S001-F-005** — both modify file 'backend/config.py' — S001-F-005 deferred to avoid parallel-edit collision
- **S001-F-004** → **S001-F-006** — both modify file 'backend/config.py' — S001-F-006 deferred to avoid parallel-edit collision
- **S001-F-004** → **S001-F-007** — both modify file 'backend/config.py' — S001-F-007 deferred to avoid parallel-edit collision
- **S001-F-004** → **S001-F-009** — both modify file 'backend/api/chat.py' — S001-F-009 deferred to avoid parallel-edit collision
- **S001-F-005** → **S001-F-006** — both modify file 'backend/config.py' — S001-F-006 deferred to avoid parallel-edit collision
- **S001-F-005** → **S001-F-007** — both modify file 'backend/config.py' — S001-F-007 deferred to avoid parallel-edit collision
- **S001-F-005** → **S001-F-009** — both modify file 'backend/api/search.py' — S001-F-009 deferred to avoid parallel-edit collision
- **S001-F-006** → **S001-F-007** — both modify file 'backend/config.py' — S001-F-007 deferred to avoid parallel-edit collision
- **S001-F-006** → **S001-F-009** — both modify file 'backend/api/files.py' — S001-F-009 deferred to avoid parallel-edit collision
- **S001-F-007** → **S001-F-009** — both modify file 'src/contexts/appcontext.tsx' — S001-F-009 deferred to avoid parallel-edit collision

_Conflicts mean the target requirement was pushed to a later wave because it would have modified the same file as the source. Both still execute; they just can't be parallel._
