# Sprint 1 Implementation Plan

## Overview

This document provides a prioritized, dependency-aware implementation roadmap for Sprint 1 of the BAMF AI Case Management System. The plan is organized into phases based on dependencies between requirements and code components.

## Case-Instance Scoping Architecture

All content in this system is scoped to specific case instances (ACTEs). When switching cases, **everything switches**:

| Component | Scoping | Path Pattern |
|-----------|---------|--------------|
| **Context** | Per case instance | `backend/data/contexts/cases/{caseId}/` |
| **Documents** | Per case instance | `public/documents/{caseId}/{folderId}/` |
| **Forms** | Per case instance | `sampleCaseFormData[caseId]` |
| **Folders** | Per case instance | Defined in case's folder structure |

### Key Principles:

1. **Complete Isolation**: ACTE-2024-001's content is never mixed with ACTE-2024-002
2. **Dynamic Creation**: New cases get their own directories from templates
3. **Modular Demo**: German Integration Course (ACTE-2024-001) is the main demo case
4. **Template System**: Templates enable creating new cases of each type

### Directory Structure:
```
backend/data/contexts/
├── cases/
│   ├── ACTE-2024-001/    # German Integration Course
│   ├── ACTE-2024-002/    # Asylum Application
│   └── ACTE-2024-003/    # Family Reunification
└── templates/
    ├── integration_course/
    ├── asylum_application/
    └── family_reunification/

public/documents/
├── ACTE-2024-001/
│   ├── personal-data/
│   ├── certificates/
│   └── ...
├── ACTE-2024-002/
└── templates/
```

## Requirements Summary

| ID | Name | Category | Complexity |
|----|------|----------|------------|
| NFR-002 | Modular Backend Architecture | Non-Functional | Moderate |
| D-001 | Hierarchical Context Data Schema | Data | Simple |
| D-002 | Case-Type Form Schemas | Data | Simple |
| D-003 | Sample Document Text Content | Data | Simple |
| F-001 | Document Assistant Agent - WebSocket | Functional | Complex |
| F-002 | Document Context Management System | Functional | Moderate |
| F-003 | Form Auto-Fill from Documents | Functional | Complex |
| F-004 | AI-Powered Form Field Generator | Functional | Complex |
| F-005 | Case-Level Form Management | Functional | Moderate |
| F-006 | Replace Mock Documents with Text Files | Functional | Simple |
| NFR-001 | Real-Time AI Response Performance | Non-Functional | Moderate |
| NFR-003 | Local Storage Without Database | Non-Functional | Simple |

## Dependency Graph

```
NFR-002 (Backend Structure)
    │
    ├──▶ F-001 (WebSocket Service)
    │        │
    │        ├──▶ NFR-001 (Performance)
    │        │
    │        └──▶ F-003 (Form Auto-Fill)
    │                 │
    │                 └──▶ F-004 (AI Field Generator)
    │
D-001 (Context Schema)
    │
    └──▶ F-002 (Context Management)
              │
              └──▶ F-003 (Form Auto-Fill)

D-002 (Form Schemas)
    │
    └──▶ F-005 (Case-Level Forms)
              │
              └──▶ F-003 (Form Auto-Fill)

D-003 (Sample Documents)
    │
    └──▶ F-006 (Document Loading)
              │
              └──▶ F-003 (Form Auto-Fill)

NFR-003 (LocalStorage)
    │
    └──▶ F-004 (AI Field Generator)
```

## Code-Graph Component Impact

| Component | Affected by Requirements |
|-----------|-------------------------|
| `src/contexts/AppContext.tsx` | F-001, F-003, F-004, F-005, NFR-003 |
| `src/components/workspace/AIChatInterface.tsx` | F-001, F-003, NFR-001 |
| `src/components/workspace/FormViewer.tsx` | F-005 |
| `src/components/workspace/AdminConfigPanel.tsx` | F-004, F-005 |
| `src/components/workspace/DocumentViewer.tsx` | F-006 |
| `src/components/workspace/CaseTreeExplorer.tsx` | F-006 |
| `src/types/case.ts` | F-004, F-005 |
| `src/data/mockData.ts` | D-002, F-005, F-006 |
| `backend/` (new) | NFR-002, F-001, F-002, F-003, F-004 |

