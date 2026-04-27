# Sprint 5 Implementation Plan

## Overview

This document provides a strategic implementation roadmap for Sprint 5 requirements, organized by phases based on dependencies, complexity, and foundational importance. The plan prioritizes foundational infrastructure first, followed by core features, and finally integration and polish.

---

## Requirements Summary

### Functional Requirements (16 total)
| ID | Title | Complexity | Dependencies |
|----|-------|------------|--------------|
| S5-001 | Natural Language Form Field Modification with SHACL Validation | Complex | D-S5-001 |
| S5-002 | AI Form Fill with Suggested Values and UX Module | Moderate | None |
| S5-003 | Semantic Search with Multi-Language Support | Complex | S5-004 (pdf_service) |
| S5-004 | Multi-Format Translation Service | Complex | S5-008 (for .eml), S5-007 (file persistence) |
| S5-005 | Case Validation Agent | Complex | S5-011, S5-013, D-S5-003 |
| S5-006 | Document Renders Management System | Moderate | S5-007 |
| S5-007 | Container-Compatible File Persistence | Complex | None (Foundation) |
| S5-008 | Email File Support (.eml) | Moderate | S5-006 |
| S5-009 | Improved Chat Information Presentation | Moderate | None |
| S5-010 | Optional Persistent Chat History | Low | None |
| S5-011 | Cascading Context with Document Tree View | Moderate | S5-007 |
| S5-012 | Document Type Capabilities and Command Availability | Low | S5-004 |
| S5-013 | Enhanced Acte Context Research | Moderate | D-S5-003 |
| S5-014 | UI Language Toggle (German/English) | Moderate | None |
| S5-015 | Initial Document Setup for Test Acte | Low | S5-007 |
| S5-016 | Drag-and-Drop Document Management Across Folders | Low | S5-007, S5-006 |

### Non-Functional Requirements (3 total)
| ID | Title | Related To |
|----|-------|------------|
| NFR-S5-001 | Multi-Language AI Response Accuracy | S5-003, S5-004 |
| NFR-S5-002 | SHACL Validation Performance | S5-001 |
| NFR-S5-003 | Document Processing Scalability | S5-004, S5-003 |

### Data Requirements (3 total)
| ID | Title | Related To |
|----|-------|------------|
| D-S5-001 | SHACL Property Shape Schema | S5-001 |
| D-S5-002 | Document Registry Schema | S5-007, S5-006 |
| D-S5-003 | Enhanced Case Context Schema | S5-005, S5-013 |

---

## Dependency Graph

```
D-S5-001 ──┐
           ├──> S5-001 (SHACL Form Modification)
           │
D-S5-002 ──┤
           ├──> S5-007 (File Persistence) ──┬──> S5-006 (Renders) ──┬──> S5-016 (Drag-Drop)
           │                                │                       └──> S5-008 (Email)
           │                                │
           │                                ├──> S5-011 (Tree View) ──> S5-005 (Validation)
           │                                │
           │                                └──> S5-015 (Test Documents)
           │
D-S5-003 ──┼──> S5-013 (Context Research) ──> S5-005 (Validation)
           │
           └──> S5-004 (Translation) ──┬──> S5-003 (Semantic Search)
                                       └──> S5-012 (Doc Capabilities)

S5-002 (Form Suggestions) ──────────────────> Independent
S5-009 (Chat Formatting) ──────────────────> Independent
S5-010 (Chat History) ─────────────────────> Independent
S5-014 (i18n Toggle) ──────────────────────> Independent
```

---

## Phase 1: Foundation (Data Schemas & Infrastructure)

**Goal:** Establish data structures and infrastructure that other features depend on.

### 1.1 D-S5-001: SHACL Property Shape Schema
**Priority:** Critical (Foundation)
**Estimated Complexity:** Moderate
**Dependencies:** None

**Files to Create/Modify:**
- Backend (models only):
  - `backend/models/shacl_property_shape.py` (new)
  - `backend/schemas/validation_patterns.py` (new)
- Frontend (types only):
  - `src/types/shacl.ts` (update)

**Scope:** Define SHACL PropertyShape model, validation patterns (email, phone, name, date, address), and TypeScript interfaces.

---

### 1.2 D-S5-002: Document Registry Schema
**Priority:** Critical (Foundation)
**Estimated Complexity:** Moderate
**Dependencies:** None

**Files to Create/Modify:**
- Backend (data only):
  - `backend/schemas/document_registry_schema.json` (new)
  - `backend/data/document_manifest.json` (new - initial structure)
- Frontend (types only):
  - `src/types/document-registry.ts` (new)

