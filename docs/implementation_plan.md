# Implementation Plan - BAMF AI Case Management System

## Overview

This document provides a prioritized, dependency-aware implementation roadmap for the BAMF AI Case Management System. The plan covers Sprint 1 (completed foundation), Sprint 2 (Admin Features - completed), and Sprint 3 (Document Processing Features - Anonymization Service).

---

## Sprint 1 Summary (Completed)

Sprint 1 established the foundational architecture with case-instance scoping. All core requirements are implemented:

| ID | Name | Status | Notes |
|----|------|--------|-------|
| NFR-002 | Modular Backend Architecture | ✅ Complete | FastAPI with services/tools/api layers |
| D-001 | Hierarchical Context Data Schema | ✅ Complete | Case-instance scoped contexts |
| D-002 | Case-Type Form Schemas | ✅ Complete | 7-field form with case-level management |
| D-003 | Sample Document Text Content | ✅ Complete | Text files in case-specific directories |
| F-001 | Document Assistant Agent | ✅ Complete | WebSocket + Gemini streaming |
| F-002 | Document Context Management | ✅ Complete | Cascading context system |
| F-003 | Form Auto-Fill | ✅ Complete | Document extraction with confidence |
| F-004 | AI-Powered Field Generator | ⚠️ Partial | Basic implementation, Sprint 2 enhances |
| F-005 | Case-Level Form Management | ✅ Complete | Forms persist across folders |
| F-006 | Document Loading | ✅ Complete | Text file loading from case directories |
| NFR-001 | Real-Time Performance | ✅ Complete | Streaming with &lt;2s first token |
| NFR-003 | Local Storage | ✅ Complete | localStorage persistence |

---

## Sprint 2 Summary (Completed)

Sprint 2 delivered the Admin Features with NLP interface and SHACL standardization.

| ID | Name | Status | Notes |
|----|------|--------|-------|
| S2-001 | Conversational Field Addition | ✅ Complete | NLP field generation via admin panel |
| S2-002 | Dynamic Structure Definition (SHACL/JSON-LD) | ✅ Complete | SHACL schemas for all fields |
| S2-003 | Legacy Form Standardization | ✅ Complete | All forms migrated to SHACL |
| S2-004 | Multi-Format Contextual Extraction | ✅ Complete | Document processor abstraction ready |

---

## Sprint 3: Document Processing Features - Anonymization Service

### Primary Goal
Implement PII anonymization capabilities by integrating an external anonymization service as an AI agent tool, enabling users to redact sensitive information from identity documents.

### Sprint 3 Requirements Summary

| ID | Name | Priority | Complexity | Dependencies |
|----|------|----------|------------|--------------|
| S3-001 | Anonymization Service Integration | Must-have | Complex | F-001 (WebSocket), S2-004 (Document Processing) |
| S3-002 | Document Viewer Image Support with Download | Must-have | Simple | F-006 (Document Loading) |

---

## Dependency Graph - Sprint 2

```
S2-002 (SHACL Schema Definition)
    │
    ├──▶ S2-001 (Conversational Field Addition)
    │        │
    │        └──▶ AdminConfigPanel AI Fields Tab enhancement
    │
    └──▶ S2-003 (Legacy Form Standardization)
              │
              └──▶ mockData.ts migration

F-002 (Existing Context Management)
    │
    └──▶ S2-004 (Multi-Format Contextual Extraction)
              │
              ├──▶ PDF Support (stub for future)
              │
              └──▶ Enhanced cascading context
```

---

## Code-Graph Component Impact - Sprint 2

| Component | Affected by Requirements |
|-----------|-------------------------|
| `src/types/case.ts` | S2-002, S2-003 |
| `src/data/mockData.ts` | S2-003 |
| `src/components/workspace/AdminConfigPanel.tsx` | S2-001 |
| `src/components/workspace/FormViewer.tsx` | S2-003 |
| `backend/services/field_generator.py` (new) | S2-001, S2-002 |
| `backend/api/admin.py` (new) | S2-001 |
| `backend/schemas/shacl.py` (new) | S2-002 |
| `backend/services/context_manager.py` | S2-004 |
| `backend/tools/document_processor.py` (new) | S2-004 |

