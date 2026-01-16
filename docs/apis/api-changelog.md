# BAMF ACTE Companion - API Changelog

## Overview

This document tracks all changes to the BAMF ACTE Companion API documentation and architecture. Since the application is currently a frontend-only prototype, this changelog documents the evolution of the API specification and simulated features.

**Current Status:** API specification is in planning phase. All endpoints documented are planned for future implementation.

---

## Version Format

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

---

## [Unreleased]

### Planned Features
- Authentication and authorization system for admin endpoints
- Batch document upload endpoint
- Document comparison endpoint
- Case export/import endpoints
- Advanced search with filters and facets
- Document versioning and history
- Audit log API endpoints
- REST endpoints for legacy AI operations (convert, translate)
- Message history persistence
- File upload via WebSocket
- Additional language support beyond German and English
- OCR integration for image-based documents
- SHACL validation enforcement on client side
- Form template library with SHACL metadata
- PDF anonymization support (currently only images supported)

---

## [2.2.0] - 2026-01-16

### Added - Custom Context Rules API (S5-017)

This release adds the Custom Context Rules API, enabling users to define custom validation rules and required documents for cases through the /Aktenkontext slash command. Rules are stored per-case and can be managed programmatically through REST endpoints.

#### New API Module: backend/api/custom_context.py

**Endpoint: GET /api/custom-context/{case_id}**

**Location:** `backend/api/custom_context.py:105-129`

Retrieve all custom validation rules and required documents for a case.

**Response Format:**
```json
{
  "success": true,
  "message": "Found 2 custom rule(s)",
  "rules": [
    {
      "id": "custom-rule-abc12345",
      "type": "validation_rule",
      "createdAt": "2026-01-16T14:30:00Z",
      "targetFolder": "Evidence",
      "rule": "Only PDFs should be allowed in here",
      "ruleType": "file_type"
    }
  ]
}
```

**Endpoint: POST /api/custom-context/{case_id}/rule**

**Location:** `backend/api/custom_context.py:132-177`

Add a custom validation rule to the case context.

**Request Format:**
```json
{
  "targetFolder": "Evidence",
  "ruleType": "file_type",
  "rule": "Only PDFs should be allowed in here"
}
```

**Response Format:**
```json
{
  "success": true,
  "message": "Validation rule added successfully",
  "rule": {
    "id": "custom-rule-abc12345",
    "type": "validation_rule",
    "createdAt": "2026-01-16T14:30:00Z",
    "targetFolder": "Evidence",
    "rule": "Only PDFs should be allowed in here",
    "ruleType": "file_type"
  }
}
```

**Endpoint: POST /api/custom-context/{case_id}/document**

**Location:** `backend/api/custom_context.py:180-225`

Add a custom required document to the case context.

**Request Format:**
```json
{
  "description": "Proof of German language proficiency (B1 certificate)",
  "targetFolder": "Language Certificates"
}
```

**Response Format:**
```json
{
  "success": true,
  "message": "Required document added successfully",
  "rule": {
    "id": "custom-doc-def67890",
    "type": "required_document",
    "createdAt": "2026-01-16T14:25:00Z",
    "targetFolder": "Language Certificates",
    "rule": "Proof of German language proficiency (B1 certificate)",
    "ruleType": "document_requirement"
  }
}
```

**Endpoint: DELETE /api/custom-context/{case_id}/{rule_id}**

**Location:** `backend/api/custom_context.py:228-277`

Remove a custom validation rule or required document from the case.

**Response Format:**
```json
{
  "success": true,
  "message": "Rule removed successfully",
  "rule": {
    "id": "custom-rule-abc12345",
    "type": "validation_rule",
    "createdAt": "2026-01-16T14:30:00Z",
    "targetFolder": "Evidence",
    "rule": "Only PDFs should be allowed in here",
    "ruleType": "file_type"
  }
}
```

**Key Features:**
- **Case-Scoped Rules:** Each case has its own set of custom rules
- **Two Rule Types:**
  - `validation_rule`: Custom validation rules for folders/files
  - `required_document`: Custom required document definitions
- **Target Folder Support:** Rules can be applied to specific folders
- **Persistent Storage:** Rules stored in `backend/data/contexts/cases/{caseId}/custom_rules.json`
- **Unique IDs:** Each rule gets a unique ID (format: `custom-rule-{hex}` or `custom-doc-{hex}`)
- **Timestamps:** ISO 8601 creation timestamps for chronological ordering
- **Rule Types:** Support for file_type, content, metadata, completeness, and document_requirement classifications
- **CRUD Operations:** Full create, read, and delete support (update via delete + create)

**Rule Storage Format:**
```json
{
  "caseId": "ACTE-2024-001",
  "lastModified": "2026-01-16T14:30:00Z",
  "rules": [
    {
      "id": "custom-rule-abc12345",
      "type": "validation_rule",
      "createdAt": "2026-01-16T14:30:00Z",
      "targetFolder": "Evidence",
      "rule": "Only PDFs should be allowed in here",
      "ruleType": "file_type"
    }
  ]
}
```

**Integration:**
- Works seamlessly with /Aktenkontext slash command in the AI chat interface
- Rules can be created via chat or REST API
- Supports dynamic case-specific requirements
- Enables user-driven validation and document management

**Use Cases:**
- Define folder-specific file type restrictions
- Specify additional required documents for submission
- Create custom validation checks for special cases
- Document case-specific requirements that aren't in the default context

---

## [2.1.0] - 2026-01-16

### Added - Case Validation API (S5-005)

This release adds the Case Validation API, providing AI-powered case validation for submission completeness. The validation service uses Google Gemini 2.5 Flash to analyze form data, documents, and case context, returning structured assessments with scores, warnings, and recommendations.

#### New API Module: backend/api/validation.py

**Endpoint: POST /api/validation/case/{case_id}**

**Location:** `backend/api/validation.py:82-158`

AI-powered case validation for submission completeness.

**Request Format:**
```json
{
  "formData": {
    "fullName": "John Doe",
    "dateOfBirth": "1990-01-15"
  },
  "language": "de",
  "documentContents": {
    "doc-001": "text content"
  }
}
```

**Response Format:**
```json
{
  "success": true,
  "score": 75,
  "summary": "Case is mostly complete but missing some required documents.",
  "warnings": [
    {
      "severity": "critical",
      "category": "missing_documents",
      "title": "Missing ID Document",
      "details": ["No passport uploaded"]
    }
  ],
  "recommendations": [
    "Upload a valid passport or national ID",
    "Complete the address section"
  ],
  "error": null
}
```

**Key Features:**
- **AI-Powered Analysis:** Uses Gemini 2.5 Flash model for intelligent validation
- **Multilingual Support:** Responses in German or English
- **Comprehensive Checking:** Analyzes form data, documents, and case context
- **Score-Based Assessment:** 1-100 score (90-100=ready, 70-89=minor, 50-69=significant, <50=critical)
- **Structured Warnings:** Categorized by severity (critical, high, medium, low) and type
- **Actionable Recommendations:** Clear next steps for case completion
- **Context-Aware:** Checks against case-specific required documents from context files
- **Document Analysis:** Can analyze cached document text contents

**Endpoint: GET /api/validation/health**

**Location:** `backend/api/validation.py:161-188`

Health check for validation service with Gemini API status.

**Response Format:**
```json
{
  "status": "healthy",
  "service": "case_validation",
  "gemini_initialized": true,
  "ai_powered": true
}
```

**Health Status:**
- `healthy`: Service fully operational with Gemini API
- `degraded`: Service running but Gemini API not initialized
- `unhealthy`: Service error occurred

#### New Service: backend/services/validation_service.py

**Location:** `backend/services/validation_service.py`

**Service Implementation:**
- **CaseValidationService:** Singleton service for AI-powered validation
- **ValidationResult:** Structured result with score, summary, warnings, recommendations
- **ValidationWarning:** Individual warning with severity, category, title, details

**Key Methods:**
- `validate_case()`: Main validation method (async)
  - Loads case context including required documents
  - Builds comprehensive validation prompt
  - Calls Gemini API with focused generation config
  - Parses and structures AI response
  - Returns ValidationResult
- `_build_validation_prompt()`: Constructs prompt with:
  - Case information (ID, type, name)
  - Required documents from context
  - Form data with completeness status
  - Document tree view
  - Document contents (if provided)
- `_parse_validation_response()`: Robust JSON parsing with:
  - Markdown code block removal
  - JSON extraction and truncation repair
  - Fallback handling for parsing failures
  - Localized error messages

**Technical Details:**
- **Model:** Gemini 2.5 Flash
- **Temperature:** 0.3 (for consistent JSON output)
- **Max Tokens:** 4096
- **Pattern:** Singleton with lazy initialization
- **Error Handling:** Graceful fallbacks and localized messages

**Use Cases:**
- Pre-submission case validation
- Identify missing documents before submission
- Check form completeness
- Get actionable recommendations
- Quality assurance checks

**Performance:**
- Typical response time: 1-3 seconds
- Depends on case complexity and document count
- Cached context files improve performance

---

## [2.0.0] - 2026-01-12

### Added - Sprint 5 Completion: Context API, Search API, and Render Management

This release completes Sprint 5 with three major features: hierarchical document tree views with caching (S5-011), semantic search with cross-language support (S5-003), and document render deletion (S5-006).

#### S5-011: Context API with Tree Cache Management

**New API Module: backend/api/context.py**

**Endpoint: GET /api/context/tree/{case_id}**

**Location:** `backend/api/context.py:35-126`

Retrieve hierarchical document tree view for a case with ASCII tree formatting.

**Response Format:**
```json
{
  "treeView": "Case ACTE-2024-001:\n├── Personal Data (5 documents)\n│   ├── Passport_Scan.pdf\n│   └── Birth_Certificate.pdf\n...",
  "folders": ["Personal Data", "Applications", "Evidence"],
  "documentCount": 10
}
```

**Key Features:**
- **ASCII Tree Formatting:** Uses ├── └── characters for hierarchical display
- **Folder Display Names:** Retrieves human-readable names from context files
- **Empty Folder Support:** Shows folders even when they contain no documents
- **Document Listing:** Lists all documents with original filenames
- **Performance Caching:** Tree views are cached in memory for fast retrieval

**Tree Cache Management:**

The document tree cache is automatically invalidated to ensure accuracy:
- **POST /api/files/upload:** Cache invalidated after file upload
- **DELETE /api/files/{case_id}/{folder_id}/{filename}:** Cache invalidated after file deletion
- **DELETE /api/files/renders/{case_id}/{document_id}/{render_id}:** Cache invalidated after render deletion

Cache invalidation triggers:
1. File operation completes successfully
2. `invalidate_tree_cache(case_id)` is called
3. Next tree view request regenerates and caches the tree

**Performance Metrics:**
- First call (cache miss): 100-300ms (generates and caches tree)
- Cached calls (cache hit): < 50ms (returns cached tree)
- Cache invalidation: < 10ms (removes cached entry)

