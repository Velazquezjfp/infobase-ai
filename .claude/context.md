# BAMF ACTE Companion - Project Context (Updated: 2026-01-14)

## Current Session Summary (Sprint 5 Completion)

This session focused on completing **S5-006 (Document Renders)** and **S5-003 (Semantic Search)** requirements, fixing critical bugs in the document management and AI context pipeline.

### Key Issues Resolved
1. ✅ Render creation not working (missing `documentId` in anonymization request)
2. ✅ Render display not working (DocumentViewer using wrong file path)
3. ✅ Delete render button not working (API endpoint implemented)
4. ✅ AI can't read PDFs (text extraction not updating AppContext)
5. ✅ Semantic search failing (file path missing `public/` prefix)
6. ✅ Cascade deletion missing (renders not deleted with parent document)

---

## Document Management System Architecture

### Core Components

#### 1. **Document Registry Service** (S5-007)
**File**: `backend/services/document_registry.py`

**Purpose**: Single source of truth for document metadata

**Key Functions**:
- `load_manifest()` - Load from `backend/data/document_manifest.json`
- `save_manifest()` - Persist changes to disk
- `register_document()` - Add new document with original render
- `unregister_document()` - **CASCADE DELETE** all renders + manifest entry
- `add_render_to_document()` - Add anonymized/translated renders
- `remove_render_from_document()` - Remove specific render
- `reconcile()` - Sync filesystem with manifest, skip render files

**Data Structure**:
```json
{
  "documentId": "doc_xxx",
  "caseId": "ACTE-2024-001",
  "folderId": "personal-data",
  "fileName": "Passport.pdf",
  "filePath": "public/documents/ACTE-2024-001/personal-data/Passport.pdf",
  "renders": [
    {
      "id": "render_original_xxx",
      "type": "original",
      "name": "Passport.pdf",
      "filePath": "public/documents/.../Passport.pdf",
      "createdAt": "2026-01-14T10:00:00Z"
    },
    {
      "id": "render_anon_xxx",
      "type": "anonymized",
      "name": "Passport_anonymized.pdf",
      "filePath": "public/documents/.../Passport_anonymized.pdf",
      "createdAt": "2026-01-14T10:05:00Z"
    }
  ]
}
```

#### 2. **File Service** (S4-001, S4-002, S5-006)
**File**: `backend/services/file_service.py`

**Key Functions**:
- `delete_file()` - Delete file with security validation
- `add_document_render()` - Register render in manifest
- `delete_document_render()` - Delete render file + update manifest
- `sanitize_filename()` - Security sanitization
- `validate_case_path()` - Path traversal prevention