---

## Phase 1: SHACL Foundation (Independent)

**Goal:** Establish SHACL/JSON-LD schema standard that all other requirements depend on.

**Can be done in parallel:** No - this is foundational for S2-001 and S2-003.

### 1.1 S2-002: Dynamic Structure Definition (SHACL & JSON-LD)

**Priority:** Must-have (foundation for NLP field generation)
**Dependencies:** None
**Complexity:** Moderate

**Files to Create (backend):**
- `backend/schemas/__init__.py` - Schema package
- `backend/schemas/shacl.py` - SHACL property and node shape definitions
- `backend/schemas/jsonld_context.py` - JSON-LD context definitions

**Files to Create (frontend):**
- `src/types/shacl.ts` - TypeScript interfaces for SHACL metadata

**Files to Modify (frontend):**
- `src/types/case.ts` - Extend FormField with SHACL metadata property

**SHACL Schema Structure:**
```json
{
  "@context": {
    "sh": "http://www.w3.org/ns/shacl#",
    "schema": "http://schema.org/",
    "xsd": "http://www.w3.org/2001/XMLSchema#"
  },
  "@type": "sh:PropertyShape",
  "sh:path": "schema:givenName",
  "sh:datatype": "xsd:string",
  "sh:minCount": 1,
  "sh:maxCount": 1,
  "sh:name": "Full Name",
  "sh:description": "The applicant's full legal name"
}
```

**Rationale:** SHACL provides semantic meaning to form fields, enabling better AI understanding during extraction and allowing validation of field constraints. JSON-LD representation ensures interoperability.

**Scope:**
- Backend: Python schema definitions only
- Frontend: TypeScript types only

---

## Phase 2: NLP Interface (Depends on Phase 1)

**Goal:** Implement natural language form field generation with SHACL output.

**Dependencies:** Phase 1 must be complete.

### 2.1 S2-001: Conversational Field Addition

**Priority:** Must-have (core admin feature)
**Dependencies:** S2-002 (SHACL schema)
**Complexity:** Complex

**Files to Create (backend):**
- `backend/services/field_generator.py` - NLP to SHACL field generation service
- `backend/api/admin.py` - Admin REST API endpoints

**Files to Create (frontend):**
- `src/lib/adminApi.ts` - API client for admin endpoints

**Files to Modify (frontend):**
- `src/components/workspace/AdminConfigPanel.tsx` - Enhance AI Fields tab

**Key Features:**
1. Natural language input textarea (existing from F-004)
2. Parse commands like "I need a choice, a drop-down, a list and add these options"
3. Generate SHACL-compliant FormField specification
4. Preview generated field with editable properties
5. Add to form with SHACL metadata

**API Endpoint:**
```
POST /api/admin/generate-field
Request: { "prompt": "Add a dropdown for marital status with options single, married, divorced" }
Response: {
  "field": {
    "id": "marital_status",
    "label": "Marital Status",
    "type": "select",
    "options": ["Single", "Married", "Divorced"],
    "required": false,
    "shaclMetadata": {
      "@context": {...},
      "@type": "sh:PropertyShape",
      "sh:path": "schema:maritalStatus",
      ...
    }
  }
}
```

**Rationale:** Administrators can create form fields using natural language instead of manual configuration. The AI interprets intent and generates semantically-rich SHACL specifications.

**Scope:**
- Backend: Field generator service + admin API
- Frontend: Enhanced admin panel tab + API client

---

## Phase 3: Migration (Depends on Phase 1)

**Goal:** Migrate existing form schemas to SHACL/JSON-LD standard.

**Dependencies:** Phase 1 must be complete.

### 3.1 S2-003: Legacy Form Standardization

**Priority:** Must-have (ensures unified schema)
**Dependencies:** S2-002 (SHACL schema)
**Complexity:** Simple

**Files to Create (backend):**
- `backend/scripts/migrate_forms_to_shacl.py` - One-time migration script

**Files to Modify (frontend):**
- `src/data/mockData.ts` - Add SHACL metadata to all 7 existing form fields
- `src/components/workspace/FormViewer.tsx` - Handle SHACL-enhanced fields (display metadata in admin mode)