**Scope:** Define JSON Schema for document registry, create initial manifest file structure.

---

### 1.3 D-S5-003: Enhanced Case Context Schema
**Priority:** Critical (Foundation)
**Estimated Complexity:** High
**Dependencies:** None

**Files to Create/Modify:**
- Backend (data only):
  - `backend/schemas/case_context_schema.json` (new)
  - `backend/data/contexts/cases/ACTE-2024-001/case.json` (major update)
  - `backend/data/contexts/templates/integration_course/case.json` (new)
  - `backend/data/contexts/templates/asylum_application/case.json` (new)
  - `backend/data/contexts/templates/family_reunification/case.json` (new)
- Documentation:
  - `docs/requirements/context-research-sources.md` (new)

**Scope:** Research BAMF requirements, create comprehensive case context with 15+ required documents, 10+ regulations, 20+ common issues. Pure data/research task.

---

### 1.4 S5-007: Container-Compatible File Persistence
**Priority:** Critical (Foundation)
**Estimated Complexity:** High
**Dependencies:** D-S5-002

**Files to Create/Modify:**
- Backend (services + API):
  - `backend/services/document_registry.py` (new)
  - `backend/api/documents.py` (new)
  - `backend/config.py` (update - add DOCUMENTS_BASE_PATH)
  - `backend/main.py` (update - startup scan)
- Frontend (context + API):
  - `src/contexts/AppContext.tsx` (update - loadDocumentsFromBackend)

**Scope:** Implement document registry service, manifest persistence, filesystem reconciliation on startup, document tree API endpoint.

---

## Phase 2: Core Services (Backend Services)

**Goal:** Build core backend services that enable feature implementations.

### 2.1 S5-009: Improved Chat Information Presentation
**Priority:** High
**Estimated Complexity:** Moderate
**Dependencies:** None (can run parallel)

**Files to Create/Modify:**
- Frontend:
  - `src/lib/messageFormatter.ts` (new)
  - `src/components/ui/CodeBlock.tsx` (new)
  - `src/components/workspace/DataTable.tsx` (new)
  - `src/components/workspace/AIChatInterface.tsx` (update)
- Backend:
  - `backend/services/gemini_service.py` (update - format_response)

**Scope:** Markdown rendering, HTML sanitization, code block syntax highlighting, message aggregation, table rendering.

---

### 2.2 S5-010: Optional Persistent Chat History
**Priority:** Medium
**Estimated Complexity:** Low
**Dependencies:** None (can run parallel)

**Files to Create/Modify:**
- Backend:
  - `backend/services/conversation_manager.py` (new)
  - `backend/services/gemini_service.py` (update)
  - `backend/config.py` (update - ENABLE_CHAT_HISTORY flag)
  - `backend/api/chat.py` (update - history endpoint)
- Frontend:
  - `src/components/workspace/AIChatInterface.tsx` (update - Clear History button)

**Scope:** In-memory conversation history, context window management, token budget calculation. Disabled by default.

---

### 2.3 S5-014: UI Language Toggle (German/English)
**Priority:** Medium
**Estimated Complexity:** Moderate
**Dependencies:** None (can run parallel)

**Files to Create/Modify:**
- Frontend:
  - `src/i18n/config.ts` (new)
  - `src/i18n/locales/de.json` (new)
  - `src/i18n/locales/en.json` (new)
  - `src/components/workspace/WorkspaceHeader.tsx` (update)
  - `src/contexts/AppContext.tsx` (update - language state)
  - `src/App.tsx` (update - I18nextProvider)
  - Multiple component files (update - replace hardcoded strings)
- Backend:
  - `backend/services/gemini_service.py` (update - language parameter)

**Scope:** i18next setup, translation files, language toggle button, AI language parameter.

---

### 2.4 S5-006: Document Renders Management System
**Priority:** High
**Estimated Complexity:** Moderate
**Dependencies:** S5-007

**Files to Create/Modify:**
- Frontend:
  - `src/types/case.ts` (update - Document.renders, DocumentRender interface)
  - `src/components/workspace/CaseTreeExplorer.tsx` (update - RenderContainer)
  - `src/contexts/AppContext.tsx` (update - selectedRender, selectDocument)
- Backend:
  - `backend/services/file_service.py` (update - render management)
  - `backend/tools/anonymization_tool.py` (update - return render)

**Scope:** Render container UI, collapsible render list, delete render functionality, render type icons.

---

### 2.5 S5-011: Cascading Context with Document Tree View
**Priority:** High
**Estimated Complexity:** Moderate
**Dependencies:** S5-007