**Use Cases:**
- Frontend tree view components
- Debugging document structure
- Manual verification of folder hierarchy
- Context display for users

---

#### S5-003: Semantic Search API with Cross-Language Support

**New API Module: backend/api/search.py**

**Endpoint: POST /api/search/semantic**

**Location:** `backend/api/search.py:103-266`

Perform semantic search on document content using natural language queries with Gemini AI.

**Request Format:**
```json
{
  "query": "passport number",
  "documentContent": "Full document text...",
  "documentType": "pdf",
  "documentPath": "/path/to/document.pdf",
  "queryLanguage": "en",
  "documentLanguage": "de"
}
```

**Response Format:**
```json
{
  "highlights": [
    {
      "start": 125,
      "end": 145,
      "relevance": 0.95,
      "matchedText": "Passnummer: 123456789",
      "context": "Direct match: passport number field"
    }
  ],
  "count": 1,
  "matchSummary": "Found 1 relevant passage (cross-language: English → German)",
  "queryLanguage": "en",
  "documentLanguage": "de",
  "isCrossLanguage": true
}
```

**Key Features:**
- **Semantic Understanding:** Matches meaning, not just keywords
- **Cross-Language Search:** Search German documents with English queries (and vice versa)
- **Automatic Language Detection:** Detects query and document languages automatically
- **PDF Text Extraction:** Automatic text extraction from PDF files using PDF service
- **Text Highlighting:** Returns exact character positions for matched text
- **Relevance Scoring:** Each match includes relevance score (0.0-1.0)
- **Context Explanation:** Explains why each passage matched

**Supported Document Types:**
- Text files (txt, md, etc.) via `documentContent` parameter
- PDF files via `documentPath` parameter with automatic extraction

**Supported Languages:**
- German (de)
- English (en)

**Cross-Language Examples:**
- English query "passport number" matches German "Reisepassnummer", "Passnummer", "Pass-Nr."
- German query "Geburtsdatum" matches English "date of birth", "birth date", "DOB"

**New Service: PDF Service**

**Location:** `backend/services/pdf_service.py`

Provides PDF text extraction capabilities:
- `extract_text(file_path)`: Extract all text from PDF file
- Integrates with PyMuPDF (fitz) library
- Handles multi-page PDFs
- Character position tracking for highlighting

**New Tool: Language Detector**

**Location:** `backend/tools/language_detector.py`

Provides language detection and cross-language search support:
- `detect_language(text)`: Detect language of text (de/en)
- `detect_query_and_document_languages(query, document)`: Detect both languages
- `is_cross_language_search(query_lang, doc_lang)`: Check if search is cross-language
- `get_language_name(lang_code)`: Get human-readable language name

**Health Check Endpoint: GET /api/search/health**

**Location:** `backend/api/search.py:269-286`

Returns search service status and capabilities:
```json
{
  "status": "healthy",
  "service": "semantic_search",
  "gemini_initialized": true,
  "pdf_support": true,
  "cross_language_support": true
}
```

**Performance Metrics:**
- Text document search: 1-3 seconds
- PDF document search: 2-5 seconds (includes extraction)
- Language detection: < 100ms
- Cross-language search: No additional overhead

**Use Cases:**
- Document search across cases
- Data extraction from documents
- Cross-language compliance checking
- Quality assurance for document completeness

---

#### S5-006: Document Render Deletion

**New Endpoint: DELETE /api/files/renders/{case_id}/{document_id}/{render_id}**

**Location:** `backend/api/files.py:496-565`

Delete a specific render (anonymized, translated, etc.) from a document.

**Response Format:**
```json
{
  "success": true,
  "message": "Render deleted successfully",
  "render_id": "550e8400-e29b-41d4-a716-446655440002",
  "document_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

**Key Features:**
- **Render-Specific Deletion:** Deletes only the specified render, not the parent document
- **Registry Integration:** Removes render entry from document registry manifest
- **File System Cleanup:** Deletes render file from storage
- **Cache Invalidation:** Automatically invalidates tree cache after deletion

**Render Deletion Process:**
1. Locate render in document registry by `render_id`
2. Remove render entry from parent document's `renders` array
3. Delete render file from filesystem
4. Persist updated manifest to disk
5. Invalidate tree cache for case

**Use Cases:**
- Remove anonymized document versions when no longer needed
- Delete translated documents after review
- Storage management and cleanup
- Privacy compliance (remove renders with sensitive data)

---

### Changed

**File Operations - Cache Invalidation Integration:**

All file operations now trigger tree cache invalidation to ensure tree views stay synchronized:

**POST /api/files/upload** (Updated)
- Location: `backend/api/files.py:67-217`
- Now invalidates tree cache after successful upload
- Ensures new files appear immediately in tree views

**DELETE /api/files/{case_id}/{folder_id}/{filename}** (Updated)
- Location: `backend/api/files.py:220-347`
- Now invalidates tree cache after successful deletion
- Ensures deleted files disappear immediately from tree views

**Context Manager Service:**
- Added `invalidate_tree_cache(case_id)` function for cache management
- Added `generate_document_tree(case_id)` function with caching support
- Integrated with file operations for automatic cache invalidation

---

### New Files

**Backend API Modules:**
- `backend/api/context.py` (127 lines) - Context API endpoints for tree views
- `backend/api/search.py` (287 lines) - Semantic search API endpoints

**Backend Services:**
- `backend/services/pdf_service.py` (150+ lines) - PDF text extraction service

**Backend Tools:**
- `backend/tools/language_detector.py` (200+ lines) - Language detection for search

---

### Dependencies

**New Python Dependencies:**
- PyMuPDF (fitz) - PDF text extraction (if not already present)
- All other dependencies already included in existing requirements

---

### Migration Notes

**Non-Breaking Changes:**

All changes are backward compatible:
- New endpoints are additions only
- Existing file operation endpoints unchanged (only enhanced with cache invalidation)
- Cache invalidation is automatic and transparent
- No frontend changes required

**Frontend Integration Recommendations:**

To use the new features:

1. **Document Tree View:**
```javascript
// Fetch and display tree view
const tree = await fetch(`/api/context/tree/${caseId}`).then(r => r.json());
console.log(tree.treeView); // Display ASCII tree
```

2. **Semantic Search:**
```javascript
// Search document with natural language
const results = await fetch('/api/search/semantic', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'passport number',
    documentContent: documentText,
    documentType: 'txt'
  })
}).then(r => r.json());