**Migration Mapping:**

| Current Field | SHACL Property | Schema.org Type |
|---------------|----------------|-----------------|
| fullName | sh:path schema:name | xsd:string |
| birthDate | sh:path schema:birthDate | xsd:date |
| countryOfOrigin | sh:path schema:nationality | xsd:string |
| existingLanguageCertificates | sh:path schema:knows | xsd:string |
| coursePreference | sh:path schema:courseCode | xsd:string |
| currentAddress | sh:path schema:address | xsd:string |
| reasonForApplication | sh:path schema:description | xsd:string |

**Rationale:** All existing forms must follow the same SHACL/JSON-LD definitions as newly created fields, ensuring a unified schema across the system.

**Scope:**
- Backend: Migration script (one-time)
- Frontend: Data file + form viewer updates

---

## Phase 4: Enhanced Context (Can parallel with Phase 2-3)

**Goal:** Improve contextual extraction with better cascading and future PDF support.

**Dependencies:** F-002 (existing context management)

### 4.1 S2-004: Multi-Format Contextual Extraction

**Priority:** Should-have (improves AI accuracy)
**Dependencies:** F-002 (context management)
**Complexity:** Moderate

**Files to Create (backend):**
- `backend/tools/document_processor.py` - Document processing abstraction
- `backend/tools/text_processor.py` - Text file processor (current functionality)
- `backend/tools/pdf_processor.py` - PDF processor (stub for future)

**Files to Modify (backend):**
- `backend/services/context_manager.py` - Enhanced cascading logic
- `backend/services/gemini_service.py` - Better context injection

**Files to Modify (frontend):**
- `src/components/workspace/AIChatInterface.tsx` - Context source indicators

**Cascading Context Precedence:**
```
Document Context (highest priority)
    ↓ overrides
Folder Context
    ↓ overrides
Case Context (lowest priority)
```

**Document Processor Interface:**
```python
class DocumentProcessor(ABC):
    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """Extract text content from document."""
        pass

    @abstractmethod
    def get_metadata(self, file_path: str) -> dict:
        """Extract document metadata."""
        pass

    @abstractmethod
    def supports_format(self, file_extension: str) -> bool:
        """Check if processor supports file format."""
        pass
```

**Rationale:** The cascading context ensures AI responses are contextually accurate. The document processor abstraction prepares for future PDF support without major refactoring.

**Scope:**
- Backend: Document processor interface + enhanced context manager
- Frontend: Context indicators in chat

---

## Implementation Order Summary

```
Phase 1: SHACL Foundation (Required First)
├── S2-002: SHACL/JSON-LD Schema Definitions
│   ├── backend/schemas/shacl.py
│   ├── backend/schemas/jsonld_context.py
│   ├── src/types/shacl.ts
│   └── src/types/case.ts (extend FormField)

Phase 2: NLP Interface (After Phase 1)
├── S2-001: Conversational Field Addition
│   ├── backend/services/field_generator.py
│   ├── backend/api/admin.py
│   ├── src/lib/adminApi.ts
│   └── src/components/workspace/AdminConfigPanel.tsx

Phase 3: Migration (After Phase 1, parallel with Phase 2)
├── S2-003: Legacy Form Standardization
│   ├── backend/scripts/migrate_forms_to_shacl.py
│   ├── src/data/mockData.ts
│   └── src/components/workspace/FormViewer.tsx

Phase 4: Enhanced Context (Parallel with Phase 2-3)
└── S2-004: Multi-Format Contextual Extraction
    ├── backend/tools/document_processor.py
    ├── backend/tools/text_processor.py
    ├── backend/tools/pdf_processor.py (stub)
    ├── backend/services/context_manager.py
    └── src/components/workspace/AIChatInterface.tsx
```

---

## File Change Summary - Sprint 2

| Requirement | New Files | Modified Files |
|-------------|-----------|----------------|
| S2-002 | 4 (schemas, types) | 1 (case.ts) |
| S2-001 | 3 (field_generator, admin.py, adminApi.ts) | 1 (AdminConfigPanel) |
| S2-003 | 1 (migration script) | 2 (mockData, FormViewer) |
| S2-004 | 3 (document processors) | 2 (context_manager, AIChatInterface) |
| **Total** | **11 new files** | **6 file modifications** |