**Files to Create/Modify:**
- Backend:
  - `backend/services/context_manager.py` (update - generate_document_tree)
  - `backend/api/context.py` (new)
  - `backend/services/gemini_service.py` (update - include tree view)
- Frontend:
  - `src/contexts/AppContext.tsx` (update - tree refresh)
  - `src/types/context.ts` (new)

**Scope:** Tree view generator, cache management, tree in AI prompts, auto-refresh on document changes.

---

## Phase 3: Document Processing Features

**Goal:** Implement document processing capabilities (translation, email, search).

### 3.1 S5-008: Email File Support (.eml)
**Priority:** High
**Estimated Complexity:** Moderate
**Dependencies:** S5-006

**Files to Create/Modify:**
- Backend:
  - `backend/services/email_service.py` (new)
  - `backend/tools/email_processor.py` (new)
  - `backend/api/documents.py` (update - email endpoint)
- Frontend:
  - `src/types/case.ts` (update - Document type includes 'eml')
  - `src/components/workspace/EmailViewer.tsx` (new)
  - `src/components/workspace/DocumentViewer.tsx` (update - email rendering)
  - `src/lib/documentApi.ts` (new)

**Scope:** Email parsing (headers, body, attachments), EmailViewer component, email translation support.

---

### 3.2 S5-004: Multi-Format Translation Service
**Priority:** High
**Estimated Complexity:** High
**Dependencies:** S5-007, S5-008

**Files to Create/Modify:**
- Backend:
  - `backend/services/translation_service.py` (new)
  - `backend/services/image_translation_service.py` (new)
  - `backend/services/pdf_translation_service.py` (new)
  - `backend/services/ocr_service.py` (new)
  - `backend/api/translation.py` (new)
- Frontend:
  - `src/components/workspace/DocumentViewer.tsx` (update - translate button)
  - `src/lib/translationApi.ts` (new)
  - `src/types/translation.ts` (new)

**Scope:** Text translation, image OCR + overlay translation, PDF text extraction + translation, translation API.

---

### 3.3 S5-003: Semantic Search with Multi-Language Support
**Priority:** High
**Estimated Complexity:** High
**Dependencies:** S5-004 (uses pdf_service)

**Files to Create/Modify:**
- Backend:
  - `backend/api/search.py` (new)
  - `backend/services/pdf_service.py` (new)
  - `backend/services/gemini_service.py` (update - semantic_search)
  - `backend/tools/language_detector.py` (new)
- Frontend:
  - `src/components/workspace/DocumentViewer.tsx` (update - search button)
  - `src/components/workspace/HighlightedText.tsx` (new)
  - `src/contexts/AppContext.tsx` (update - search state)
  - `src/types/search.ts` (new)

**Scope:** Search dialog, text highlighting, cross-language semantic search, PDF text extraction.

---

### 3.4 S5-012: Document Type Capabilities and Command Availability
**Priority:** Medium
**Estimated Complexity:** Low
**Dependencies:** S5-004

**Files to Create/Modify:**
- Backend:
  - `backend/config/document_capabilities.py` (new)
  - `backend/services/capability_validator.py` (new)
  - `backend/api/chat.py` (update - capability validation)
  - `backend/services/gemini_service.py` (update - capabilities in prompt)
- Frontend:
  - `src/constants/documentCapabilities.ts` (new)
  - `src/components/workspace/DocumentViewer.tsx` (update - button states)
  - `src/components/workspace/AIChatInterface.tsx` (update - command validation)

**Scope:** Capability matrix, dynamic toolbar states, tooltips on disabled buttons, AI capability awareness.

---

## Phase 4: Form & Validation Features

**Goal:** Implement form management and case validation features.

### 4.1 S5-002: AI Form Fill with Suggested Values and UX Module
**Priority:** High
**Estimated Complexity:** Moderate
**Dependencies:** None

**Files to Create/Modify:**
- Backend:
  - `backend/tools/form_parser.py` (update - extract_form_data with confidence)
  - `backend/api/chat.py` (update - form_suggestion message)
- Frontend:
  - `src/components/workspace/SuggestedValue.tsx` (new)
  - `src/components/workspace/FormViewer.tsx` (update - suggestions state)
  - `src/components/workspace/AIChatInterface.tsx` (update - /fill-form handler)
  - `src/types/websocket.ts` (update - FormSuggestionMessage)
  - `src/types/case.ts` (update - SuggestedValue, FormSuggestions)

**Scope:** Suggested value component, inline suggestions under fields, accept/reject actions, confidence display.

---

### 4.2 S5-001: Natural Language Form Field Modification with SHACL Validation
**Priority:** High
**Estimated Complexity:** High
**Dependencies:** D-S5-001

