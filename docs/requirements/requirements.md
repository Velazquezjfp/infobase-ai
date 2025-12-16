# Project Requirements - BAMF AI Case Management System

## Functional Requirements

## F-001: Document Assistant Agent - Backend WebSocket Service

**Status:** proposed

**Description:**
Implement a Python FastAPI backend service with WebSocket support for real-time AI conversation with document context. The service connects to Google Gemini API using GEMINI_API_KEY from .env file ("AIzaSyA25jr2EC9eaQtUs50OHleoz69B7ULh1ZU"). The agent accepts document content (initially text files, PDF support later) and provides natural language responses including translation, summarization, and Q&A. The WebSocket endpoint at ws://localhost:8000/ws/chat/{case_id} maintains stateless sessions (no persistence required for POC). The agent has access to a form parsing tool that can read current folder's FormField[] structure from AppContext and update field values by sending JSON updates back to the frontend.

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

## F-002: Document Context Management System

**Status:** proposed

**Description:**
Implement a hierarchical context inheritance system providing AI agents with domain-specific knowledge at three levels: (1) Case-level context defining the "German Integration Course Application" process including BAMF regulations, required documents (birth certificate, passport, language certificates), validation rules, and common errors; (2) Folder-level context specifying what each folder should contain and validation criteria - Personal Data folder expects identity documents with specific fields (full name, date of birth, nationality), Certificates folder expects language proficiency evidence (A1-C2 levels, Goethe Institut or equivalent), etc.; (3) Document-level context including selected document content. Context is stored as JSON files in data/contexts/ directory and loaded by the backend agent when processing requests. Frontend passes currentCase.id and selectedFolder.id in WebSocket messages so backend can retrieve appropriate context hierarchy.

**Changes Required:**
- Data: Case-level context JSON defining Integration Course process
  - Source: backend/data/contexts/case_types/integration_course.json (new file)
  - Schema: { "name": "German Integration Course Application", "description": "...", "regulations": [], "required_documents": [], "validation_rules": [], "common_issues": [] }
- Data: Folder-level context JSON for each folder type
  - Source: backend/data/contexts/folders/personal_data.json, certificates.json, integration_docs.json, applications.json, emails.json, evidence.json (new files)
  - Schema: { "folder_name": "Personal Data", "purpose": "...", "required_documents": [], "validation_criteria": [], "common_mistakes": [] }
- Backend: Context manager service loading and merging context hierarchy
  - Source: backend/services/context_manager.py (new file)
  - Methods: load_case_context(case_id), load_folder_context(folder_id), merge_contexts(case_ctx, folder_ctx, doc_ctx) -> str
- Backend: Update Gemini service to accept and use hierarchical context
  - Source: backend/services/gemini_service.py
  - Update: generate_response() to accept context parameter and include in system prompt
- Frontend: Update WebSocket messages to include case_id and folder_id
  - Source: src/types/websocket.ts
  - Update: ChatRequest interface to include caseId: string, folderId: string | null

**Test Cases:**
- TC-F-002-01: Request context for case "ACTE-2024-001", verify integration_course.json loaded correctly
- TC-F-002-02: Request context for folder "personal-data", verify personal_data.json loaded with 3+ validation rules
- TC-F-002-03: Send chat message with birth certificate in Personal Data folder, verify agent mentions "date of birth" and "nationality" validation
- TC-F-002-04: Send chat message with A1 certificate in Certificates folder, verify agent recognizes Goethe Institut as valid issuer
- TC-F-002-05: Upload document to wrong folder, verify agent suggests correct folder based on context
- TC-F-002-06: Request context for non-existent folder_id, verify graceful fallback to case-level context only

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

## F-005: Folder-Specific Form Management

**Status:** proposed

**Description:**
Implement dynamic form selection based on currentFolder context. Currently, mockData.ts defines single initialFormFields array used globally. Extend Case interface to include folderForms mapping folder IDs to FormField arrays. Create folder-specific forms: Personal Data folder shows identity fields (name, birthDate, nationality, passportNumber), Certificates folder shows certification fields (certificateType, issuingInstitution, level, issueDate, expiryDate), Integration Course Documents folder shows enrollment fields (courseProvider, startDate, courseType, hoursPerWeek), Applications folder shows application fields (applicationDate, status, reviewedBy). When user selects a document or navigates to a folder, FormViewer.tsx displays the appropriate form. Forms can be edited in AdminConfigPanel Forms tab with folder selector dropdown. AI document assistant uses the active folder's form schema for auto-fill operations.

**Changes Required:**
- Types: Extend Case interface with folderForms mapping
  - Source: src/types/case.ts (line 19-25)
  - Add: folderForms?: Record<string, FormField[]> to Case interface