---

## Risk Mitigation

### High-Risk Items

1. **S2-002 (SHACL Schema)** - Complex standard
   - Mitigation: Start with minimal required properties
   - Fallback: Simplified JSON-LD without full SHACL validation

2. **S2-001 (NLP Field Generation)** - AI interpretation accuracy
   - Mitigation: Provide preview/edit before adding
   - Fallback: Manual field creation remains available

### Medium-Risk Items

3. **S2-003 (Migration)** - Backward compatibility
   - Mitigation: SHACL metadata is optional property, existing forms work without it
   - Fallback: Gradual migration, not all-at-once

4. **S2-004 (PDF Support)** - External library dependency
   - Mitigation: Create interface now, implement later
   - Fallback: Text-only extraction remains default

---

## Success Criteria - Sprint 2 ✅ COMPLETED

Sprint 2 is complete - all criteria met:

1. ✅ Admin can generate form fields via natural language in AI Fields tab
2. ✅ Generated fields include SHACL/JSON-LD semantic metadata
3. ✅ All 7 existing form fields have SHACL metadata
4. ✅ Context cascading properly prioritizes Document > Folder > Case
5. ✅ Field generation endpoint POST /api/admin/generate-field works
6. ✅ FormViewer displays SHACL metadata in admin mode
7. ✅ Document processor interface ready for PDF support (stub)
8. ✅ Natural language commands like "add a dropdown for X" are correctly interpreted

---

## Sprint 3: Anonymization Service - Detailed Implementation

### Dependency Graph - Sprint 3

```
F-001 (WebSocket Chat Service)
    │
    └──▶ S3-001 (Anonymization Service Integration)
              │
              ├──▶ Backend: anonymization_service.py (API client)
              │
              ├──▶ Backend: anonymization_tool.py (AI agent tool)
              │
              ├──▶ Backend: Gemini service tool registration
              │
              └──▶ Frontend: DocumentViewer + AppContext updates

S2-004 (Document Processing Abstraction)
    │
    └──▶ S3-001 (Uses processor pattern for image handling)
```

### Code-Graph Component Impact - Sprint 3

| Component | Affected by Requirements |
|-----------|-------------------------|
| `backend/services/anonymization_service.py` (new) | S3-001 |
| `backend/tools/anonymization_tool.py` (new) | S3-001 |
| `backend/services/gemini_service.py` | S3-001 |
| `backend/api/chat.py` | S3-001 |
| `src/components/workspace/DocumentViewer.tsx` | S3-001, S3-002 |
| `src/components/workspace/AIChatInterface.tsx` | S3-001 |
| `src/contexts/AppContext.tsx` | S3-001 |
| `src/types/websocket.ts` | S3-001 |

---

## Phase 5: Anonymization Service (Sprint 3)

**Goal:** Enable PII detection and masking for identity documents.

### 5.1 S3-001: Anonymization Service Integration

**Priority:** Must-have (core document processing feature)
**Dependencies:** F-001 (WebSocket), S2-004 (Document Processing)
**Complexity:** Complex

**Files to Create (backend):**
- `backend/services/anonymization_service.py` - External API client
- `backend/tools/anonymization_tool.py` - AI agent tool wrapper

**Files to Modify (backend):**
- `backend/services/gemini_service.py` - Register anonymization tool
- `backend/api/chat.py` - Handle anonymization messages

**Files to Modify (frontend):**
- `src/components/workspace/DocumentViewer.tsx` - Wire up Anonymize button
- `src/components/workspace/AIChatInterface.tsx` - Handle anonymization responses
- `src/contexts/AppContext.tsx` - Auto-select anonymized document
- `src/types/websocket.ts` - Add anonymization message types

**Key Implementation Steps:**

1. **Backend Service Layer**
   ```python
   # backend/services/anonymization_service.py
   class AnonymizationService:
       API_URL = "http://localhost:5000/ai-analysis"
       SECRET_KEY = "2b5e151428aed2a6aff7158846cf4f2c"

       async def anonymize_image(self, base64_image: str) -> AnonymizationResult:
           """Send image to external service, receive anonymized version."""
           pass
   ```