**Files to Create/Modify:**
- Backend:
  - `backend/api/admin.py` (update - POST /api/admin/modify-form)
  - `backend/services/shacl_generator.py` (new)
  - `backend/schemas/schema_org_mappings.py` (new)
- Frontend:
  - `src/components/workspace/FormViewer.tsx` (update - NL dialog, SHACL dialog, validation)
  - `src/types/case.ts` (update - validationPattern, semanticType)
  - `src/types/shacl.ts` (update - FormModificationResponse, ValidationResult)

**Scope:** NL input dialog, SHACL visualization, real-time validation, schema.org mapping, pattern validation.

---

### 4.3 S5-013: Enhanced Acte Context Research
**Priority:** Medium
**Estimated Complexity:** Moderate
**Dependencies:** D-S5-003

**Files to Create/Modify:**
- Backend:
  - `backend/services/context_manager.py` (update - validate_case_context)
  - `backend/models/regulation.py` (new)
- Data (research):
  - Update case.json files with researched data (if not done in D-S5-003)

**Scope:** Context validation, regulation reference system, complete enhancement of case contexts.

---

### 4.4 S5-005: Case Validation Agent
**Priority:** High
**Estimated Complexity:** High
**Dependencies:** S5-011, S5-013, D-S5-003

**Files to Create/Modify:**
- Backend:
  - `backend/services/validation_service.py` (new)
  - `backend/api/validation.py` (new)
  - `backend/models/validation.py` (new)
- Frontend:
  - `src/components/workspace/WorkspaceHeader.tsx` (update - Validate Case button)
  - `src/components/workspace/ValidationReportDialog.tsx` (new)
  - `src/components/workspace/AIChatInterface.tsx` (update - /validate-case)
  - `src/types/validation.ts` (new)

**Scope:** Case/folder validation, multi-language document matching, validation report dialog, missing document suggestions.

---

## Phase 5: UX Polish & Testing Setup

**Goal:** Complete remaining features and set up test data.

### 5.1 S5-015: Initial Document Setup for Test Acte
**Priority:** Medium
**Estimated Complexity:** Low
**Dependencies:** S5-007

**Files to Create/Modify:**
- Data:
  - `root_docs/` directory (new - 7 sample documents)
    - `Geburtsurkunde.jpg`
    - `Email.eml`
    - `Sprachzeugnis-Zertifikat.pdf`
    - `Anmeldeformular.pdf`
    - `Personalausweis.png`
    - `Aufenthalstitel.png`
    - `Notenspiegel.pdf`
- Backend:
  - `backend/scripts/initialize_test_documents.py` (new)
  - `backend/main.py` (update - startup initialization)
- Frontend:
  - `src/data/mockData.ts` (update - document references)

**Scope:** Create sample documents, initialization script, document mapping to folders.

---

### 5.2 S5-016: Drag-and-Drop Document Management Across Folders
**Priority:** Low
**Estimated Complexity:** Low
**Dependencies:** S5-007, S5-006

**Files to Create/Modify:**
- Backend:
  - `backend/api/documents.py` (update - PATCH /move)
  - `backend/services/document_registry.py` (update - move_document)
- Frontend:
  - `src/components/workspace/CaseTreeExplorer.tsx` (update - drag handlers)
  - `src/contexts/AppContext.tsx` (update - moveDocument function)
  - `src/types/case.ts` (update - folderId optional)

**Scope:** Draggable documents, droppable folders, visual drag indicators, move API.

---

## Phase 6: Performance & Quality (NFRs)

**Goal:** Address non-functional requirements.

### 6.1 NFR-S5-001: Multi-Language AI Response Accuracy
**Dependencies:** S5-003, S5-004

**Files to Create/Modify:**
- Backend:
  - `backend/tools/language_detector.py` (ensure ≥95% accuracy)
  - `backend/services/gemini_service.py` (cross-language prompts)
  - `backend/tests/test_multilanguage.py` (new)
  - `backend/tests/test_performance.py` (new)

**Scope:** Language detection accuracy, cross-language prompt engineering, performance benchmarks.

---

### 6.2 NFR-S5-002: SHACL Validation Performance
**Dependencies:** S5-001

**Files to Create/Modify:**
- Frontend:
  - `src/components/workspace/FormViewer.tsx` (update - debouncing, caching)
- Backend:
  - `backend/services/shacl_generator.py` (optimize)

**Scope:** Validation debouncing (300ms), validation caching, async validation, ≤100ms per field.

---

### 6.3 NFR-S5-003: Document Processing Scalability
**Dependencies:** S5-003, S5-004