---

## Phase 1: Foundation (Independent Requirements)

**Goal:** Establish backend structure and create all data files that have no dependencies.

**Can be done in parallel:** Yes - all items in this phase are independent.

### 1.1 NFR-002: Modular Backend Architecture

**Priority:** Must-have (foundation for all AI features)
**Dependencies:** None
**Complexity:** Moderate

**Files to Create (backend only):**
- `backend/main.py` - FastAPI entry point
- `backend/requirements.txt` - Python dependencies
- `backend/api/__init__.py` - API package
- `backend/services/__init__.py` - Services package
- `backend/tools/__init__.py` - Tools package
- `backend/data/contexts/__init__.py` - Data package
- `backend/tests/__init__.py` - Tests package

**Rationale:** Backend structure must exist before any AI services can be implemented. This is the foundational requirement.

**Scope:** Backend directory structure only. No frontend changes.

---

### 1.2 D-001: Hierarchical Context Data Schema (Case-Instance Scoped)

**Priority:** Must-have (provides domain knowledge for AI)
**Dependencies:** None
**Complexity:** Simple

**Directory Structure:**
```
backend/data/contexts/
├── cases/
│   └── ACTE-2024-001/           # German Integration Course case
│       ├── case.json            # Case-level context
│       └── folders/
│           ├── personal-data.json
│           ├── certificates.json
│           ├── integration-docs.json
│           ├── applications.json
│           ├── emails.json
│           └── evidence.json
└── templates/                    # Templates for new case creation
    └── integration_course/
        ├── case.json
        └── folders/
```

**Files to Create:**
- `backend/data/contexts/cases/ACTE-2024-001/case.json`
- `backend/data/contexts/cases/ACTE-2024-001/folders/personal-data.json`
- `backend/data/contexts/cases/ACTE-2024-001/folders/certificates.json`
- `backend/data/contexts/cases/ACTE-2024-001/folders/integration-docs.json`
- `backend/data/contexts/cases/ACTE-2024-001/folders/applications.json`
- `backend/data/contexts/cases/ACTE-2024-001/folders/emails.json`
- `backend/data/contexts/cases/ACTE-2024-001/folders/evidence.json`
- `backend/data/contexts/templates/integration_course/` (template copy)

**Rationale:** Context is case-instance scoped - each ACTE has its own context directory. When switching cases, all context switches. New cases can be created from templates.

**Scope:** JSON data files with case-instance directory structure.

---

### 1.3 D-003: Sample Document Text Content (Case-Instance Scoped)

**Priority:** Must-have (required for testing AI features)
**Dependencies:** None
**Complexity:** Simple

**Directory Structure:**
```
public/documents/
├── ACTE-2024-001/                    # German Integration Course case
│   ├── personal-data/
│   │   ├── Birth_Certificate.txt
│   │   └── Passport_Scan.txt
│   ├── certificates/
│   │   └── Language_Certificate_A1.txt
│   ├── integration-docs/
│   ├── applications/
│   │   └── Integration_Application.txt
│   ├── emails/
│   │   └── Confirmation_Email.txt
│   └── evidence/
│       └── School_Transcripts.txt
└── templates/                        # Templates for new case creation
    └── integration_course/
```

**Files to Create for ACTE-2024-001:**
- `public/documents/ACTE-2024-001/personal-data/Birth_Certificate.txt`
- `public/documents/ACTE-2024-001/personal-data/Passport_Scan.txt`
- `public/documents/ACTE-2024-001/certificates/Language_Certificate_A1.txt`
- `public/documents/ACTE-2024-001/applications/Integration_Application.txt`
- `public/documents/ACTE-2024-001/emails/Confirmation_Email.txt`
- `public/documents/ACTE-2024-001/evidence/School_Transcripts.txt`