2. **Backend Tool Layer**
   ```python
   # backend/tools/anonymization_tool.py
   def anonymize_document(file_path: str) -> AnonymizationResult:
       """
       1. Read image file and convert to base64
       2. Call AnonymizationService
       3. Save result as {filename}_anonymized.{ext}
       4. Return result with new file path
       """
       pass
   ```

3. **Frontend Integration**
   - DocumentViewer: On Anonymize click → send WebSocket message
   - AIChatInterface: Handle `anonymization_complete` → notify user
   - AppContext: After completion → `setSelectedDocument(anonymizedDoc)`

**Message Flow:**
```
User clicks Anonymize → Frontend sends WebSocket message
    → Backend receives → Calls anonymization_tool
    → Tool calls AnonymizationService → External API
    → API returns anonymized base64 → Tool saves file
    → Backend sends anonymization_complete message
    → Frontend receives → Updates document tree, selects new file
```

**Rationale:** The anonymization feature is critical for handling sensitive identity documents in compliance workflows. Using an external service keeps the trained model isolated and secure.

**Scope:**
- Backend: Service client + tool wrapper + message handling
- Frontend: Button wiring + response handling + document selection

---

### 5.2 S3-002: Document Viewer Image Support with Download

**Priority:** Must-have (essential for viewing and downloading anonymization results)
**Dependencies:** F-006 (Document Loading)
**Complexity:** Simple

**Files to Modify (frontend):**
- `src/components/workspace/DocumentViewer.tsx` - Add image rendering and download

**Key Implementation Steps:**

1. **Detect Image Files**
   ```tsx
   const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'];
   const isImage = imageExtensions.includes(selectedDocument.type.toLowerCase());
   ```

2. **Construct Image Path**
   ```tsx
   const imagePath = `/documents/${currentCase.id}/${selectedDocument.folderId}/${selectedDocument.name}`;
   ```

3. **Render Image**
   - Add `<img>` element with proper styling
   - Include error handling for failed loads
   - Add loading state indicator
   - Ensure responsive scaling within viewer panel

4. **Implement Download Handler**
   - Add `handleDownloadImage()` function
   - Use fetch + blob approach for reliable downloads
   - Preserve original filename in download
   - Show success/error toast notifications

**Component Update:**
```tsx
// In DocumentViewer.tsx - Add to document preview section
{isImage ? (
  <div className="flex items-center justify-center h-full p-4">
    <img
      src={imagePath}
      alt={selectedDocument.name}
      className="max-w-full max-h-full object-contain rounded-lg shadow-md"
      onError={(e) => {
        e.currentTarget.src = ''; // Clear broken image
        // Show error state
      }}
    />
  </div>
) : selectedDocument.type === 'txt' ? (
  // Existing text rendering...
) : (
  // Existing placeholder...
)}
```

**Download Handler:**
```tsx
const handleDownloadImage = async () => {
  try {
    const response = await fetch(imagePath);
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = selectedDocument.name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    toast({ title: 'Download started' });
  } catch (error) {
    toast({ title: 'Download failed', variant: 'destructive' });
  }
};
```

**Rationale:** Image viewing and downloading is essential for case workers to inspect identity documents, verify anonymization results, and save anonymized versions for further processing or archival.

**Scope:**
- Frontend: DocumentViewer component update only

---

## Implementation Order Summary - Sprint 3

```
Phase 5: Anonymization Service & Image Viewer
├── S3-002: Document Viewer Image Support with Download (can be done first or in parallel)
│   ├── Step 1: src/components/workspace/DocumentViewer.tsx (image rendering)
│   └── Step 2: src/components/workspace/DocumentViewer.tsx (download handler)
│
└── S3-001: Anonymization Service Integration
    ├── Step 1: backend/services/anonymization_service.py (API client)
    ├── Step 2: backend/tools/anonymization_tool.py (AI agent tool)
    ├── Step 3: backend/services/gemini_service.py (register tool)
    ├── Step 4: backend/api/chat.py (message handling)
    ├── Step 5: src/types/websocket.ts (message types)
    ├── Step 6: src/components/workspace/DocumentViewer.tsx (button)
    ├── Step 7: src/components/workspace/AIChatInterface.tsx (response)
    └── Step 8: src/contexts/AppContext.tsx (auto-select)
```