- Data: Create folder-specific form templates
  - Source: src/data/mockData.ts
  - Add: personalDataForm, certificatesForm, integrationCourseForm, applicationsForm arrays
- Data: Update mockCase with folderForms mapping
  - Source: src/data/mockData.ts (line 51-111)
  - Add: folderForms: { "personal-data": personalDataForm, "certificates": certificatesForm, ... }
- Frontend: Update FormViewer to select form based on current folder
  - Source: src/components/workspace/FormViewer.tsx
  - Add: Compute activeForm = currentCase.folderForms?.[currentFolderId] || formFields
- Frontend: Update AppContext to manage folder-specific forms
  - Source: src/contexts/AppContext.tsx
  - Add: currentFolderId state, updateFormFieldForFolder(folderId, fieldId, value)
- Frontend: Update AdminConfigPanel Forms tab with folder selector
  - Source: src/components/workspace/AdminConfigPanel.tsx (line 472-538)
  - Add: Select dropdown to choose folder, edit that folder's form fields
- Backend: Update form parser to receive folder-specific schema
  - Source: backend/tools/form_parser.py
  - Update: extract_form_data to accept folder_id parameter for correct schema selection

**Test Cases:**
- TC-F-005-01: Click "Personal Data" folder, verify FormViewer displays name, birthDate, nationality fields
- TC-F-005-02: Click "Certificates" folder, verify FormViewer displays certificateType, issuingInstitution, level fields
- TC-F-005-03: Click document in "Integration Course Documents", verify courseProvider, startDate fields displayed
- TC-F-005-04: Fill form in "Personal Data" folder, switch to "Certificates" folder, verify Personal Data values persist
- TC-F-005-05: Open AdminConfigPanel Forms tab, select "Certificates" folder, add new field, verify appears in Certificates form only
- TC-F-005-06: Send "/fillForm" command in Personal Data folder with birth certificate, verify only Personal Data fields filled
- TC-F-005-07: Create new case, verify all folders have default empty forms, no cross-contamination

**Created:** 2025-12-16T19:45:00Z

---

## F-006: Replace Mock Documents with Text Files

**Status:** proposed

**Description:**
Convert current mock document system to use actual text files stored locally. Replace src/data/mockData.ts PDF references with .txt files in public/documents/ directory maintaining same filenames (Birth_Certificate.txt, Passport_Scan.txt, Language_Certificate_A1.txt, etc.). Update Document interface content property to store full text content loaded from files. Modify CaseTreeExplorer.tsx and DocumentViewer.tsx to load file content from public directory using fetch(). When document is selected, load text content and pass to AI chat interface. Maintain original metadata structure for document type, size, uploadedAt. Prepare architecture for future PDF support by keeping file type as 'pdf' in metadata but serving .txt during POC phase.

**Changes Required:**
- Data: Create text file versions of mock documents
  - Source: public/documents/Birth_Certificate.txt, Passport_Scan.txt, Language_Certificate_A1.txt, Integration_Application.txt, School_Transcripts.txt, Confirmation_Email.txt (new files)
  - Content: Realistic sample text for each document type (German/English mixed as appropriate)
- Frontend: Update Document interface to support content loading
  - Source: src/types/case.ts (line 1-9)
  - Current content?: string is sufficient, ensure it's populated from file
- Frontend: Add document loader utility function
  - Source: src/lib/documentLoader.ts (new file)
  - Function: loadDocumentContent(documentPath: string) -> Promise<string>
- Frontend: Update CaseTreeExplorer document click to load content
  - Source: src/components/workspace/CaseTreeExplorer.tsx
  - Update: Document click handler to call loadDocumentContent and set selectedDocument.content
- Frontend: Update DocumentViewer to display text content
  - Source: src/components/workspace/DocumentViewer.tsx (line 139-151)
  - Update: activeTab='pdf' view to display document.content in pre-formatted text box instead of placeholder
- Frontend: Update AIChatInterface to access document content
  - Source: src/components/workspace/AIChatInterface.tsx
  - Update: Send selectedDocument.content in WebSocket messages when document context needed
- Data: Update mockData.ts documents with file paths
  - Source: src/data/mockData.ts (line 61-107)
  - Update: Document objects to include filePath: '/documents/Birth_Certificate.txt' property

**Test Cases:**
- TC-F-006-01: Click Birth_Certificate.txt in tree, verify content loads and displays in DocumentViewer
- TC-F-006-02: Select document, send chat message "Summarize this", verify AI receives full text content
- TC-F-006-03: Document with 5000+ characters, verify full content loads without truncation
- TC-F-006-04: Load document with German umlauts (ä, ö, ü, ß), verify UTF-8 encoding preserved
- TC-F-006-05: Click document while previous document loading, verify no race condition or stale content
- TC-F-006-06: Refresh page with document selected, verify content reloads correctly
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

