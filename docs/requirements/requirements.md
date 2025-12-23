# Project Requirements - BAMF AI Case Management System

## Functional Requirements

## F-001: Document Assistant Agent - Backend WebSocket Service

**Status:** proposed

**Description:**
Implement a Python FastAPI backend service with WebSocket support for real-time AI conversation with document context. The service connects to Google Gemini API using GEMINI_API_KEY from .env file ("AIzaSyA25j****"). The agent accepts document content (initially text files, PDF support later) and provides natural language responses including translation, summarization, and Q&A. The WebSocket endpoint at ws://localhost:8000/ws/chat/{case_id} maintains stateless sessions (no persistence required for POC). The agent has access to a form parsing tool that can read current folder's FormField[] structure from AppContext and update field values by sending JSON updates back to the frontend.

**Changes Required:**
- Backend: FastAPI application with WebSocket route at /ws/chat/{case_id}
  - Source: backend/main.py (new file)
  - Dependencies: fastapi, websockets, google-generativeai, python-dotenv
- Backend: Gemini integration service class accepting text content and context
  - Source: backend/services/gemini_service.py (new file)
  - Methods: initialize_client(), generate_response(prompt, document_content, context)
- Backend: Form parsing tool/function for structured data extraction
  - Source: backend/tools/form_parser.py (new file)
  - Function: parse_document_to_form(document_text: str, form_schema: List[FormField]) -> Dict[str, str]
- Frontend: WebSocket client in AIChatInterface.tsx replacing mock responses
  - Source: src/components/workspace/AIChatInterface.tsx (lines 28-256)
  - Replace: handleSubmit function to send via WebSocket instead of setTimeout mock
- Frontend: Add WebSocket connection state management in AppContext
  - Source: src/contexts/AppContext.tsx
  - Add: wsConnection: WebSocket | null, connectWebSocket(), disconnectWebSocket()
- Types: Add WebSocket message types for request/response
  - Source: src/types/websocket.ts (new file)
  - Interfaces: ChatRequest, ChatResponse, FormUpdateMessage

**Test Cases:**
- TC-F-001-01: Connect to ws://localhost:8000/ws/chat/ACTE-2024-001, send "Hello", verify response within 3 seconds
- TC-F-001-02: Send document text (500 chars) + question "What is this about?", verify summary response
- TC-F-001-03: Send German text + command "Translate to English", verify translated response
- TC-F-001-04: Send document with name "John Doe" + instruction "Fill the form", verify FormUpdateMessage with name field populated
- TC-F-001-05: Disconnect WebSocket, verify connection cleanup and no memory leaks
- TC-F-001-06: Send request without GEMINI_API_KEY, verify error response "API key not configured"
- TC-F-001-07: Send 3 rapid messages, verify all responses received in order

**Created:** 2025-12-16T19:45:00Z

---

## F-002: Document Context Management System (Case-Instance Scoped)

**Status:** proposed

**Description:**
Implement a hierarchical context inheritance system providing AI agents with case-instance-specific knowledge. Each case (ACTE) has its own context directory ensuring complete isolation. Context is loaded from `backend/data/contexts/cases/{caseId}/` and includes:

1. **Case-level context**: `cases/{caseId}/case.json` - defines case type, regulations, required documents, validation rules
2. **Folder-level context**: `cases/{caseId}/folders/{folderId}.json` - specifies folder's expected documents and validation criteria
3. **Document-level context**: Selected document content passed from frontend

When switching cases:
- Context manager loads new case's context files
- AI agent receives case-specific knowledge (different for Integration Course vs Asylum Application)
- All responses are scoped to the active case

For new cases:
- Context created from templates in `backend/data/contexts/templates/{caseType}/`
- New case gets its own context directory that can be customized

**Changes Required:**
- Backend: Context manager with case-instance path resolution
  - Source: backend/services/context_manager.py (new file)
  - Methods:
    - load_case_context(case_id) → loads from `cases/{case_id}/case.json`
    - load_folder_context(case_id, folder_id) → loads from `cases/{case_id}/folders/{folder_id}.json`
    - create_case_from_template(case_id, case_type) → copies template to new case directory
    - merge_contexts(case_ctx, folder_ctx, doc_ctx) → combines for AI prompt
- Backend: Update Gemini service to use case-scoped context
  - Source: backend/services/gemini_service.py
  - Update: generate_response(case_id, folder_id, ...) resolves context from case directory
- Frontend: Update WebSocket messages to include case_id and folder_id
  - Source: src/types/websocket.ts
  - Update: ChatRequest interface to include caseId: string, folderId: string | null
- Frontend: Clear and reload context when switching cases
  - Source: src/contexts/AppContext.tsx
  - Update: Trigger context reload when currentCase changes

**Test Cases:**
- TC-F-002-01: Load ACTE-2024-001 context, verify case.json loaded from cases/ACTE-2024-001/
- TC-F-002-02: Load folder context for ACTE-2024-001/personal-data, verify folder-specific rules
- TC-F-002-03: Switch to ACTE-2024-002, verify different case context loaded (Asylum Application)
- TC-F-002-04: Send chat in ACTE-2024-001, verify Integration Course context in AI response
- TC-F-002-05: Create new case ACTE-2024-004 from template, verify context directory created
- TC-F-002-06: Request context for non-existent case, verify graceful error handling