---

## File Change Summary - Sprint 3

| Requirement | New Files | Modified Files |
|-------------|-----------|----------------|
| S3-001 | 2 (anonymization_service.py, anonymization_tool.py) | 6 (gemini_service, chat.py, DocumentViewer, AIChatInterface, AppContext, websocket.ts) |
| S3-002 | 0 | 1 (DocumentViewer.tsx) |
| **Total** | **2 new files** | **7 file modifications** |

---

## Risk Mitigation - Sprint 3

### High-Risk Items

1. **External Service Dependency** - Service availability
   - Mitigation: Implement timeout and retry logic
   - Fallback: Clear error message if service unavailable

2. **Large Image Processing** - Memory/bandwidth concerns
   - Mitigation: Validate image size before processing
   - Fallback: Compress large images before sending

### Medium-Risk Items

3. **File Path Management** - Correct directory for saved files
   - Mitigation: Use original file path as reference
   - Fallback: Save to case's documents root folder

4. **Base64 Encoding** - Correct format with data URI prefix
   - Mitigation: Validate format before API call
   - Fallback: Auto-add prefix if missing

---

## Success Criteria - Sprint 3

Sprint 3 is complete when:

**S3-001: Anonymization Service Integration**
1. ☐ Anonymize button in DocumentViewer triggers actual anonymization
2. ☐ External anonymization service is called with correct base64 format
3. ☐ Anonymized image is saved with `_anonymized` suffix in same directory
4. ☐ UI automatically switches to display newly created anonymized document
5. ☐ Agent can be instructed via chat to anonymize current document
6. ☐ Original document remains unchanged after anonymization
7. ☐ Error handling works when service is unavailable
8. ☐ All 10 test cases pass

**S3-002: Document Viewer Image Support with Download**
9. ☐ Image files (JPG, PNG, GIF, WEBP, BMP) display directly in DocumentViewer
10. ☐ Images scale responsively while maintaining aspect ratio
11. ☐ Error handling displays graceful message for failed image loads
12. ☐ Switching between image and text documents works correctly
13. ☐ Anonymized images display correctly after anonymization completes
14. ☐ Download button triggers file download with correct filename
15. ☐ Downloaded anonymized images preserve `_anonymized` suffix
16. ☐ Download error handling shows appropriate toast message
17. ☐ All 10 test cases pass

---

## Next Steps

To implement Sprint 3:

**S3-002 (Recommended to start first - simpler):**
1. Use `/start-requirement S3-002` to get detailed task breakdown
2. Update DocumentViewer.tsx to render image files
3. Test with existing image files in case folders
4. Create test files in `docs/tests/S3-002/` directory

**S3-001 (After S3-002 is complete):**
1. Start with backend service layer - `anonymization_service.py`
2. Use `/start-requirement S3-001` to get detailed task breakdown
3. Ensure external anonymization service is running at localhost:5000
4. Run tests after each component completion
5. Create test files in `docs/tests/S3-001/` directory

---

## Sprint 4: File Management Features

### Primary Goal
Implement functional file upload and deletion capabilities, enabling case workers to add new documents to cases via drag-and-drop and remove unnecessary uploads.

### Sprint 4 Requirements Summary

| ID | Name | Priority | Complexity | Dependencies |
|----|------|----------|------------|--------------|
| S4-001 | Drag-and-Drop File Upload | Must-have | Moderate | F-006 (Document Loading) |
| S4-002 | File Deletion | Must-have | Simple | S4-001 (Uploads folder) |

---

## Dependency Graph - Sprint 4

