# Tools, Commands & Capabilities

This document describes the tested and available features in the BAMF ACTE Companion.

---

## External Service Dependencies

| Service | URL | Required For | How to Run |
|---------|-----|-------------|------------|
| **Google Gemini API** | Cloud (API key) | All AI features | Set `GEMINI_API_KEY` in `backend/.env` |
| **Anonymization Service** | `localhost:5000` | Anonymization of identity documents | Docker container |
| **IDIRS OpenSearch** | `localhost:8010` | Hybrid document search and RAG queries | Docker container |

---

## Context-Aware AI Chat

The AI assistant is context-aware: its knowledge changes dynamically based on where the user is navigating. When a user selects a case, opens a folder, or views a document, the AI automatically receives the relevant context for that location.

**How context injection works:**

1. **Case level** -- The AI knows the case regulations, required documents, and validation rules (e.g., IntV, AufenthG for integration courses)
2. **Folder level** -- The AI additionally knows which documents are expected in that folder, folder-specific validation criteria, and common issues
3. **Document level** -- The AI additionally receives the extracted content of the currently viewed document

This means chatting with the AI always happens in the context of the user's current location. Switching folders or documents automatically changes what the AI knows, without the user needing to explain or re-upload anything.

---

## Slash Commands (Tested)

All slash commands are typed in the AI chat interface. Type `/` to see the autocomplete dropdown.

### `/translate` -- Document Translation

Translates the current document to German via the Gemini API.

- **Works on:** Emails (EML) and text-based documents
- **Dependencies:** Gemini API
- **Test documents:** Emails in `root_docs/` (e.g., `Email.eml`)

### `/anonymize` -- PII Anonymization

Masks personal data (names, dates, ID numbers) on identity documents. Designed for documents in Arabic and/or Farsi.

- **Works on:** PNG/JPG images (passports, ID cards, birth certificates)
- **Dependencies:** Anonymization Docker service (`localhost:5000`)
- **Test documents:** `root_docs/Personalausweis.png`, `root_docs/Geburtsurkunde.jpg`, `root_docs/Aufenthalstitel.png`
- **Result:** Shows the anonymized result in the chat

### `/fillForm` -- AI Form Auto-Fill

Extracts data from the current document and fills form fields automatically.

- **Works on:** PDFs with extractable text (non-scanned, no images or tables -- straightforward text extraction)
- **Dependencies:** Gemini API + a document open in the viewer + form fields defined
- **Test documents:** `root_docs/Anmeldeformular.pdf`, `root_docs/Sprachzeugnis-Zertifikat.pdf`
- **Behavior:** Empty fields are filled directly; conflicting values show accept/reject suggestions

### `/Dokumentsuche` -- Hybrid Document Search

Searches across the external IDIRS OpenSearch document index using hybrid retrieval (BM25 + kNN).

- **Syntax:** `/Dokumentsuche [key=value...] "search query"`
- **Example:** `/Dokumentsuche referenznummer=AKTE-2024-001 "er ist Ingenieur"`
- **Dependencies:** IDIRS OpenSearch Docker (`localhost:8010`)
- **Result:** Markdown table with document name, type, document ID, and relevance score

### `/Dokumente-abfragen` -- RAG Document Querying

Queries specific documents by ID using RAG with AI confidence analysis.

- **Syntax:** `/Dokumente-abfragen docId1 [docId2...] "question"`
- **Example:** `/Dokumente-abfragen 0cbd201aad34f9ca "What is the candidate's current residence?"`
- **Dependencies:** IDIRS OpenSearch Docker (`localhost:8010`) + Gemini API
- **Result:** AI-generated answer with confidence percentage (>= 80% green, < 80% yellow warning with disclaimer)
- **Workflow:** Use `/Dokumentsuche` first to find document IDs, then `/Dokumente-abfragen` to query them

### `/Aktenkontext` -- Custom Validation Rules

Adds custom rules that the AI enforces during case validation.

- **Syntax:** `/Aktenkontext Regeln Ordner <folder> "rule description"`
- **Dependencies:** None (rules stored locally in JSON)
- **Variants:** Folder rules, file type rules, content rules, metadata rules, completeness rules, required documents

### `/removeAktenkontext` -- Remove Custom Rules

Removes a previously added custom rule. Shows existing rules for selection.

---