// Highlight matched text
results.highlights.forEach(h => {
  highlightText(h.start, h.end, h.relevance);
});
```

3. **Render Deletion:**
```javascript
// Delete anonymized render
await fetch(`/api/files/renders/${caseId}/${documentId}/${renderId}`, {
  method: 'DELETE'
});
```

---

### Performance Impact

**Context API:**
- Negligible impact with caching enabled
- Cache miss: 100-300ms (first call)
- Cache hit: < 50ms (subsequent calls)
- Cache invalidation: < 10ms

**Search API:**
- Search time: 1-5 seconds depending on document size and type
- PDF extraction adds 1-2 seconds for large PDFs
- Language detection: < 100ms

**Render Deletion:**
- Deletion time: 50-200ms
- Includes file deletion and registry update
- Cache invalidation: < 10ms

---

### Security Considerations

- No authentication on new endpoints (planned for future)
- Context API is read-only (no security risk)
- Search API processes document content in-memory (no storage)
- Render deletion validates document and render IDs
- All file operations maintain existing security checks

---

### Known Limitations

- Context API: Tree cache is in-memory (cleared on application restart)
- Search API: Supports only German and English languages
- Search API: PDF extraction may fail for image-based PDFs (OCR planned)
- Render deletion: No undo/rollback capability
- No authentication on any endpoints

---

### Breaking Changes

None. All changes are backward compatible additions or enhancements.

---

## [1.9.0] - 2026-01-12

### Added - Sprint 5 Advanced Features: Form Modification, Document Registry, and Regulation Model

This release introduces AI-powered form modification (S5-001), container-compatible document persistence (S5-007), and enhanced context validation with regulation models (S5-013).

#### S5-001: Natural Language Form Modification

**New Endpoint: POST /api/admin/modify-form**

**Location:** `backend/api/admin.py:247-348`

AI-powered form modification using natural language commands with automatic SHACL generation and Schema.org semantic type inference.

**Request Format:**
```json
{
  "command": "Add an email field for contact email",
  "currentFields": [
    {
      "id": "name",
      "label": "Full Name",
      "type": "text",
      "value": "",
      "required": true
    }
  ],
  "caseId": "ACTE-2024-001"
}
```

**Response Format:**
```json
{
  "fields": [...],
  "shaclShape": {
    "@context": {
      "sh": "http://www.w3.org/ns/shacl#",
      "schema": "http://schema.org/",
      "xsd": "http://www.w3.org/2001/XMLSchema#",
      "acte": "http://bamf.example.de/acte#"
    },
    "@type": "sh:NodeShape",
    "sh:targetClass": "acte:IntegrationCourseApplication",
    "sh:property": [...]
  },
  "modifications": [
    "Added field 'Contact Email' (email)"
  ],
  "message": "Form modified successfully"
}
```

**Key Features:**
- **Natural Language Commands**: "Add email field", "Remove phone number", "Add dropdown for status"
- **Automatic Semantic Inference**: Maps field labels to Schema.org types (email → schema:email, phone → schema:telephone)
- **Validation Pattern Generation**: Automatic regex patterns for emails, phones, postal codes, etc.
- **Complete SHACL Shape**: Generates full SHACL NodeShape for entire form with PropertyShapes
- **Multiple Operations**: Add, remove, and modify fields
- **Multilingual Support**: Commands in English and German

**Supported Field Types:**
- `text`: Standard text input with semantic validation
- `date`: Date picker with date validation
- `select`: Dropdown with predefined options
- `textarea`: Multi-line text input

**Semantic Type Mappings:**
| Field Label | Schema.org Type | Validation |
|------------|----------------|------------|
| email | schema:email | Email regex |
| phone | schema:telephone | Phone regex |
| name | schema:name | Name validation |
| birth date | schema:birthDate | Date validation |
| address | schema:address | Address validation |
| postal code | schema:postalCode | Postal validation |
| nationality | schema:nationality | Country validation |
| gender | schema:gender | Gender validation |

**New Service: SHACL Generator**

**Location:** `backend/services/shacl_generator.py`

Provides comprehensive SHACL shape generation with:
- Schema.org semantic type inference from field labels
- Automatic validation pattern generation
- PropertyShape generation for individual fields
- NodeShape generation for complete forms
- JSON-LD context generation
- Support for all form field types (text, date, select, textarea)

---

#### S5-007: Document Registry and Container-Compatible Persistence

**New API Module: backend/api/documents.py**

Three new endpoints for document registry management:

**1. GET /api/documents/tree/{case_id}**

**Location:** `backend/api/documents.py:68-151`

Retrieve complete document tree for a case from the registry manifest.

**Response Format:**
```json
{
  "folders": [
    {
      "id": "personal-data",
      "name": "Personal Data",
      "documents": [
        {
          "id": "doc-abc123",
          "name": "Birth_Certificate.pdf",
          "type": "pdf",
          "size": "245 KB",
          "uploadedAt": "2024-01-15T10:30:00Z",
          "metadata": {...},
          "caseId": "ACTE-2024-001",
          "folderId": "personal-data"
        }
      ],
      "subfolders": [],
      "isExpanded": true
    }
  ],
  "rootDocuments": []
}
```

**2. GET /api/documents/all**

**Location:** `backend/api/documents.py:154-200`

Retrieve all documents across all cases with full registry metadata.

**Response Format:**
```json
{
  "success": true,
  "count": 15,
  "documents": [
    {
      "documentId": "doc-abc123",
      "caseId": "ACTE-2024-001",
      "folderId": "personal-data",
      "fileName": "Birth_Certificate.pdf",
      "filePath": "public/documents/ACTE-2024-001/personal-data/Birth_Certificate.pdf",
      "uploadedAt": "2024-01-15T10:30:00Z",
      "fileHash": "sha256:abc123...",
      "renders": []
    }
  ]
}
```

**3. GET /api/documents/health**

**Location:** `backend/api/documents.py:203-260`

Health check for document registry service.

**Response Format:**
```json
{
  "service": "documents",
  "status": "ready",
  "features": {
    "document_tree": true,
    "manifest_persistence": true,
    "filesystem_reconciliation": true
  },
  "manifest": {
    "loaded": true,
    "document_count": 15
  },
  "storage": {
    "available": true,
    "path": "/home/user/project/public/documents"
  }
}
```

**New Service: Document Registry**

**Location:** `backend/services/document_registry.py` (710 lines)

Comprehensive document registry/manifest system providing:

**Core Features:**
- **Manifest Persistence**: Single source of truth in `backend/data/document_manifest.json`
- **Container-Friendly**: Uses configurable `DOCUMENTS_BASE_PATH`
- **Filesystem Reconciliation**: Automatic on startup
  - Discovers orphaned files (on disk but not in manifest)
  - Detects missing files (in manifest but not on disk)
  - Verifies file integrity with SHA-256 hashes
- **Document Tree Building**: Hierarchical folder structure for frontend
- **Render Tracking**: Tracks anonymized/translated document versions

**Key Functions:**
- `load_manifest()`: Load registry from disk
- `save_manifest()`: Persist registry to disk
- `register_document()`: Add document to registry
- `unregister_document()`: Remove document from registry
- `find_document_by_path()`: Locate document in registry
- `build_document_tree()`: Build hierarchical tree for case
- `get_all_documents()`: Retrieve all documents
- `reconcile_manifest_with_filesystem()`: Sync manifest with disk

**Document Registry Schema:**
```json
{
  "version": "1.0",
  "schemaVersion": "1.0",
  "lastUpdated": "2026-01-12T12:00:00Z",
  "documents": [
    {
      "documentId": "uuid",
      "caseId": "ACTE-2024-001",
      "folderId": "personal-data",
      "fileName": "document.pdf",
      "filePath": "public/documents/...",
      "uploadedAt": "2026-01-12T10:00:00Z",
      "fileHash": "sha256:...",
      "renders": []
    }
  ]
}
```

**File Operations Integration:**

Modified endpoints to integrate with document registry:

**POST /api/files/upload** (Updated)
- Now automatically registers uploaded files in document registry
- Calculates SHA-256 file hash for integrity
- Creates document entry with UUID
- Graceful degradation: upload succeeds even if registration fails

**DELETE /api/files/{case_id}/{folder_id}/{filename}** (Updated)
- Now automatically unregisters deleted files from document registry
- Removes document entry and all associated renders
- Graceful degradation: deletion succeeds even if unregistration fails

**Reconciliation on Startup:**

Application now performs automatic filesystem reconciliation:
1. Loads manifest from disk
2. Scans filesystem for all documents
3. Identifies orphaned files (not in manifest)
4. Registers orphaned files with generated metadata
5. Identifies missing files (in manifest but not on disk)
6. Logs missing files as warnings
7. Saves updated manifest

**Benefits:**
- Documents persist across container restarts
- No data loss when containers are recreated
- Automatic recovery from inconsistent states
- Frontend always has accurate document list

---

#### S5-013: Enhanced Context Validation with Regulation Model

**New Model: Regulation**

**Location:** `backend/models/regulation.py` (250 lines)

Type-safe access to regulation data from case contexts.

**Regulation Dataclass:**
```python
@dataclass
class Regulation:
    id: str
    title: str
    summary: str
    url: str
    relevance: str
```

**Key Features:**
- `from_dict()`: Create Regulation from JSON data
- `validate()`: Check data quality (URL format, content length, etc.)
- `get_regulation_details()`: Find regulation by ID
- `validate_regulations_list()`: Validate all regulations in list

**Enhanced Context Manager**

**Location:** `backend/services/context_manager.py` (Updated with ValidationResult)

**ValidationResult Dataclass:**
- Structured validation results with errors, warnings, and statistics
- Statistics: document counts, regulation counts, common issue counts, etc.
- `get_summary()`: Human-readable summary
- `to_dict()`: JSON serialization

**New Function: validate_case_context()**

Validates case contexts against schema v2.0 requirements:

**Validation Checks:**
1. Schema version must be "2.0"
2. Required fields present
3. Document validation (minimum 15 required documents)
4. Regulation validation (minimum 10 regulations with valid URLs)
5. Common issues validation (minimum 20 with severity levels)
6. Validation rules present (at least 1)

**Validation Results:**

| Case Context | Documents | Regulations | Common Issues | Status |
|--------------|-----------|-------------|---------------|--------|
| ACTE-2024-001 | 17 | 11 | 24 | PASS |
| Integration Template | 17 | 11 | 24 | PASS |
| Asylum Template | 15 | 11 | 24 | PASS |
| Family Reunification | 17 | 11 | 22 | PASS |

---

### Changed

**File Operations:**
- `POST /api/files/upload`: Now registers documents in document registry
- `DELETE /api/files/{case_id}/{folder_id}/{filename}`: Now unregisters documents from registry

**Context Manager:**
- Added `ValidationResult` dataclass for structured validation results
- Added `validate_case_context()` method for context validation
- Enhanced with regulation model integration

**Configuration:**
- Added `DOCUMENTS_BASE_PATH` configuration variable for container compatibility

---

### New Files

**Backend API:**
- `backend/api/documents.py` (313 lines) - Document registry API endpoints

**Backend Services:**
- `backend/services/document_registry.py` (710 lines) - Document registry/manifest system
- `backend/services/shacl_generator.py` (370 lines) - SHACL shape generation service

**Backend Models:**
- `backend/models/regulation.py` (250 lines) - Regulation model with validation

**Backend Schemas:**
- `backend/schemas/schema_org_mappings.py` (306 lines) - Schema.org semantic type mappings

**Data Files:**
- `backend/data/document_manifest.json` - Document registry manifest (persistent storage)

**Tests and Demos:**
- `demo_s5_013_regulation_model.py` (131 lines) - Regulation model demonstration
- `test_s5_013_validation.py` (143 lines) - Context validation tests

---

### Dependencies

**New Python Dependencies:**
- No new external dependencies required
- Uses existing FastAPI, Pydantic, and standard library modules

---

### Migration Notes

**Document Registry Migration:**
- Existing files will be automatically discovered and registered on first startup
- No manual migration required
- Manifest file will be created automatically: `backend/data/document_manifest.json`
- Recommend backing up `public/documents/` directory before first run

**Context Validation:**
- Schema v1.0 contexts will fail validation (by design)
- Upgrade contexts to schema v2.0 to pass validation
- See D-S5-003 documentation for schema v2.0 requirements

---

### Performance Impact

**Document Registry:**
- Startup time increased by ~100-500ms for reconciliation (depends on document count)
- Document tree retrieval: < 100ms (reads from manifest, no filesystem scanning)
- File upload: +10-20ms for registration
- File deletion: +10-20ms for unregistration

**Form Modification:**
- Typical response time: 1-3 seconds (AI processing)
- SHACL generation: < 100ms

---

### Security Considerations

- Document registry manifest is stored in plain JSON (no encryption)
- No authentication on new endpoints (planned for future)
- File hashes (SHA-256) provide integrity verification
- Document registry prevents path traversal attacks

---

### Breaking Changes

None. All changes are backward compatible.

---

## [1.6.0] - 2026-01-12

### Added - Sprint 5 Enhancements: Multilingual Support and Smart Form Extraction

This release introduces multilingual chat capabilities (S5-014), intelligent form field suggestion mode (S5-002), and optional conversation history management (S5-010).

#### S5-014: Multilingual Chat Support

**WebSocket Language Query Parameter**

The WebSocket chat endpoint now accepts an optional `language` query parameter for multilingual AI responses:

**Location:** `backend/api/chat.py:85-137`

**Connection Format:**
```
ws://localhost:8000/ws/chat/{case_id}?language={lang}
```

**Supported Languages:**
- `de` (German) - Default
- `en` (English)

**Features:**
1. **Translated Welcome Messages:**
   - German: "Verbunden mit KI-Assistent für Akte-2024-001"
   - English: "Connected to AI assistant for Case-2024-001"
   - Case ID prefix also localized (ACTE → Akte/Case)

2. **Language-Aware AI Responses:**
   - All AI responses generated in the specified language
   - Applies to chat responses, error messages, and confirmations

3. **Per-Message Language Override:**
   - New `language` field in chat messages
   - Overrides connection-level language setting for specific messages
   - Enables mixed-language conversations when needed

**Example Connection:**
```javascript
// English connection
const ws = new WebSocket('ws://localhost:8000/ws/chat/ACTE-2024-001?language=en');

