# BAMF ACTE Companion

AI-powered case management system for BAMF asylum case processing. Features context-aware document analysis, intelligent form filling with SHACL validation, dynamic AI context injection, and natural language administration.

## What This App Does

A caseworker opens an **Akte** (case file) containing folders of documents (passports, certificates, emails, evidence). An AI assistant understands the full case context -- regulations, required documents, validation rules -- and helps the caseworker:

- **Analyze documents** with case-specific knowledge (e.g. "Is this passport valid for this application type?")
- **Auto-fill forms** by extracting data from uploaded documents, with suggestions for conflicting values
- **Validate the case** before submission, scoring completeness and flagging issues
- **Modify forms** via natural language ("Add a required email field for contact")
- **Search documents** semantically across languages
- **Translate** documents between German, English, and Arabic
- **Anonymize** identity documents (PII masking via external service)
- **Add custom rules** that the AI enforces during validation

The AI's context changes dynamically as the user navigates between cases, folders, and documents -- see [Context Management](#context-management) below.

## Quick Start

### Prerequisites

- **Node.js 16+** and npm
- **Python 3.8+**
- **Google Gemini API key** ([get one here](https://aistudio.google.com/app/apikey))

### Start the App

```bash
# 1. Configure API key
echo "GEMINI_API_KEY=your_api_key_here" > backend/.env

# 2. Start everything
./start.sh
```

The script installs dependencies and starts both services:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs

Login with any name (no auth system -- this is a demo).

<details>
<summary>Manual setup</summary>

**Terminal 1 -- Backend:**
```bash
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt
echo "GEMINI_API_KEY=your_key" > backend/.env
PYTHONPATH="${PWD}:${PYTHONPATH}" python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 -- Frontend:**
```bash
npm install
npm run dev
```
</details>

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, shadcn/ui, Tailwind CSS, TanStack Query |
| Backend | FastAPI (Python), Uvicorn, Pydantic |
| AI | Google Gemini API (gemini-2.5-flash) |
| Real-time | WebSocket (chat streaming, form updates, notifications) |
| Storage | JSON files on filesystem -- **no database** |
| i18n | i18next with German and English locales |

## Architecture Overview

The system has four layers with strict separation:

```
Frontend (React SPA)  -->  API Layer (FastAPI Routers)  -->  Services Layer  -->  JSON File Storage
       |                         |                              |
   WebSocket  <--->  Chat API (streaming)  <--->  Gemini Service + Context Manager
```

See the full architecture diagram: [`docs/diagrams/architecture.mmd`](docs/diagrams/architecture.mmd)

### Backend: 9 API Routers, 12 Services

**API Routers** (`backend/api/`):

| Router | Prefix | Purpose |
|--------|--------|---------|
| `chat.py` | WebSocket `/ws/chat/{case_id}` | Real-time AI chat with streaming |
| `admin.py` | `/api/admin` | NL field generation, form modification |
| `files.py` | `/api/files` | Upload, delete, duplicate detection |
| `documents.py` | `/api/documents` | Document tree, PDF extraction, email parsing |
| `search.py` | `/api/search` | Semantic search across documents |
| `validation.py` | `/api/validation` | AI-powered case scoring and warnings |
| `context.py` | `/api/context` | Case context and document tree view |
| `custom_context.py` | `/api/custom-context` | Custom validation rules CRUD |
| `folders.py` | `/api/folders` | Folder CRUD, reorder, bulk update |

**Services** (`backend/services/`):

| Service | Purpose |
|---------|---------|
| `gemini_service.py` | Central AI brain -- chat, analysis, extraction, translation, search |
| `context_manager.py` | Hierarchical context loading with case isolation and tree caching |
| `validation_service.py` | Case validation with structured scoring and custom rules |
| `shacl_generator.py` | NL form modification with SHACL shape generation |
| `field_generator.py` | AI-powered form field creation with SHACL metadata |
| `conversation_manager.py` | In-memory chat history with token budget |
| `document_registry.py` | Document manifest tracking with filesystem reconciliation |
| `translation_service.py` | Multi-language document translation via Gemini |
| `email_service.py` | EML parsing with multi-encoding support |
| `pdf_service.py` | PDF text extraction with position data |
| `file_service.py` | Upload validation, sanitization, secure storage |
| `anonymization_service.py` | PII masking via external black-box service |

**Schemas & Models** (`backend/schemas/`, `backend/models/`):
- SHACL PropertyShape model with JSON-LD serialization
- Schema.org mappings (60+ property types)
- Validation patterns (email, phone, postal code, etc.)
- JSON-LD context definitions

### Frontend: 16 Workspace Components

| Component | File | Purpose |
|-----------|------|---------|
| `AIChatInterface` | Chat with AI, streaming, slash commands, context indicator |
| `CaseTreeExplorer` | Document tree sidebar with folders, drag-drop upload |
| `DocumentViewer` | PDF, images, emails, text -- with semantic search highlights |
| `FormViewer` | Dynamic form with AI auto-fill and SHACL validation |
| `AdminConfigPanel` | Folder config, document types, macros, SHACL visualization |
| `WorkspaceHeader` | Case selector, language toggle, theme |
| `CaseContextDialog` | View injected AI context with custom rules |
| `ContextHierarchyDialog` | Visual context cascade tree |
| `SubmitCaseDialog` | AI-powered case validation and scoring |
| `PDFViewer` | PDF rendering with search highlights |
| `EmailViewer` | Email display with headers and attachments |
| `FileDropZone` | Drag-and-drop upload zone |
| `NewCaseDialog` | Template-based case creation |
| `CaseSearchDialog` | Search across cases |
| `HighlightedText` | Search result highlighting |
| `DataTable` | Generic data table |

**State management**: Single `AppContext.tsx` manages global state including WebSocket connections, case/folder/document selection, form fields, chat messages, language, and theme.

## Context Management

The core architectural idea: **the AI gets different context depending on where the user is navigating**.

### The Cascade: Case > Folder > Document > Custom Rules

```
User clicks "ACTE-2024-001"
  --> Case context loaded (regulations, required docs, validation rules)

User clicks "Personal Data" folder
  --> + Folder context added (expected docs: passport, birth cert; validation: name consistency)

User clicks "Reisepass.png"
  --> + Document content added (OCR-extracted text from passport)

User adds custom rule: /Aktenkontext Regeln Ordner Evidence "Only PDFs allowed"
  --> + Custom rule stored and enforced during validation
```

Every chat message carries `caseId + folderId + documentContent`. The backend loads the appropriate context files, merges them with precedence (Document > Folder > Case), and builds an 8-section prompt for Gemini.

When the user **switches folders**, the folder context changes automatically -- the AI immediately knows different validation criteria, expected documents, and common mistakes for that folder.

See the full flow: [`docs/diagrams/context-management-flow.mmd`](docs/diagrams/context-management-flow.mmd)

### Storage: All JSON, No Database

| Data | Path |
|------|------|
| Case context | `backend/data/contexts/cases/{caseId}/case.json` |
| Folder contexts | `backend/data/contexts/cases/{caseId}/folders/{folderId}.json` |
| Custom rules | `backend/data/contexts/cases/{caseId}/custom_rules.json` |
| Folder config | `backend/data/contexts/cases/{caseId}/folder_config.json` |
| Document manifest | `backend/data/document_manifest.json` |
| Case templates | `backend/data/contexts/templates/{caseType}/` |
| Document files | `public/documents/{caseId}/{folderId}/` |

Complete isolation between cases. No cross-case data contamination.

## Key Features in Detail

### SHACL-Based Form Validation

Admin says: *"Add a required email field for contact email"*

The system:
1. Parses the NL command via Gemini (temp=0.1 for precision)
2. Maps "email" to `schema:email` via 60+ schema.org mappings
3. Assigns email regex validation pattern
4. Generates a SHACL `PropertyShape` with `sh:pattern`, `sh:minCount`, `sh:datatype`
5. Wraps in a `NodeShape` with JSON-LD `@context`
6. Frontend validates input against the SHACL constraints in real-time

See: [`docs/diagrams/shacl-and-formfill-flow.mmd`](docs/diagrams/shacl-and-formfill-flow.mmd)

### AI Form Fill Agent

User says: *"Fill the form from this document"*

The system:
1. Detects fill/extract/populate keywords in the message
2. Sends document text + form schema to Gemini for extraction
3. Categorizes results: **direct updates** (empty fields) vs **suggestions** (conflicts with existing values)
4. Direct updates apply automatically; suggestions show accept/reject UI
5. All filled values are validated against SHACL constraints

### Custom Validation Rules

Users add rules via slash commands in chat:

| Command | Example |
|---------|---------|
| `/Aktenkontext Regeln Ordner <folder> "<rule>"` | Folder-specific validation |
| `/Aktenkontext Regeln Dateityp "<rule>"` | File type rules |
| `/Aktenkontext Dokumente "<description>"` | Required document |
| `/removeAktenkontext "<rule_id>"` | Remove a rule |

Rules are stored in `custom_rules.json` and injected into the validation prompt with "MUST be checked" priority.

### WebSocket Communication

Chat uses WebSocket at `ws://localhost:8000/ws/chat/{caseId}`.

**Message types:**

| Type | Direction | Purpose |
|------|-----------|---------|
| `chat` | Client > Server | User message with context IDs |
| `chat_response` | Server > Client | Complete AI response |
| `chat_chunk` | Server > Client | Streaming response chunk |
| `form_update` | Server > Client | Auto-fill field updates |
| `form_suggestion` | Server > Client | Suggested field values (needs approval) |
| `anonymize` | Client > Server | Anonymization request |
| `anonymization_complete` | Server > Client | Anonymization result |
| `translate` | Client > Server | Translation request |
| `translation_complete` | Server > Client | Translation result |
| `system` | Server > Client | System notifications |
| `error` | Server > Client | Error messages |

## Documentation & Diagrams

### Architecture Diagrams (Mermaid)

All diagrams are in `docs/diagrams/` as `.mmd` files. Render them with any Mermaid viewer (VS Code extension, GitHub, mermaid.live).

| Diagram | File | Shows |
|---------|------|-------|
| System Architecture | [`architecture.mmd`](docs/diagrams/architecture.mmd) | All 4 layers: frontend, API, services, storage with connections |
| SHACL + Form Fill | [`shacl-and-formfill-flow.mmd`](docs/diagrams/shacl-and-formfill-flow.mmd) | NL form modification flow + AI form fill agent flow |
| Context Management | [`context-management-flow.mmd`](docs/diagrams/context-management-flow.mmd) | Dynamic context cascade, prompt assembly, custom rules |
| LLM Context + History | [`llm-context-and-history.mmd`](docs/diagrams/llm-context-and-history.mmd) | How Gemini consumes dynamic context, per-Akte history isolation, what changes on navigation |

### Code Graph (Knowledge Base)

The code graph is a machine-readable knowledge base of all code entities and their relationships.

| File | Purpose |
|------|---------|
| [`docs/code-graph/code-graph.json`](docs/code-graph/code-graph.json) | 222 entities, 368 relations -- the full code knowledge base |
| [`docs/code-graph/graph_visualization.html`](docs/code-graph/graph_visualization.html) | Interactive D3.js visualization -- open in a browser |
| [`docs/code-graph/manifest.json`](docs/code-graph/manifest.json) | Code graph metadata |

**For AI agents (Claude, Copilot, etc.):** The code graph is designed to be queried via MCP (Model Context Protocol). To understand how any part of the system works:

1. Set the graph path: `set_graph_path("./docs/code-graph/code-graph.json")`
2. Search by keyword: `search_nodes("context manager")` -- finds entities matching the query
3. Open specific nodes: `open_nodes(["backend/services/gemini_service.py"])` -- shows all observations and relations
4. Find paths: `find_paths("AppContext", "gemini_service")` -- traces how frontend connects to backend
5. Advanced search: `advanced_search(entityType="Service")` -- find all services
6. Get statistics: `get_statistics()` -- overview of entity types and connections

The graph contains observations (facts about each entity) and relations (imports, calls, defines, uses). This lets an AI understand the full dependency chain without reading every file.

**For developers:** Open `docs/code-graph/graph_visualization.html` in a browser to interactively explore all components, services, and their connections. Nodes are clickable and draggable.

### Other Documentation

| Location | Contents |
|----------|----------|
| `docs/requirements/` | Requirements docs, sprint plans, quick reference |
| `docs/apis/` | API endpoint documentation, changelog, authentication |
| `docs/tests/` | Test suites organized by requirement ID (D-001, F-001, S2-001, etc.) |
| `.claude/context.md` | AI session context with implementation details |
| `http://localhost:8000/docs` | Live Swagger UI (when backend is running) |

## Project Structure

```
bamf-acte-companion/
├── src/                              # Frontend (React + TypeScript)
│   ├── components/
│   │   ├── workspace/               # 16 workspace components
│   │   └── ui/                      # 47 UI components (shadcn/ui + custom)
│   ├── contexts/
│   │   └── AppContext.tsx            # Global state + WebSocket management
│   ├── types/                        # 7 type definition files
│   ├── hooks/                        # Custom hooks (toast, mobile)
│   ├── i18n/locales/                 # de.json, en.json
│   ├── pages/                        # Index, Workspace, Login, NotFound
│   └── lib/                          # Utilities, localStorage
│
├── backend/                          # Backend (FastAPI + Python)
│   ├── api/                          # 9 API routers (40+ endpoints)
│   ├── services/                     # 12 service modules
│   ├── schemas/                      # SHACL, JSON-LD, schema.org, validation patterns
│   ├── models/                       # Data models (SHACL shapes, regulations)
│   ├── tools/                        # Document processing, anonymization, language detection
│   └── data/
│       └── contexts/
│           ├── cases/                # Per-case context (case.json, folders/, custom_rules.json)
│           └── templates/            # Case type templates
│
├── public/documents/                 # Case document files (PDFs, images, emails)
│
├── docs/
│   ├── diagrams/                     # Mermaid architecture diagrams (.mmd)
│   ├── code-graph/                   # Knowledge base (JSON + interactive HTML)
│   ├── requirements/                 # Sprint requirements and plans
│   ├── apis/                         # API documentation
│   └── tests/                        # Test suites by requirement ID
│
└── start.sh                          # One-command startup script
```

## Development

### Commands

```bash
# Frontend
npm run dev              # Dev server on :5173
npm run build            # Production build
npm run lint             # ESLint

# Backend (activate venv first: source backend/venv/bin/activate)
PYTHONPATH="${PWD}:${PYTHONPATH}" python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Both
./start.sh               # Start frontend + backend together
```

### Environment

Create `backend/.env`:
```
GEMINI_API_KEY=your_key_here
```

The `.env` file is gitignored. Never commit API keys.

### Sample Case Data

The app ships with one pre-configured case:

- **ACTE-2024-001** (German Integration Course) -- with 6 folders: personal-data, certificates, evidence, emails, applications, integration-docs. Includes sample documents, regulations (IntV, AufenthG), and validation rules.

Case templates exist for additional types (asylum application, family reunification) but only ACTE-2024-001 has full sample data.

## Troubleshooting

<details>
<summary>Connection Error / Backend not reachable</summary>

```bash
# Check if backend is running
ps aux | grep uvicorn

# Verify .env file
cat backend/.env

# Start backend manually
source backend/venv/bin/activate
PYTHONPATH="${PWD}:${PYTHONPATH}" python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
</details>

<details>
<summary>Port already in use</summary>

```bash
lsof -ti:5173 | xargs kill -9   # Frontend
lsof -ti:8000 | xargs kill -9   # Backend
```
</details>

<details>
<summary>Python venv issues</summary>

```bash
rm -rf backend/venv
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt
```
</details>

<details>
<summary>Module import errors</summary>

```bash
export PYTHONPATH="${PWD}:${PYTHONPATH}"
# Always run from project root
```
</details>

<details>
<summary>WebSocket connection failed</summary>

Check CORS in `backend/main.py` allows `http://localhost:5173`.
</details>

## License

Proprietary -- BAMF Internal Use Only