**Created:** 2025-12-16T19:45:00Z

---

## F-003: Form Auto-Fill from Document Content

**Status:** proposed

**Description:**
Enable AI agent to automatically populate FormField values in src/contexts/AppContext.tsx by analyzing document content. When user sends chat command like "Fill the form from this document" or "Extract data to form", the backend Gemini agent uses the form_parser.py tool which receives current formFields array structure (id, label, type, options, required) from frontend, extracts relevant data from document text, and returns JSON mapping of field IDs to extracted values. Frontend receives FormUpdateMessage via WebSocket and calls updateFormField() for each field. The agent uses folder context to understand which fields are relevant (e.g., Personal Data folder → name, birthDate, countryOfOrigin fields). Support text, date, select, and textarea field types from FormField interface.

**Changes Required:**
- Backend: Form parser tool with Gemini-powered field extraction
  - Source: backend/tools/form_parser.py (new file)
  - Function: extract_form_data(document_text: str, form_fields: List[dict], context: str) -> Dict[str, str]
- Backend: Register form parser as callable tool in Gemini service
  - Source: backend/services/gemini_service.py
  - Add: register_tool("parse_form", form_parser.extract_form_data)
- Frontend: Handle FormUpdateMessage WebSocket responses
  - Source: src/components/workspace/AIChatInterface.tsx
  - Add: WebSocket onMessage handler for type="form_update" calling updateFormField() for each field
- Frontend: Add form fill command to quick actions
  - Source: src/components/workspace/AIChatInterface.tsx (line 19-26)
  - Add: { command: '/fillForm', label: 'Fill Form', icon: 'FileInput' }
- Types: FormUpdateMessage interface
  - Source: src/types/websocket.ts
  - Interface: { type: "form_update", updates: Record<string, string>, confidence: Record<string, number> }

**Test Cases:**
- TC-F-003-01: Select document with "Name: John Doe", send "/fillForm", verify formFields['name'].value = "John Doe"
- TC-F-003-02: Document with "Born: 15.05.1990", verify formFields['birthDate'].value = "1990-05-15" (ISO format)
- TC-F-003-03: Document with "Afghanistan origin", verify formFields['countryOfOrigin'].value = "Afghanistan"
- TC-F-003-04: Document in German "Geburtsdatum: 15.05.1990", verify correct date extraction despite language
- TC-F-003-05: Document with ambiguous data, verify agent asks clarification instead of guessing
- TC-F-003-06: Form with select field "Course Preference", document mentions "intensive course", verify value matches options array
- TC-F-003-07: Multiple documents selected, verify agent processes all and merges non-conflicting data

**Created:** 2025-12-16T19:45:00Z

---

## F-004: AI-Powered Form Field Generator - Admin Interface

**Status:** proposed