// German connection (default)
const ws = new WebSocket('ws://localhost:8000/ws/chat/ACTE-2024-001?language=de');
```

**Example Message with Language Override:**
```json
{
  "type": "chat",
  "content": "What documents are required?",
  "language": "en"
}
```

**Backward Compatibility:**
- Language parameter is optional
- Defaults to German ('de') when not specified
- Existing clients continue to work without changes

---

#### S5-002: Smart Form Field Suggestion Mode

**Enhanced Form Extraction with Current Values**

The form extraction system now supports intelligent categorization of extracted values based on current form state:

**Location:** `backend/tools/form_parser.py:195-263`, `backend/api/chat.py:341-406`

**New Message Parameter: `currentFormValues`**

When provided, enables smart form extraction that categorizes results into:
1. **Direct Updates** - Empty fields filled automatically
2. **Suggestions** - Non-empty fields requiring user approval
3. **Ignored** - Fields with identical values (no action needed)

**Message Format:**
```json
{
  "type": "chat",
  "content": "Extract form fields from this document",
  "formSchema": [...],
  "currentFormValues": {
    "field_id": "current_value",
    ...
  }
}
```

**New Response Message Type: `form_suggestion`**

```json
{
  "type": "form_suggestion",
  "suggestions": {
    "field_id": {
      "value": "extracted_value",
      "confidence": 0.95,
      "current": "current_value"
    }
  },
  "timestamp": null
}
```

**Extraction Logic:**

1. **Empty Field (current value is blank):**
   - Action: Fill directly without user confirmation
   - Sent as `form_update` message

2. **Non-Empty Field with Different Value:**
   - Action: Present as suggestion requiring approval
   - Sent as `form_suggestion` message
   - Includes both current and suggested values for comparison

3. **Non-Empty Field with Identical Value:**
   - Action: Ignore (no update needed)
   - Not included in any response messages

**Enhanced Confirmation Messages:**

The AI now provides detailed summaries:
```
"I've extracted form data: 2 fields filled, 3 suggestions available, 1 field unchanged."
```

**Backward Compatibility:**
- `currentFormValues` parameter is optional
- When not provided, uses legacy behavior (all fields as direct updates)
- Existing form extraction requests continue to work unchanged

**New Backend Functions:**
- `compare_values()`: Categorizes extracted values by comparison
- Enhanced `parse_extraction_result()`: Supports suggestion mode

---

#### S5-010: Conversation History Management (Optional)

**New Conversation Manager Service**

**Location:** `backend/services/conversation_manager.py`

Manages in-memory conversation history for multi-turn AI chat sessions with case-scoped isolation.

**Features:**
- Per-case conversation storage
- Automatic context window management (max N messages)
- Token budget calculation and truncation
- Thread-safe operations

**Configuration:**

New environment variable in `backend/config.py`:

```bash
ENABLE_CHAT_HISTORY=false  # Default: disabled for POC phase
MAX_CONVERSATION_HISTORY=10  # Maximum messages per case
MAX_TOKENS_PER_REQUEST=30000  # Token limit per request
```

**New API Endpoint: Clear Conversation History**

**Location:** `backend/api/chat.py:550-610`

```
POST /api/chat/clear/{case_id}
```

**Request:**
```bash
curl -X POST http://localhost:8000/api/chat/clear/ACTE-2024-001
```

**Response (Success):**
```json
{
  "success": true,
  "case_id": "ACTE-2024-001",
  "messages_cleared": 5,
  "message": "Successfully cleared 5 message(s) from conversation history"
}
```

**Response (Feature Disabled):**
```json
{
  "success": false,
  "case_id": "ACTE-2024-001",
  "messages_cleared": 0,
  "message": "Chat history feature is disabled"
}
```

**Usage:**
- Clear conversation history when starting new topic
- Reset context without disconnecting WebSocket
- Privacy: Remove sensitive conversation data
- Only works when `ENABLE_CHAT_HISTORY=true`

**Implementation Notes:**
- History stored in-memory only (cleared on restart)
- By design for POC phase
- Can be extended to persistent storage in future
- Thread-safe for concurrent access

**ConversationManager Class Methods:**
- `add_message(case_id, role, content)`: Add message to history
- `get_conversation_history(case_id, max_messages)`: Retrieve history
- `clear_conversation(case_id)`: Clear history for case
- `get_token_budget(case_id, reserve_tokens)`: Calculate available tokens

---

### Changed

- **WebSocket endpoint**: Now accepts optional `language` query parameter
- **Chat message format**: Added optional `language` and `currentFormValues` fields
- **System welcome messages**: Now translated based on language preference
- **Form extraction responses**: Split into direct updates and suggestions when `currentFormValues` provided
- **Chat confirmation messages**: Enhanced with detailed extraction summaries

### Backend Service Additions

- **ConversationManager** (`backend/services/conversation_manager.py`): Chat history management
- **Configuration module** (`backend/config.py`): Centralized configuration settings

### Message Type Additions

- **form_suggestion**: New message type for suggested form field changes requiring approval

### Non-Breaking Changes

All changes are backward compatible:
- Existing WebSocket connections work without language parameter (defaults to German)
- Form extraction works without `currentFormValues` (uses legacy mode)
- Conversation history feature disabled by default
- All existing message formats and endpoints remain functional

---

## [1.5.0] - 2025-12-24

### Added - Document Anonymization and Enhanced Context Management (S2-004)

This release introduces real-time document anonymization capabilities via WebSocket and implements major enhancements to the context management system for improved AI response accuracy.

#### New Feature: Document Anonymization via WebSocket

**New Message Type: `anonymize`**

The WebSocket chat endpoint now supports document anonymization through a new message type:

**Location:** `backend/api/chat.py:172-178, 379-466`

**Incoming Message Format:**
```json
{
  "type": "anonymize",
  "filePath": "/path/to/document.jpg",
  "folderId": "optional-folder-id"
}
```

**Response Message Format (`anonymization_complete`):**
```json
{
  "type": "anonymization_complete",
  "originalPath": "/path/to/document.jpg",
  "anonymizedPath": "/path/to/anonymized/document.jpg",
  "detectionsCount": 5,
  "success": true,
  "error": null,
  "timestamp": null
}
```

**Follow-up Confirmation (`chat_response`):**
```json
{
  "type": "chat_response",
  "content": "Document anonymized successfully. Found and masked 5 PII fields. The anonymized version has been saved.",
  "timestamp": null
}
```

**Anonymization Workflow:**

1. **Client Request:**
   - Client sends `anonymize` message with file path
   - Only image files (PNG, JPG, JPEG) currently supported
   - Optionally includes folder ID for context

2. **Server Processing:**
   - Validates file path and format
   - Calls anonymization service via `anonymization_tool`
   - Detects and masks PII fields (names, addresses, IDs, etc.)
   - Creates anonymized version with "_anonymized" suffix
   - Counts number of PII detections

3. **Server Response:**
   - `anonymization_complete` message with full details
   - Follow-up `chat_response` with human-readable confirmation
   - Error handling for unsupported formats or service failures

**Supported File Formats:**
- PNG (.png)
- JPEG (.jpg, .jpeg)
- Other image formats supported by the anonymization service

**Error Cases:**
- No file path provided
- Unsupported file format (non-image)
- Anonymization service failure
- File not found or inaccessible

**New Backend Module: `anonymization_tool`**

Location: `backend/tools/anonymization_tool.py`

Provides:
- `anonymize_document(file_path)`: Async function to anonymize a document
- `is_supported_format(file_path)`: Check if file format is supported
- `AnonymizationResult` dataclass: Structured result format

**Integration with WebSocket:**
- New `handle_anonymization()` async function in `chat.py`
- Seamless integration with existing message protocol
- Real-time processing and response delivery
- Comprehensive error handling and validation

#### Enhanced Context Management System (S2-004)

**Location:** `backend/services/context_manager.py`

Major enhancements to improve context-aware AI responses:

**New Classes and Data Structures:**

1. **`ContextSource` Enum:**
   - CASE - Case-level context
   - FOLDER - Folder-level context
   - DOCUMENT - Document-level context
   - USER - User-provided context
   - SYSTEM - System-level context

2. **`ContextEntry` Dataclass:**
   - Tracks individual context entries with source attribution
   - Fields: `key`, `value`, `source`, `priority`
   - Enables granular context tracking and conflict resolution

3. **`MergedContext` Dataclass:**
   - Result of merging multiple contexts
   - Includes merged data and source tracking
   - Provides transparency about context origins

**New Functions:**

1. **`resolve_conflict(entries: List[ContextEntry]) -> ContextEntry`:**
   - Intelligent conflict resolution based on source priority
   - Priority order: DOCUMENT > USER > FOLDER > CASE > SYSTEM
   - Returns the highest priority entry when conflicts occur

2. **`merge_contexts_with_tracking(contexts: List[Dict], sources: List[ContextSource]) -> MergedContext`:**
   - Enhanced context merging with full source tracking
   - Handles nested dictionaries and lists
   - Preserves context provenance for debugging
   - Tracks which sources contributed to final context

**Context Precedence:**

The new system enforces clear precedence rules:
- Document-specific context overrides folder context
- Folder context overrides case context
- Case context overrides system defaults
- User-provided context has high priority

**Benefits:**

1. **Better AI Accuracy:** More relevant context leads to more accurate responses
2. **Conflict Resolution:** Automatic handling of conflicting context values
3. **Source Tracking:** Full transparency about where context came from
4. **Debugging Support:** Easier to trace context-related issues
5. **Scalability:** Clean architecture for adding new context sources

#### New Document Processing Framework (S2-004)

**Location:** `backend/tools/document_processor.py`, `backend/tools/pdf_processor.py`, `backend/tools/text_processor.py`

Introduced a flexible document processing framework for multi-format support:

**Base Classes:**

1. **`DocumentProcessor` (ABC):**
   - Abstract base class for document processors
   - Methods: `extract_text()`, `get_metadata()`, `supports_format()`
   - Ensures consistent interface across all processors

2. **`DocumentMetadata` Dataclass:**
   - Standardized metadata structure
   - Fields: file_path, format, page_count, encoding, size, created_at, modified_at, custom_metadata
   - Consistent metadata across all document types

3. **`ExtractionResult` Dataclass:**
   - Structured extraction results
   - Fields: text, metadata, success, error, processor_used
   - Enables reliable result handling

**Implemented Processors:**

1. **`TextProcessor`:**
   - Handles plain text files (.txt)
   - UTF-8 encoding support with fallback
   - Metadata extraction (size, dates, line count)
   - Location: `backend/tools/text_processor.py`

2. **`PDFProcessor` (Stub):**
   - Placeholder for PDF processing
   - Currently raises `NotImplementedError`
   - Planned for Phase 3 implementation
   - Location: `backend/tools/pdf_processor.py`

**Utility Functions:**

- `get_processor(file_path)`: Returns appropriate processor for file type
- `get_supported_extensions()`: Lists all supported file extensions
- `is_supported(file_path)`: Check if file type is supported

**Framework Architecture:**

```
DocumentProcessor (ABC)
├── TextProcessor (implemented)
├── PDFProcessor (stub, Phase 3)
└── [Future processors...]
```

**Use Cases:**

- Document text extraction for AI processing
- Metadata collection for search indexing
- Format-agnostic document handling
- Easy addition of new document formats

**Current Support:**

- Text files: Fully implemented
- PDF files: Structure in place, implementation pending

#### Updated Backend Configuration

**Modified Files:**
- `backend/api/chat.py`: Added anonymization message handling
- `backend/tools/__init__.py`: Added document processor exports
- `backend/services/gemini_service.py`: Minor enhancements for context handling

**New Dependencies:**
- No new external dependencies added
- Utilizes existing libraries for image processing

#### Documentation Updates

**Updated Files:**

1. **`docs/apis/endpoints.md`:**
   - Added anonymization message type documentation
   - Detailed anonymization workflow section
   - Anonymization request/response examples
   - Updated Message Types Summary
   - Added error cases for anonymization
   - Updated Known Limitations
   - Updated version to 1.5.0

2. **`docs/apis/api-changelog.md`:**
   - Added version 1.5.0 entry (this document)

3. **`docs/apis/.last-sync.json`:**
   - Updated last_commit to 9154f40
   - Updated documentation_version to 1.5.0
   - Updated last_sync timestamp
   - Added new tracked paths for document processors

#### Testing and Validation

**Test Suite Added:**

Location: `docs/tests/S2-004/`

Comprehensive test coverage for new features:

1. **Context Management Tests:**
   - `test_case_context_fallback.py`: Context fallback mechanisms
   - `test_conflict_resolution.py`: Conflict resolution logic
   - `test_context_precedence.py`: Context priority rules

2. **Document Processor Tests:**
   - `test_text_processor.py`: Text file processing
   - `test_pdf_processor_support.py`: PDF processor detection
   - `test_pdf_processor_not_implemented.py`: Phase 3 stub validation

3. **UI Context Indicators:**
   - `test_ui_context_indicators.md`: UI context display guidelines

**Test Results:**

Location: `docs/tests/S2-004/test-results.json`, `docs/tests/S2-004/TEST_SUMMARY.md`

All tests passing with comprehensive coverage of new functionality.

#### Migration Notes

**Non-Breaking Changes:**

All changes are backward compatible:
- Existing WebSocket messages work unchanged
- New `anonymize` message type is addition only
- Context management enhancements are internal improvements
- No changes to existing API contracts

**Frontend Integration:**

To use the new anonymization feature:

1. **Add Anonymization UI:**
   ```javascript
   function anonymizeDocument(filePath) {
     ws.send(JSON.stringify({
       type: "anonymize",
       filePath: filePath,
       folderId: currentFolderId
     }));
   }
   ```

2. **Handle Anonymization Results:**
   ```javascript
   case "anonymization_complete":
     if (message.success) {
       showSuccess(`Anonymized: ${message.anonymizedPath}`);
       showInfo(`Masked ${message.detectionsCount} PII fields`);
     } else {
       showError(`Anonymization failed: ${message.error}`);
     }
     break;
   ```

3. **Display Anonymized Documents:**
   - Show both original and anonymized versions
   - Indicate number of PII fields masked
   - Provide download option for anonymized version

**No Action Required:**

Existing functionality continues to work:
- Chat messages unchanged
- Form extraction unchanged
- Health checks unchanged
- Streaming responses unchanged

#### Security Considerations

**Anonymization Security:**

- Anonymized files created in same directory as originals
- Original files preserved (never modified)
- File path validation to prevent directory traversal
- Format validation to prevent processing of executable files
- Error messages sanitized (no system path disclosure)

**Context Management Security:**

- Context isolation per case maintained
- No cross-case context leakage
- Context sources clearly tracked
- User-provided context has controlled priority

**Known Limitations:**

- No authentication (planned for future)
- Anonymization only for image files (PDF support coming in Phase 3)
- No automatic cleanup of anonymized files
- No versioning for anonymized documents

#### Performance Impact

**Anonymization Performance:**

- Typical processing time: 2-5 seconds for images
- Depends on image size and complexity
- Async processing prevents WebSocket blocking
- Real-time progress feedback via WebSocket

**Context Management Performance:**

- Enhanced tracking adds minimal overhead
- Context merging optimized for typical case sizes
- No significant impact on response times
- Memory usage remains within acceptable bounds

#### Use Cases

**Primary Use Cases:**

1. **Privacy-Compliant Document Sharing:**
   - Anonymize documents before sharing with third parties
   - Remove PII from case files for training purposes
   - Create redacted versions for public records requests

2. **Automated PII Detection:**
   - Identify documents containing sensitive information
   - Count PII occurrences for compliance reporting
   - Flag documents requiring manual review

3. **Context-Aware AI Assistance:**
   - Better responses through enhanced context tracking
   - Automatic conflict resolution in multi-source contexts
   - Improved accuracy in document-specific queries

#### Future Enhancements

**Planned for Next Releases:**

1. **PDF Anonymization:**
   - Complete PDFProcessor implementation (Phase 3)
   - Text-based PDF anonymization
   - OCR-based PDF anonymization for scanned documents

2. **Advanced Anonymization:**
   - Customizable PII detection rules
   - Partial anonymization (selective field masking)
   - Anonymization templates for specific document types

3. **Context Enhancements:**
   - User preference contexts
   - Historical context (previous interactions)
   - Machine learning-based context suggestions

4. **Batch Operations:**
   - Batch anonymization of multiple documents
   - Progress tracking for long-running operations
   - Scheduled anonymization jobs

---

## [1.4.0] - 2025-12-23

### Added - Admin API with AI-Powered Form Field Generation

This release introduces a new Admin API module with endpoints for administrative operations, featuring AI-powered form field generation with SHACL semantic metadata support.

#### New Admin API Module

**New Endpoints:**

1. **POST /api/admin/generate-field** - Generate form field from natural language
   - Source: `backend/api/admin.py:100-193`
   - AI-powered field generation from natural language prompts
   - SHACL-compliant metadata generation
   - Supports English and German prompts
   - Rule-based extraction with AI fallback

2. **GET /api/admin/health** - Admin service health check
   - Source: `backend/api/admin.py:196-217`
   - Service status verification
   - Feature availability reporting

#### Form Field Generation Service

**New Service: FieldGenerator**

Located in `backend/services/field_generator.py`, this service provides:

**Core Capabilities:**
- Natural language prompt parsing
- Rule-based field extraction for common patterns
- AI-powered generation for complex prompts (via Gemini)
- SHACL metadata generation with JSON-LD format
- Field validation and specification normalization

**Supported Field Types:**
- `text` - Standard text input fields
- `date` - Date picker fields
- `select` - Dropdown fields with options
- `textarea` - Multi-line text fields

**Example Prompts:**
```
"Add a text field for passport number"
"Add dropdown for marital status with options single, married, divorced"
"I need a required date field for visa expiry"
"Create a textarea for additional notes"
```

**Generation Process:**

1. **Prompt Analysis**: Parse natural language input
2. **Pattern Matching**: Try rule-based extraction first
3. **AI Fallback**: Use Gemini for ambiguous cases
4. **Field Construction**: Build field specification
5. **SHACL Generation**: Add semantic metadata
6. **Validation**: Verify field completeness

**Performance:**
- Rule-based extraction: < 100ms
- AI-based generation: 1-3 seconds
- Typical response time: 1-3 seconds

#### SHACL Schema Support

**New Module: backend/schemas/**

Provides SHACL (Shapes Constraint Language) schema definitions for semantic form metadata:

**Key Files:**
- `backend/schemas/shacl.py` - SHACL shape classes (SHACLPropertyShape, SHACLNodeShape)
- `backend/schemas/jsonld_context.py` - JSON-LD context definitions
- `backend/schemas/__init__.py` - Module initialization

**SHACLPropertyShape Features:**
- Semantic property paths (e.g., "schema:name", "schema:birthDate")
- XSD datatype definitions
- Cardinality constraints (sh:minCount, sh:maxCount)
- Allowed values (sh:in) for select fields
- Pattern validation (sh:pattern)
- String length constraints

**SHACLNodeShape Features:**
- Form-level shape definitions
- Property collection management
- Target class specification
- JSON-LD serialization/deserialization

**SHACL Metadata Benefits:**
1. **Semantic Interoperability**: Fields linked to Schema.org vocabulary
2. **Machine-Readable Validation**: Constraints can be validated automatically
3. **Linked Data Integration**: Compatible with RDF and semantic web technologies
4. **Standard Compliance**: Uses W3C SHACL specification
5. **Future-Proof**: Supports advanced validation and reasoning

**JSON-LD Context:**
```json
{
  "@context": {
    "sh": "http://www.w3.org/ns/shacl#",
    "schema": "http://schema.org/",
    "xsd": "http://www.w3.org/2001/XMLSchema#"
  }
}
```

**Example SHACL Metadata:**
```json
{
  "@context": { ... },
  "@type": "sh:PropertyShape",
  "sh:path": "schema:maritalStatus",
  "sh:datatype": "xsd:string",
  "sh:name": "Marital Status",
  "sh:description": "The person's marital status",
  "sh:in": {
    "@list": ["single", "married", "divorced"]
  }
}
```

#### Updated Backend Configuration

**Modified Files:**
- `backend/main.py` - Added admin router registration

**CORS Updates:**
Added new development ports to CORS allowed origins:
- Port 8080 (configured Vite dev server)
- Port 5174 (alternate Vite port)

Existing ports retained:
- Port 5173 (default Vite)
- Port 3000 (alternative dev)

**HTTP Methods:**
Updated from wildcard `*` to explicit list:
- GET
- POST
- PUT
- DELETE
- OPTIONS
- PATCH

**Router Registration:**
```python
app.include_router(admin_router, tags=["admin"])
```

#### API Request/Response Models

**New Pydantic Models (backend/api/admin.py):**

1. **GenerateFieldRequest**
   - `prompt`: str (3-500 characters)
   - Validation: min/max length constraints

2. **GeneratedFieldResponse**
   - `id`: str (field identifier)
   - `label`: str (human-readable label)
   - `type`: str (text, date, select, textarea)
   - `value`: str (default value)
   - `options`: Optional[List[str]] (for select fields)
   - `required`: bool
   - `shaclMetadata`: Optional[dict] (SHACL JSON-LD)

3. **GenerateFieldResponse** (wrapper)
   - `field`: GeneratedFieldResponse
   - `message`: str

4. **ErrorResponse**
   - `error`: str
   - `detail`: Optional[str]

#### Error Handling

**HTTP Status Codes:**
- `200 OK` - Field generated successfully
- `400 Bad Request` - Invalid prompt or validation failure
- `500 Internal Server Error` - Service error (e.g., Gemini API failure)

**Error Response Format:**
```json
{
  "detail": {
    "error": "Field generation failed",
    "detail": "Specific error message"
  }
}
```

**Validation Errors:**
```json
{
  "detail": {
    "error": "Generated field validation failed",
    "validation_errors": ["Field ID is missing", "Invalid field type"]
  }
}
```

#### Security & Limitations

**Current State:**
- No authentication implemented (public endpoints)
- Input validation on prompt length (3-500 chars)
- Error messages sanitized (no sensitive info exposure)

**Planned Enhancements:**
- Authentication and authorization
- Rate limiting per user/IP
- Request logging and audit trail
- RBAC for admin operations

**Known Limitations:**
- Maximum prompt length: 500 characters
- Requires Gemini API key for complex prompts
- Generated field IDs in camelCase only
- SHACL validation not enforced client-side yet
- No field type beyond text, date, select, textarea

#### Documentation Updates

**Updated Files:**

1. **docs/apis/endpoints.md**
   - Added "Admin Operations" section
   - Detailed POST /api/admin/generate-field documentation
   - Added GET /api/admin/health documentation
   - SHACL metadata explanation
   - Code examples (cURL, JavaScript, Python)
   - Updated version to 1.4.0

2. **docs/apis/openapi.yaml**
   - Added "Admin" tag
   - Added /api/admin/generate-field endpoint spec
   - Added /api/admin/health endpoint spec
   - Added GeneratedField schema with SHACL properties
   - Request examples for text, select, and date fields
   - Updated version to 1.4.0

3. **docs/apis/openapi.json**
   - Auto-generated from openapi.yaml
   - Matches YAML specification
   - Updated version to 1.4.0

4. **docs/apis/api-changelog.md**
   - Added version 1.4.0 entry (this document)

5. **docs/apis/.last-sync.json**
   - Updated last_commit to 29f8271
   - Updated documentation_version to 1.4.0
   - Updated last_sync timestamp
   - Added new tracked paths:
     - backend/api/admin.py
     - backend/services/field_generator.py
     - backend/schemas/shacl.py
     - backend/schemas/jsonld_context.py
     - backend/schemas/__init__.py
   - Added new implemented endpoints
   - Added notes about SHACL support and admin API

#### Migration Notes

**Non-Breaking Changes:**

All changes are backward compatible:
- No existing endpoints modified
- New admin endpoints are additions
- CORS configuration expanded (existing origins retained)
- HTTP methods made explicit (same methods supported)

**Integration Requirements:**

For frontend integration:
1. Add admin panel for field generation
2. Implement prompt input UI (textarea with 3-500 char validation)
3. Display generated field preview with SHACL metadata
4. Add field to form builder/editor
5. Optional: Implement SHACL validation on client side

**No Action Required:**

Existing functionality continues to work:
- WebSocket chat endpoint unchanged
- Form extraction endpoint unchanged
- Health check endpoints unchanged
- All AI and chat operations unchanged

#### Use Cases

**Primary Use Cases:**

1. **Dynamic Form Building**
   - Admin creates new fields using natural language
   - No need to manually write JSON specifications
   - Rapid form prototyping and iteration

2. **Semantic Form Metadata**
   - Forms linked to Schema.org vocabulary
   - Machine-readable validation constraints
   - Integration with linked data systems

3. **Multilingual Administration**
   - German and English prompts supported
   - Helps non-technical staff create forms
   - Reduces language barriers in form design

4. **Template Generation**
   - Quickly generate reusable field definitions
   - Build libraries of common field types
   - Standardize form structure across applications

#### Technical Implementation Details

**Technology Stack:**
- FastAPI for REST API
- Pydantic for request/response validation
- Google Gemini for AI-powered generation
- SHACL/JSON-LD for semantic metadata
- Python dataclasses for schema modeling

**Dependencies:**
- No new external dependencies (uses existing Gemini integration)
- Standard library: json, re, typing
- FastAPI built-ins: HTTPException, APIRouter

**Code Architecture:**
```
backend/
├── api/
│   └── admin.py           # Admin REST endpoints
├── services/
│   └── field_generator.py  # Field generation logic
└── schemas/
    ├── __init__.py
    ├── shacl.py           # SHACL data classes
    └── jsonld_context.py   # JSON-LD helpers