**Security Features**:
- Max file size: 15 MB
- Filename sanitization (removes `..`, `/`, `\`)
- Path traversal prevention
- Cannot delete 'original' render type

#### 3. **PDF Service** (S5-003)
**File**: `backend/services/pdf_service.py`

**Purpose**: Extract text from PDFs for AI context and search

**Key Functions**:
- `extract_text(pdf_path)` - Full text extraction
- `extract_text_with_positions(pdf_path)` - Text with coordinates
- `get_page_count(pdf_path)` - Page count

**Dependencies**: `pdfplumber` library

---

## API Endpoints Reference

### Files API (`/api/files`)
**Router**: `backend/api/files.py`

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/api/files/upload` | POST | Upload file with duplicate detection | ✅ S4-001 |
| `/api/files/{case_id}/{folder_id}/{filename}` | DELETE | Delete file with cascade to renders | ✅ S4-002 |
| `/api/files/renders/{case_id}/{document_id}/{render_id}` | DELETE | Delete specific render | ✅ S5-006 |
| `/api/files/{case_id}/{folder_id}/{filename}/exists` | GET | Check file existence | ✅ S4-001 |
| `/api/files/health` | GET | Health check | ✅ |

**Changes in This Session**:
- Added DELETE render endpoint (lines 496-565)
- Added tree cache invalidation to upload/delete endpoints

### Documents API (`/api/documents`)
**Router**: `backend/api/documents.py`

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/api/documents/tree/{case_id}` | GET | Get document tree | ✅ S5-007 |
| `/api/documents/extract-pdf-text` | POST | Extract text from PDF | ✅ S5-003 |
| `/api/documents/all` | GET | Get all documents | ✅ |
| `/api/documents/health` | GET | Health check | ✅ |

**Changes in This Session**:
- Fixed PDF extraction path to include `public/` prefix

### Search API (`/api/search`)
**Router**: `backend/api/search.py`

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/api/search/semantic` | POST | Semantic search with Gemini AI | ✅ S5-003 |
| `/api/search/health` | GET | Health check | ✅ S5-003 |

**Features**:
- Cross-language search (German query → English document)
- Text highlighting with character positions
- PDF support via `documentPath` parameter
- Returns relevance scores (0.0-1.0)

**Changes in This Session**:
- Fixed file path to include `public/` prefix in frontend request

### Context API (`/api/context`)
**Router**: `backend/api/context.py`

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/api/context/tree/{case_id}` | GET | Get ASCII tree view | ✅ S5-011 |

**Features**:
- Hierarchical ASCII tree (├── └──)
- Performance caching (100-300ms → <50ms)
- Auto invalidation on file operations

---

## Frontend Architecture

### AppContext (State Management)
**File**: `src/contexts/AppContext.tsx`

**Critical State**:
- `selectedDocument` - Currently selected document
- `selectedRender` - Currently selected render ID (S5-006)
- `searchQuery`, `searchHighlights` - Search state (S5-003)
- `formFields` - Case form data
- `wsConnection` - WebSocket for chat

**Key Functions**:
- `selectDocumentWithRender(doc, renderId)` - Select document and render
- `updateSelectedDocumentContent(content)` - **NEW**: Store extracted PDF text
- `performSemanticSearch(query, documentId)` - Semantic search
- `sendChatMessage(content, documentContent)` - Send to AI with context
- `refreshDocuments()` - Reload document tree

**Changes in This Session**:
- Added `documentId` to anonymization request (line 766)
- Added `updateSelectedDocumentContent()` method (lines 331-347)
- Fixed PDF path in semantic search to include `public/` (line 864)
- Fixed semantic search to use selected render path (lines 851-858)
- Exported `updateSelectedDocumentContent` in context value (line 1019)

### CaseTreeExplorer (Document Tree)
**File**: `src/components/workspace/CaseTreeExplorer.tsx`

**Features**:
- Folder/document tree with drag-drop upload
- RenderContainer for multi-render documents
- Delete render functionality with confirmation

**Components**:
- `FolderItem` - Folder with upload support
- `RenderContainer` - Expandable render list (S5-006)

**Changes in This Session**:
- Implemented `handleDeleteRender()` with API call (lines 241-287)
- Added `refreshDocuments` to useApp hooks (lines 168, 480)
- Fixed delete button to call backend and refresh UI

### DocumentViewer (Document Display)
**File**: `src/components/workspace/DocumentViewer.tsx`

**Features**:
- Visual PDF display
- Text extraction for AI context
- Semantic search integration
- Render selection support

**Changes in This Session**:
- Added `selectedRender` from useApp (line 37)
- Added `updateSelectedDocumentContent` from useApp (line 39)
- Calculate `activeRender` from selected render ID (lines 65-67)
- Use render's file path for display (lines 70-84)
- Store extracted PDF text in AppContext (lines 144-147)
- Fixed PDF extraction path with `public/` prefix (line 129)
- Updated useEffect dependencies to trigger on render change (line 102, 170)

---

## Data Flow: PDF Document Selection → AI Context

```
User Selects PDF: "Notenspiegel.pdf"
    ↓
┌─────────────────────────────────────────┐
│ DocumentViewer Component                │
│ • Shows visual PDF to user              │
│ • Calls POST /api/documents/extract-pdf │
│   with path: public/documents/.../pdf   │
│ • Receives extracted text               │
│ • Stores in local state (for display)   │
│ • Calls updateSelectedDocumentContent() │✅
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ AppContext.updateSelectedDocumentContent│
│ • Updates selectedDocument.content      │✅
│ • Updates document in currentCase       │✅
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Cascading Context Now Available:        │
│ ✅ Case context: ACTE-2024-001          │
│ ✅ Folder context: Evidence             │
│ ✅ Document context: PDF extracted text │
└─────────────────────────────────────────┘
    ↓
    ├──→ AI Chat (reads content) ✅
    ├──→ /fill form (extracts data) ✅
    └──→ Semantic search (highlights) ✅
```

---

## Data Flow: Anonymization → Render Creation

```
User Clicks "Anonymize" on Passport.pdf
    ↓
┌─────────────────────────────────────────┐
│ AppContext.sendChatMessage()            │
│ • Sends WebSocket message:              │
│   type: 'anonymize'                     │
│   documentId: doc_xxx ✅ (FIXED)        │
│   filePath: public/documents/.../pdf    │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Backend: anonymize_document()           │
│ • Calls AnonymizationService            │
│ • Saves to Passport_anonymized.pdf      │
│ • Calls add_document_render() ✅        │
│   with document_id + render_type        │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ document_registry.add_render()          │
│ • Adds render to document.renders[]     │
│ • Saves manifest                        │
│ • Returns render metadata               │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ WebSocket Response                      │
│ • type: 'anonymization_complete'        │
│ • renderMetadata: {...} ✅              │
│ • documentId: doc_xxx ✅                │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Frontend: AppContext handles response   │
│ • Adds render to document.renders[]     │
│ • Calls loadDocumentsFromBackend()      │
│ • Document shows "2 renders" badge ✅   │
└─────────────────────────────────────────┘
```

---

## Data Flow: Cascade Deletion

```
User Deletes Document: "Passport.pdf" (has 2 renders)
    ↓
┌─────────────────────────────────────────┐
│ DELETE /api/files/{case}/{folder}/{file}│
│ • find_document_by_path() gets doc      │
│ • delete_file() removes original        │
│ • unregister_document() CASCADE ✅      │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ document_registry.unregister_document() │
│ • Find document and its renders         │
│ • Loop through renders array:           │
│   - Skip 'original' (already deleted)   │
│   - Delete Passport_anonymized.pdf ✅   │
│   - Delete Passport_translated.pdf ✅   │
│ • Remove from manifest                  │
│ • Save manifest                         │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Result: ALL files deleted               │
│ ✅ Passport.pdf (original)              │
│ ✅ Passport_anonymized.pdf (render)     │
│ ✅ Passport_translated_de.pdf (render)  │
│ ✅ Manifest entry removed               │
│ ✅ No orphaned files                    │
└─────────────────────────────────────────┘
```

---

## Sprint 5 Requirements Status

### ✅ Fully Implemented (This Session)

#### S5-006: Document Renders Management System
**Status**: ✅ COMPLETE

**Implementation**:
- Documents have `renders[]` array with original + processed versions
- RenderContainer shows expandable list when multiple renders exist
- Visual indicators: chevron icon, "X renders" badge
- Delete render button with confirmation dialog
- Backend cascade deletion implemented

**Files Modified**:
- `src/contexts/AppContext.tsx` (lines 766, 331-347, 1019)
- `src/components/workspace/CaseTreeExplorer.tsx` (lines 168, 241-287, 480)
- `src/components/workspace/DocumentViewer.tsx` (lines 37, 39, 64-84, 102, 170)
- `backend/services/document_registry.py` (lines 314-337)
- `backend/api/files.py` (lines 496-565)
- `backend/services/file_service.py` (lines 583-650)

**API Endpoints**:
- `DELETE /api/files/renders/{case_id}/{document_id}/{render_id}` - Delete render

#### S5-003: Semantic Search with Multi-Language Support
**Status**: ✅ COMPLETE

**Implementation**:
- Semantic search button in DocumentViewer
- Cross-language support (German ↔ English)
- PDF text extraction for AI context
- Text highlighting with character positions
- Search navigation (previous/next highlights)

**Files Modified**:
- `src/contexts/AppContext.tsx` (lines 331-347, 860-868, 1019)
- `src/components/workspace/DocumentViewer.tsx` (lines 39, 125-129, 144-147)
- `src/types/search.ts` (line 68 - added `documentPath`)
- `backend/api/search.py` (existing - no changes needed)
- `backend/services/pdf_service.py` (existing - no changes needed)

**API Endpoints**:
- `POST /api/search/semantic` - Semantic search with Gemini
- `POST /api/documents/extract-pdf-text` - Extract PDF text

**Components**:
- `src/components/workspace/HighlightedText.tsx` - Highlight rendering
- `src/components/workspace/PDFViewer.tsx` - PDF display with search

### ✅ Previously Implemented

#### S5-007: Container-Compatible File Persistence
- Document manifest system (`backend/data/document_manifest.json`)
- Filesystem reconciliation on startup
- SHA-256 file integrity verification

#### S5-011: Cascading Context with Document Tree View
- `GET /api/context/tree/{case_id}` - ASCII tree view
- Tree caching with automatic invalidation
- Performance: 100-300ms → <50ms cached

#### S5-014: UI Language Toggle
- German/English UI translation
- i18n integration

#### S5-002: AI Form Fill with Suggested Values
- Inline suggestion UI with accept/reject
- Confidence scores
- Form value comparison

#### S5-004: Multi-Format Translation Service
- Document translation with render creation

### ⏳ Pending Requirements

#### S5-005: Case Validation Agent
**Status**: NOT STARTED

#### S5-008: Email File Support (.eml)
**Status**: NOT STARTED

#### S5-012: Document Type Capabilities and Command Availability
**Status**: NOT STARTED

#### S5-016: Drag-and-Drop Document Management Across Folders
**Status**: NOT STARTED

---

## Critical File Connections

### Document Management Pipeline

```
Frontend Upload
    ↓
POST /api/files/upload
    ↓
backend/api/files.py (lines 83-180)
    ↓
backend/services/file_service.py
    ├─> save_uploaded_file()
    └─> backend/services/document_registry.py
        └─> register_document() (creates original render)
            └─> save_manifest()

Frontend Delete
    ↓
DELETE /api/files/{case}/{folder}/{file}
    ↓
backend/api/files.py (lines 267-368)
    ↓
backend/services/file_service.py
    ├─> delete_file() (delete original)
    └─> backend/services/document_registry.py
        └─> unregister_document() ✅ CASCADE
            ├─> Delete all render files
            └─> Remove from manifest
```

### Anonymization/Processing Pipeline

```
User Clicks "Anonymize"
    ↓
src/contexts/AppContext.tsx::sendChatMessage()
    ↓
WebSocket: type='anonymize', documentId=xxx ✅
    ↓
backend/api/chat.py::handle_anonymize()
    ↓
backend/tools/anonymization_tool.py
    ├─> AnonymizationService (Gemini API)
    ├─> Save file: original_anonymized.ext
    └─> backend/services/file_service.py
        └─> add_document_render()
            └─> backend/services/document_registry.py
                └─> add_render_to_document()
                    └─> save_manifest()
    ↓
WebSocket Response: renderMetadata + documentId
    ↓
src/contexts/AppContext.tsx (lines 577-627)
    └─> Add render to document.renders[]
    └─> Refresh document tree
```

### AI Context Pipeline (FIXED THIS SESSION)

```
User Selects PDF Document
    ↓
src/components/workspace/DocumentViewer.tsx
    ├─> Display visual PDF ✅
    └─> Extract text (lines 123-147)
        ↓
        POST /api/documents/extract-pdf-text
        path: "public/documents/{case}/{folder}/{file}" ✅
        ↓
        backend/services/pdf_service.py
        └─> extract_text() using pdfplumber
        ↓
        Returns: { text: "...", pageCount: 10 }
        ↓
        updateSelectedDocumentContent(text) ✅ NEW
        ↓
        selectedDocument.content = extracted text ✅
    ↓
AI Agent Now Sees:
    ✅ Case context (regulations, required docs)
    ✅ Folder context (folder purpose, validation)
    ✅ Document content (extracted PDF text)
    ↓
AI Can Now:
    ✅ Answer questions about PDF
    ✅ Extract form data with /fill form
    ✅ Perform semantic search
```

### Semantic Search Pipeline (FIXED THIS SESSION)

```
User Clicks "Search" Button
    ↓
Enter query: "course preferences"
    ↓
src/contexts/AppContext.tsx::performSemanticSearch()
    ├─> Get selectedRender (if applicable) ✅
    ├─> Build file path with public/ prefix ✅
    └─> POST /api/search/semantic
        {
          query: "course preferences",
          documentPath: "public/documents/{case}/{folder}/{file}",
          documentType: "pdf"
        }
    ↓
backend/api/search.py::semantic_search()
    ├─> Extract PDF text via pdf_service
    ├─> Detect languages (query + document)
    ├─> Call gemini_service.semantic_search()
    └─> Returns highlights with positions
    ↓
Frontend receives:
    {
      highlights: [
        { start: 245, end: 268, relevance: 0.95,
          matchedText: "Preferred course: Morning" }
      ],
      count: 1,
      matchSummary: "Found 1 match"
    }
    ↓
src/components/workspace/HighlightedText.tsx
    └─> Wraps text with <mark> elements
    └─> Active highlight has amber background
```

---

## Files Modified This Session

### Backend Files Created (3 new services)

| File | Lines | Purpose | Requirement |
|------|-------|---------|-------------|
| `backend/services/email_service.py` | 341 | Email parsing with multi-encoding support | S5-008 |
| `backend/services/translation_service.py` | 241 | Document translation via Gemini | S5-004 |

### Backend Files Modified (5 files)

| File | Lines | Changes | Requirement |
|------|-------|---------|-------------|
| `backend/services/document_registry.py` | 314-337 | Added cascade deletion of render files | S5-003, S5-006 |
| `backend/api/files.py` | 496-565 | Added DELETE render endpoint | S5-006 |
| `backend/services/file_service.py` | - | Added `delete_document_render()` | S5-006 |
| `backend/api/documents.py` | 15, 390-478 | Added `parse-email` endpoint, imports | S5-008 |
| `backend/api/chat.py` | 11, 196-202, 547-662 | Added translation WebSocket handler | S5-004 |
| `backend/requirements.txt` | 37-38 | Added `html2text==2024.2.26` | S5-008 |

### Frontend Files Created (1 new component)

| File | Lines | Purpose | Requirement |
|------|-------|---------|-------------|
| `src/components/workspace/EmailViewer.tsx` | 154 | Email display with RTL support | S5-008 |

### Frontend Files Modified (5 files)

| File | Lines | Changes | Requirement |
|------|-------|---------|-------------|
| `src/contexts/AppContext.tsx` | 31, 50-52, 137, 331-347, 705-763, 766, 860-868, 1019, 1109-1110 | Added translation state, `updateSelectedDocumentContent()`, handlers | S5-003, S5-004, S5-006, S5-008 |
| `src/components/workspace/CaseTreeExplorer.tsx` | 168, 241-287, 480 | Implemented delete render handler | S5-006 |
| `src/components/workspace/DocumentViewer.tsx` | 12, 29-30, 37, 39, 63-64, 64-84, 102, 125-129, 144-147, 158-182, 170, 260-298, 413-418, 464-475 | Email viewer, translation, render selection, path fixes | S5-003, S5-004, S5-006, S5-008 |
| `src/types/search.ts` | 62, 68 | Made `documentContent` optional, added `documentPath` | S5-003 |
| `src/types/case.ts` | 24 | Added `'eml'` to Document type union | S5-008 |
| `src/types/websocket.ts` | 118-158 | Added `TranslationRequest`, `TranslationResponse` | S5-004 |

### Total Session Impact
- **3 new services created** (email, translation)
- **1 new component created** (EmailViewer)
- **11 files modified**
- **4 requirements completed** (S5-003, S5-004 email, S5-006, S5-008)
- **1,100+ lines of code** added

---

## Key Architectural Decisions

### 1. **Single Source of Truth**: Document Manifest
- All document metadata in `backend/data/document_manifest.json`
- Filesystem reconciliation on startup
- Registry updates trigger tree cache invalidation

### 2. **Render System** (S5-006)
- Documents can have multiple renders (original, anonymized, translated)
- Renders stored as array in document entry
- UI shows expandable container when renders.length > 1
- Delete button only on non-original renders

### 3. **Cascade Deletion** (S5-003/S5-006)
- Deleting parent document deletes ALL render files
- Prevents orphaned anonymized/translated files
- Implemented in `unregister_document()`

### 4. **PDF Handling** (S5-003)
- Visual display for user (PDFViewer component)
- Text extraction for AI (stored in document.content)
- Single extraction, multiple uses (chat, form fill, search)
- No OCR needed - pdfplumber extracts native text

### 5. **Path Conventions**
- **Backend filesystem**: `public/documents/{case}/{folder}/{file}`
- **Frontend URLs**: `/documents/{case}/{folder}/{file}` (proxy to backend)
- **Root docs**: `root_docs/{file}` (case-independent)

---

## Testing Verification

### S5-006 Tests ✅
- TC-S5-006-01: Single render displays as normal file ✅
- TC-S5-006-02: Anonymize creates expandable container ✅
- TC-S5-006-03: Expand shows "Original" and "Anonymized" ✅
- TC-S5-006-04: Click render displays correct version ✅
- TC-S5-006-09: Delete render removes from UI ✅
- **Cascade deletion**: Delete parent removes all renders ✅

### S5-003 Tests ✅
- TC-S5-003-01: Search button opens dialog ✅
- TC-S5-003-02: Query finds and highlights text ✅
- TC-S5-003-04: Cross-language German→English ✅
- TC-S5-003-09: PDF text extracted automatically ✅
- TC-S5-003-13: Semantic matching works ✅
- **AI reads PDF**: Context available for chat ✅

#### S5-008: Email File Support (.eml)
**Status**: ✅ COMPLETE

**Implementation**:
- Parse .eml files with multi-encoding support (UTF-8, ISO-8859-6 Arabic)
- Display emails with headers (From, To, Subject, Date)
- RTL text support for Arabic
- Extract email body for AI context
- Attachment metadata display

**Files Created**:
- `backend/services/email_service.py` (341 lines) - Email parser with encoding support
- `src/components/workspace/EmailViewer.tsx` (154 lines) - Email display component

**Files Modified**:
- `backend/requirements.txt` (lines 37-38) - Added `html2text==2024.2.26`
- `backend/api/documents.py` (lines 15, 390-478) - Added `parse-email` endpoint
- `src/types/case.ts` (line 24) - Added `'eml'` to Document type union
- `src/components/workspace/DocumentViewer.tsx` (lines 12, 63-64, 158-182, 464-475) - EmailViewer integration

**API Endpoints**:
- `POST /api/documents/parse-email` - Parse .eml and extract email data

**Components**:
- `src/components/workspace/EmailViewer.tsx` - Email display with RTL support

#### S5-004: Multi-Format Translation Service (Email Portion)
**Status**: ✅ COMPLETE (emails only, PDF/image translation pending)

**Implementation**:
- Translate emails via Gemini API
- Create translated renders (not duplicate documents)
- Preserve email headers (From, To, Date)
- Translate subject and body to any language
- WebSocket-based translation with render registration

**Files Created**:
- `backend/services/translation_service.py` (241 lines) - Translation service with Gemini

**Files Modified**:
- `backend/api/chat.py` (lines 11, 196-202, 547-662) - Added translation WebSocket handler
- `src/types/websocket.ts` (lines 118-158) - Added `TranslationRequest`, `TranslationResponse`
- `src/contexts/AppContext.tsx` (lines 50-52, 137, 705-763, 1109-1110) - Translation state and handler
- `src/components/workspace/DocumentViewer.tsx` (lines 29-30, 260-298, 413-418) - Translation button

**WebSocket Messages**:
- Request: `type='translate'` with `documentId`, `targetLanguage`
- Response: `type='translation_complete'` with `renderMetadata`

---

## Data Flow: Email Parsing → AI Context

```
User Selects Email.eml
    ↓
DocumentViewer.tsx detects type === 'eml'
    ↓
POST /api/documents/parse-email
    {
      documentPath: "public/documents/ACTE-2024-001/emails/Email.eml"
    }
    ↓
backend/services/email_service.py
    ├─> Parse with BytesParser
    ├─> Decode headers (handles ISO-8859-6 Arabic)
    ├─> Extract body (plain text or HTML→text)
    └─> Extract attachments metadata
    ↓
Returns EmailData:
    {
      from_addr: "...",
      to_addr: "...",
      subject: "Change in course type preference",
      date: "Fri, 09 Jan 2026 13:11:48 +0000",
      body_text: "Arabic text...",
      attachments: []
    }
    ↓
Frontend:
    ├─> EmailViewer displays with RTL formatting ✅
    ├─> updateSelectedDocumentContent(body_text) ✅
    └─> selectedDocument.content = email body text
    ↓
AI Agent Sees:
    ✅ Case context
    ✅ Folder context
    ✅ Email content (Arabic text readable)
```

## Data Flow: Email Translation → Render Creation

```
User Clicks "Translate" on Email.eml
    ↓
DocumentViewer::handleTranslate('de')
    ↓
WebSocket: type='translate', documentId=xxx, targetLanguage='de'
    ↓
backend/api/chat.py::handle_translation()
    ↓
translation_service.translate_email()
    ├─> email_service.parse_eml_file()
    ├─> Gemini translates subject (Arabic → German)
    ├─> Gemini translates body (Arabic → German)
    ├─> Create new EmailMessage
    │   - From/To/Date: PRESERVED
    │   - Subject: Translated
    │   - Body: Translated
    ├─> Save as Email_translated_de.eml
    └─> add_document_render()
        └─> Adds render: type='translated', metadata={language:'de'}
    ↓
WebSocket Response: renderMetadata + documentId
    ↓
AppContext handles 'translation_complete'
    ├─> Adds render to document.renders[]
    ├─> Toast: "Translated to DE"
    └─> Refreshes document tree
    ↓
Result:
    ✅ Email.eml shows "2 renders"
    ✅ Expand: "Original" (Arabic) + "Translated" (German)
    ✅ Click "Translated" → Shows German email
    ✅ No duplicate document created
```

---

## Next Steps for Remaining Requirements

### Pending: S5-005, S5-012, S5-016

When you reference a requirement:
1. I'll identify it from `docs/requirements/sprint5_requirements.md`
2. Check `docs/implementation_plan.md` for planned approach
3. Provide detailed context and implementation strategy
4. Track progress in this context document
5. Update code-graph after completion

**Ready to tackle the remaining requirements!** 🚀

Which requirement would you like to work on next?
- **S5-005**: Case Validation Agent
- **S5-008**: Email File Support (.eml)
- **S5-012**: Document Type Capabilities and Command Availability
- **S5-016**: Drag-and-Drop Document Management Across Folders