## Toolbar Buttons (Tested)

Some features are also available as buttons in the document viewer toolbar, with a key difference: **buttons create a new document rendition** (a new version stored alongside the original), while slash commands show results in the chat.

### Translation Button

Translates the current document and creates a translated rendition.

- **Works on:** Email objects (EML) and text-based documents
- **Dependencies:** Gemini API
- **Result:** A new translated document render appears in the document tree

### Anonymization Button

Anonymizes the current document and creates an anonymized rendition.

- **Works on:** PNG/JPG images with Arabic and/or Farsi text (passports, IDs, certificates)
- **Dependencies:** Anonymization Docker service (`localhost:5000`)
- **Test documents:** Images in `root_docs/` (Personalausweis, Geburtsurkunde, Aufenthalstitel)
- **Result:** A new anonymized document render appears in the document tree

---

## Demo Documents

Test documents are located in **`root_docs/`** at the project root:

| File | Type | Use For |
|------|------|---------|
| `Personalausweis.png` | ID card image | Anonymization testing |
| `Geburtsurkunde.jpg` | Birth certificate image | Anonymization testing |
| `Aufenthalstitel.png` | Residence permit image | Anonymization testing |
| `Anmeldeformular.pdf` | Registration form PDF | Form fill testing |
| `Sprachzeugnis-Zertifikat.pdf` | Language certificate PDF | Form fill testing |
| `Notenspiegel.pdf` | Transcript PDF | Document analysis |
| `Email.eml` | Email | Translation testing |

A pre-configured case **ACTE-2024-001** (German Integration Course) is available in `public/documents/ACTE-2024-001/` with documents already distributed across 6 folders.

---

## All Registered Integrations (Reference)

The following is the complete list of all slash commands and API endpoints registered in the system. Not all have been fully tested -- the section above covers what is verified and working.

### All Slash Commands (16)

| Command | Description | Pattern | Status |
|---------|-------------|---------|--------|
| `/translate` | Translate document to German | WebSocket | Tested |
| `/anonymize` | PII masking on identity documents | WebSocket | Tested |
| `/fillForm` | Auto-fill form from document | WebSocket | Tested |
| `/Dokumentsuche` | Hybrid search in external DB | REST | Tested |
| `/Dokumente-abfragen` | RAG query with AI confidence | REST | Tested |
| `/Aktenkontext` | Add custom validation rules | REST | Tested |
| `/removeAktenkontext` | Remove custom rules | REST | Tested |
| `/validateCase` | AI case validation and scoring | WebSocket | Registered |
| `/search` | Semantic search in case documents | WebSocket | Registered |
| `/addDocument` | Upload document to case | UI action | Registered |
| `/convert` | Convert document format | WebSocket | Registered |
| `/transcribe` | Extract text from document | WebSocket | Registered |
| `/generateEmail` | Generate notification email | WebSocket | Registered |
| `/extractMetadata` | Extract document metadata | WebSocket | Registered |
| `/changeActeName` | Rename the current case | WebSocket | Registered |
| `/switchCase` | Switch to a different case | WebSocket | Registered |

### All Backend API Routers (10)

| Router | Prefix | Purpose |
|--------|--------|---------|
| `chat.py` | WebSocket `/ws/chat/{case_id}` | Real-time AI chat with streaming |
| `admin.py` | `/api/admin` | Field generation, form modification |
| `files.py` | `/api/files` | Upload, delete, duplicate detection |
| `documents.py` | `/api/documents` | Document tree, PDF extraction, email parsing |
| `search.py` | `/api/search` | Semantic search across documents |
| `validation.py` | `/api/validation` | AI-powered case scoring |
| `context.py` | `/api/context` | Case context and document tree |
| `custom_context.py` | `/api/custom-context` | Custom validation rules CRUD |
| `folders.py` | `/api/folders` | Folder CRUD, reorder, bulk update |
| `idirs.py` | `/api/idirs` | IDIRS hybrid search and RAG proxy |

### Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | *(required)* | Google Gemini API key |
| `IDIRS_BASE_URL` | `http://localhost:8010` | IDIRS OpenSearch API URL |
| `IDIRS_TIMEOUT` | `30` | IDIRS request timeout (seconds) |
| `RAG_CONFIDENCE_THRESHOLD` | `0.80` | High/low confidence threshold |