**Files to Create/Modify:**
- Backend:
  - `backend/config.py` (update - timeouts)
  - `backend/services/resource_monitor.py` (new)
  - `backend/services/pdf_translation_service.py` (update - chunked processing)
  - `backend/api/translation.py` (update - progress WebSocket)

**Scope:** Timeout handling, memory monitoring, chunked PDF processing, progress indicators.

---

## Implementation Order (Summary)

### Week 1: Foundation
1. D-S5-001: SHACL Property Shape Schema
2. D-S5-002: Document Registry Schema
3. D-S5-003: Enhanced Case Context Schema (research)
4. S5-007: Container-Compatible File Persistence

### Week 2: Core Services (Parallel)
5. S5-009: Improved Chat Information Presentation
6. S5-010: Optional Persistent Chat History
7. S5-014: UI Language Toggle
8. S5-006: Document Renders Management

### Week 3: Document Processing
9. S5-011: Cascading Context with Tree View
10. S5-008: Email File Support
11. S5-004: Multi-Format Translation Service
12. S5-003: Semantic Search

### Week 4: Forms & Validation
13. S5-012: Document Type Capabilities
14. S5-002: AI Form Fill with Suggestions
15. S5-001: NL Form Modification with SHACL
16. S5-013: Enhanced Acte Context Research

### Week 5: Polish & NFRs
17. S5-005: Case Validation Agent
18. S5-015: Initial Document Setup
19. S5-016: Drag-and-Drop Documents
20. NFR-S5-001, NFR-S5-002, NFR-S5-003

---

## Risk Assessment

### High Risk Items
1. **S5-004 (Translation)**: Complex multi-format handling, OCR integration, PDF manipulation
   - Mitigation: Start with text translation, add image/PDF incrementally

2. **S5-001 (SHACL)**: NLP interpretation complexity, real-time SHACL generation
   - Mitigation: Use well-defined Gemini prompts, limit field types initially

3. **S5-005 (Validation)**: Multi-language document matching accuracy
   - Mitigation: Leverage Gemini for inference, start with English/German

### Medium Risk Items
1. **S5-007 (Persistence)**: Filesystem reconciliation edge cases
2. **S5-003 (Search)**: Cross-language semantic accuracy
3. **NFR-S5-003 (Scalability)**: Large file handling

### Low Risk Items
- S5-009, S5-010, S5-014, S5-015, S5-016: Straightforward implementations

---

## Key Architectural Decisions

1. **Document Registry**: JSON manifest file for persistence (Docker-friendly)
2. **Renders vs Copies**: Renders stored as metadata on parent document
3. **Chat History**: In-memory only (no database), optional feature flag
4. **i18n**: react-i18next with JSON translation files
5. **SHACL Validation**: Client-side validation with backend shape generation

---

## Testing Strategy

All requirements have test cases defined in the requirements document. Test files are generated in `docs/tests/S5-XXX/` directories. Execute tests after implementing each requirement using the bone-test-executor agent.

---

## File Summary by Requirement

| Requirement | New Files | Modified Files |
|-------------|-----------|----------------|
| D-S5-001 | 2 backend | 1 frontend |
| D-S5-002 | 2 backend | 1 frontend |
| D-S5-003 | 5 backend | 0 |
| S5-001 | 2 backend | 3 frontend |
| S5-002 | 0 | 4 frontend, 2 backend |
| S5-003 | 4 backend, 2 frontend | 2 backend, 2 frontend |
| S5-004 | 5 backend, 2 frontend | 1 frontend |
| S5-005 | 4 backend, 2 frontend | 2 frontend |
| S5-006 | 0 | 4 frontend, 2 backend |
| S5-007 | 2 backend | 3 backend, 1 frontend |
| S5-008 | 3 backend, 2 frontend | 2 frontend, 1 backend |
| S5-009 | 3 frontend | 2 frontend, 1 backend |
| S5-010 | 1 backend | 3 backend, 1 frontend |
| S5-011 | 2 backend, 1 frontend | 3 backend, 1 frontend |
| S5-012 | 2 backend, 1 frontend | 3 backend, 2 frontend |
| S5-013 | 1 backend | 1 backend |
| S5-014 | 3 frontend | 4 frontend, 1 backend |
| S5-015 | 1 backend | 2 backend, 1 frontend |
| S5-016 | 0 | 3 frontend, 2 backend |

---

*Plan created: 2026-01-12*
*Sprint Goal: Enable natural language-driven form modifications with semantic validation, implement AI-powered document search and translation across multiple formats, improve document render management, and add comprehensive case validation capabilities.*