**Rationale:** Documents are case-instance scoped - each ACTE has its own documents directory. When switching cases, document tree shows only that case's documents. Ahmad Ali's documents are ONLY in ACTE-2024-001.

**Scope:** Text files with case-instance directory structure.

---

### 1.4 D-002: Case-Type Form Schemas

**Priority:** Must-have (defines form structure for case types)
**Dependencies:** None (types already support required structure)
**Complexity:** Simple

**Files to Verify:**
- `src/data/mockData.ts` - Verify form definitions exist

**Changes:**
- Verify `initialFormFields: FormField[]` has 7 fields
- Verify `sampleCaseFormData` maps case IDs to form data
- Each case has ONE form template (not folder-specific)

**Rationale:** Form schemas are at the case level, not folder level. The existing initialFormFields array and sampleCaseFormData already support this structure.

**Scope:** Data verification. The existing implementation already uses case-level forms.

---

## Phase 2: Core Infrastructure

**Goal:** Build the core services that other features depend on.

**Dependencies:** Phase 1 must be complete.

### 2.1 F-001: Document Assistant Agent - WebSocket Service

**Priority:** Must-have (core AI functionality)
**Dependencies:** NFR-002 (backend structure)
**Complexity:** Complex

**Files to Create (backend):**
- `backend/services/gemini_service.py` - Gemini API integration
- `backend/api/chat.py` - WebSocket endpoint

**Files to Create (frontend):**
- `src/types/websocket.ts` - WebSocket message types

**Files to Modify (frontend):**
- `src/contexts/AppContext.tsx` - Add WebSocket state management
- `src/components/workspace/AIChatInterface.tsx` - Replace mock with WebSocket

**Rationale:** WebSocket service is the foundation for all AI-powered features. Must be implemented before form auto-fill and field generation.

**Scope:**
- Backend: Gemini service + WebSocket route
- Frontend: Types + context + chat interface

---

### 2.2 F-002: Document Context Management System (Case-Instance Scoped)

**Priority:** Must-have (enables context-aware AI responses)
**Dependencies:** D-001 (context schema files), NFR-002 (backend)
**Complexity:** Moderate

**Files to Create (backend):**
- `backend/services/context_manager.py` - Case-instance context loading and merging

**Key Methods:**
- `load_case_context(case_id)` → loads from `cases/{case_id}/case.json`
- `load_folder_context(case_id, folder_id)` → loads from `cases/{case_id}/folders/{folder_id}.json`
- `create_case_from_template(case_id, case_type)` → creates new case directory from template
- `merge_contexts(case_ctx, folder_ctx, doc_ctx)` → combines for AI prompt

**Files to Modify (backend):**
- `backend/services/gemini_service.py` - Accept case_id for context resolution

**Files to Modify (frontend):**
- `src/types/websocket.ts` - Add caseId, folderId to ChatRequest
- `src/contexts/AppContext.tsx` - Reload context when case changes

**Rationale:** Context is case-instance scoped - each ACTE has its own context. When switching cases, AI receives different context. Supports dynamic case creation from templates.

**Scope:**
- Backend: Context manager with case-instance path resolution
- Frontend: WebSocket types + context reload on case switch

---

### 2.3 F-006: Replace Mock Documents with Text Files (Case-Instance Scoped)

**Priority:** Must-have (enables real document loading)
**Dependencies:** D-003 (sample documents exist)
**Complexity:** Simple

**Files to Create (frontend):**
- `src/lib/documentLoader.ts` - Case-aware document loading utility

**Key Function:**
- `loadDocumentContent(caseId, folderId, filename)` → fetches from `/documents/${caseId}/${folderId}/${filename}`