## D-001: Hierarchical Context Data Schema

**Status:** proposed

**Description:**
Define JSON schema for case-level and folder-level context files stored in backend/data/contexts/. Case context schema includes: { "caseType": "integration_course", "name": "German Integration Course Application", "description": "Process for managing integration course applications submitted to BAMF", "regulations": [{ "id": "§43_AufenthG", "title": "Integration course entitlement", "summary": "..." }], "requiredDocuments": [{ "documentType": "birth_certificate", "mandatory": true, "validationRules": ["must_be_certified", "max_age_6_months"] }], "validationRules": [{ "rule_id": "age_verification", "condition": "...", "action": "..." }], "commonIssues": [{ "issue": "Missing translation", "severity": "warning", "suggestion": "..." }] }. Folder context schema includes: { "folderId": "personal-data", "folderName": "Personal Data", "purpose": "Identity verification documents", "expectedDocuments": [], "validationCriteria": [], "processingGuidelines": [], "commonMistakes": [] }. All context files versioned with "schemaVersion": "1.0".

**Changes Required:**
- Data: Case context JSON for Integration Course type
  - Source: backend/data/contexts/case_types/integration_course.json
  - Schema: As described above with 5+ regulations, 10+ required documents, 8+ validation rules
- Data: Personal Data folder context
  - Source: backend/data/contexts/folders/personal_data.json
  - Content: expectedDocuments: ["birth_certificate", "passport", "national_id"], validationCriteria: ["name_consistency", "valid_dates", "certified_translations"]
- Data: Certificates folder context
  - Source: backend/data/contexts/folders/certificates.json
  - Content: expectedDocuments: ["language_certificate"], validationCriteria: ["recognized_institution", "cefr_level_valid", "within_validity_period"]
- Data: Integration Course Documents folder context
  - Source: backend/data/contexts/folders/integration_docs.json
  - Content: expectedDocuments: ["course_confirmation", "attendance_records"], validationCriteria: ["minimum_hours", "provider_accredited"]
- Data: Applications & Forms folder context
  - Source: backend/data/contexts/folders/applications.json
  - Content: expectedDocuments: ["application_form", "signed_declarations"], validationCriteria: ["all_required_fields", "valid_signature"]
- Data: Emails folder context
  - Source: backend/data/contexts/folders/emails.json
  - Content: expectedDocuments: ["correspondence"], validationCriteria: ["official_sender", "relevant_to_case"]
- Data: Additional Evidence folder context
  - Source: backend/data/contexts/folders/evidence.json
  - Content: expectedDocuments: ["supporting_documents"], validationCriteria: ["relevant_to_application"]

**Test Cases:**
- TC-D-001-01: Load integration_course.json, verify schemaVersion="1.0" and all required top-level keys present
- TC-D-001-02: Validate regulations array, verify each regulation has id, title, summary fields
- TC-D-001-03: Load personal_data.json, verify expectedDocuments includes "birth_certificate" and "passport"
- TC-D-001-04: Load certificates.json, verify validationCriteria includes "cefr_level_valid" rule
- TC-D-001-05: Parse all context files with JSON validator, verify no syntax errors
- TC-D-001-06: Verify total context size for integration_course.json <100KB for performance
- TC-D-001-07: Load all 6 folder contexts, verify no duplicate folderId values

**Created:** 2025-12-16T19:45:00Z

---

## D-002: Folder-Specific Form Schemas

**Status:** proposed

**Description:**
Define TypeScript FormField arrays for each folder type with appropriate fields, types, and validation. Personal Data form includes: name (text, required), birthDate (date, required), nationality (text, required), passportNumber (text, required), passportExpiry (date, required), placeOfBirth (text, required), currentAddress (textarea, required). Certificates form includes: certificateType (select with options: ["Language", "Education", "Professional"], required), issuingInstitution (text, required), level (select with CEFR levels A1-C2, required), issueDate (date, required), expiryDate (date, optional), certificateNumber (text, optional). Integration Course form includes: courseProvider (text, required), courseType (select: ["Intensive", "Evening", "Weekend", "Online"], required), startDate (date, required), expectedEndDate (date, required), hoursPerWeek (text, required), courseLocation (text, required). Applications form includes: applicationDate (date, required), status (select: ["Draft", "Submitted", "Under Review", "Approved", "Rejected"], required), reviewedBy (text, optional), notes (textarea, optional).