```
F-006 (Document Loading - Existing)
    │
    └──▶ S4-001 (Drag-and-Drop File Upload)
              │
              ├──▶ Backend: files.py API endpoints
              │
              ├──▶ Backend: file_service.py (upload/validation)
              │
              ├──▶ Frontend: FileDropZone.tsx (drop handling)
              │
              └──▶ S4-002 (File Deletion)
                        │
                        ├──▶ Backend: DELETE endpoint
                        │
                        ├──▶ Frontend: Delete button + confirmation
                        │
                        └──▶ Frontend: Document tree update
```

### Code-Graph Component Impact - Sprint 4

| Component | Affected by Requirements |
|-----------|-------------------------|
| `backend/api/files.py` (new) | S4-001, S4-002 |
| `backend/services/file_service.py` (new) | S4-001, S4-002 |
| `src/components/workspace/FileDropZone.tsx` (new) | S4-001 |
| `src/components/workspace/DocumentViewer.tsx` | S4-001 |
| `src/components/workspace/CaseTreeExplorer.tsx` | S4-002 |
| `src/components/ui/DeleteConfirmDialog.tsx` (new) | S4-002 |
| `src/components/ui/UploadProgress.tsx` (new) | S4-001 |
| `src/lib/fileApi.ts` (new) | S4-001, S4-002 |
| `src/types/file.ts` (new) | S4-001, S4-002 |
| `src/contexts/AppContext.tsx` | S4-001, S4-002 |
| `src/data/mockData.ts` | S4-001 |

---

## Phase 6: File Upload (Sprint 4)

### 6.1 S4-001: Drag-and-Drop File Upload

**Priority:** Must-have (core file management feature)
**Dependencies:** F-006 (Document Loading)
**Complexity:** Moderate

**Files to Create (backend):**
- `backend/api/files.py` - File upload/delete endpoints
- `backend/services/file_service.py` - File management service

**Files to Create (frontend):**
- `src/components/workspace/FileDropZone.tsx` - Drag-and-drop component
- `src/components/ui/UploadProgress.tsx` - Upload progress indicator
- `src/lib/fileApi.ts` - API client for file operations
- `src/types/file.ts` - File-related types

**Files to Modify (frontend):**
- `src/components/workspace/DocumentViewer.tsx` - Integrate drop zone
- `src/data/mockData.ts` - Add uploads folder to case structure
- `src/contexts/AppContext.tsx` - Add document refresh method

**Key Implementation Steps:**

1. **Backend File API**
   ```python
   # backend/api/files.py
   @router.post("/api/files/upload")
   async def upload_file(file: UploadFile, case_id: str, folder_id: str = "uploads"):
       # Validate size (15 MB max)
       # Save to public/documents/{case_id}/{folder_id}/
       pass
   ```

2. **Frontend Drop Zone**
   - Handle drag events (enter, over, leave, drop)
   - Validate file size before upload
   - Show progress during upload
   - Update document tree on completion

3. **Visual States**
   - Idle: Normal appearance
   - Drag-over: Highlighted border, "Drop files here" message
   - Uploading: Progress bar with percentage
   - Success/Error: Toast notifications

**Scope:**
- Backend: File API endpoints + service layer
- Frontend: Drop zone component + progress UI + API client

---

### 6.2 S4-002: File Deletion

**Priority:** Must-have (completes file management)
**Dependencies:** S4-001 (Uploads folder must exist)
**Complexity:** Simple

**Files to Create (frontend):**
- `src/components/ui/DeleteConfirmDialog.tsx` - Confirmation modal

**Files to Modify (backend):**
- `backend/api/files.py` - Add DELETE endpoint

**Files to Modify (frontend):**
- `src/components/workspace/CaseTreeExplorer.tsx` - Add delete button
- `src/lib/fileApi.ts` - Add deleteFile function
- `src/contexts/AppContext.tsx` - Add removeDocumentFromFolder method

**Key Implementation Steps:**

1. **Delete Button UI**
   - Show trash icon on hover for files in uploads folder
   - Red color to indicate destructive action
   - Only visible in uploads folder (not system folders)

2. **Confirmation Dialog**
   - Modal with clear warning message
   - Cancel and Delete buttons
   - Prevent accidental deletion

3. **Backend Security**
   - Validate file path is within case directory
   - Prevent path traversal attacks
   - Return appropriate error codes