**Description:**
Add new "AI Fields" tab to AdminConfigPanel.tsx (6th tab after Folders, Doc Types, Macros, Forms, Metadata) enabling admins to request new form fields using natural language. The interface includes a textarea for field requests (e.g., "Add a text field for mother's maiden name" or "Add dropdown for education level with options: high school, bachelor, master, doctorate") and a "Generate Field" button. The request is sent to backend LLM service (Google ADK or simplified LangGraph flow) which parses the natural language, generates FormField structure with semantic metadata (JSON-LD @context for field semantics), and returns field specification. Frontend displays preview with editable properties before adding to formFields array. Use Kolibri components (https://github.com/public-ui) for the input interface. Fields are stored in AppContext.formFields and persisted to localStorage (no database for POC).

**Changes Required:**
- Frontend: New AI Fields tab in AdminConfigPanel
  - Source: src/components/workspace/AdminConfigPanel.tsx (after line 236)
  - Add: TabsTrigger value="ai-fields" and TabsContent with Kolibri textarea component
- Frontend: Field request form with natural language input and preview
  - Source: src/components/workspace/AdminConfigPanel.tsx
  - Add: FieldGeneratorForm component with state for prompt, loading, preview
- Backend: Field generator service endpoint POST /api/admin/generate-field
  - Source: backend/api/admin.py (new file)
  - Endpoint: generate_field(request: FieldGenerationRequest) -> FormFieldSpec
- Backend: Gemini-based field parser with structured output
  - Source: backend/services/field_generator.py (new file)
  - Function: parse_field_request(prompt: str) -> FormFieldSpec with JSON-LD metadata
- Types: Add FormFieldSpec with JSON-LD metadata
  - Source: src/types/case.ts
  - Extend: FormField with optional metadata: { "@context": string, "@type": string, "semanticType": string }
- Frontend: LocalStorage persistence for form configurations
  - Source: src/contexts/AppContext.tsx
  - Add: useEffect to sync formFields to localStorage, loadFormFieldsFromStorage()

**Test Cases:**
- TC-F-004-01: Enter "Add text field for passport number", click Generate, verify preview shows type="text", label="Passport Number", required=false
- TC-F-004-02: Enter "Add required date field for visa expiry", verify preview shows type="date", required=true
- TC-F-004-03: Enter "Add dropdown for marital status: single, married, divorced, widowed", verify type="select", options array has 4 items
- TC-F-004-04: Generate field in German "Füge Textfeld für Reisepassnummer hinzu", verify field created correctly despite language
- TC-F-004-05: Enter ambiguous request "add field for details", verify LLM asks clarification via response message
- TC-F-004-06: Generate field, edit label in preview, click Add, verify edited label saved to formFields
- TC-F-004-07: Refresh page, verify generated fields persist from localStorage
- TC-F-004-08: Verify JSON-LD metadata includes @type for semantic field identification by document parser

**Created:** 2025-12-16T19:45:00Z

---

## F-005: Case-Level Form Management

**Status:** proposed

**Description:**
Implement case-level form management where each case has a single form template. Currently, mockData.ts defines single initialFormFields array used globally. The form is displayed at the case level (not folder level) - when a case is loaded, its associated form appears in the FormViewer panel. The form remains constant as users navigate between folders within the same case. Different cases can have different form templates based on case type (e.g., "German Integration Course Application", "Asylum Application", "Family Reunification"). When switching cases via search or selection, the FormViewer loads the new case's form template and data. Form data is stored per-case in AppContext's allCaseFormData mapping. The AI document assistant can fill form fields from any document in any folder since the form applies to the entire case.

**Changes Required:**
- Types: Ensure Case interface supports case-level form data
  - Source: src/types/case.ts (line 19-25)
  - Verify: Case interface has formFields or reference to form template
- Data: Define case-specific form templates by case type
  - Source: src/data/mockData.ts
  - Add: caseFormTemplates mapping case type to FormField[] arrays
- Data: Update mockCases with form data per case
  - Source: src/data/mockData.ts
  - Add: sampleCaseFormData mapping case IDs to form field values
- Frontend: Ensure FormViewer displays form for current case (not folder)
  - Source: src/components/workspace/FormViewer.tsx
  - Verify: Form title shows case name, form persists across folder navigation
- Frontend: Update AppContext to manage case-level form state
  - Source: src/contexts/AppContext.tsx
  - Verify: formFields state tied to currentCase, allCaseFormData stores per-case data
- Frontend: AdminConfigPanel Forms tab edits the current case's form
  - Source: src/components/workspace/AdminConfigPanel.tsx
  - Verify: Form editor applies to selected case, not folders
- Backend: Form parser receives case context (not folder-specific)
  - Source: backend/tools/form_parser.py
  - Update: extract_form_data uses case_id parameter to retrieve correct form schema

**Test Cases:**
- TC-F-005-01: Load case ACTE-2024-001, verify FormViewer shows "German Integration Course Application" form with 7 fields
- TC-F-005-02: Navigate to different folders within same case, verify form remains unchanged
- TC-F-005-03: Fill form fields, navigate to different folder, verify field values persist
- TC-F-005-04: Switch to case ACTE-2024-002 via search, verify form loads with different data
- TC-F-005-05: Edit form in AdminConfigPanel, verify changes apply to current case only
- TC-F-005-06: Send "/fillForm" command from any folder, verify form fields populated correctly
- TC-F-005-07: Create new case, verify empty form with appropriate template for case type

**Created:** 2025-12-16T19:45:00Z

---

## F-006: Replace Mock Documents with Text Files (Case-Instance Scoped)

**Status:** proposed

**Description:**
Convert current mock document system to use actual text files stored in case-specific directories. Documents are stored at `public/documents/{caseId}/{folderId}/{filename}` ensuring complete isolation between cases. When a case is loaded, the document tree shows only that case's documents. The document loader constructs paths dynamically based on current case ID and folder ID.

When switching cases:
1. CaseTreeExplorer updates to show new case's folder/document structure
2. Document paths are resolved using `currentCase.id`
3. Previously loaded document content is cleared
4. New case's documents become accessible

For new cases:
1. Document directory created at `public/documents/{newCaseId}/`
2. Folder subdirectories created matching case's folder structure
3. Documents can be uploaded/created in the new case's directory

**Changes Required:**
- Frontend: Document loader utility with case-aware paths
  - Source: src/lib/documentLoader.ts (new file)
  - Function: loadDocumentContent(caseId: string, folderId: string, filename: string) -> Promise<string>
  - Path construction: `/documents/${caseId}/${folderId}/${filename}`
- Frontend: Update Document interface to support case-scoped paths
  - Source: src/types/case.ts (line 1-9)
  - Add: caseId and folderId to Document interface for path resolution
- Frontend: Update CaseTreeExplorer to use case-scoped document loading
  - Source: src/components/workspace/CaseTreeExplorer.tsx
  - Update: Document click constructs path from currentCase.id + folder.id + document.name
- Frontend: Update DocumentViewer to display text content
  - Source: src/components/workspace/DocumentViewer.tsx (line 139-151)
  - Update: Display document.content in pre-formatted text box
- Frontend: Clear document state when switching cases
  - Source: src/contexts/AppContext.tsx
  - Update: Reset selectedDocument when currentCase changes
- Frontend: Update AIChatInterface with case context in requests
  - Source: src/components/workspace/AIChatInterface.tsx
  - Update: Include caseId in document content requests
- Data: Update mockData.ts to generate case-scoped paths
  - Source: src/data/mockData.ts
  - Update: Document filePath uses template: `/documents/${caseId}/${folderId}/${filename}`

**Test Cases:**
- TC-F-006-01: Load ACTE-2024-001, click Birth_Certificate.txt, verify loads from /documents/ACTE-2024-001/personal-data/
- TC-F-006-02: Switch to ACTE-2024-002, verify ACTE-2024-001 documents NOT displayed in tree
- TC-F-006-03: Select document in ACTE-2024-001, switch cases, verify document viewer clears
- TC-F-006-04: Create new case ACTE-2024-004, verify empty document tree ready for uploads
- TC-F-006-05: Load document with German umlauts, verify UTF-8 encoding preserved
- TC-F-006-06: Request document from different case's path, verify access prevented or 404
- TC-F-006-07: Document file missing (404), verify graceful error message "Failed to load document content"

**Created:** 2025-12-16T19:45:00Z

---

## Non-Functional Requirements

## NFR-001: Real-Time AI Response Performance

**Status:** proposed

**Description:**
WebSocket chat responses must deliver first token within 2 seconds for standard queries (<500 chars document + <100 chars question). Full response for document summary (1000 words) must complete within 10 seconds. Form auto-fill operation parsing 2000-character document with 7 fields must complete within 5 seconds. Gemini API calls should use streaming responses to provide progressive updates to frontend. Frontend displays typing indicator immediately on send, and streaming responses update message content in real-time. Backend implements connection pooling for Gemini API to minimize latency. No optimization for concurrent users required in POC phase.

**Changes Required:**
- Backend: Implement streaming responses from Gemini API
  - Source: backend/services/gemini_service.py
  - Update: generate_response() to use stream=True parameter and yield chunks
- Backend: Add response timing metrics logging
  - Source: backend/services/gemini_service.py
  - Add: Log response start/end times, token count, latency
- Frontend: Handle streaming WebSocket message updates
  - Source: src/components/workspace/AIChatInterface.tsx
  - Update: WebSocket onMessage to append partial content to existing message
- Backend: Implement connection pooling for Gemini client
  - Source: backend/services/gemini_service.py
  - Add: Singleton pattern for genai.GenerativeModel instance
- Backend: Set Gemini API timeout to 30 seconds
  - Source: backend/services/gemini_service.py
  - Add: request_timeout=30 parameter to API calls

**Test Cases:**
- TC-NFR-001-01: Send "Hello" message, verify first token received within 2 seconds
- TC-NFR-001-02: Send 500-char document + "Summarize", verify first token within 2 seconds, complete within 10 seconds
- TC-NFR-001-03: Send "/fillForm" with 2000-char document, verify completion within 5 seconds
- TC-NFR-001-04: Send message, verify typing indicator displays immediately (<100ms)
- TC-NFR-001-05: Monitor streaming response, verify UI updates at least every 500ms during generation
- TC-NFR-001-06: Send 10 sequential requests, verify no performance degradation (average time increase <10%)

**Created:** 2025-12-16T19:45:00Z

---

## NFR-002: Modular Backend Architecture

**Status:** proposed

**Description:**
Python backend must follow clean architecture with separation of concerns: (1) API layer (FastAPI routes) handles HTTP/WebSocket protocol, (2) Service layer (services/) contains business logic for Gemini integration, context management, field generation, (3) Tools layer (tools/) provides reusable functions for form parsing, document processing, (4) Data layer (data/) stores context configurations and templates. Each module has single responsibility, clear interfaces, and comprehensive docstrings. Use dependency injection for services to enable testing. Project structure: backend/ with subdirs api/, services/, tools/, data/contexts/, tests/, requirements.txt, main.py. Follow Python PEP 8 style guide. Use type hints for all function signatures.

**Changes Required:**
- Backend: Project structure setup
  - Source: backend/ directory with subdirectories api/, services/, tools/, data/contexts/, tests/
- Backend: Main FastAPI application entry point
  - Source: backend/main.py
  - Content: FastAPI app initialization, CORS middleware, WebSocket route registration, startup/shutdown events
- Backend: API routes module for admin and chat endpoints
  - Source: backend/api/admin.py, backend/api/chat.py (new files)
  - Pattern: Router-based route organization, request/response models using Pydantic
- Backend: Service layer with dependency injection
  - Source: backend/services/gemini_service.py, context_manager.py, field_generator.py
  - Pattern: Class-based services with __init__ dependency injection, abstract base classes for interfaces
- Backend: Tools module with pure functions
  - Source: backend/tools/form_parser.py, document_processor.py (new files)
  - Pattern: Stateless functions with type hints, no external dependencies
- Backend: Requirements management
  - Source: backend/requirements.txt
  - Content: fastapi==0.104.1, websockets==12.0, google-generativeai==0.3.1, python-dotenv==1.0.0, uvicorn==0.24.0

**Test Cases:**
- TC-NFR-002-01: Import services/gemini_service.py from api/chat.py, verify no circular dependencies
- TC-NFR-002-02: Instantiate GeminiService with mock API key, verify initialization without external calls
- TC-NFR-002-03: Run pylint on backend/, verify score ≥ 8.0/10
- TC-NFR-002-04: Run mypy type checker, verify zero type errors
- TC-NFR-002-05: Read any service file, verify all functions have docstrings with Args, Returns, Raises sections
- TC-NFR-002-06: Check requirements.txt, verify all dependencies pinned to specific versions

**Created:** 2025-12-16T19:45:00Z

---

## NFR-003: Local Storage Without Database

**Status:** proposed

**Description:**
POC phase requires zero database dependencies. All persistent data stored using browser localStorage and backend filesystem JSON files. Frontend stores formFields, folderForms, adminConfig in localStorage with keys "bamf_form_fields", "bamf_folder_forms", "bamf_admin_config". Backend stores context configurations in data/contexts/ directory as JSON files. Chat sessions are stateless - no conversation history stored. Document files stored in public/documents/ directory. Implement localStorage utility functions for serialization/deserialization with error handling. Backend uses Python json module for file operations with proper error handling for file not found, JSON parsing errors. Maximum localStorage size 5MB checked before saves.

**Changes Required:**
- Frontend: LocalStorage utility module
  - Source: src/lib/localStorage.ts (new file)
  - Functions: saveToLocalStorage(key, data), loadFromLocalStorage(key), clearLocalStorage(key)
- Frontend: Persist formFields to localStorage
  - Source: src/contexts/AppContext.tsx
  - Add: useEffect(() => saveToLocalStorage("bamf_form_fields", formFields), [formFields])
- Frontend: Load formFields from localStorage on app start
  - Source: src/contexts/AppContext.tsx
  - Update: Initial state = loadFromLocalStorage("bamf_form_fields") || initialFormFields
- Frontend: Persist folderForms mapping to localStorage
  - Source: src/contexts/AppContext.tsx
  - Add: Similar useEffect for folderForms state
- Backend: Context file loader with error handling
  - Source: backend/services/context_manager.py
  - Add: load_json_file(path) with try/catch for FileNotFoundError, JSONDecodeError
- Frontend: LocalStorage quota check before save
  - Source: src/lib/localStorage.ts
  - Add: Check localStorage used space, warn if >4.5MB, prevent save if >4.9MB

**Test Cases:**
- TC-NFR-003-01: Add 3 form fields, refresh page, verify fields persist from localStorage
- TC-NFR-003-02: Clear localStorage, refresh page, verify app loads with default initialFormFields
- TC-NFR-003-03: Generate 50 form fields, verify localStorage quota check prevents save with warning message
- TC-NFR-003-04: Save malformed JSON to localStorage, verify app handles gracefully with fallback to defaults
- TC-NFR-003-05: Backend loads missing context file, verify returns empty context instead of crashing
- TC-NFR-003-06: Backend loads context file with invalid JSON, verify logs error and returns empty context
- TC-NFR-003-07: Open app in 2 browser tabs, modify form in tab 1, verify tab 2 doesn't see changes (no real-time sync)

**Created:** 2025-12-16T19:45:00Z

---

## Data Requirements

## D-001: Hierarchical Context Data Schema (Case-Instance Scoped)

**Status:** proposed

**Description:**
Define JSON schema for case-instance and folder-level context files stored in backend/data/contexts/. Each case (ACTE) has its own context directory containing case-specific and folder-specific context files. This ensures complete modularity - when switching cases, all context switches with it. New cases can be created dynamically with their own context directories.

**Directory Structure:**
```
backend/data/contexts/
├── cases/
│   ├── ACTE-2024-001/           # German Integration Course case
│   │   ├── case.json            # Case-level context
│   │   └── folders/
│   │       ├── personal-data.json
│   │       ├── certificates.json
│   │       ├── integration-docs.json
│   │       ├── applications.json
│   │       ├── emails.json
│   │       └── evidence.json
│   ├── ACTE-2024-002/           # Asylum Application case
│   │   ├── case.json
│   │   └── folders/
│   │       └── ...
│   └── ACTE-2024-003/           # Family Reunification case
│       ├── case.json
│       └── folders/
│           └── ...
└── templates/                    # Templates for new cases
    ├── integration_course/
    ├── asylum_application/
    └── family_reunification/
```

Case context schema: { "caseId": "ACTE-2024-001", "caseType": "integration_course", "name": "German Integration Course Application", "description": "...", "regulations": [], "requiredDocuments": [], "validationRules": [], "commonIssues": [] }. Folder context schema: { "folderId": "personal-data", "folderName": "Personal Data", "purpose": "...", "expectedDocuments": [], "validationCriteria": [], "commonMistakes": [] }. All context files versioned with "schemaVersion": "1.0".

**Changes Required:**
- Data: Case context JSON for ACTE-2024-001 (Integration Course)
  - Source: backend/data/contexts/cases/ACTE-2024-001/case.json
  - Schema: caseId, caseType, name, regulations (5+), requiredDocuments (10+), validationRules (8+)
- Data: Folder contexts for ACTE-2024-001
  - Source: backend/data/contexts/cases/ACTE-2024-001/folders/*.json
  - Files: personal-data.json, certificates.json, integration-docs.json, applications.json, emails.json, evidence.json
- Data: Template contexts for new case creation
  - Source: backend/data/contexts/templates/integration_course/
  - Purpose: Copy template folder when creating new Integration Course case
- Backend: Context manager supports case-instance paths
  - Source: backend/services/context_manager.py
  - Methods: load_case_context(case_id) loads from cases/{case_id}/case.json
  - Methods: load_folder_context(case_id, folder_id) loads from cases/{case_id}/folders/{folder_id}.json
  - Methods: create_case_context(case_id, case_type) copies from templates/{case_type}/ to cases/{case_id}/

**Test Cases:**
- TC-D-001-01: Load ACTE-2024-001/case.json, verify caseId="ACTE-2024-001" and schemaVersion="1.0"
- TC-D-001-02: Load ACTE-2024-001/folders/personal-data.json, verify expectedDocuments includes "birth_certificate"
- TC-D-001-03: Switch to ACTE-2024-002, verify different case.json loaded with different caseType
- TC-D-001-04: Create new case ACTE-2024-004 from integration_course template, verify context files created
- TC-D-001-05: Load non-existent case context, verify graceful fallback or error message
- TC-D-001-06: Verify each case directory is isolated - changes to ACTE-2024-001 don't affect ACTE-2024-002
- TC-D-001-07: Parse all context files with JSON validator, verify no syntax errors

**Created:** 2025-12-16T19:45:00Z

---

## D-002: Case-Type Form Schemas

**Status:** proposed

**Description:**
Define TypeScript FormField arrays for each case type with appropriate fields, types, and validation. Each case has a single form template based on its case type. Integration Course Application form includes: fullName (text, required), birthDate (date, required), countryOfOrigin (text, required), existingLanguageCertificates (text, optional), coursePreference (select with options: ["Intensive Course", "Evening Course", "Weekend Course"], optional), currentAddress (textarea, required), reasonForApplication (textarea, required). This matches the existing 7-field form structure. Additional case types can have different form templates: Asylum Application form, Family Reunification form, etc. Form templates are defined in mockData.ts and mapped to cases via sampleCaseFormData. The AI document assistant uses the case's form schema for auto-fill operations regardless of which folder the user is viewing.

**Changes Required:**
- Data: Integration Course Application form field definition
  - Source: src/data/mockData.ts
  - Verify: initialFormFields array has 7 fields matching current implementation
- Data: Define case-type form templates mapping
  - Source: src/data/mockData.ts
  - Add: caseFormTemplates object mapping case types to FormField[] arrays
- Data: Update sampleCaseFormData with form values per case
  - Source: src/data/mockData.ts
  - Verify: sampleCaseFormData maps case IDs to Record<string, string> form data
- Types: Validate FormField interface supports all field types
  - Source: src/types/case.ts (line 27-34)
  - Verify: type union includes 'text' | 'date' | 'select' | 'textarea', options? property exists
- Frontend: FormViewer renders form for current case type
  - Source: src/components/workspace/FormViewer.tsx
  - Verify: Uses formFields from AppContext tied to currentCase

**Test Cases:**
- TC-D-002-01: Import initialFormFields, verify array length = 7, required fields have required=true
- TC-D-002-02: Check coursePreference field options, verify includes "Intensive Course", "Evening Course", "Weekend Course"
- TC-D-002-03: Verify sampleCaseFormData has entries for ACTE-2024-001, ACTE-2024-002, ACTE-2024-003
- TC-D-002-04: Load case ACTE-2024-001, verify form fields match initialFormFields schema
- TC-D-002-05: Validate FormField interface, verify each field has id, label, type, value properties
- TC-D-002-06: Switch between cases, verify form structure consistent but data differs
- TC-D-002-07: Render FormViewer with form, verify select dropdowns populate correctly

**Created:** 2025-12-16T19:45:00Z

---

## D-003: Sample Document Text Content (Case-Instance Scoped)

**Status:** proposed

**Description:**
Create realistic sample text files stored in case-specific directories. Each case (ACTE) has its own documents folder ensuring complete isolation - documents for ACTE-2024-001 are only accessible when that case is active. When switching cases, the document tree shows only that case's documents. New cases can have their own document directories created dynamically.

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
│   │   └── (empty initially)
│   ├── applications/
│   │   └── Integration_Application.txt
│   ├── emails/
│   │   └── Confirmation_Email.txt
│   └── evidence/
│       └── School_Transcripts.txt
├── ACTE-2024-002/                    # Asylum Application case
│   └── ...                           # Different documents for this case
├── ACTE-2024-003/                    # Family Reunification case
│   └── ...                           # Different documents for this case
└── templates/                        # Document templates for new cases
    └── integration_course/
        └── (sample structure)
```

For ACTE-2024-001 (Ahmad Ali's German Integration Course case):
- Birth_Certificate.txt: German certificate with Vorname: Ahmad, Nachname: Ali, Geburtsdatum: 15.05.1990, Geburtsort: Kabul
- Passport_Scan.txt: P123456789, AHMAD ALI, Issue: 20.05.2020, Expiry: 20.05.2028
- Language_Certificate_A1.txt: Goethe-Institut, Niveau A1, Kursteilnehmer: Ahmad Ali, 15.06.2023
- Integration_Application.txt: Partially filled form with course preference
- Confirmation_Email.txt: From bamf@example.de confirming receipt
- School_Transcripts.txt: Kabul University records

Each file 300-5000 characters, UTF-8 encoding, realistic formatting.

**Changes Required:**
- Data: Create ACTE-2024-001 document directory structure
  - Source: public/documents/ACTE-2024-001/
  - Subdirs: personal-data/, certificates/, integration-docs/, applications/, emails/, evidence/
- Data: Birth Certificate for ACTE-2024-001
  - Source: public/documents/ACTE-2024-001/personal-data/Birth_Certificate.txt
  - Content: German certificate for Ahmad Ali, born 15.05.1990 in Kabul
- Data: Passport for ACTE-2024-001
  - Source: public/documents/ACTE-2024-001/personal-data/Passport_Scan.txt
  - Content: Passport P123456789 for AHMAD ALI
- Data: Language Certificate for ACTE-2024-001
  - Source: public/documents/ACTE-2024-001/certificates/Language_Certificate_A1.txt
  - Content: Goethe-Institut A1 certificate
- Data: Integration Application for ACTE-2024-001
  - Source: public/documents/ACTE-2024-001/applications/Integration_Application.txt
- Data: Confirmation Email for ACTE-2024-001
  - Source: public/documents/ACTE-2024-001/emails/Confirmation_Email.txt
- Data: School Transcripts for ACTE-2024-001
  - Source: public/documents/ACTE-2024-001/evidence/School_Transcripts.txt
- Frontend: Update mockData.ts document paths to use case-specific paths
  - Source: src/data/mockData.ts
  - Update: filePath to use `/documents/${caseId}/${folderId}/${filename}`

**Test Cases:**
- TC-D-003-01: Load ACTE-2024-001/personal-data/Birth_Certificate.txt, verify contains "Ahmad Ali"
- TC-D-003-02: Switch to ACTE-2024-002, verify ACTE-2024-001 documents NOT accessible
- TC-D-003-03: Load document from wrong case path, verify 404 or access denied
- TC-D-003-04: Create new case ACTE-2024-004, verify empty document directory created
- TC-D-003-05: Send Birth_Certificate.txt to AI with case context, verify case-aware response
- TC-D-003-06: Verify all text files are valid UTF-8, German umlauts display correctly
- TC-D-003-07: Navigate folders in ACTE-2024-001, verify documents match folder structure

**Created:** 2025-12-16T19:45:00Z

---

## Sprint 2 Requirements - Admin Features

---

## S2-001: Conversational Field Addition

**Status:** implemented
**Progress:** implemented.

**Description:**
The system must provide an input space, such as an "AI Forms" tab, where administrators can enter natural language commands. The system must interpret strings like "I need a choice, a drop-down, a list and add these options" to automatically add the fields to the form. This is intended to remove the need for manual selection of field types (e.g., date, text) or technical coding. The generated fields must include SHACL/JSON-LD semantic metadata for interoperability and validation.

**Changes Required:**
- Backend: NLP field generation service
  - Source: backend/services/field_generator.py (new file)
  - Methods: parse_field_request(prompt: str) -> FormFieldSpec
  - Uses Gemini API for natural language interpretation
- Backend: Admin API endpoint
  - Source: backend/api/admin.py (new file)
  - Endpoint: POST /api/admin/generate-field
  - Request: { prompt: string }
  - Response: { field: FormFieldSpec with SHACL metadata }
- Frontend: API client for admin endpoints
  - Source: src/lib/adminApi.ts (new file)
  - Function: generateField(prompt: string) -> Promise<FormFieldSpec>
- Frontend: Enhanced AI Fields tab in AdminConfigPanel
  - Source: src/components/workspace/AdminConfigPanel.tsx
  - Add: Natural language textarea input
  - Add: Field preview with editable properties
  - Add: SHACL metadata display
  - Add: "Add to Form" action

**Test Cases:**
- TC-S2-001-01: Enter "Add text field for passport number", verify field generated with type="text"
- TC-S2-001-02: Enter "Add dropdown for education level with options high school, bachelor, master", verify select field with 3 options
- TC-S2-001-03: Enter "I need a required date field for visa expiry", verify type="date" and required=true
- TC-S2-001-04: Enter ambiguous request "add field for details", verify clarification response
- TC-S2-001-05: Verify generated field includes SHACL metadata with @context and @type
- TC-S2-001-06: Edit generated field label in preview, add to form, verify edited label saved
- TC-S2-001-07: Generate field in German "Füge ein Textfeld für Reisepassnummer hinzu", verify correct interpretation

**Created:** 2025-12-22T00:00:00Z

---

## S2-002: Dynamic Structure Definition (SHACL & JSON-LD)

**Status:** implemented

**Description:**
The system shall use SHACL (Shapes Constraint Language) represented as JSON-LD for all form field definitions. This technical standard will be used to structure and validate dynamic form elements generated by the NLP interface. SHACL provides semantic meaning to form fields, enabling better AI understanding during extraction and allowing validation of field constraints.

**Changes Required:**
- Backend: SHACL schema package
  - Source: backend/schemas/__init__.py (new file)
  - Exports: SHACLPropertyShape, SHACLNodeShape, JSONLDContext
- Backend: SHACL property and node shape definitions
  - Source: backend/schemas/shacl.py (new file)
  - Classes: SHACLPropertyShape with properties (sh:path, sh:datatype, sh:minCount, sh:maxCount, sh:name, sh:description)
  - Classes: SHACLNodeShape for form-level validation shapes
- Backend: JSON-LD context definitions
  - Source: backend/schemas/jsonld_context.py (new file)
  - Constants: SHACL_CONTEXT, SCHEMA_ORG_CONTEXT
  - Functions: build_field_context(field_type: str) -> dict
- Frontend: TypeScript interfaces for SHACL metadata
  - Source: src/types/shacl.ts (new file)
  - Interfaces: SHACLPropertyShape, SHACLNodeShape, JSONLDContext
- Frontend: Extend FormField interface
  - Source: src/types/case.ts
  - Add: shaclMetadata?: SHACLPropertyShape property

**Test Cases:**
- TC-S2-002-01: Create SHACLPropertyShape for text field, verify @context includes SHACL namespace
- TC-S2-002-02: Create SHACLPropertyShape with required constraint, verify sh:minCount = 1
- TC-S2-002-03: Create SHACLPropertyShape for date field, verify sh:datatype = xsd:date
- TC-S2-002-04: Validate JSON-LD context against JSON-LD specification
- TC-S2-002-05: Verify TypeScript SHACLPropertyShape interface matches Python class
- TC-S2-002-06: Import SHACL schemas in field_generator service, verify no import errors

**Created:** 2025-12-22T00:00:00Z

---

## S2-003: Legacy Form Standardization

**Status:** implemented
**Progress:** All form templates in mockData.ts have SHACL metadata. FormViewer displays SHACL info in admin mode. Migration script created.

**Description:**
All existing forms within the system (such as the current holder structures in mockData.ts) must be updated or migrated to follow the same SHACL/JSON-LD definitions used for newly created fields. This ensures a unified schema across the entire information base. The migration preserves backward compatibility - existing forms work without SHACL metadata, but gain semantic richness when metadata is added.

**Changes Required:**
- Backend: Migration script for form schemas
  - Source: backend/scripts/migrate_forms_to_shacl.py (new file)
  - Function: generate_shacl_for_field(field: FormField) -> SHACLPropertyShape
  - Function: migrate_all_fields() -> List[FormField with SHACL]
- Frontend: Update mockData.ts with SHACL metadata
  - Source: src/data/mockData.ts
  - Update: Add shaclMetadata property to all 7 initialFormFields
  - Mapping: fullName → schema:name, birthDate → schema:birthDate, countryOfOrigin → schema:nationality, etc.
- Frontend: Handle SHACL-enhanced fields in FormViewer
  - Source: src/components/workspace/FormViewer.tsx
  - Add: Display SHACL semantic type in admin mode
  - Add: Show field constraints from SHACL metadata

**Test Cases:**
- TC-S2-003-01: Load initialFormFields, verify all 7 fields have shaclMetadata property
- TC-S2-003-02: Verify fullName field has sh:path = "schema:name"
- TC-S2-003-03: Verify birthDate field has sh:datatype = "xsd:date"
- TC-S2-003-04: Load form without SHACL metadata, verify backward compatibility (no errors)
- TC-S2-003-05: Display form in admin mode, verify SHACL semantic type shown
- TC-S2-003-06: Run migration script, verify output matches expected SHACL structure

**Created:** 2025-12-22T00:00:00Z

---

## S2-004: Multi-Format Contextual Extraction

**Status:** proposed

**Description:**
The system must utilize a "cascading effect" for context, pulling data from the active case, the specific folder, and the document being visualized. Context precedence: Document > Folder > Case. While currently tested with text files, the system must eventually support PDFs and other formats for form-filling and extraction tasks. This requirement creates the abstraction layer for future format support.

**Changes Required:**
- Backend: Document processor abstraction
  - Source: backend/tools/document_processor.py (new file)
  - Abstract class: DocumentProcessor with methods extract_text(), get_metadata(), supports_format()
- Backend: Text file processor implementation
  - Source: backend/tools/text_processor.py (new file)
  - Class: TextProcessor implementing DocumentProcessor for .txt files
- Backend: PDF processor stub (future implementation)
  - Source: backend/tools/pdf_processor.py (new file)
  - Class: PDFProcessor with NotImplementedError for future PDF support
- Backend: Enhanced context cascading
  - Source: backend/services/context_manager.py
  - Update: merge_contexts() with clear precedence logic
  - Add: resolve_conflict(doc_value, folder_value, case_value) helper
- Backend: Better context injection in Gemini service
  - Source: backend/services/gemini_service.py
  - Update: _build_prompt() to clearly delineate context sources
- Frontend: Context source indicators in chat
  - Source: src/components/workspace/AIChatInterface.tsx
  - Add: Visual indicator showing which context level provided data

**Test Cases:**
- TC-S2-004-01: Send chat with document, folder, and case context, verify document context takes precedence
- TC-S2-004-02: Conflict in field value between folder and case, verify folder wins
- TC-S2-004-03: Use TextProcessor to extract text from .txt file, verify content correct
- TC-S2-004-04: Check PDFProcessor.supports_format(".pdf"), verify returns True
- TC-S2-004-05: Call PDFProcessor.extract_text(), verify raises NotImplementedError with helpful message
- TC-S2-004-06: Chat response includes context source indicator, verify visible in UI
- TC-S2-004-07: Process document without folder context, verify case context used as fallback

**Created:** 2025-12-22T00:00:00Z

---