```

**Testing:**
- Manual testing via cURL and API clients
- Integration testing recommended for production
- Unit tests for field_generator service recommended

#### Future Enhancements

**Planned for Next Releases:**

1. **Authentication & Authorization**
   - JWT-based authentication
   - Role-based access control (admin only)
   - API key management

2. **Advanced Field Types**
   - Number fields with range validation
   - Email fields with format validation
   - URL fields
   - File upload fields
   - Nested object fields

3. **Field Templates**
   - Pre-built field template library
   - Custom template creation and management
   - Template versioning and history

4. **SHACL Validation**
   - Server-side SHACL validation enforcement
   - Client-side SHACL validator library
   - Validation error reporting with SHACL paths

5. **Batch Operations**
   - Generate multiple fields from single prompt
   - Bulk field import/export
   - Form template generation

6. **Internationalization**
   - Support for additional languages
   - Localized field labels and descriptions
   - Multi-language SHACL metadata

---

## [1.3.0] - 2025-12-18

### Enhanced - Advanced Form Field Extraction Capabilities

This release significantly enhances the AI-powered form field extraction system with multilingual support, advanced date format conversion, fuzzy select field matching, and field-specific confidence scoring.

#### Enhanced Multilingual Support

**German-English Field Mapping:**

Added explicit German-English field mappings in extraction prompt:
- 'Vorname' or 'Rufname' → firstName
- 'Nachname' or 'Familienname' → lastName
- 'Name' or 'Vollständiger Name' → fullName
- 'Geburtsdatum' or 'Geboren' → birthDate
- 'Geburtsort' → placeOfBirth
- 'Staatsangehörigkeit' or 'Nationalität' → nationality
- 'Passnummer' or 'Reisepassnummer' → passportNumber
- 'Adresse' or 'Anschrift' → address

**Key Improvements:**
- Documents can be in German or English without configuration
- AI extracts actual data values, not field labels
- Proper handling of German special characters (umlauts: ä, ö, ü, ß)
- Semantic understanding of field meanings across languages
- Support for mixed-language documents

**Use Case:**
German birth certificate with "Geburtsdatum: 15.05.1990" correctly extracts birthDate as "1990-05-15"

#### Advanced Date Format Conversion

**New Helper Function: `_convert_to_iso_date()`**

Intelligently converts multiple date formats to ISO 8601 (YYYY-MM-DD):

Supported input formats:
- German format: DD.MM.YYYY (e.g., 15.05.1990 → 1990-05-15)
- Slash format: DD/MM/YYYY (e.g., 20/03/1995 → 1995-03-20)
- Hyphen format: DD-MM-YYYY (e.g., 01-12-1985 → 1985-12-01)
- Short year formats: DD.MM.YY, DD/MM/YY
- Already ISO: YYYY-MM-DD (passes through)

**Date Validation:**
- Validates dates are realistic (years 1900-2030 for birthdates)
- Checks date component validity (no invalid dates like 32.13.2000)
- Returns None for unparseable dates rather than guessing

**Confidence Scoring for Dates:**
- 0.95: Valid ISO format date (no conversion needed)
- 0.80: Successfully converted from another format
- 0.50: Questionable format (flagged for review)

**Example Conversions:**
```
'15.05.1990' → '1990-05-15' (confidence: 0.80)
'2000-03-20' → '2000-03-20' (confidence: 0.95)
'01/12/1985' → '1985-12-01' (confidence: 0.80)
```

#### Fuzzy Select Field Matching

**New Helper Function: `_match_select_option()`**

Three-tier matching strategy for select fields with predefined options:

1. **Exact Match (Case-Insensitive):** Priority matching
   - 'evening' matches option 'Evening' → confidence 0.95
   - 'INTENSIVE' matches option 'Intensive' → confidence 0.95

2. **Partial Match:** Substring matching
   - 'weekend classes' matches option 'Weekend' → confidence 0.80
   - 'intensive course' contains 'intensive', matches 'Intensive Course' → confidence 0.80

3. **Word-Based Match:** Individual word intersection
   - 'online learning' matches option 'Online Course' (word 'online' matches) → confidence 0.80
   - 'evening program' matches 'Evening Course' (word 'evening' matches) → confidence 0.80

**Fallback Behavior:**
- If no match found: field omitted or confidence 0.40 if returned
- Prioritizes first exact match, then first partial match, then first word match
- Case-insensitive throughout all matching tiers

**Example:**
```
Options: ["Intensive Course", "Evening Course", "Weekend Course", "Online Course"]