**Scope:**
- Backend: DELETE endpoint with security validation
- Frontend: Delete button + confirmation dialog + tree update

---

## Implementation Order Summary - Sprint 4

```
Phase 6: File Management
├── S4-001: Drag-and-Drop File Upload (start first)
│   ├── Step 1: backend/api/files.py (POST endpoint)
│   ├── Step 2: backend/services/file_service.py (validation/save)
│   ├── Step 3: src/types/file.ts (TypeScript types)
│   ├── Step 4: src/lib/fileApi.ts (API client)
│   ├── Step 5: src/components/workspace/FileDropZone.tsx (drop handling)
│   ├── Step 6: src/components/ui/UploadProgress.tsx (progress bar)
│   ├── Step 7: src/components/workspace/DocumentViewer.tsx (integrate)
│   └── Step 8: src/data/mockData.ts (uploads folder)
│
└── S4-002: File Deletion (after S4-001)
    ├── Step 1: backend/api/files.py (DELETE endpoint)
    ├── Step 2: src/lib/fileApi.ts (deleteFile function)
    ├── Step 3: src/components/ui/DeleteConfirmDialog.tsx (confirmation)
    ├── Step 4: src/components/workspace/CaseTreeExplorer.tsx (delete button)
    └── Step 5: src/contexts/AppContext.tsx (removeDocumentFromFolder)
```

---

## File Change Summary - Sprint 4

| Requirement | New Files | Modified Files |
|-------------|-----------|----------------|
| S4-001 | 5 (files.py, file_service.py, FileDropZone, UploadProgress, file.ts, fileApi.ts) | 3 (DocumentViewer, mockData, AppContext) |
| S4-002 | 1 (DeleteConfirmDialog.tsx) | 3 (files.py, CaseTreeExplorer, AppContext) |
| **Total** | **6 new files** | **6 file modifications** |

---

## Risk Mitigation - Sprint 4

### High-Risk Items

1. **File Size Validation** - Large uploads can crash server
   - Mitigation: Validate size on both frontend and backend
   - Fallback: Streaming upload with chunking for large files

2. **Security - Path Traversal** - Malicious filenames
   - Mitigation: Sanitize filenames, validate paths
   - Fallback: Use UUID-based storage names

### Medium-Risk Items

3. **Upload Progress Tracking** - May not work with simple POST
   - Mitigation: Use XMLHttpRequest with progress events
   - Fallback: Show indeterminate progress spinner

4. **Concurrent Uploads** - Multiple files at once
   - Mitigation: Queue uploads, process sequentially
   - Fallback: Allow only single file upload

---

## Success Criteria - Sprint 4

Sprint 4 is complete when:

**S4-001: Drag-and-Drop File Upload**
1. ☐ Drag file onto document viewer shows drop zone indicator
2. ☐ Drop file under 15 MB uploads successfully
3. ☐ Drop file over 15 MB shows size limit error
4. ☐ Upload progress bar shows percentage
5. ☐ Success toast shown on upload completion
6. ☐ Uploaded file appears in "uploads" folder in tree
7. ☐ Multiple files can be uploaded sequentially
8. ☐ All 10 test cases pass

**S4-002: File Deletion**
9. ☐ Delete button visible on hover for uploads folder files
10. ☐ Confirmation dialog appears before deletion
11. ☐ File removed from filesystem on confirm
12. ☐ File removed from document tree immediately
13. ☐ Cancel button prevents deletion
14. ☐ Path traversal attacks rejected
15. ☐ All 10 test cases pass

---

## Next Steps

To implement Sprint 4:

**S4-001 (Start first - upload before delete):**
1. Use `/start-requirement S4-001` to get detailed task breakdown
2. Create backend file API endpoints
3. Create frontend drop zone component
4. Test with various file sizes

**S4-002 (After S4-001 is complete):**
1. Use `/start-requirement S4-002` to get detailed task breakdown
2. Add DELETE endpoint to backend
3. Create confirmation dialog
4. Add delete button to tree explorer

---

*Last Updated*: 2025-12-24
*Version*: 4.0 (Sprint 4 - File Management Features)
*Sprint*: Sprint 4 - File Management Features (Upload & Deletion)