**Changes Required:**
- Data: Personal Data form field definition
  - Source: src/data/mockData.ts
  - Add: export const personalDataForm: FormField[] with 7 fields as specified
- Data: Certificates form field definition
  - Source: src/data/mockData.ts
  - Add: export const certificatesForm: FormField[] with 6 fields including CEFR level select
- Data: Integration Course Documents form field definition
  - Source: src/data/mockData.ts
  - Add: export const integrationCourseForm: FormField[] with 6 fields
- Data: Applications & Forms form field definition
  - Source: src/data/mockData.ts
  - Add: export const applicationsForm: FormField[] with 4 fields including status select
- Data: Update mockCase folderForms mapping
  - Source: src/data/mockData.ts (line 51)
  - Add: folderForms property mapping folder IDs to respective form arrays
- Types: Validate FormField interface supports all field types
  - Source: src/types/case.ts (line 27-34)
  - Verify: type union includes 'text' | 'date' | 'select' | 'textarea', options? property exists

**Test Cases:**
- TC-D-002-01: Import personalDataForm, verify array length = 7, all required fields have required=true
- TC-D-002-02: Check certificatesForm level field options, verify includes all CEFR levels A1, A2, B1, B2, C1, C2
- TC-D-002-03: Verify integrationCourseForm courseType options match expected values
- TC-D-002-04: Check applicationsForm status field, verify "Draft" is first option
- TC-D-002-05: Validate all form arrays, verify each FormField has id, label, type, value properties
- TC-D-002-06: Check mockCase.folderForms, verify keys match folder IDs: "personal-data", "certificates", "integration-docs", "applications"
- TC-D-002-07: Render FormViewer with each form, verify select dropdowns populate correctly

**Created:** 2025-12-16T19:45:00Z

---

## D-003: Sample Document Text Content

**Status:** proposed

**Description:**
Create realistic sample text files for POC testing with appropriate content for German integration course case. Files must include mix of German and English text reflecting real-world scenarios. Birth_Certificate.txt: German birth certificate with fields Vorname, Nachname, Geburtsdatum (15.05.1990), Geburtsort (Kabul), Staatsangehörigkeit (Afghanistan), certification stamps. Passport_Scan.txt: Passport number, issue/expiry dates, personal data matching birth certificate. Language_Certificate_A1.txt: Goethe Institut certificate showing A1 level completion, student name, issue date (2023-06-15). Integration_Application.txt: Partially filled application form with name, address, course preference (Intensive Course). School_Transcripts.txt: Education history from Kabul University. Confirmation_Email.txt: Email from bamf@example.de confirming application receipt. Each file 300-2000 characters, UTF-8 encoding, realistic formatting.

**Changes Required:**
- Data: Birth Certificate text file
  - Source: public/documents/Birth_Certificate.txt (new file)
  - Content: German certificate with personal details (Name: Ahmad Ali, Geboren: 15.05.1990, Geburtsort: Kabul, Afghanistan)
- Data: Passport Scan text file
  - Source: public/documents/Passport_Scan.txt (new file)
  - Content: Passport P123456789, Issue: 20.05.2020, Expiry: 20.05.2028, Name: AHMAD ALI
- Data: Language Certificate text file
  - Source: public/documents/Language_Certificate_A1.txt (new file)
  - Content: Goethe-Institut certificate, Niveau A1, Kursteilnehmer: Ahmad Ali, Ausstellungsdatum: 15.06.2023
- Data: Integration Application text file
  - Source: public/documents/Integration_Application.txt (new file)
  - Content: Application form fields with some filled values, course preference indicated
- Data: School Transcripts text file
  - Source: public/documents/School_Transcripts.txt (new file)
  - Content: Academic records from Kabul University, grades, completion date
- Data: Confirmation Email text file
  - Source: public/documents/Confirmation_Email.txt (new file)
  - Content: From: bamf@example.de, Subject: Application Received, Date: 18.01.2024, body confirming receipt

**Test Cases:**
- TC-D-003-01: Load Birth_Certificate.txt, verify contains "Ahmad Ali" and "15.05.1990"
- TC-D-003-02: Load Passport_Scan.txt, verify passport number P123456789 present
- TC-D-003-03: Send Language_Certificate_A1.txt to AI, ask "What level?", verify response mentions "A1"
- TC-D-003-04: Send Birth_Certificate.txt, command "/fillForm", verify name and birthDate extracted correctly
- TC-D-003-05: Verify all text files are valid UTF-8, no encoding errors when loading
- TC-D-003-06: Check file sizes, verify all files between 300-2000 characters
- TC-D-003-07: Load documents in DocumentViewer, verify German umlauts (ä, ö, ü) display correctly

**Created:** 2025-12-16T19:45:00Z

---