Extracted: "intensive" → Matched: "Intensive Course" (exact, 0.95)
Extracted: "EVENING" → Matched: "Evening Course" (exact, 0.95)
Extracted: "weekend classes" → Matched: "Weekend Course" (partial, 0.80)
Extracted: "I prefer online" → Matched: "Online Course" (word-based, 0.80)
```

#### Enhanced Confidence Scoring

**Field-Type-Specific Confidence:**

Previous version used default 0.85 for all fields. New version calculates confidence based on field type and validation results:

**Date Fields:**
- 0.95: Valid ISO format (YYYY-MM-DD)
- 0.80: Converted from DD.MM.YYYY or similar format
- 0.50: Questionable or ambiguous date format

**Select Fields:**
- 0.95: Exact case-insensitive match to an option
- 0.80: Fuzzy match (partial or word-based)
- 0.40: No clear match found (usually omitted)

**Text Fields:**
- 0.90: Normal length text (2-200 characters)
- 0.60: Very short text (<2 characters, possibly incomplete)
- 0.70: Very long text (>200 characters, possibly extracted incorrectly)

**Textarea Fields:**
- 0.85: Standard confidence for multi-line text

**Confidence Interpretation Guidelines:**

Added to documentation:
- Scores ≥ 0.85: Generally safe for automatic form filling
- Scores 0.70-0.84: Recommended to highlight for user review (yellow/warning UI)
- Scores < 0.70: Require manual verification before use (red/error UI)

#### Improved Extraction Instructions

**Enhanced Prompt Structure:**

Expanded extraction prompt from 4 sections to 6 comprehensive sections:

1. **Field Extraction Rules** (existing, enhanced)
   - Semantic field label matching
   - Omit ambiguous fields rather than guessing
   - Extract complete values

2. **Multilingual Document Handling** (NEW)
   - German-English field mapping table
   - 8 common field mappings with examples
   - Emphasis on extracting values, not labels

3. **Date Format Conversion** (NEW)
   - Explicit conversion rules with examples
   - Multiple format support documentation
   - Validation guidelines

4. **Select Field Matching** (NEW)
   - Fuzzy matching strategies explained
   - Case-insensitive matching rules
   - Partial and word-based matching examples

5. **Text Field Extraction** (enhanced)
   - Special character preservation (umlauts, accents, hyphens)
   - Whitespace trimming rules
   - Line break handling for textarea

6. **Output Format** (existing, enhanced)
   - Stricter JSON formatting requirements
   - Emphasis on no markdown code blocks
   - Field ID vs label clarification

**Prompt Quality Improvements:**
- More explicit examples for each rule
- Clear "do this, not that" formatting
- Better handling of edge cases
- Reduced ambiguity in instructions

#### Better Error Handling

**Markdown Code Block Cleaning:**

AI responses sometimes wrap JSON in markdown code blocks. New cleaning logic:
```python
if cleaned_response.startswith("```"):
    lines = cleaned_response.split("\n")
    cleaned_response = "\n".join(lines[1:-1])
    cleaned_response = cleaned_response.replace("```json", "").replace("```", "").strip()
