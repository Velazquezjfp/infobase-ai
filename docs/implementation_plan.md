# Implementation Plan - BAMF AI Case Management System

## Overview

This document provides a prioritized, dependency-aware implementation roadmap for the BAMF AI Case Management System. The plan covers Sprint 1 (completed foundation) and Sprint 2 (Admin Features - NLP interface and SHACL standardization).

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

## Sprint 2: Admin Features - NLP Interface & Schema Standardization

### Primary Goal
Transition from manual form-field coding to a Natural Language Processing (NLP) interface while standardizing the underlying data schema using SHACL/JSON-LD.

### Sprint 2 Requirements Summary

| ID | Name | Priority | Complexity | Dependencies |
|----|------|----------|------------|--------------|
| S2-001 | Conversational Field Addition | Must-have | Complex | F-004 (partial) |
| S2-002 | Dynamic Structure Definition (SHACL/JSON-LD) | Must-have | Moderate | None |
| S2-003 | Legacy Form Standardization | Must-have | Simple | S2-002 |
| S2-004 | Multi-Format Contextual Extraction | Should-have | Moderate | F-002 |

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

## Success Criteria - Sprint 2

Sprint 2 is complete when:

1. ✅ Admin can generate form fields via natural language in AI Fields tab
2. ✅ Generated fields include SHACL/JSON-LD semantic metadata
3. ✅ All 7 existing form fields have SHACL metadata
4. ✅ Context cascading properly prioritizes Document > Folder > Case
5. ✅ Field generation endpoint POST /api/admin/generate-field works
6. ✅ FormViewer displays SHACL metadata in admin mode
7. ✅ Document processor interface ready for PDF support (stub)
8. ✅ Natural language commands like "add a dropdown for X" are correctly interpreted

---

## Next Steps

After completing this plan:

1. Start with Phase 1 (S2-002) - SHACL schema definitions
2. Use `/start-requirement S2-002` to get detailed task breakdown
3. Run tests after each requirement completion
4. Update test-matrix.md with Sprint 2 test cases
5. Create test files in `docs/tests/S2-XXX/` directories

---

*Last Updated*: 2025-12-22
*Version*: 2.0 (Sprint 2 - Admin Features)
*Sprint*: Sprint 2 - Admin Features (NLP Interface & SHACL Standardization)