**Files to Modify (frontend):**
- `src/data/mockData.ts` - Document paths use case-scoped template
- `src/components/workspace/CaseTreeExplorer.tsx` - Load content using currentCase.id
- `src/components/workspace/DocumentViewer.tsx` - Display loaded content
- `src/contexts/AppContext.tsx` - Clear selectedDocument when case changes

**Rationale:** Documents are case-instance scoped - each ACTE has its own documents directory. When switching cases, document tree shows only that case's documents. Prevents cross-case document access.

**Scope:** Frontend only. Case-aware document loading + tree explorer + viewer.

---

### 2.4 NFR-003: Local Storage Without Database

**Priority:** Must-have (enables persistence without backend DB)
**Dependencies:** None (can be done in parallel with 2.1-2.3)
**Complexity:** Simple

**Files to Create (frontend):**
- `src/lib/localStorage.ts` - Storage utility functions

**Files to Modify (frontend):**
- `src/contexts/AppContext.tsx` - Add persistence effects

**Rationale:** LocalStorage utilities are needed for form field persistence in F-004 and general state persistence. Simple utility module.

**Scope:** Frontend only. Utility module + context integration.

---

## Phase 3: Feature Implementation

**Goal:** Implement the main user-facing features.

**Dependencies:** Phase 2 must be complete.

### 3.1 F-005: Case-Level Form Management

**Priority:** Must-have (each case has a form)
**Dependencies:** D-002 (form schemas)
**Complexity:** Moderate

**Files to Verify (frontend):**
- `src/types/case.ts` - Verify Case interface supports form data
- `src/data/mockData.ts` - Verify sampleCaseFormData maps case IDs to form data
- `src/contexts/AppContext.tsx` - Verify formFields tied to currentCase
- `src/components/workspace/FormViewer.tsx` - Verify displays case form
- `src/components/workspace/AdminConfigPanel.tsx` - Verify admin can edit form

**Rationale:** Case-level forms ensure the form persists across folder navigation. The form is tied to the case, not individual folders.

**Scope:** Frontend verification. The existing implementation already uses case-level forms.

---

### 3.2 F-003: Form Auto-Fill from Document Content

**Priority:** Must-have (core AI feature)
**Dependencies:** F-001 (WebSocket), F-002 (context), F-005 (case-level forms), F-006 (documents)
**Complexity:** Complex

**Files to Create (backend):**
- `backend/tools/form_parser.py` - Field extraction tool

**Files to Modify (backend):**
- `backend/services/gemini_service.py` - Register form parser tool

**Files to Modify (frontend):**
- `src/types/websocket.ts` - Add FormUpdateMessage type
- `src/data/mockData.ts` - Add /fillForm command
- `src/components/workspace/AIChatInterface.tsx` - Handle form updates

**Rationale:** Form auto-fill is the primary AI feature that extracts data from documents into form fields. It depends on all previous infrastructure.

**Scope:**
- Backend: Form parser tool + Gemini tool registration
- Frontend: Types + chat interface updates

---

### 3.3 NFR-001: Real-Time AI Response Performance

**Priority:** Should-have (improves UX)
**Dependencies:** F-001 (WebSocket service exists)
**Complexity:** Moderate

**Files to Modify (backend):**
- `backend/services/gemini_service.py` - Add streaming, connection pooling

**Files to Modify (frontend):**
- `src/components/workspace/AIChatInterface.tsx` - Handle streaming messages

**Rationale:** Performance optimization should be done after the basic WebSocket functionality works. Streaming improves perceived responsiveness.

**Scope:**
- Backend: Gemini service streaming
- Frontend: Chat interface streaming support

---

## Phase 4: Admin Features

**Goal:** Implement admin-facing features for form management.

**Dependencies:** Phases 2-3 should be complete.

### 4.1 F-004: AI-Powered Form Field Generator

**Priority:** Nice-to-have (admin convenience feature)
**Dependencies:** F-001 (WebSocket/API), F-003 (form infrastructure), NFR-003 (localStorage)
**Complexity:** Complex