```

**Field Validation:**

Enhanced validation in `parse_extraction_result()`:
- Validates extracted fields exist in schema before processing
- Logs warnings for fields not in schema (prevents silent failures)
- Type-specific validation for each field type
- Skips empty or None values
- Converts all values to strings for consistency

**Confidence-Based Field Omission:**

Fields with very low confidence (<0.40) are typically omitted from results rather than returned with low confidence, reducing false positives.

**Error Logging:**

Comprehensive logging throughout extraction pipeline:
- Document length and field count logged at start
- Warnings for invalid dates, non-matching select options, schema mismatches
- Error details for JSON parsing failures
- Success message with count of extracted fields

#### Technical Implementation

**Source File Modified:**
- `backend/tools/form_parser.py` (lines 59-419)

**New Functions Added:**
- `_convert_to_iso_date()` (lines 348-380): Multi-format date converter
- `_match_select_option()` (lines 382-419): Three-tier fuzzy matching
- `_is_valid_iso_date()` (lines 324-346): ISO date validator

**Enhanced Functions:**
- `build_extraction_prompt()`: Expanded from 4 to 6 instruction sections
- `parse_extraction_result()`: Added field-specific confidence scoring and validation

**Dependencies:**
- No new dependencies required
- Uses Python standard library: `json`, `re`, `datetime`

#### Performance Impact

**No Performance Degradation:**
- Helper functions are lightweight (O(n) complexity)
- Date parsing tries formats sequentially but fails fast
- Fuzzy matching is O(n*m) where n=options, m=words (typically small)
- Overall extraction time remains 2-5 seconds

**Improved Accuracy:**
- Reduced manual correction needed for dates in German format
- Better select field matching reduces user intervention
- Confidence scores help prioritize manual review

#### Documentation Updates

**Updated Files:**
- `docs/apis/endpoints.md`: Enhanced "Form Field Extraction via WebSocket" section
  - Expanded extraction features list with new capabilities
  - Detailed confidence scoring guidelines with interpretation
  - Enhanced best practices (8 items, up from 6)
  - Added helper functions documentation
  - Updated limitations list

- `docs/apis/api-changelog.md`: Added version 1.3.0 entry (this document)

- `docs/apis/.last-sync.json`: Updated metadata
  - New commit hash: 9be633c8ac4d170e2600c299f29655513af3bce2
  - Updated sync timestamp: 2025-12-18
  - Version incremented: 1.2.0 → 1.3.0

#### Migration Guide

**Non-Breaking Changes:**

All changes are backward compatible:
- Existing form extraction requests work without modification
- Default behavior improved (better extraction quality)
- Confidence scores now more granular but same range (0.0-1.0)
- API contract unchanged (same request/response structure)

**Recommended UI Updates:**

To take advantage of new confidence scoring:

1. **Visual Confidence Indicators:**
```javascript
function getConfidenceColor(confidence) {
  if (confidence >= 0.85) return 'green';   // Auto-accept
  if (confidence >= 0.70) return 'yellow';  // Review recommended
  return 'red';                             // Verification required
}
```

2. **Confidence Tooltips:**
Show confidence scores on hover with interpretation:
- "High confidence (95%) - auto-filled"
- "Medium confidence (80%) - please review"
- "Low confidence (60%) - verification required"

3. **Batch Review:**
Implement "Review all low-confidence fields" button to help users quickly verify questionable extractions

**No Action Required:**

Existing integrations automatically benefit from:
- Improved German document handling
- Better date format conversion
- Smarter select field matching
- More accurate confidence scores

#### Use Case Examples

**Example 1: German Birth Certificate**

Document content:
```
Geburtsurkunde
Vorname: Ahmad
Nachname: Ali
Geburtsdatum: 15.05.1990
Geburtsort: Kabul, Afghanistan
Staatsangehörigkeit: Afghanisch
```

Form schema:
```json
[
  {"id": "firstName", "label": "First Name", "type": "text", "required": true},
  {"id": "lastName", "label": "Last Name", "type": "text", "required": true},
  {"id": "birthDate", "label": "Date of Birth", "type": "date", "required": true},
  {"id": "placeOfBirth", "label": "Place of Birth", "type": "text", "required": false},
  {"id": "nationality", "label": "Nationality", "type": "text", "required": true}
]
```

Extraction result:
```json
{
  "updates": {
    "firstName": "Ahmad",
    "lastName": "Ali",
    "birthDate": "1990-05-15",
    "placeOfBirth": "Kabul, Afghanistan",
    "nationality": "Afghanisch"
  },
  "confidence": {
    "firstName": 0.90,
    "lastName": 0.90,
    "birthDate": 0.80,
    "placeOfBirth": 0.90,
    "nationality": 0.90
  }
}
```

Note: birthDate confidence 0.80 because converted from German format DD.MM.YYYY

**Example 2: Course Enrollment with Select Field**

Document content:
```
Integration Course Application
Name: Maria Schmidt
I would like to attend evening classes due to work schedule.
```

Form schema:
```json
[
  {"id": "name", "label": "Full Name", "type": "text", "required": true},
  {"id": "coursePreference", "label": "Course Type", "type": "select",
   "options": ["Intensive Course", "Evening Course", "Weekend Course", "Online Course"],
   "required": true}
]
```

Extraction result:
```json
{
  "updates": {
    "name": "Maria Schmidt",
    "coursePreference": "Evening Course"
  },
  "confidence": {
    "name": 0.90,
    "coursePreference": 0.80
  }
}
```

Note: "evening classes" fuzzy matched to "Evening Course" with confidence 0.80

#### Benefits Summary

**For Developers:**
- More reliable extraction with less manual correction
- Field-specific confidence scores enable smart UI decisions
- Better error handling reduces debugging time
- Comprehensive logging aids troubleshooting

**For End Users:**
- German documents work seamlessly without translation
- Dates in German format automatically converted
- More fields extracted successfully on first attempt
- Clear confidence indicators help prioritize review

**For BAMF Officers:**
- Reduced data entry time (more accurate auto-fill)
- Visual confidence cues highlight fields needing attention
- Multilingual document support (German/English)
- Better extraction quality means faster case processing

---

## [1.2.0] - 2025-12-18

### Added - Streaming Response Support for Real-Time AI Chat

This release adds streaming support to the WebSocket chat endpoint, enabling real-time, progressive delivery of AI responses for improved user experience and perceived performance.

#### Streaming Response Feature

**New Message Type:**
- `chat_chunk` - Streaming response chunks with completion flag
  - `content`: Partial response text
  - `is_complete`: Boolean flag indicating stream completion
  - `timestamp`: Message timestamp

**Enhanced Message Protocol:**

Clients can now control response delivery mode via the `stream` parameter:
```json
{
  "type": "chat",
  "content": "User question",
  "stream": true  // Enable streaming (default)
}
```

**Response Modes:**

1. **Streaming Mode (stream: true, default):**
   - Multiple `chat_chunk` messages with `is_complete: false`
   - Final `chat_chunk` with `is_complete: true` and empty content
   - Time-to-first-token: 200-500ms
   - Progressive rendering of AI responses

2. **Non-Streaming Mode (stream: false):**
   - Single `chat_response` message with complete text
   - Simpler integration for batch processing
   - Same total latency as streaming

**Performance Improvements:**

- Time-to-first-token metrics: Averages 200-500ms
- Total response latency: 1-3 seconds (unchanged)
- Better perceived performance through progressive content delivery
- Comprehensive logging of performance metrics:
  - Time-to-first-token
  - Total latency
  - Token counts
  - Response lengths

**Backend Implementation:**

Enhanced `GeminiService.generate_response()`:
- Return type: `Union[str, AsyncGenerator[str, None]]`
- New `_generate_streaming_response()` async generator method
- Automatic performance tracking and logging
- Graceful fallback to non-streaming on errors

Enhanced `chat.py` message handling:
- Automatic detection of streaming vs non-streaming responses
- Chunk-by-chunk delivery in streaming mode
- Completion marker sent after final chunk
- Form extraction remains non-streaming (appropriate for structured data)

**Benefits:**

- Improved user experience with real-time feedback
- Lower perceived latency for long responses
- Better engagement during AI processing
- Maintains backward compatibility (stream defaults to true)
- No breaking changes to existing clients

**Use Cases:**

Streaming mode ideal for:
- Interactive chat interfaces
- Long-form AI responses
- User-facing conversational AI
- Real-time content generation

Non-streaming mode ideal for:
- Automated workflows
- Batch processing
- Response caching and logging
- Form field extraction

**Technical Details:**

Source files modified:
- `backend/services/gemini_service.py`: Streaming generator implementation
- `backend/api/chat.py`: Streaming message protocol handling

Performance metrics logged:
- First token latency
- Total response latency
- Token counts
- Response lengths
- Case ID for tracking

**Documentation Updates:**
- Updated `docs/apis/endpoints.md` with streaming protocol
- Added code examples for both streaming modes
- Performance characteristics documented
- Use case guidance provided

---

## [1.1.0] - 2025-12-18

### Added - Backend Implementation with WebSocket and AI Integration

This release marks the beginning of backend API implementation using FastAPI. Core AI functionality is now available through WebSocket communication with Google Gemini integration.

#### Backend Infrastructure

**Framework & Architecture:**
- FastAPI backend initialized (`backend/main.py`)
- Clean architecture with separation of concerns:
  - `backend/api/` - HTTP/WebSocket protocol handling
  - `backend/services/` - Business logic and AI integration
  - `backend/tools/` - Reusable stateless utility functions
  - `backend/data/` - Configuration files and context data
- CORS middleware configured for local development
- Lifecycle management (startup/shutdown events)
- Logging infrastructure

**Health Check Endpoints:**
- `GET /health` - Backend service health check
- `GET /` - API root information endpoint
- `GET /api/chat/health` - Chat service health with Gemini status

#### Real-Time Communication

**WebSocket Chat Endpoint:**
- `WS /ws/chat/{case_id}` - Real-time, case-scoped AI chat
  - Bidirectional message exchange
  - Connection manager for case isolation
  - Support for multiple message types
  - Automatic context loading per case

**Message Protocol:**

Incoming message types:
- `chat` - User messages and AI interaction requests

Outgoing message types:
- `system` - System notifications and connection status
- `chat_response` - AI-generated text responses
- `form_update` - Extracted form field values with confidence scores
- `error` - Error notifications and validation failures

**Case-Scoped Context:**
- Each WebSocket connection isolated to single case
- Automatic loading of case-level context from JSON files
- Optional folder-level context for specific document groups
- Complete case isolation (no cross-case data access)

#### AI Integration

**Google Gemini Service:**
- `GeminiService` class with singleton pattern (`backend/services/gemini_service.py`)
- Integration with Google Gemini 2.5 Flash model
- Environment-based API key configuration
- Configurable generation parameters (temperature, top_p, max_tokens)
- User-friendly error messages for quota/timeout issues

**Context Management:**
- `ContextManager` service for hierarchical context loading (`backend/services/context_manager.py`)
- Case-level context: regulations, required documents, validation rules
- Folder-level context: expected documents, validation criteria
- Context merging with precedence: Document > Folder > Case
- Template-based case creation support

**Context File Structure:**
```
backend/data/contexts/
├── cases/
│   └── {case_id}/
│       ├── case.json
│       └── folders/
│           └── {folder_id}.json
└── templates/
    └── {case_type}/
```

#### Form Field Extraction

**AI-Powered Data Extraction:**
- `form_parser` tool for document field extraction (`backend/tools/form_parser.py`)
- Intelligent field mapping with semantic understanding
- Date normalization to ISO 8601 format
- Multi-language document support
- Confidence scoring (0.0-1.0) for each extracted field

**Extraction Features:**
- Automatic detection via keywords: "fill", "extract", "populate"
- Validation against form schema before extraction
- Partial extraction (only found fields returned)
- Type-aware extraction (text, date, select, textarea)
- Structured prompt engineering for consistent results

**Form Schema Support:**
```json
{
  "id": "field_identifier",
  "label": "Field Label",
  "type": "text|date|select|textarea",
  "required": boolean,
  "options": ["array", "for", "select"]
}
```

**Extraction Workflow:**
1. Client sends chat message with `formSchema` and `documentContent`
2. Backend builds extraction prompt with field definitions
3. Gemini AI analyzes document and extracts values
4. Results parsed and validated against schema
5. Two responses sent: `form_update` + `chat_response`

#### Technical Details

**Dependencies Added:**
- FastAPI 0.104.1 - Web framework
- Uvicorn 0.24.0 - ASGI server
- google-generativeai 0.3.1 - Gemini API client
- Pydantic 2.5.2 - Data validation
- python-dotenv 1.0.0 - Environment configuration

**AI Model Configuration:**
- Model: gemini-2.5-flash (fast, cost-effective, latest)
- Temperature: 0.7
- Top P: 0.8
- Top K: 40
- Max Output Tokens: 2048

**Performance Characteristics:**
- WebSocket connection per case maintained by ConnectionManager
- Context loaded per message from filesystem (no caching)
- Typical AI response time: 1-3 seconds
- Form extraction: 2-5 seconds depending on complexity

#### Known Limitations

**Not Yet Implemented:**
- Authentication/authorization system
- Case management REST endpoints
- Document storage and retrieval
- Persistent message history
- WebSocket message streaming
- Connection rate limiting
- OCR support for images
- File uploads via WebSocket

**Current Constraints:**
- No authentication (case isolation only)
- Single connection per case (no concurrent)
- Text-only document processing
- Maximum ~10,000 character document length
- Frontend still using mock data (integration pending)

#### Migration Impact

**Non-Breaking Changes:**
- All new functionality (no existing APIs affected)
- Frontend integration not yet required
- Backward compatible with existing simulated operations

**Frontend Integration Required:**
- Update `AIChatInterface.tsx` to use WebSocket
- Replace simulated AI operations with real backend calls
- Add WebSocket connection management
- Handle new message types (form_update, system, error)
- Implement confidence score display for form extraction

#### Documentation Updates

**New Documentation:**
- WebSocket endpoint comprehensive documentation
- Message protocol specification
- Form extraction guide with examples
- Context management architecture
- Health check endpoint documentation

**Updated Files:**
- `docs/apis/.last-sync.json` - Added backend file tracking
- `docs/apis/endpoints.md` - Added WebSocket and health endpoints
- `docs/apis/api-changelog.md` - Version 1.1.0 changelog
- API status changed: "planned" → "partial_implementation"

#### Configuration Required

**Environment Variables:**
```bash
GEMINI_API_KEY=your_google_gemini_api_key_here
```

**Running the Backend:**
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**WebSocket Test:**
```bash
# Using wscat
wscat -c ws://localhost:8000/ws/chat/ACTE-2024-001
```

---

## [1.0.0] - 2025-12-16

### Added - Initial API Documentation

#### Documentation Structure
- Created comprehensive API documentation in `docs/apis/` directory
- Added OpenAPI 3.0 specification (YAML and JSON formats)
- Created detailed endpoint reference with examples
- Documented authentication architecture
- Added this changelog

#### API Endpoints (Planned)

**Authentication**
- `POST /auth/login` - User authentication with JWT tokens
- `POST /auth/logout` - Invalidate access token
- `POST /auth/refresh` - Refresh expired access token

**Case Management**
- `GET /cases` - List cases with filtering and pagination
- `POST /cases` - Create new case from template
- `GET /cases/{caseId}` - Get case details
- `PATCH /cases/{caseId}` - Update case metadata

**Document Operations**
- `GET /cases/{caseId}/documents` - List case documents
- `POST /cases/{caseId}/documents` - Upload document
- `GET /cases/{caseId}/documents/{documentId}` - Get document
- `DELETE /cases/{caseId}/documents/{documentId}` - Delete document

**AI Operations**
- `POST /ai/convert` - Convert document format
- `POST /ai/translate` - Translate document to German
- `POST /ai/anonymize` - Redact personal information
- `POST /ai/extract-metadata` - Extract structured metadata
- `POST /ai/validate-case` - Check case completeness

**Form Management**
- `GET /cases/{caseId}/forms` - Get application form data
- `PUT /cases/{caseId}/forms` - Update form data

**Search**
- `GET /search` - Full-text search across documents

#### Current Implementation (Simulated)

**Source Files:**
- `src/pages/Login.tsx` - Simulated login (no validation)
- `src/contexts/AppContext.tsx` - State management with mock data
- `src/data/mockData.ts` - Mock case, document, and form data
- `src/components/workspace/AIChatInterface.tsx` - Simulated AI operations via slash commands
- `src/components/workspace/CaseTreeExplorer.tsx` - Simulated document upload
- `src/components/workspace/FormViewer.tsx` - Form state management
- `src/components/workspace/DocumentViewer.tsx` - Document display

**Simulated Features:**
- User authentication (username only, no password)
- Case browsing and switching
- Document tree navigation
- AI chat with slash commands:
  - `/convert` - Document format conversion
  - `/translate` - Translation to German
  - `/anonymize` - PII redaction
  - `/search` - Document search
  - `/validateCase` - Case completeness check
  - `/generateEmail` - Email generation
  - `/extractMetadata` - Metadata extraction
- Form auto-fill from AI chat
- Context-aware folder highlighting

**Technology Stack:**
- React 18.3 with TypeScript 5.8
- Vite 5.4 for build tooling
- React Router 6.30 for routing
- @tanstack/react-query 5.83 (configured but not yet used)
- shadcn/ui components
- Client-side state via React Context

#### Data Models

**Core Types** (`src/types/case.ts`):
```typescript
type DocumentType = 'pdf' | 'xml' | 'json' | 'docx';
type CaseStatus = 'open' | 'pending' | 'completed';
type FormFieldType = 'text' | 'date' | 'select' | 'textarea';
type ChatRole = 'user' | 'assistant';

interface Document {
  id: string;
  name: string;
  type: DocumentType;
  size: string;
  uploadedAt: string;
  metadata?: Record<string, any>;
  content?: string;
}

interface Folder {
  id: string;
  name: string;
  documents: Document[];
  subfolders: Folder[];
  isExpanded?: boolean;
}

interface Case {
  id: string;
  name: string;
  createdAt: string;
  status: CaseStatus;
  folders: Folder[];
}

interface FormField {
  id: string;
  label: string;
  type: FormFieldType;
  value: string;
  options?: string[];
  required?: boolean;
}

interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  timestamp: string;
  command?: string;
}
```

#### Authentication Architecture

**Current:** Simple username storage in React Context
- No password validation
- No token management
- No session persistence
- No role-based access control

**Planned:** JWT-based authentication
- Access tokens (1 hour expiration)
- Refresh tokens (7 days expiration)
- Role-based permissions (admin, officer, viewer)
- Granular permission system
- HttpOnly cookie storage
- Automatic token refresh

#### Security Considerations

**Planned Security Features:**
- HTTPS-only communication
- Password hashing (bcrypt/Argon2)
- Rate limiting (5 login attempts per 15 minutes)
- CSRF protection
- Token blacklist for logout
- Content Security Policy
- Audit logging

---

## [0.0.0] - 2024-12-16

### Initial Prototype

- Created frontend-only prototype application
- Implemented UI components with shadcn/ui
- Created mock data structures
- Simulated AI chat interface
- Basic case and document management UI
- Drag-and-drop document upload (UI only)

---

## Migration Notes

### From Prototype to Production API

When implementing the real backend API, the following changes will be required:

#### Frontend Changes
1. Replace `src/contexts/AppContext.tsx` state management with React Query calls
2. Update `src/pages/Login.tsx` to call `/api/v1/auth/login`
3. Add authentication token management (localStorage + auto-refresh)
4. Replace all `setTimeout` simulations with actual API calls
5. Update `src/components/workspace/AIChatInterface.tsx` to call AI endpoints
6. Implement proper error handling and loading states
7. Add retry logic for failed requests

#### Backend Implementation Required
1. Set up API server (Node.js/Python/Java based on requirements)
2. Implement authentication endpoints with JWT
3. Create case management CRUD endpoints
4. Implement file upload and storage system
5. Integrate AI services for document processing
6. Set up database for persistent storage
7. Implement search indexing (Elasticsearch/PostgreSQL full-text)
8. Add rate limiting and security middleware
9. Set up logging and monitoring

#### Breaking Changes from Simulation
- Case IDs will come from backend (not generated client-side)
- Document uploads will be real multipart/form-data
- AI operations will be asynchronous (job queue pattern)
- Authentication required for all protected endpoints
- Error responses will follow standard format

---

## Deprecation Policy

When the API is implemented:
- Deprecated endpoints will be marked 6 months before removal
- Breaking changes will always result in a new major version
- All deprecations will be documented in this changelog
- Migration guides will be provided for breaking changes

---

## Versioning Strategy

### API Versioning
- URL path versioning: `/v1/`, `/v2/`, etc.
- Version specified in OpenAPI spec `info.version`
- Each major version supported for minimum 12 months after successor release

### Documentation Versioning
- Documentation version tracks API specification version
- Git tags for each version release
- Documentation archived for previous versions

---

## Related Documentation

- [OpenAPI Specification](/docs/apis/openapi.yaml)
- [Endpoint Reference](/docs/apis/endpoints.md)
- [Authentication Guide](/docs/apis/authentication.md)
- [Architecture Overview](/docs/apis/README.md)

---

## Questions & Support

For questions about the API or to report issues with this documentation:
- Email: api@bamf.example.de
- Internal Wiki: [BAMF Development Portal](https://internal.bamf.example.de)

---

**Changelog Maintained By:** BAMF Development Team
**Last Updated:** 2025-12-16
**Format:** [Keep a Changelog](https://keepachangelog.com/)