**Files to Create (backend):**
- `backend/services/field_generator.py` - Field generation service
- `backend/api/admin.py` - Admin API endpoint

**Files to Modify (frontend):**
- `src/types/case.ts` - Add JSON-LD metadata to FormField
- `src/components/workspace/AdminConfigPanel.tsx` - Add AI Fields tab

**Rationale:** AI field generation is an advanced feature that builds on existing AI infrastructure. Lower priority than core document processing.

**Scope:**
- Backend: Field generator service + admin API
- Frontend: Types + admin panel tab

---

## Implementation Order Summary

```
Week 1: Foundation
├── Day 1-2: Phase 1 (All parallel)
│   ├── NFR-002: Backend structure
│   ├── D-001: Context JSON files
│   ├── D-002: Form schema definitions
│   └── D-003: Sample document files
│
└── Day 3-5: Phase 2 (Sequential)
    ├── F-001: WebSocket service
    ├── F-002: Context management (after F-001)
    ├── F-006: Document loading (parallel with F-002)
    └── NFR-003: LocalStorage (parallel)

Week 2: Features
├── Day 6-7: Phase 3
│   ├── F-005: Case-level forms
│   ├── F-003: Form auto-fill (after F-005)
│   └── NFR-001: Performance (after F-003)
│
└── Day 8-10: Phase 4
    └── F-004: AI field generator

Week 2 End: Testing & Polish
└── Day 11-14: Integration testing
```

---

## Risk Mitigation

### High-Risk Items

1. **F-001 (WebSocket + Gemini)** - Complex integration
   - Mitigation: Test Gemini API separately before WebSocket integration
   - Fallback: Keep mock responses as fallback while developing

2. **F-003 (Form Auto-Fill)** - Depends on many components
   - Mitigation: Implement incrementally, test each dependency first
   - Fallback: Manual form filling remains available

### Medium-Risk Items

3. **NFR-001 (Performance)** - Streaming complexity
   - Mitigation: Implement basic non-streaming first, add streaming later
   - Fallback: Non-streaming responses are acceptable for POC

---

## File Change Summary by Requirement

| Requirement | New Files | Modified Files |
|-------------|-----------|----------------|
| NFR-002 | 7 (backend structure) | 0 |
| D-001 | 7 (JSON files) | 0 |
| D-002 | 0 | 1 (mockData.ts) |
| D-003 | 6 (text files) | 0 |
| F-001 | 3 (backend + types) | 2 (AppContext, AIChatInterface) |
| F-002 | 1 (context_manager.py) | 2 (gemini_service, websocket.ts) |
| F-006 | 1 (documentLoader.ts) | 3 (mockData, CaseTree, DocViewer) |
| NFR-003 | 1 (localStorage.ts) | 1 (AppContext) |
| F-005 | 0 | 0 (verify existing case-level forms) |
| F-003 | 1 (form_parser.py) | 3 (gemini, types, chat) |
| NFR-001 | 0 | 2 (gemini_service, AIChatInterface) |
| F-004 | 2 (field_gen, admin.py) | 2 (types, AdminConfigPanel) |

**Total:** 29 new files, 21 file modifications (some files modified by multiple requirements)

---

## Success Criteria

Sprint 1 is complete when:

1. ✅ Backend starts and serves WebSocket connections
2. ✅ AI chat responds to questions about documents
3. ✅ "/fillForm" extracts data into form fields
4. ✅ Each case displays its form (persists across folder navigation)
5. ✅ Document content loads from text files
6. ✅ Context influences AI responses appropriately
7. ✅ Form changes persist across page refresh
8. ✅ First AI response token arrives within 2 seconds
9. ✅ Admin can generate fields via natural language (nice-to-have)

---

## Next Steps

After completing this plan:

1. Start with Phase 1 items in parallel
2. Use `/start-requirement <ID>` to get detailed task breakdown
3. Run tests after each requirement completion
4. Update requirement status in requirements.md as work progresses
