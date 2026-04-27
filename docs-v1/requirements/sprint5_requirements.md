# Sprint 5 Requirements - Advanced AI Form Management & Multi-Document Processing

## Overview

Sprint 5 introduces advanced AI-powered form management with SHACL validation, multi-language support, improved document processing workflows, and enhanced file management. This sprint focuses on semantic form field creation, intelligent suggestion systems, multi-format document processing (images, PDFs, emails), and comprehensive case validation.

**Sprint Goal:** Enable natural language-driven form modifications with semantic validation, implement AI-powered document search and translation across multiple formats, improve document render management, and add comprehensive case validation capabilities.

---

## Functional Requirements

---

## S5-001: Natural Language Form Field Modification with SHACL Validation

**Status:** proposed

**Description:**
Enable administrators to modify existing forms using natural language commands through a dialog interface. When a field is added via natural language (e.g., "Add an email field", "Add a phone number field"), the system automatically generates SHACL shapes using schema.org vocabulary to assign semantic types and validation patterns. For example, an email field automatically gets pattern validation for '@' symbol (regex: `^[^\s@]+@[^\s@]+\.[^\s@]+$`), and a name field gets alphanumeric-only validation (regex: `^[a-zA-ZÀ-ÿ\s'-]+$`). The SHACL shape is created and updated in real-time as the form structure changes. A dialog icon in the FormViewer allows users to visualize the current SHACL shape for the entire form.

**Technical Requirements:**
- Natural language processing via Gemini API to interpret field modification commands
- Automatic SHACL PropertyShape generation using schema.org vocabulary
- Real-time SHACL shape synchronization when form structure changes
- SHACL visualization dialog in FormViewer showing JSON-LD representation
- Pattern validation based on semantic type (email, phone, name, date, etc.)
- Support for field operations: add, remove, modify, reorder

**Changes Required:**
- Frontend: Natural language input dialog in FormViewer
  - Source: src/components/workspace/FormViewer.tsx
  - Add: Dialog with textarea for natural language commands
  - Add: "Modify Form" button to open dialog
  - Add: Command history showing recent modifications
- Frontend: SHACL visualization dialog
  - Source: src/components/workspace/FormViewer.tsx
  - Add: "View SHACL" icon button in form header
  - Add: Dialog displaying JSON-LD formatted SHACL shape with syntax highlighting
  - Add: Copy to clipboard functionality for SHACL shape
- Backend: Form modification service endpoint
  - Source: backend/api/admin.py
  - Endpoint: POST /api/admin/modify-form
  - Request: { command: string, currentFields: FormField[], caseId: string }
  - Response: { fields: FormField[], shaclShape: SHACLNodeShape, modifications: string[] }
- Backend: SHACL generator with schema.org mapping
  - Source: backend/services/shacl_generator.py (new file)
  - Methods: generate_property_shape(field: FormField) -> SHACLPropertyShape
  - Methods: generate_node_shape(fields: List[FormField]) -> SHACLNodeShape
  - Methods: get_schema_org_type(field_type: str, field_label: str) -> str
  - Methods: get_validation_pattern(semantic_type: str) -> Optional[str]
- Backend: Schema.org mapping definitions
  - Source: backend/schemas/schema_org_mappings.py (new file)
  - Mappings: email -> schema:email with email regex pattern
  - Mappings: phone -> schema:telephone with phone regex pattern
  - Mappings: name -> schema:name with alphanumeric pattern
  - Mappings: date -> schema:Date with ISO date pattern
  - Mappings: address -> schema:address with address pattern
- Frontend: Update FormField interface to track SHACL validation
  - Source: src/types/case.ts
  - Add: validationPattern?: string to FormField interface
  - Add: semanticType?: string to FormField interface
- Frontend: Client-side SHACL validation on form submission
  - Source: src/components/workspace/FormViewer.tsx
  - Add: validateFieldWithSHACL(field: FormField, value: string) -> ValidationResult
  - Add: Display validation errors inline under each field
- Types: SHACL shape response types
  - Source: src/types/shacl.ts
  - Add: FormModificationResponse interface
  - Add: ValidationResult interface with isValid, errors properties

**SHACL Pattern Examples:**
```json
{
  "email": {
    "sh:path": "schema:email",
    "sh:pattern": "^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$",
    "sh:message": "Email must contain @ symbol and valid domain"
  },
  "name": {
    "sh:path": "schema:name",
    "sh:pattern": "^[a-zA-ZÀ-ÿ\\s'-]+$",
    "sh:message": "Name must contain only letters, spaces, hyphens, and apostrophes"
  },
  "phone": {
    "sh:path": "schema:telephone",
    "sh:pattern": "^[\\d\\s\\+\\-\\(\\)]+$",
    "sh:message": "Phone number contains invalid characters"
  }
}
```

**Test Cases:**
- TC-S5-001-01: Enter "Add an email field for contact email", verify field created with type="text", validationPattern includes '@'
- TC-S5-001-02: Verify generated SHACL shape has sh:path="schema:email" and sh:pattern for email validation
- TC-S5-001-03: Enter "Add a phone number field", verify field has sh:pattern="^[\\d\\s\\+\\-\\(\\)]+$"
- TC-S5-001-04: Enter "Add a name field for applicant full name", verify field has alphanumeric-only validation pattern
- TC-S5-001-05: Click "View SHACL" icon, verify dialog displays complete JSON-LD SHACL shape for all form fields
- TC-S5-001-06: Modify form by adding a field, verify SHACL shape updates automatically in real-time
- TC-S5-001-07: Enter invalid email "testexample.com" in email field, verify validation error displayed inline
- TC-S5-001-08: Enter name with numbers "John123", verify validation error "Name must contain only letters"
- TC-S5-001-09: Enter "Remove the phone number field", verify field removed and SHACL shape updated
- TC-S5-001-10: Enter ambiguous command "Add a field", verify clarification request from AI
- TC-S5-001-11: Copy SHACL shape to clipboard, verify valid JSON-LD format
- TC-S5-001-12: Add date field, verify sh:datatype="xsd:date" and sh:pattern for ISO date format

**Created:** 2026-01-09T16:00:00Z

---

## S5-002: AI Form Fill with Suggested Values and UX Module

**Status:** proposed

**Description:**
Enhance the existing "/fill form" slash command to intelligently handle cases where form fields already contain data. When the AI Gemini model analyzes a document and finds data that could populate the form, it compares with existing values. If a field is already populated but the AI finds a different or additional value, the system presents the AI-suggested value as a suggestion underneath the current value with an elegant UX module. The module displays the suggested value with a checkmark icon to accept and an X icon to reject. This avoids disruptive popups or extra views while maintaining clarity. Multiple fields can have suggestions simultaneously.

**Technical Requirements:**
- Gemini analyzes document content and extracts potential field values
- Compare extracted values with current form field values
- Generate suggestions only when extracted value differs from current value
- Display suggestions inline under form fields with accept/reject actions
- Support multiple simultaneous suggestions across different fields
- Maintain suggestion state until user accepts or rejects
- Track suggestion confidence scores to prioritize high-confidence suggestions

**Changes Required:**
- Backend: Enhanced form extraction with value comparison
  - Source: backend/tools/form_parser.py
  - Update: extract_form_data() to return both values and confidence scores
  - Add: compare_values(current: str, extracted: str) -> ValueComparison
  - Add: ValueComparison model with fields: isDifferent, confidence, reason
- Backend: Update form fill WebSocket message
  - Source: backend/api/chat.py
  - Update: Handle /fill-form command with existing field values
  - Response: FormSuggestionMessage with suggestions array
- Frontend: Suggested value UX component
  - Source: src/components/workspace/SuggestedValue.tsx (new file)
  - Props: currentValue, suggestedValue, confidence, onAccept, onReject, fieldLabel
  - Visual: Chip/badge showing "Suggested: [value]" with check/X icons
  - Styling: Subtle background color (blue-50), inline display under field
- Frontend: Integrate suggestions into FormViewer
  - Source: src/components/workspace/FormViewer.tsx
  - Add: suggestions state mapping fieldId to SuggestedValue
  - Add: Display SuggestedValue component under fields with suggestions
  - Add: handleAcceptSuggestion(fieldId) to update field value
  - Add: handleRejectSuggestion(fieldId) to dismiss suggestion
- Frontend: Update form fill command handler
  - Source: src/components/workspace/AIChatInterface.tsx
  - Update: /fill-form command to send current form values in request
  - Add: Handle form_suggestion message type from WebSocket
- Types: Form suggestion message types
  - Source: src/types/websocket.ts
  - Add: FormSuggestionMessage interface
  - Add: FieldSuggestion interface with fieldId, currentValue, suggestedValue, confidence
- Types: Suggestion state types
  - Source: src/types/case.ts
  - Add: SuggestedValue interface with value, confidence, source
  - Add: FormSuggestions type as Record<string, SuggestedValue>

**UX Module Design:**
```tsx
// Under each form field with suggestion
<div className="mt-1 flex items-center gap-2 text-sm">
  <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-50 rounded-md border border-blue-200">
    <span className="text-blue-700">Suggested: {suggestedValue}</span>
    <span className="text-blue-500 text-xs">({confidence}% confidence)</span>
    <button onClick={onAccept} className="text-green-600 hover:text-green-700">
      <Check size={16} />
    </button>
    <button onClick={onReject} className="text-red-600 hover:text-red-700">
      <X size={16} />
    </button>
  </div>
</div>
```

**Test Cases:**
- TC-S5-002-01: Form field "Name" has value "John Doe", run /fill-form with document containing "John David Doe", verify suggestion appears
- TC-S5-002-02: Verify suggestion displays inline under field with check and X icons
- TC-S5-002-03: Click check icon, verify field value updates to suggested value and suggestion disappears
- TC-S5-002-04: Click X icon, verify suggestion is dismissed without changing field value
- TC-S5-002-05: Multiple fields have suggestions, verify all display simultaneously without layout issues
- TC-S5-002-06: Form field empty, run /fill-form, verify value fills directly without suggestion (no suggestion for empty fields)
- TC-S5-002-07: Suggested value identical to current value, verify no suggestion displayed
- TC-S5-002-08: Verify confidence score displays as percentage (e.g., "85% confidence")
- TC-S5-002-09: Accept suggestion, verify chat message confirms "Updated field 'Name' with suggested value"
- TC-S5-002-10: Run /fill-form twice on different documents, verify suggestions update correctly
- TC-S5-002-11: Navigate away from form and back, verify dismissed suggestions remain dismissed
- TC-S5-002-12: Field with low confidence suggestion (<50%), verify displayed with warning color (yellow)

**Created:** 2026-01-09T16:00:00Z

---

## S5-003: Semantic Search with Multi-Language Support

**Status:** proposed

**Description:**
Implement a semantic search button in the DocumentViewer that allows users to search for information within documents using natural language queries. The system highlights relevant paragraphs, words, or phrases where the information exists. Multiple highlights can appear in a single document. The search uses Google Gemini API for semantic understanding. PDFs are automatically processed and sent to Gemini for analysis. Multi-language support is built-in: if the user makes a request in German and the document is in English, Gemini handles the translation and highlights the English text that corresponds to the German query (and vice versa for any language pair).

**Technical Requirements:**
- Semantic search powered by Gemini AI with document context
- Highlight matching text in DocumentViewer with visual emphasis
- Support multiple simultaneous highlights in different locations
- Multi-language query-document matching (German query → English document highlights)
- Automatic PDF text extraction and processing for Gemini
- Search button integrated in DocumentViewer toolbar
- Display search results count and navigation between highlights

**Changes Required:**
- Frontend: Search interface in DocumentViewer
  - Source: src/components/workspace/DocumentViewer.tsx
  - Add: "Search" button in toolbar with search icon
  - Add: Search dialog with input field for semantic query
  - Add: Results indicator showing "X matches found"
  - Add: Navigation arrows to jump between highlights (previous/next)
- Frontend: Text highlighting component
  - Source: src/components/workspace/HighlightedText.tsx (new file)
  - Component: Wraps document text with highlight markers
  - Props: text, highlights (array of { start, end, relevance })
  - Styling: Yellow background for highlights, darker yellow for active highlight
- Frontend: Search state management
  - Source: src/contexts/AppContext.tsx
  - Add: searchQuery state
  - Add: searchHighlights state (array of text ranges)
  - Add: activeHighlightIndex state
  - Add: performSemanticSearch(query: string, documentId: string) function
- Backend: Semantic search endpoint
  - Source: backend/api/search.py (new file)
  - Endpoint: POST /api/search/semantic
  - Request: { query: string, documentContent: string, documentType: string, queryLanguage: string, documentLanguage: string }
  - Response: { highlights: SearchHighlight[], count: number, matchSummary: string }
- Backend: PDF text extraction service
  - Source: backend/services/pdf_service.py (new file)
  - Methods: extract_text_with_positions(pdf_path: string) -> List[TextBlock]
  - Methods: TextBlock model with text, page, position coordinates
  - Dependencies: PyPDF2 or pdfplumber for text extraction
- Backend: Gemini semantic search integration
  - Source: backend/services/gemini_service.py
  - Add: semantic_search(query: string, document_text: string, query_lang: string, doc_lang: string) -> List[SearchHighlight]
  - Add: Prompt engineering for cross-language semantic matching
  - Add: Return text ranges/positions of relevant passages
- Backend: Multi-language detection
  - Source: backend/tools/language_detector.py (new file)
  - Method: detect_language(text: string) -> str (ISO 639-1 code)
  - Use: langdetect library or Gemini API for language detection
- Types: Search result types
  - Source: src/types/search.ts (new file)
  - Interface: SearchHighlight with start, end, relevance, matchedText, context
  - Interface: SemanticSearchRequest and SemanticSearchResponse
- Frontend: Scroll to highlight functionality
  - Source: src/components/workspace/DocumentViewer.tsx
  - Add: scrollToHighlight(index: number) using refs and scrollIntoView
  - Add: Active highlight indicator with border or different color

**Gemini Prompt Template for Semantic Search:**
```python
f"""Analyze the following document and find all passages relevant to the user's query.

Query (in {query_language}): {query}

Document (in {document_language}):
{document_text}

Return a JSON array of all relevant text passages with their exact positions in the document.
If the query and document languages differ, match by semantic meaning, not literal translation.

Format:
[
  {{
    "matched_text": "exact text from document",
    "start_position": character_index,
    "end_position": character_index,
    "relevance_score": 0.0-1.0,
    "context": "brief explanation of why this matches"
  }}
]
"""
```

**Test Cases:**
- TC-S5-003-01: Click Search button, verify search dialog opens with input field
- TC-S5-003-02: Enter query "passport number", verify Gemini finds and highlights relevant text
- TC-S5-003-03: Document has 3 matching paragraphs, verify all 3 highlighted with yellow background
- TC-S5-003-04: Query in German "Reisepassnummer" on English document with "passport number", verify English text highlighted
- TC-S5-003-05: Query in English "birth date" on German document with "Geburtsdatum", verify German text highlighted
- TC-S5-003-06: Verify search results indicator shows "3 matches found"
- TC-S5-003-07: Click next arrow, verify navigation to second highlight with active indicator
- TC-S5-003-08: Click previous arrow, verify navigation back to first highlight
- TC-S5-003-09: PDF document, verify text extracted automatically and search works correctly
- TC-S5-003-10: Perform search with no matches, verify message "No matches found"
- TC-S5-003-11: Multiple words/phrases highlighted, verify each has individual highlight span
- TC-S5-003-12: Close search, verify highlights clear and document returns to normal view
- TC-S5-003-13: Semantic query "when was the person born" matches "Date of Birth: 15.05.1990"
- TC-S5-003-14: Search in Arabic document with German query, verify cross-language matching works

**Created:** 2026-01-09T16:00:00Z

---

## S5-004: Multi-Format Translation Service

**Status:** proposed

**Description:**
Implement a comprehensive translation service supporting three document types: text documents, images, and PDFs. When the Translation button is clicked:
- **Text documents**: Produce a new text document with translated content
- **Images**: Produce a new image with masked/overlaid text in the target language (similar to Google Lens translation feature)
- **PDFs**: Extract text from PDF, translate it, and produce a new PDF with translated text replacing original text (preserving layout)

The service handles pre-processing and post-processing of PDFs. When translating images, the system detects text regions, translates the text, and overlays the translation in the same visual location. For PDFs, text is extracted while preserving structure, translated, and re-injected into the PDF layout.

**Technical Requirements:**
- Gemini API for text translation (all language pairs)
- OCR for text detection in images (Tesseract or Google Cloud Vision)
- Image manipulation for text overlay (PIL/Pillow)
- PDF text extraction and manipulation (PyPDF2, ReportLab)
- Translation button in DocumentViewer toolbar
- Automatic render creation (original → translated render)
- Support for multiple languages (German, English, Arabic, etc.)

**Changes Required:**
- Frontend: Translation button in DocumentViewer
  - Source: src/components/workspace/DocumentViewer.tsx
  - Add: "Translate" button in toolbar with globe icon
  - Add: Language selection dropdown (target language)
  - Add: Loading indicator during translation process
  - Add: Automatic switch to translated render on completion
- Backend: Translation orchestration service
  - Source: backend/services/translation_service.py (new file)
  - Methods: translate_document(file_path: string, source_lang: string, target_lang: string, doc_type: string) -> TranslationResult
  - Methods: Routing logic based on document type (text/image/pdf)
- Backend: Text document translation
  - Source: backend/services/translation_service.py
  - Method: translate_text_document(content: string, source_lang: string, target_lang: string) -> string
  - Uses: Gemini API for translation
- Backend: Image translation service
  - Source: backend/services/image_translation_service.py (new file)
  - Methods: translate_image(image_path: string, source_lang: string, target_lang: string) -> str (output_path)
  - Step 1: OCR to detect text regions with bounding boxes (using Tesseract)
  - Step 2: Extract text from each region
  - Step 3: Translate text via Gemini
  - Step 4: Overlay translated text on image at same position (using Pillow)
  - Step 5: Save as new image with _translated suffix
- Backend: PDF translation service
  - Source: backend/services/pdf_translation_service.py (new file)
  - Methods: translate_pdf(pdf_path: string, source_lang: string, target_lang: string) -> str (output_path)
  - Step 1: Extract text from PDF with position metadata (PyPDF2)
  - Step 2: Translate all text via Gemini (batch translation)
  - Step 3: Create new PDF with translated text in original positions (ReportLab)
  - Step 4: Preserve original layout, fonts, and structure
  - Note: PDF images are ignored, only text is translated
- Backend: Translation API endpoint
  - Source: backend/api/translation.py (new file)
  - Endpoint: POST /api/translate/document
  - Request: { filePath: string, caseId: string, folderId: string, sourceLanguage: string, targetLanguage: string }
  - Response: { success: boolean, translatedPath: string, documentType: string }
- Backend: OCR integration
  - Source: backend/services/ocr_service.py (new file)
  - Methods: detect_text_regions(image_path: string) -> List[TextRegion]
  - Methods: TextRegion model with text, bbox (x, y, width, height), confidence
  - Dependencies: pytesseract, Pillow
- Frontend: Update document renders management
  - Source: src/contexts/AppContext.tsx
  - Add: addDocumentRender(originalDocId: string, renderType: string, renderPath: string)
  - Add: DocumentRender type with originalId, renderType ('translated' | 'anonymized'), path
- Frontend: API client for translation
  - Source: src/lib/translationApi.ts (new file)
  - Function: translateDocument(filePath: string, targetLanguage: string) -> Promise<TranslationResult>
- Types: Translation result types
  - Source: src/types/translation.ts (new file)
  - Interface: TranslationResult with success, translatedPath, sourceLanguage, targetLanguage
  - Interface: TextRegion with text, bbox, confidence

**Translation Workflow Example (Image):**
```python
# backend/services/image_translation_service.py
def translate_image(image_path, source_lang, target_lang):
    # 1. Load image
    img = Image.open(image_path)

    # 2. OCR to detect text regions
    text_regions = ocr_service.detect_text_regions(image_path)

    # 3. Translate each text region
    translations = []
    for region in text_regions:
        translated_text = gemini_service.translate(region.text, source_lang, target_lang)
        translations.append((region.bbox, translated_text))

    # 4. Overlay translated text on image
    draw = ImageDraw.Draw(img)
    for bbox, translated_text in translations:
        # Mask original text with background color
        draw.rectangle(bbox, fill='white')
        # Draw translated text at same position
        draw.text((bbox[0], bbox[1]), translated_text, fill='black', font=font)

    # 5. Save translated image
    output_path = image_path.replace('.png', '_translated.png')
    img.save(output_path)
    return output_path
```

**Test Cases:**
- TC-S5-004-01: Click Translate on text document, select German → English, verify new text file created with English content
- TC-S5-004-02: Translate image with German text to English, verify new image has English text overlaid
- TC-S5-004-03: Verify original text in image is masked/covered before overlay
- TC-S5-004-04: Translate PDF with German text, verify new PDF has English text in same layout positions
- TC-S5-004-05: PDF with images and text, verify only text is translated, images remain unchanged
- TC-S5-004-06: Verify translated document has "_translated" suffix in filename
- TC-S5-004-07: Translate document twice (English → German → French), verify multiple renders created
- TC-S5-004-08: Translate Arabic text to German in image, verify RTL text handled correctly
- TC-S5-004-09: Click Translate, verify loading indicator shown during processing
- TC-S5-004-10: Translation completes, verify UI auto-switches to display translated document
- TC-S5-004-11: Multi-paragraph text document, verify all paragraphs translated maintaining structure
- TC-S5-004-12: Image with multiple text regions, verify all regions translated and positioned correctly
- TC-S5-004-13: Large PDF (10+ pages), verify all pages translated successfully
- TC-S5-004-14: Translation fails (network error), verify error message displayed gracefully

**Created:** 2026-01-09T16:00:00Z

---

## S5-005: Case Validation Agent

**Status:** proposed

**Description:**
Implement an AI-powered case validation system that assesses whether a case is complete according to the required documents for that case type. The validation agent analyzes the available context (case type, required documents list from case.json) and the actual documents present in the case folders. The system performs intelligent document name matching across languages (e.g., "Reisepass" → "passport", "Geburtsurkunde" → "birth certificate"). When the user clicks the "Validate Case" button, the agent provides a detailed breakdown:
- List of present documents with confirmation
- List of missing critical documents
- List of missing optional documents
- Overall case status (Complete / Incomplete / Needs Clarification)

If the navigation is inside a specific folder, the validation scopes to that folder only, checking if expected documents for that folder type are present (without reading document contents, purely by document name and type inference).

**Technical Requirements:**
- Context-aware validation using case.json required documents list
- Multi-language document name matching (German ↔ English ↔ Arabic)
- Folder-scoped validation when inside a folder
- Case-level validation when at case root
- Gemini AI for intelligent document name inference and categorization
- Validation button in workspace toolbar
- Detailed validation report in chat interface

**Changes Required:**
- Backend: Case validation service
  - Source: backend/services/validation_service.py (new file)
  - Methods: validate_case(case_id: string) -> ValidationReport
  - Methods: validate_folder(case_id: string, folder_id: string) -> FolderValidationReport
  - Methods: match_document_name(document_name: string, expected_doc_types: List[str], languages: List[str]) -> Optional[str]
- Backend: Document name matching with Gemini
  - Source: backend/services/validation_service.py
  - Method: infer_document_type(document_name: string, context: str) -> DocumentTypeInference
  - Uses: Gemini to understand document type from name in any language
  - Example: "Personalausweis.png" → matches "passport" or "id_card"
- Backend: Required documents loader
  - Source: backend/services/context_manager.py
  - Update: load_case_context() to include requiredDocuments array
  - Update: load_folder_context() to include expectedDocuments array
- Backend: Validation API endpoint
  - Source: backend/api/validation.py (new file)
  - Endpoint: POST /api/validate/case
  - Request: { caseId: string, folderId?: string }
  - Response: { status: string, report: ValidationReport, summary: string }
- Backend: Validation report model
  - Source: backend/models/validation.py (new file)
  - Class: ValidationReport with fields:
    - status: 'complete' | 'incomplete' | 'needs_clarification'
    - presentDocuments: List[PresentDocument] (name, type, folder)
    - missingCriticalDocuments: List[MissingDocument] (type, importance, suggestions)
    - missingOptionalDocuments: List[MissingDocument]
    - overallScore: float (0.0-1.0)
    - recommendations: List[str]
- Frontend: Validate Case button
  - Source: src/components/workspace/WorkspaceHeader.tsx
  - Add: "Validate Case" button in toolbar with shield-check icon
  - Add: Loading state during validation
  - Add: Badge showing validation status (complete/incomplete)
- Frontend: Validation report display
  - Source: src/components/workspace/ValidationReportDialog.tsx (new file)
  - Component: Dialog showing detailed validation results
  - Sections: Present Documents (green), Missing Critical (red), Missing Optional (yellow)
  - Visual: Progress bar showing completion percentage
  - Actions: "Add Document" quick link for each missing document
- Frontend: Integrate validation in chat
  - Source: src/components/workspace/AIChatInterface.tsx
  - Add: /validate-case slash command
  - Add: Validation report as formatted chat message with expandable sections
- Types: Validation types
  - Source: src/types/validation.ts (new file)
  - Interface: ValidationReport
  - Interface: PresentDocument with name, type, folder, matchConfidence
  - Interface: MissingDocument with type, importance ('critical' | 'optional'), suggestions
  - Type: ValidationStatus = 'complete' | 'incomplete' | 'needs_clarification'

**Validation Report Example:**
```json
{
  "status": "incomplete",
  "overallScore": 0.65,
  "presentDocuments": [
    { "name": "Anmeldeformular.pdf", "type": "application_form", "folder": "applications", "matchConfidence": 0.95 },
    { "name": "Geburtsurkunde.jpg", "type": "birth_certificate", "folder": "personal-data", "matchConfidence": 0.98 }
  ],
  "missingCriticalDocuments": [
    { "type": "passport", "importance": "critical", "suggestions": ["Check Personal Data folder", "Alternative: ID card (Personalausweis)"] }
  ],
  "missingOptionalDocuments": [
    { "type": "language_certificate", "importance": "optional", "suggestions": ["Recommended for faster processing"] }
  ],
  "recommendations": [
    "Upload passport scan to Personal Data folder",
    "Consider adding language certificate to strengthen application"
  ],
  "summary": "Case is incomplete. Application form and birth certificate are present, but passport is missing. Passport is required for case completion."
}
```

**Gemini Prompt for Document Matching:**
```python
f"""You are a document validation expert. Match the document name to expected document types.

Document name: {document_name}
Expected document types for this case: {', '.join(expected_types)}
Case type: {case_type}

Consider:
- Multi-language matching (German, English, Arabic)
- Common abbreviations and variations
- Context from case type

Examples:
- "Reisepass" or "Pass" → passport
- "Geburtsurkunde" → birth_certificate
- "Personalausweis" → id_card or passport (alternative)
- "Email.eml" → correspondence or communication

Return JSON:
{{
  "matched_type": "document_type or null",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}}
"""
```

**Test Cases:**
- TC-S5-005-01: Click Validate Case, verify validation report displayed in dialog
- TC-S5-005-02: Case with all required documents present, verify status="complete" and score=1.0
- TC-S5-005-03: Case missing passport, verify missingCriticalDocuments includes "passport"
- TC-S5-005-04: Document named "Reisepass.png" matches required "passport", verify matched correctly
- TC-S5-005-05: Document named "Personalausweis.png", verify suggested as alternative to passport
- TC-S5-005-06: Validation in German document names, verify English expected types matched correctly
- TC-S5-005-07: Navigate to "Personal Data" folder, click Validate, verify only folder documents checked
- TC-S5-005-08: Folder validation, verify report says "Validating Personal Data folder only"
- TC-S5-005-09: Ambiguous document name "Document1.pdf", verify status="needs_clarification" with recommendation
- TC-S5-005-10: Type /validate-case in chat, verify validation triggered and report shown in chat
- TC-S5-005-11: Validation report, click "Add Document" for missing passport, verify upload dialog opens
- TC-S5-005-12: Case with no documents, verify all required documents listed as missing
- TC-S5-005-13: Document "Email.eml" in Emails folder, verify matched to correspondence type
- TC-S5-005-14: Arabic document name "جواز سفر" (passport in Arabic), verify matched correctly

**Created:** 2026-01-09T16:00:00Z

---

## S5-006: Document Renders Management System

**Status:** proposed

**Description:**
Replace the current document cloning system with a document renders management system. Instead of creating separate clone documents when anonymizing, translating, or modifying documents, the system creates different "renders" of the same document. A document can have multiple renders (original, anonymized, translated_de, translated_en, etc.). In the document explorer (left sidebar), when a document has multiple renders, it appears inside a collapsible container/folder showing all available renders. Users can click on any render to view that version. This approach keeps the document tree clean while maintaining access to all versions.

**Technical Requirements:**
- Document renders stored as metadata array on parent document
- Collapsible render container in CaseTreeExplorer
- Visual indication of multi-render documents (icon or badge)
- Render types: 'original', 'anonymized', 'translated_{lang}', 'annotated'
- Clicking a render switches the DocumentViewer to display that render
- Delete render option (keeping original)
- Automatic render creation when anonymizing or translating

**Changes Required:**
- Types: Document render data structures
  - Source: src/types/case.ts
  - Update: Document interface to include renders?: DocumentRender[]
  - Add: DocumentRender interface with id, type, name, filePath, createdAt, metadata
  - Add: RenderType = 'original' | 'anonymized' | 'translated' | 'annotated'
- Frontend: Render container in document tree
  - Source: src/components/workspace/CaseTreeExplorer.tsx
  - Add: RenderContainer component for documents with multiple renders
  - Add: Collapsible/expandable render list under parent document
  - Add: Visual indicator (chevron icon) showing document has renders
  - Add: Indent renders under parent document
- Frontend: Render selection handling
  - Source: src/contexts/AppContext.tsx
  - Add: selectedRender state tracking which render is active
  - Update: selectDocument() to handle render selection
  - Add: getRenderPath(documentId: string, renderId: string) -> string
- Backend: Render metadata storage
  - Source: backend/services/file_service.py
  - Add: add_document_render(document_id: string, render_type: string, file_path: string) -> DocumentRender
  - Add: get_document_renders(document_id: string) -> List[DocumentRender]
  - Add: delete_document_render(document_id: string, render_id: string) -> bool
- Backend: Update anonymization to create renders
  - Source: backend/tools/anonymization_tool.py
  - Update: Return render metadata instead of new document
  - Update: WebSocket response includes renderType='anonymized'
- Backend: Update translation to create renders
  - Source: backend/services/translation_service.py
  - Update: Return render metadata with renderType='translated_{lang}'
- Frontend: Delete render functionality
  - Source: src/components/workspace/CaseTreeExplorer.tsx
  - Add: Delete icon (trash) on render items (not visible on original)
  - Add: Confirmation dialog "Delete this render?"
  - Add: API call to delete render file and metadata
- Frontend: Render type icons
  - Source: src/components/workspace/CaseTreeExplorer.tsx
  - Add: Icon mapping for render types
    - original: FileText
    - anonymized: EyeOff
    - translated: Globe
    - annotated: Edit
- Frontend: Automatic collapse when single render
  - Source: src/components/workspace/CaseTreeExplorer.tsx
  - Logic: If document has only one render (original), display as normal file
  - Logic: If document has 2+ renders, display as expandable container

**Render Container UI Example:**
```tsx
// Document with multiple renders
<div className="document-with-renders">
  <div className="document-header" onClick={toggleExpand}>
    <ChevronRight className={expanded ? 'rotate-90' : ''} />
    <FileText />
    <span>Birth_Certificate.jpg</span>
    <Badge variant="secondary">{renderCount} renders</Badge>
  </div>
  {expanded && (
    <div className="renders-list ml-6">
      <div className="render-item" onClick={() => selectRender('original')}>
        <FileText size={14} />
        <span>Original</span>
      </div>
      <div className="render-item" onClick={() => selectRender('anonymized')}>
        <EyeOff size={14} />
        <span>Anonymized</span>
        <button onClick={deleteRender}><Trash size={12} /></button>
      </div>
      <div className="render-item" onClick={() => selectRender('translated_de')}>
        <Globe size={14} />
        <span>German Translation</span>
        <button onClick={deleteRender}><Trash size={12} /></button>
      </div>
    </div>
  )}
</div>
```

**Test Cases:**
- TC-S5-006-01: Document with only original render, verify displays as normal file (no expansion)
- TC-S5-006-02: Anonymize document, verify document converts to expandable container with 2 renders
- TC-S5-006-03: Click expand chevron, verify renders list shows "Original" and "Anonymized"
- TC-S5-006-04: Click "Anonymized" render, verify DocumentViewer displays anonymized version
- TC-S5-006-05: Translate document to German, verify third render "German Translation" appears
- TC-S5-006-06: Badge shows "3 renders" when document has 3 renders
- TC-S5-006-07: Click delete icon on anonymized render, verify confirmation dialog appears
- TC-S5-006-08: Confirm delete render, verify render removed from list and file deleted
- TC-S5-006-09: Delete all renders except original, verify document reverts to normal file display
- TC-S5-006-10: Verify original render cannot be deleted (no delete button)
- TC-S5-006-11: Create multiple translations (German, English, French), verify all listed under parent
- TC-S5-006-12: Refresh page, verify render structure persists (loaded from metadata)
- TC-S5-006-13: Render icons display correctly (EyeOff for anonymized, Globe for translated)
- TC-S5-006-14: Collapse expanded document, verify renders hidden but selection maintained

**Created:** 2026-01-09T16:00:00Z

---

## S5-007: Container-Compatible File Persistence

**Status:** proposed

**Description:**
Fix file persistence issues when restarting the application, particularly in preparation for dockerization. Currently, some documents remain in the file system after restart but are not visible to the frontend. Implement a robust document storage system that persists across restarts by maintaining a document registry/manifest. The system should use a consistent local path for document storage (e.g., `/var/app/documents/` inside container, mapped to host volume). When the app starts, it scans the documents directory and rebuilds the document tree from the file system. This ensures that uploaded documents persist and remain visible even after container restarts. For now, focus on local machine paths; Docker volume mapping will be addressed in final deployment phase.

**Technical Requirements:**
- Document registry/manifest file tracking all documents
- Automatic document tree rebuild on application start
- Consistent document storage path across restarts
- File system scanning on startup to sync with manifest
- Handle orphaned files (in filesystem but not in manifest)
- Handle missing files (in manifest but not in filesystem)
- Container-friendly architecture (single root document path)

**Changes Required:**
- Backend: Document registry service
  - Source: backend/services/document_registry.py (new file)
  - Methods: register_document(case_id: string, folder_id: string, document: Document) -> bool
  - Methods: unregister_document(document_id: string) -> bool
  - Methods: get_all_documents() -> List[DocumentRegistryEntry]
  - Methods: rebuild_from_filesystem(base_path: string) -> DocumentTree
  - Methods: sync_manifest_with_filesystem() -> SyncReport
- Backend: Document manifest storage
  - Source: backend/data/document_manifest.json (new file)
  - Format: JSON array of DocumentRegistryEntry
  - Fields: documentId, caseId, folderId, fileName, filePath, uploadedAt, renders
  - Persistence: Saved after every document operation (upload, delete, render creation)
- Backend: Startup document scan
  - Source: backend/main.py
  - Add: @app.on_event("startup") async def scan_documents()
  - Logic: Load manifest, scan filesystem, reconcile differences
  - Logic: Add orphaned files to manifest, mark missing files
- Backend: File storage path configuration
  - Source: backend/config.py (new file or update existing)
  - Constant: DOCUMENTS_BASE_PATH = os.getenv("DOCUMENTS_PATH", "public/documents")
  - Note: For containers, this will be "/var/app/documents" mounted as volume
- Backend: Reconciliation logic
  - Source: backend/services/document_registry.py
  - Method: reconcile(manifest: List[DocumentEntry], filesystem: List[FilePath]) -> ReconcileReport
  - Logic: Find orphaned files (on disk but not in manifest) and add them
  - Logic: Find missing files (in manifest but not on disk) and mark as missing
  - Logic: Verify file hashes for integrity check
- Backend: Update file operations to use registry
  - Source: backend/api/files.py
  - Update: upload_file() to call document_registry.register_document()
  - Update: delete_file() to call document_registry.unregister_document()
- Backend: Document tree builder from manifest
  - Source: backend/services/document_registry.py
  - Method: build_document_tree(case_id: string) -> CaseTree
  - Logic: Read manifest entries for case, organize into folder structure
- Frontend: Load document tree from backend on startup
  - Source: src/contexts/AppContext.tsx
  - Add: loadDocumentsFromBackend() async function
  - Add: useEffect on app mount to fetch document tree
  - API: GET /api/documents/tree/{caseId}
- Backend: Document tree API endpoint
  - Source: backend/api/documents.py (new file)
  - Endpoint: GET /api/documents/tree/{case_id}
  - Response: { folders: Folder[], documents: Document[] }
  - Source: Reads from document registry
- Types: Document registry types
  - Source: src/types/document-registry.ts (new file)
  - Interface: DocumentRegistryEntry
  - Interface: DocumentTree
  - Interface: ReconcileReport with added, removed, missing arrays

**Document Manifest Format:**
```json
{
  "version": "1.0",
  "lastUpdated": "2026-01-09T16:30:00Z",
  "documents": [
    {
      "documentId": "doc_001",
      "caseId": "ACTE-2024-001",
      "folderId": "personal-data",
      "fileName": "Birth_Certificate.jpg",
      "filePath": "public/documents/ACTE-2024-001/personal-data/Birth_Certificate.jpg",
      "uploadedAt": "2026-01-08T10:00:00Z",
      "fileHash": "sha256:abc123...",
      "renders": [
        {
          "renderId": "render_001",
          "type": "anonymized",
          "filePath": "public/documents/ACTE-2024-001/personal-data/Birth_Certificate_anonymized.jpg",
          "createdAt": "2026-01-08T10:15:00Z"
        }
      ]
    }
  ]
}
```

**Startup Reconciliation Flow:**
```python
# backend/main.py
@app.on_event("startup")
async def startup_event():
    logger.info("Starting document registry reconciliation...")

    # Load manifest
    manifest = document_registry.load_manifest()

    # Scan filesystem
    filesystem_docs = document_registry.scan_filesystem(DOCUMENTS_BASE_PATH)

    # Reconcile
    report = document_registry.reconcile(manifest, filesystem_docs)

    logger.info(f"Reconciliation complete: {len(report.added)} added, {len(report.missing)} missing")

    # Save updated manifest
    document_registry.save_manifest()
```

**Test Cases:**
- TC-S5-007-01: Upload document, restart app, verify document visible in frontend
- TC-S5-007-02: Upload document, verify entry added to document_manifest.json
- TC-S5-007-03: Manually add file to documents folder, restart app, verify file detected and added to manifest
- TC-S5-007-04: Delete file from filesystem, restart app, verify marked as missing in logs (not shown in UI)
- TC-S5-007-05: Document in manifest but missing from disk, verify startup logs warning "Missing file: ..."
- TC-S5-007-06: Multiple documents across cases, verify all loaded correctly on startup
- TC-S5-007-07: Document with renders, restart app, verify render structure preserved
- TC-S5-007-08: Check manifest file hash matches actual file, verify integrity validation
- TC-S5-007-09: Corrupt manifest file, verify app creates new manifest from filesystem scan
- TC-S5-007-10: GET /api/documents/tree/ACTE-2024-001, verify returns complete folder structure
- TC-S5-007-11: Upload document, delete from manifest only (not disk), restart, verify re-added to manifest
- TC-S5-007-12: Simulate container restart, verify all documents persist and load correctly

**Created:** 2026-01-09T16:00:00Z

---

## S5-008: Email File Support (.eml)

**Status:** proposed

**Description:**
Add support for email files (.eml format) in the document management system. Users can drag and drop .eml files into the case folders. Email files are parsed to extract sender, recipient, subject, body, and attachments. When translating an email, the system automatically translates to German (default target language) and creates a new render as discussed in S5-006. The email viewer displays email metadata (From, To, Subject, Date) and the formatted body content. Emails often contain Arabic text in case management scenarios.

**Technical Requirements:**
- Support .eml file format in document types
- Email parsing library (Python email module)
- Extract email headers (From, To, Subject, Date)
- Extract email body (plain text and HTML)
- Display email content with proper formatting in DocumentViewer
- Translation support for emails (body text only)
- Drag-and-drop upload for .eml files
- Email content rendered with metadata headers

**Changes Required:**
- Types: Add email document type
  - Source: src/types/case.ts
  - Update: Document type union to include 'eml'
  - Add: EmailMetadata interface with from, to, subject, date, body, attachments
- Backend: Email parsing service
  - Source: backend/services/email_service.py (new file)
  - Methods: parse_eml_file(file_path: string) -> EmailData
  - Methods: extract_headers(email_msg: Message) -> EmailHeaders
  - Methods: extract_body(email_msg: Message) -> EmailBody with text and html
  - Methods: extract_attachments(email_msg: Message) -> List[Attachment]
  - Dependencies: Python email module, html2text for HTML conversion
- Backend: Email document handler
  - Source: backend/tools/email_processor.py (new file)
  - Class: EmailProcessor implementing DocumentProcessor
  - Method: extract_text() returns email body text
  - Method: get_metadata() returns email headers as metadata
- Backend: Email translation
  - Source: backend/services/translation_service.py
  - Add: translate_email(eml_path: string, target_lang: string = 'de') -> string
  - Logic: Parse email, translate subject and body, preserve headers, generate new .eml
- Frontend: Email viewer component
  - Source: src/components/workspace/EmailViewer.tsx (new file)
  - Display: Email metadata header (From, To, Subject, Date)
  - Display: Email body with HTML rendering or plain text
  - Display: Attachments list (if any)
  - Styling: Card-based layout mimicking email client
- Frontend: Integrate email viewer in DocumentViewer
  - Source: src/components/workspace/DocumentViewer.tsx
  - Add: Conditional rendering for .eml files
  - Add: if (document.type === 'eml') return <EmailViewer emailData={emailData} />
- Frontend: Update file upload validation
  - Source: src/components/workspace/FileDropZone.tsx
  - Add: .eml to accepted file types
  - Add: MIME type check for message/rfc822
- Backend: Email API endpoint
  - Source: backend/api/documents.py
  - Endpoint: GET /api/documents/email/{case_id}/{folder_id}/{filename}
  - Response: { headers: EmailHeaders, body: string, attachments: List[Attachment] }
- Frontend: Email API client
  - Source: src/lib/documentApi.ts
  - Function: loadEmailContent(caseId: string, folderId: string, filename: string) -> Promise<EmailData>

**Email Viewer UI Example:**
```tsx
// EmailViewer.tsx
<div className="email-viewer p-4">
  <Card>
    <CardHeader>
      <div className="email-metadata space-y-2">
        <div><strong>From:</strong> {emailData.from}</div>
        <div><strong>To:</strong> {emailData.to}</div>
        <div><strong>Subject:</strong> {emailData.subject}</div>
        <div><strong>Date:</strong> {formatDate(emailData.date)}</div>
      </div>
    </CardHeader>
    <CardContent>
      <Separator className="my-4" />
      <div className="email-body whitespace-pre-wrap">
        {emailData.body}
      </div>
      {emailData.attachments.length > 0 && (
        <>
          <Separator className="my-4" />
          <div className="attachments">
            <strong>Attachments:</strong>
            <ul>
              {emailData.attachments.map(att => (
                <li key={att.filename}>
                  <Paperclip size={14} /> {att.filename} ({att.size})
                </li>
              ))}
            </ul>
          </div>
        </>
      )}
    </CardContent>
  </Card>
</div>
```

**Email Parsing Example:**
```python
# backend/services/email_service.py
import email
from email import policy
from email.parser import BytesParser

def parse_eml_file(file_path: str) -> EmailData:
    with open(file_path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)

    # Extract headers
    headers = {
        'from': msg['From'],
        'to': msg['To'],
        'subject': msg['Subject'],
        'date': msg['Date']
    }

    # Extract body
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_content()
                break
    else:
        body = msg.get_content()

    return EmailData(headers=headers, body=body)
```

**Test Cases:**
- TC-S5-008-01: Drag and drop .eml file into case folder, verify file uploaded successfully
- TC-S5-008-02: Click .eml file in document tree, verify EmailViewer displays with headers
- TC-S5-008-03: Email in Arabic, verify RTL text rendered correctly
- TC-S5-008-04: Verify email metadata (From, To, Subject, Date) displayed in header section
- TC-S5-008-05: Email with HTML body, verify HTML converted to formatted text
- TC-S5-008-06: Email with plain text body, verify text displayed with whitespace preserved
- TC-S5-008-07: Email with attachments, verify attachments listed at bottom
- TC-S5-008-08: Click Translate on email, verify new render created with German translation
- TC-S5-008-09: Translated email retains original headers (From, To, Date unchanged)
- TC-S5-008-10: Translated email has translated subject and body in German
- TC-S5-008-11: Email subject in Arabic, translate to German, verify correct translation
- TC-S5-008-12: Upload invalid .eml file, verify error message displayed
- TC-S5-008-13: Email with no subject, verify "No Subject" displayed
- TC-S5-008-14: Use /fill-form on email content, verify form fields populated from email text

**Created:** 2026-01-09T16:00:00Z

---

## S5-009: Improved Chat Information Presentation

**Status:** proposed

**Description:**
Fix the current chat interface issues where raw information appears, including HTML tags and broken message fragments split across multiple dialog boxes. Implement proper message formatting, HTML sanitization, markdown rendering, and ensure complete messages are displayed in single cohesive chat bubbles. The chat should present information in a user-friendly, professional manner with proper formatting for code blocks, lists, links, and structured data.

**Technical Requirements:**
- HTML sanitization to prevent raw tags in chat messages
- Markdown rendering support for formatted text
- Message aggregation to prevent fragmentation
- Code block syntax highlighting
- List formatting (bullet and numbered)
- Link rendering with proper styling
- Structured data presentation (tables, JSON, etc.)

**Changes Required:**
- Frontend: Message formatter utility
  - Source: src/lib/messageFormatter.ts (new file)
  - Functions: sanitizeHTML(content: string) -> string
  - Functions: renderMarkdown(content: string) -> ReactNode
  - Functions: formatStructuredData(data: object) -> ReactNode
  - Dependencies: DOMPurify for HTML sanitization, marked or react-markdown for Markdown
- Frontend: Update AIChatInterface message rendering
  - Source: src/components/workspace/AIChatInterface.tsx
  - Update: Message display to use renderMarkdown() instead of raw content
  - Add: Code block component with syntax highlighting (Prism.js)
  - Add: Proper list rendering with bullets/numbers
  - Remove: Any raw HTML rendering
- Backend: Message formatting on server side
  - Source: backend/services/gemini_service.py
  - Update: Format Gemini responses before sending to frontend
  - Add: Convert raw responses to Markdown format
  - Add: Structure JSON data into readable format
  - Remove: Send plain HTML to frontend
- Frontend: Chat bubble styling improvements
  - Source: src/components/workspace/AIChatInterface.tsx
  - Update: Ensure each message is a single cohesive bubble
  - Add: Max-width constraint for readability
  - Add: Proper spacing between elements (paragraphs, lists, code blocks)
  - Add: Distinct styling for user vs assistant messages
- Frontend: Code block component
  - Source: src/components/ui/CodeBlock.tsx (new file)
  - Props: code, language
  - Features: Syntax highlighting, line numbers, copy button
  - Library: Use prism-react-renderer or react-syntax-highlighter
- Backend: Prevent message fragmentation
  - Source: backend/services/gemini_service.py
  - Update: Ensure streaming responses complete before starting new message
  - Add: Message buffering to accumulate complete thoughts
  - Logic: Only send message chunk when natural break point (sentence/paragraph end)
- Frontend: Table rendering for structured data
  - Source: src/components/workspace/DataTable.tsx (new file)
  - Props: data (array of objects)
  - Renders: Clean table with headers and rows
  - Use: When AI returns tabular data (e.g., validation report)
- Frontend: Link rendering with security
  - Source: src/lib/messageFormatter.ts
  - Update: Detect URLs in text and convert to clickable links
  - Security: Add rel="noopener noreferrer" target="_blank"
  - Visual: Underline and color links

**Message Formatting Examples:**
```tsx
// Before (raw HTML/broken):
<div className="message">
  {"<p>Here is the <b>result</b></p><ul><li>Item 1</li>"}
</div>
<div className="message">
  {"<li>Item 2</li></ul>"}
</div>

// After (formatted Markdown):
<div className="message">
  <ReactMarkdown>
    {`Here is the **result**:
    - Item 1
    - Item 2`}
  </ReactMarkdown>
</div>
```

**Backend Message Formatting:**
```python
# backend/services/gemini_service.py
def format_response(raw_response: str) -> str:
    # Convert HTML to Markdown
    if '<p>' in raw_response or '<ul>' in raw_response:
        response = html_to_markdown(raw_response)
    else:
        response = raw_response

    # Structure JSON data
    if is_json_data(response):
        response = format_json_as_markdown_table(response)

    return response
```

**Test Cases:**
- TC-S5-009-01: AI response with bold text, verify **bold** renders as bold, not as asterisks
- TC-S5-009-02: AI response with list, verify bullet points render correctly, not as dashes
- TC-S5-009-03: AI response with code block, verify syntax highlighting applied
- TC-S5-009-04: AI response with link, verify link is clickable and opens in new tab
- TC-S5-009-05: AI sends raw HTML `<p>Test</p>`, verify sanitized and displays "Test" without tags
- TC-S5-009-06: Long message spanning multiple paragraphs, verify displayed in single chat bubble
- TC-S5-009-07: AI response with numbered list, verify numbers render correctly (1., 2., 3.)
- TC-S5-009-08: Verify no message fragmentation (no split messages across multiple bubbles)
- TC-S5-009-09: AI response with table data, verify rendered as clean table, not raw JSON
- TC-S5-009-10: Code block with Python syntax, verify syntax highlighting matches language
- TC-S5-009-11: Copy code block, verify copy button copies code without line numbers
- TC-S5-009-12: Message with inline code `variable`, verify backticks render as inline code style
- TC-S5-009-13: XSS attempt `<script>alert('xss')</script>`, verify sanitized and not executed
- TC-S5-009-14: Markdown headings (##), verify render as proper heading elements with styling

**Created:** 2026-01-09T16:00:00Z

---

## S5-010: Optional Persistent Chat History

**Status:** proposed

**Description:**
Evaluate and optionally implement persistent chat conversation history within the current session. Currently, the chat operates in one-shot mode (1 message, 1 response) with no memory. This requirement assesses whether maintaining chat history is feasible and beneficial for the POC. If implemented, chat history persists in-memory during the current session but is cleared when the service restarts (no database persistence). The evaluation should determine if all current requirements can still be met with one-shot requests or if conversation context improves the AI's ability to answer follow-up questions and maintain context.

**Technical Requirements:**
- Evaluate feasibility: Can all use cases work with one-shot? (Answer: Most can, but context helps)
- If implemented: In-memory conversation history per case
- Chat history cleared on app restart (no persistence)
- Context window management (limit to last N messages)
- Token budget management for Gemini API
- Optional feature flag to enable/disable chat history

**Changes Required:**
- Backend: Conversation history manager
  - Source: backend/services/conversation_manager.py (new file)
  - Methods: get_conversation_history(case_id: string) -> List[Message]
  - Methods: add_message(case_id: string, role: string, content: string)
  - Methods: clear_conversation(case_id: string)
  - Methods: get_context_window(case_id: string, max_messages: int = 10) -> List[Message]
  - Storage: In-memory dictionary mapping case_id to conversation history
- Backend: Update Gemini service to use history
  - Source: backend/services/gemini_service.py
  - Update: generate_response() to include conversation history in prompt
  - Add: Format history as chat context for Gemini
  - Add: Token counting to ensure context fits within limits
- Backend: Configuration flag
  - Source: backend/config.py
  - Add: ENABLE_CHAT_HISTORY = os.getenv("ENABLE_CHAT_HISTORY", "false").lower() == "true"
  - Logic: If disabled, use existing one-shot mode
- Frontend: Display conversation history in chat
  - Source: src/components/workspace/AIChatInterface.tsx
  - Update: Load full conversation history when case is selected
  - Verify: History displays correctly on case switch
- Backend: Clear history on app restart
  - Source: backend/main.py
  - Add: @app.on_event("shutdown") to clear in-memory history (already happens)
  - Note: No persistence layer needed for POC
- Backend: Context window management
  - Source: backend/services/conversation_manager.py
  - Method: get_context_window() returns last 10 messages (configurable)
  - Reason: Prevent token limit overflow, maintain relevant context
- Backend: Token budget calculation
  - Source: backend/services/gemini_service.py
  - Add: estimate_tokens(messages: List[Message]) -> int
  - Logic: If history + new message > token limit, truncate older messages
- Frontend: Clear conversation button
  - Source: src/components/workspace/AIChatInterface.tsx
  - Add: "Clear History" button in chat header
  - Action: Calls backend to clear conversation for current case
- Backend: Clear history endpoint
  - Source: backend/api/chat.py
  - Endpoint: DELETE /api/chat/history/{case_id}
  - Action: Clears conversation_manager history for case

**Evaluation Criteria:**
1. **One-Shot Sufficiency:**
   - /fill-form: Works with one-shot (document context is sufficient)
   - Search: Works with one-shot (query + document)
   - Translation: Works with one-shot (no prior context needed)
   - Validation: Works with one-shot (case context is sufficient)

2. **Benefits of History:**
   - Follow-up questions: "What was the passport number again?" (refers to previous response)
   - Clarifications: "I meant the German translation, not English" (corrects previous request)
   - Multi-step workflows: "Now translate that to French" (refers to previous document)

3. **Recommendation:** Implement as optional feature, disabled by default for POC

**Conversation History Format:**
```python
# In-memory storage
conversation_history = {
    "ACTE-2024-001": [
        {"role": "user", "content": "What is in this document?", "timestamp": "2026-01-09T10:00:00Z"},
        {"role": "assistant", "content": "This document is a birth certificate...", "timestamp": "2026-01-09T10:00:05Z"},
        {"role": "user", "content": "What is the birth date?", "timestamp": "2026-01-09T10:01:00Z"},
        {"role": "assistant", "content": "The birth date is 15.05.1990.", "timestamp": "2026-01-09T10:01:03Z"}
    ],
    "ACTE-2024-002": [...]
}
```

**Test Cases:**
- TC-S5-010-01: Feature flag disabled, verify one-shot mode works as before
- TC-S5-010-02: Feature flag enabled, send message, verify history stored in conversation_manager
- TC-S5-010-03: Send follow-up question "What was the name again?", verify AI uses previous context
- TC-S5-010-04: Switch case, verify conversation history switches to new case
- TC-S5-010-05: Send 15 messages, verify only last 10 included in context window
- TC-S5-010-06: Long conversation approaches token limit, verify older messages truncated
- TC-S5-010-07: Click "Clear History", verify conversation cleared and next message has no context
- TC-S5-010-08: Restart backend, verify all conversation history cleared (no persistence)
- TC-S5-010-09: Two different cases with separate conversations, verify history doesn't mix
- TC-S5-010-10: Estimate tokens for conversation, verify count is accurate (within 10%)
- TC-S5-010-11: User asks "Translate it to French" (referring to previous doc), verify AI understands reference
- TC-S5-010-12: Disabled history, verify backend doesn't store messages in conversation_manager

**Created:** 2026-01-09T16:00:00Z

---

## S5-011: Cascading Context with Document Tree View

**Status:** proposed

**Description:**
Enhance the existing cascading context system (Case > Folder > Document) by adding a tree view of the folder/document structure to the top-level parent case context. This tree view is automatically updated whenever documents are added or folders are created. The AI agent can reference this tree view to answer questions about document locations, provide overviews of what's available, and correct user misunderstandings. For example, if a user says "I don't have a passport", the agent can check the tree view and respond "Actually, I see a file named 'Reisepass.png' in your Personal Data folder." The tree view is included in the system prompt for every AI request, providing global document awareness.

**Technical Requirements:**
- Generate document tree view structure from case folders
- Include tree view in case-level context for AI prompts
- Auto-refresh tree view when documents/folders change
- Tree view format: hierarchical JSON or indented text representation
- AI can query tree view to locate documents
- Tree view included in cascading context without overriding folder/document context

**Changes Required:**
- Backend: Document tree generator
  - Source: backend/services/context_manager.py
  - Add: generate_document_tree(case_id: string) -> DocumentTreeView
  - Format: Hierarchical structure with folder names and document names
  - Example format:
    ```
    Case: ACTE-2024-001
    ├── Personal Data/
    │   ├── Birth_Certificate.jpg
    │   ├── Passport.png (Reisepass.png)
    │   └── ID_Card.png
    ├── Certificates/
    │   └── Language_Certificate_A1.pdf
    ├── Applications & Forms/
    │   └── Application_Form.pdf
    └── Emails/
        └── Confirmation.eml
    ```
- Backend: Update case context with tree view
  - Source: backend/services/context_manager.py
  - Update: load_case_context() to include documentTreeView field
  - Add: Tree view generation called on context load
- Backend: Tree view refresh trigger
  - Source: backend/api/files.py
  - Update: After file upload, trigger tree view refresh
  - Update: After file deletion, trigger tree view refresh
  - Logic: Invalidate cached tree view, regenerate on next request
- Backend: Include tree view in AI prompts
  - Source: backend/services/gemini_service.py
  - Update: _build_prompt() to include document tree view in system context
  - Format: Add section "Available documents in this case:" with tree view
- Frontend: Trigger tree view refresh
  - Source: src/contexts/AppContext.tsx
  - Update: addDocumentToFolder() to notify backend of tree update
  - Update: removeDocumentFromFolder() to notify backend of tree update
- Backend: Tree view caching
  - Source: backend/services/context_manager.py
  - Add: In-memory cache mapping case_id to tree view
  - Add: invalidate_tree_cache(case_id: string)
  - Logic: Cache tree view, regenerate only when documents change
- Backend: Tree view API endpoint
  - Source: backend/api/context.py (new file)
  - Endpoint: GET /api/context/tree/{case_id}
  - Response: { treeView: string, folders: string[], documentCount: int }
- Types: Document tree view types
  - Source: src/types/context.ts (new file)
  - Interface: DocumentTreeView with caseId, treeStructure, lastUpdated
  - Interface: TreeNode with name, type ('folder' | 'document'), children

**Document Tree View Generation:**
```python
# backend/services/context_manager.py
def generate_document_tree(case_id: str) -> str:
    case_folders = load_case_folders(case_id)
    tree_lines = [f"Case: {case_id}"]

    for folder in case_folders:
        tree_lines.append(f"├── {folder.name}/")
        for doc in folder.documents:
            prefix = "│   ├──" if doc != folder.documents[-1] else "│   └──"
            tree_lines.append(f"{prefix} {doc.name}")

    return "\n".join(tree_lines)
```

**AI Prompt with Tree View:**
```python
prompt = f"""You are an AI assistant for case management.

Current Case: {case_id}
Current Folder: {folder_id or 'Root'}

Available Documents (Tree View):
{document_tree_view}

Case Context: {case_context}
Folder Context: {folder_context}

User Question: {user_message}

Instructions:
- Use the tree view to answer questions about document availability
- If user claims a document is missing, check the tree view first
- Reference specific document locations when answering
"""
```

**Test Cases:**
- TC-S5-011-01: Load case, verify document tree view generated correctly
- TC-S5-011-02: Ask "What documents do I have?", verify AI lists documents from tree view
- TC-S5-011-03: User says "I don't have a passport", verify AI responds "I see Reisepass.png in Personal Data"
- TC-S5-011-04: Upload new document, verify tree view refreshes automatically
- TC-S5-011-05: Delete document, verify tree view updates to reflect deletion
- TC-S5-011-06: Ask "Where is my birth certificate?", verify AI responds with folder location
- TC-S5-011-07: Tree view shows German filename "Geburtsurkunde.jpg", verify AI recognizes as birth certificate
- TC-S5-011-08: Ask "Do I have any emails?", verify AI checks tree view and responds accurately
- TC-S5-011-09: Tree view cached, verify not regenerated on every request (performance)
- TC-S5-011-10: Tree view cache invalidated after document operation, verify regenerates correctly
- TC-S5-011-11: Multi-level folder structure, verify tree view displays hierarchy correctly
- TC-S5-011-12: Empty folder in tree view, verify displays as "Folder/ (empty)"
- TC-S5-011-13: Ask "How many documents are in Personal Data?", verify AI counts correctly from tree
- TC-S5-011-14: Switch to different case, verify tree view switches to new case's documents

**Created:** 2026-01-09T16:00:00Z

---

## S5-012: Document Type Capabilities and Command Availability

**Status:** proposed

**Description:**
Implement document type capability restrictions where certain tools/commands are only available for specific document types. The system defines which operations are allowed for each document type:
- **Images (jpeg, jpg, png)**: Allow anonymization and translation
- **PDFs**: Allow translation and search
- **Email (.eml)**: Allow only translation
- **Text files**: Allow all operations (translation, search, form fill)

When a document type doesn't support a command, the corresponding button should be grayed out and disabled. If a user attempts an unsupported command via chat, the AI agent should explain why the operation is not supported for that document type.

**Technical Requirements:**
- Document type capability matrix defining allowed operations
- Dynamic toolbar button enable/disable based on selected document
- AI agent awareness of document type restrictions
- Clear error messages explaining unsupported operations
- Tooltip on disabled buttons explaining why disabled

**Changes Required:**
- Backend: Document capabilities configuration
  - Source: backend/config/document_capabilities.py (new file)
  - Constant: DOCUMENT_CAPABILITIES mapping document types to allowed operations
  - Format:
    ```python
    DOCUMENT_CAPABILITIES = {
        "jpg": ["anonymize", "translate"],
        "jpeg": ["anonymize", "translate"],
        "png": ["anonymize", "translate"],
        "pdf": ["translate", "search"],
        "eml": ["translate"],
        "txt": ["translate", "search", "fill_form"]
    }
    ```
- Backend: Capability validation middleware
  - Source: backend/services/capability_validator.py (new file)
  - Methods: can_perform_operation(document_type: string, operation: string) -> bool
  - Methods: get_supported_operations(document_type: string) -> List[string]
  - Methods: get_unsupported_reason(document_type: string, operation: string) -> string
- Backend: Update command handlers to check capabilities
  - Source: backend/api/chat.py
  - Update: Each command handler (/anonymize, /translate, /search, /fill-form) checks capabilities first
  - Response: If not supported, return error message explaining restriction
- Frontend: Dynamic toolbar button states
  - Source: src/components/workspace/DocumentViewer.tsx
  - Update: Calculate enabled/disabled state for each toolbar button based on document type
  - Logic: const canAnonymize = CAPABILITIES[document.type]?.includes('anonymize')
  - Add: Disabled styling (opacity, cursor not-allowed)
- Frontend: Tooltips on disabled buttons
  - Source: src/components/workspace/DocumentViewer.tsx
  - Add: Tooltip component on toolbar buttons
  - Content: "Translation not supported for this document type" (or similar)
- Frontend: Document capabilities constant
  - Source: src/constants/documentCapabilities.ts (new file)
  - Export: DOCUMENT_CAPABILITIES matching backend configuration
  - Export: Helper functions: canAnonymize(), canTranslate(), canSearch(), canFillForm()
- Backend: AI agent capabilities awareness
  - Source: backend/services/gemini_service.py
  - Update: Include document capabilities in system prompt
  - Add: "The current document type is {type}. Supported operations: {operations}."
  - Logic: If user requests unsupported operation, AI explains restriction
- Frontend: Command validation before sending
  - Source: src/components/workspace/AIChatInterface.tsx
  - Add: validateCommand(command: string, documentType: string) -> ValidationResult
  - Logic: Check if command is supported for current document
  - UI: Show warning message if command not supported

**Document Capabilities Matrix:**
```typescript
// src/constants/documentCapabilities.ts
export const DOCUMENT_CAPABILITIES = {
  jpg: ['anonymize', 'translate'],
  jpeg: ['anonymize', 'translate'],
  png: ['anonymize', 'translate'],
  gif: ['anonymize', 'translate'],
  pdf: ['translate', 'search'],
  eml: ['translate'],
  txt: ['translate', 'search', 'fill_form'],
} as const;

export function canPerformOperation(docType: string, operation: string): boolean {
  return DOCUMENT_CAPABILITIES[docType]?.includes(operation) ?? false;
}
```

**Capability Validation Error Messages:**
```python
# backend/services/capability_validator.py
UNSUPPORTED_MESSAGES = {
    "anonymize": {
        "pdf": "Anonymization is only supported for image files (JPG, PNG). PDFs cannot be anonymized.",
        "eml": "Anonymization is not supported for email files.",
        "txt": "Anonymization is only supported for image files, not text documents."
    },
    "search": {
        "jpg": "Semantic search requires text content. Images cannot be searched.",
        "eml": "Email search is not yet supported. Use translation instead."
    },
    "fill_form": {
        "pdf": "Form filling from PDFs is not yet supported. Please extract text first.",
        "jpg": "Form filling requires text content. Images cannot be parsed for form data."
    }
}
```

**Test Cases:**
- TC-S5-012-01: Select JPG document, verify Anonymize and Translate buttons enabled, Search disabled
- TC-S5-012-02: Select PDF document, verify Translate and Search enabled, Anonymize disabled
- TC-S5-012-03: Select EML document, verify only Translate enabled, all others disabled
- TC-S5-012-04: Hover over disabled button, verify tooltip explains why disabled
- TC-S5-012-05: Select TXT document, verify all buttons enabled
- TC-S5-012-06: Type "/anonymize" on PDF, verify AI responds "Anonymization not supported for PDFs"
- TC-S5-012-07: Click disabled Search button on image, verify no action triggered
- TC-S5-012-08: Type "/search what is the passport number" on PDF, verify search executes successfully
- TC-S5-012-09: Select image, verify can anonymize and translate but not search
- TC-S5-012-10: Backend receives /search request for JPG, verify returns error response
- TC-S5-012-11: Disabled button has visual indication (gray, opacity reduced)
- TC-S5-012-12: Document with unknown type, verify all buttons disabled with "Unsupported type" tooltip
- TC-S5-012-13: Ask AI "Can I anonymize this PDF?", verify AI responds "No, only images can be anonymized"
- TC-S5-012-14: Switch from PDF to JPG, verify toolbar button states update dynamically

**Created:** 2026-01-09T16:00:00Z

---

## S5-013: Enhanced Acte Context Research

**Status:** proposed

**Description:**
Enrich the case-level context for each Acte (case type) by researching and documenting comprehensive requirements, necessary documents, common issues, and regulations. The current case context files (backend/data/contexts/cases/{caseId}/case.json) should be expanded with detailed, researched information about the specific case type (e.g., German Integration Course Application, Asylum Application). This includes:
- Complete list of required documents (critical and optional)
- Regulatory references and legal requirements
- Common mistakes and issues encountered
- Document specifications (formats, validity periods)
- Processing timelines and expectations

This enhanced context enables the AI agent to provide expert-level guidance, validate cases accurately, and assist users with comprehensive knowledge about their specific Acte type.

**Technical Requirements:**
- Research authoritative sources for each case type (BAMF regulations, official guidelines)
- Document all required documents with criticality levels
- Include regulation references (legal basis)
- Common issues and validation criteria
- Context versioning for updates
- Multi-language support (German primary, English translations)

**Changes Required:**
- Data: Enhanced context schema definition
  - Source: backend/schemas/case_context_schema.json (new file)
  - Schema: Define comprehensive structure for case context
  - Fields: requiredDocuments (array with criticality, validityPeriod, alternatives)
  - Fields: regulations (array with reference, title, url, summary)
  - Fields: commonIssues (array with issue, solution, frequency)
  - Fields: processingInfo (timeline, costs, contactInfo)
- Data: Research Integration Course requirements
  - Source: backend/data/contexts/cases/ACTE-2024-001/case.json
  - Research: Official BAMF Integration Course requirements
  - Add: 15+ required documents with specifications
  - Add: 10+ regulation references with official links
  - Add: 20+ common issues with solutions
- Data: Research Asylum Application requirements
  - Source: backend/data/contexts/templates/asylum_application/case.json
  - Research: BAMF Asylum Application process requirements
  - Add: Complete document list for asylum cases
  - Add: Relevant asylum regulations and legal basis
- Data: Research Family Reunification requirements
  - Source: backend/data/contexts/templates/family_reunification/case.json
  - Research: Family reunification requirements
  - Add: Required documents for family visa applications
- Backend: Context validation
  - Source: backend/services/context_manager.py
  - Add: validate_case_context(context: dict) -> ValidationResult
  - Logic: Ensure all required schema fields present
  - Logic: Validate regulation URLs are accessible
- Backend: Context versioning
  - Source: backend/data/contexts/cases/{caseId}/case.json
  - Add: schemaVersion, lastUpdated, researchSources fields
  - Logic: Track context version for migration compatibility
- Documentation: Research sources documentation
  - Source: docs/requirements/context-research-sources.md (new file)
  - Content: List all research sources, URLs, access dates
  - Content: Methodology for keeping contexts updated
- Backend: Regulation reference system
  - Source: backend/models/regulation.py (new file)
  - Class: Regulation with reference, title, url, summary, effectiveDate
  - Methods: get_regulation_details(reference: string) -> Regulation
- Backend: Update validation service with enhanced context
  - Source: backend/services/validation_service.py
  - Update: Use enhanced requiredDocuments from case context
  - Update: Include regulation references in validation reports
  - Update: Reference commonIssues when validation fails

**Enhanced Case Context Structure:**
```json
{
  "caseId": "ACTE-2024-001",
  "caseType": "integration_course",
  "name": "German Integration Course Application",
  "schemaVersion": "2.0",
  "lastUpdated": "2026-01-09T16:00:00Z",
  "researchSources": [
    "https://www.bamf.de/DE/Themen/Integration/Integrationskurse/integrationskurse-node.html",
    "German Integration Act (Integrationsgesetz)"
  ],
  "description": "Application for participation in German integration course according to §43 AufenthG",
  "requiredDocuments": [
    {
      "type": "passport",
      "name": "Valid passport or ID document",
      "criticality": "critical",
      "alternatives": ["id_card", "residence_permit"],
      "validityPeriod": "Must be valid for entire course duration",
      "specifications": "Clear photo, all pages legible",
      "regulationReference": "§43 Abs. 1 AufenthG"
    },
    {
      "type": "birth_certificate",
      "name": "Birth certificate",
      "criticality": "critical",
      "validityPeriod": "No expiration",
      "specifications": "Official translation if not in German/English"
    },
    {
      "type": "language_certificate",
      "name": "Previous language certificate (if available)",
      "criticality": "optional",
      "specifications": "A1-C2 level certificates accepted"
    }
  ],
  "regulations": [
    {
      "reference": "§43 AufenthG",
      "title": "Participation in integration courses",
      "url": "https://www.gesetze-im-internet.de/aufenthg_2004/__43.html",
      "summary": "Foreigners entitled to participate in integration courses",
      "effectiveDate": "2005-01-01"
    },
    {
      "reference": "IntV §4",
      "title": "Integration course content requirements",
      "url": "https://www.gesetze-im-internet.de/intv/__4.html",
      "summary": "Defines integration course structure and content"
    }
  ],
  "commonIssues": [
    {
      "issue": "Missing official translation of birth certificate",
      "solution": "Birth certificates not in German/English must have certified translation",
      "frequency": "high",
      "severity": "critical"
    },
    {
      "issue": "Expired passport",
      "solution": "Passport must be valid for at least 6 months beyond course completion",
      "frequency": "medium",
      "severity": "critical"
    },
    {
      "issue": "Unclear residence status documentation",
      "solution": "Provide current residence permit (Aufenthaltstitel) or visa",
      "frequency": "medium",
      "severity": "high"
    }
  ],
  "processingInfo": {
    "typicalTimeline": "4-6 weeks from complete application",
    "costs": "Free for eligible participants, €2.29 per hour for self-payers",
    "appealPeriod": "30 days",
    "contactEmail": "integration@bamf.bund.de",
    "contactPhone": "+49 911 943-0"
  },
  "validationRules": [
    {
      "rule": "passport_validity",
      "description": "Passport must be valid for at least 6 months beyond course completion",
      "severity": "critical"
    },
    {
      "rule": "official_translations",
      "description": "All non-German/English documents must have certified translations",
      "severity": "critical"
    }
  ]
}
```

**Test Cases:**
- TC-S5-013-01: Load case context, verify requiredDocuments array has 10+ entries
- TC-S5-013-02: Verify each required document has criticality field ('critical' or 'optional')
- TC-S5-013-03: Load regulations array, verify each has reference, title, url, and summary
- TC-S5-013-04: Click regulation URL, verify link opens to valid government webpage
- TC-S5-013-05: Validate case, verify validation uses enhanced requiredDocuments from context
- TC-S5-013-06: Missing critical document, verify validation report references regulation
- TC-S5-013-07: Common issue encountered, verify AI suggests solution from commonIssues array
- TC-S5-013-08: Ask "What documents do I need?", verify AI lists all required documents from context
- TC-S5-013-09: Ask "What if my passport is expired?", verify AI responds with commonIssues solution
- TC-S5-013-10: Verify processingInfo includes timeline, costs, and contact information
- TC-S5-013-11: Context schema validation, verify all required fields present
- TC-S5-013-12: Check lastUpdated field, verify date is recent (within 6 months)
- TC-S5-013-13: Ask "What is the legal basis for this requirement?", verify AI cites regulation reference
- TC-S5-013-14: Document has alternative (ID card instead of passport), verify validation accepts alternative

**Created:** 2026-01-09T16:00:00Z

---

## S5-014: UI Language Toggle (German/English)

**Status:** proposed

**Description:**
Implement a language toggle button in the main UI allowing users to switch between German and English interface languages. The default language is German. When the language is switched, all UI labels, buttons, tooltips, and system messages update to the selected language. The Gemini AI agent service also responds in the selected language - if UI is in German, the AI replies in German; if UI is in English, the AI replies in English. This synchronizes the user experience across both the interface and the AI assistant.

**Technical Requirements:**
- Language toggle button in main header/toolbar
- i18n internationalization system (react-i18next or similar)
- Translation files for German and English
- Persist language preference in localStorage
- Update AI agent language parameter based on UI setting
- Real-time UI update when language changes (no page reload)
- Default language: German (de)

**Changes Required:**
- Frontend: i18n configuration
  - Source: src/i18n/config.ts (new file)
  - Setup: Configure i18next with German and English translations
  - Default language: 'de'
  - Fallback language: 'en'
  - Load translations from JSON files
- Frontend: Translation files
  - Source: src/i18n/locales/de.json (new file)
  - Content: German translations for all UI strings
  - Sections: common, workspace, forms, documents, chat, validation
- Frontend: Translation files (English)
  - Source: src/i18n/locales/en.json (new file)
  - Content: English translations mirroring German structure
- Frontend: Language toggle button
  - Source: src/components/workspace/WorkspaceHeader.tsx
  - Add: Language toggle button with flag icons or language codes (DE/EN)
  - Action: Switches i18n language and saves to localStorage
  - Visual: Current language highlighted
- Frontend: Update all UI text to use i18n
  - Source: All component files
  - Update: Replace hardcoded strings with t('translation.key')
  - Scope: Buttons, labels, tooltips, error messages, form labels
- Frontend: Language state management
  - Source: src/contexts/AppContext.tsx
  - Add: currentLanguage state ('de' | 'en')
  - Add: setLanguage(lang: string) function
  - Add: Persist language to localStorage
  - Add: Load language from localStorage on app start
- Frontend: AI language parameter
  - Source: src/contexts/AppContext.tsx
  - Update: sendChatMessage() to include language parameter
  - Field: { ...message, language: currentLanguage }
- Backend: AI language handling
  - Source: backend/services/gemini_service.py
  - Update: Accept language parameter in generate_response()
  - Update: Include language instruction in system prompt
  - Prompt: "Respond to the user in {language}. German=Deutsch, English=English."
- Frontend: Dynamic language switching
  - Source: App.tsx
  - Update: Wrap app with I18nextProvider
  - Logic: Language changes trigger re-render with new translations
- Frontend: Language persistence
  - Source: src/lib/localStorage.ts
  - Add: saveLanguagePreference(lang: string)
  - Add: loadLanguagePreference() -> string | null
- Frontend: Toast notifications in selected language
  - Source: All toast/notification calls
  - Update: Use i18n translations for toast messages

**Translation File Structure:**
```json
// src/i18n/locales/de.json
{
  "common": {
    "save": "Speichern",
    "cancel": "Abbrechen",
    "delete": "Löschen",
    "edit": "Bearbeiten",
    "close": "Schließen"
  },
  "workspace": {
    "header": {
      "title": "BAMF Acte Companion",
      "validateCase": "Fall validieren",
      "adminMode": "Admin-Modus"
    },
    "documents": {
      "upload": "Dokument hochladen",
      "delete": "Dokument löschen",
      "anonymize": "Anonymisieren",
      "translate": "Übersetzen",
      "search": "Suchen"
    }
  },
  "chat": {
    "placeholder": "Geben Sie Ihre Nachricht ein...",
    "commands": {
      "fillForm": "Formular ausfüllen",
      "validateCase": "Fall validieren",
      "search": "Suchen"
    }
  },
  "validation": {
    "complete": "Vollständig",
    "incomplete": "Unvollständig",
    "missingDocuments": "Fehlende Dokumente"
  }
}

// src/i18n/locales/en.json
{
  "common": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "edit": "Edit",
    "close": "Close"
  },
  "workspace": {
    "header": {
      "title": "BAMF Acte Companion",
      "validateCase": "Validate Case",
      "adminMode": "Admin Mode"
    },
    "documents": {
      "upload": "Upload Document",
      "delete": "Delete Document",
      "anonymize": "Anonymize",
      "translate": "Translate",
      "search": "Search"
    }
  },
  "chat": {
    "placeholder": "Type your message...",
    "commands": {
      "fillForm": "Fill Form",
      "validateCase": "Validate Case",
      "search": "Search"
    }
  },
  "validation": {
    "complete": "Complete",
    "incomplete": "Incomplete",
    "missingDocuments": "Missing Documents"
  }
}
```

**Language Toggle Implementation:**
```tsx
// src/components/workspace/WorkspaceHeader.tsx
import { useTranslation } from 'react-i18next';

export function WorkspaceHeader() {
  const { i18n, t } = useTranslation();

  const toggleLanguage = () => {
    const newLang = i18n.language === 'de' ? 'en' : 'de';
    i18n.changeLanguage(newLang);
    localStorage.setItem('language', newLang);
  };

  return (
    <header>
      <h1>{t('workspace.header.title')}</h1>
      <button onClick={toggleLanguage}>
        {i18n.language === 'de' ? '🇬🇧 EN' : '🇩🇪 DE'}
      </button>
    </header>
  );
}
```

**Test Cases:**
- TC-S5-014-01: Open app, verify UI displays in German by default
- TC-S5-014-02: Click language toggle, verify UI switches to English
- TC-S5-014-03: All buttons and labels update to English without page reload
- TC-S5-014-04: Send chat message in English UI, verify AI responds in English
- TC-S5-014-05: Switch back to German, send message, verify AI responds in German
- TC-S5-014-06: Refresh page, verify language preference persists from localStorage
- TC-S5-014-07: Toast notification appears, verify text is in selected language
- TC-S5-014-08: Error message appears, verify translated correctly
- TC-S5-014-09: Form labels in FormViewer, verify display in selected language
- TC-S5-014-10: Validation report, verify status and messages translated
- TC-S5-014-11: Slash commands list, verify command labels translated
- TC-S5-014-12: Tooltip on disabled button, verify tooltip text translated
- TC-S5-014-13: Switch language while chat is open, verify existing messages don't change (new messages use new language)
- TC-S5-014-14: Admin panel labels, verify all admin UI elements translated

**Created:** 2026-01-09T16:00:00Z

---

## S5-015: Initial Document Setup for Test Acte

**Status:** proposed

**Description:**
Clean up the current irrelevant test documents and replace them with a comprehensive set of realistic sample documents under the root_docs folder. These documents should be properly mapped to the test Acte "ACTE-2024-001" (German Integration Course Application) and placed in the correct folders according to the specified mapping:
- Geburtsurkunde.jpg → Personal Data folder
- Email.eml → Emails folder
- Sprachzeugnis-Zertifikat.pdf → Certificates folder
- Anmeldeformular.pdf → Applications & Forms folder
- Personalausweis.png → Personal Data folder
- Aufenthalstitel.png → Personal Data folder
- Notenspiegel.pdf → Additional Evidence folder

These documents serve as the foundation for testing all Sprint 5 features (anonymization, translation, search, form fill, validation).

**Technical Requirements:**
- Remove existing irrelevant test documents
- Create root_docs folder with sample documents
- Map documents to correct folders in ACTE-2024-001
- Ensure documents are realistic and appropriate for Integration Course case
- Verify all document types are supported (jpg, png, pdf, eml)
- Documents should contain realistic data for testing (German text, Arabic email, etc.)

**Changes Required:**
- Data: Clean up existing documents
  - Source: public/documents/ directory
  - Action: Remove irrelevant test documents no longer needed
  - Preserve: Document structure for ACTE-2024-001
- Data: Create root_docs folder
  - Source: root_docs/ (new directory in project root)
  - Content: 7 sample documents as specified
  - Files: Geburtsurkunde.jpg, Email.eml, Sprachzeugnis-Zertifikat.pdf, Anmeldeformular.pdf, Personalausweis.png, Aufenthalstitel.png, Notenspiegel.pdf
- Data: Birth certificate image
  - Source: root_docs/Geburtsurkunde.jpg
  - Content: German birth certificate for Ahmad Ali, born 15.05.1990 in Kabul, Afghanistan
  - Format: JPG image with clear text
- Data: Email file
  - Source: root_docs/Email.eml
  - Content: Email in Arabic from BAMF regarding application confirmation
  - Format: Standard .eml format with headers and body
- Data: Language certificate PDF
  - Source: root_docs/Sprachzeugnis-Zertifikat.pdf
  - Content: Goethe-Institut German language certificate A2 level
  - Format: PDF with official certificate layout
- Data: Application form PDF
  - Source: root_docs/Anmeldeformular.pdf
  - Content: Partially filled Integration Course application form
  - Format: PDF form with fields for name, address, course preference
- Data: ID card image
  - Source: root_docs/Personalausweis.png
  - Content: German ID card (Personalausweis) front and back
  - Format: PNG image with clear photo and text
- Data: Residence permit image
  - Source: root_docs/Aufenthalstitel.png
  - Content: German residence permit (Aufenthaltstitel) document
  - Format: PNG image showing permit details
- Data: Transcript PDF
  - Source: root_docs/Notenspiegel.pdf
  - Content: University transcript (Notenspiegel) from Kabul University
  - Format: PDF with grades and course information
- Backend: Document initialization script
  - Source: backend/scripts/initialize_test_documents.py (new file)
  - Purpose: Copy documents from root_docs to correct case folders
  - Logic: Copy each file to public/documents/ACTE-2024-001/{folder}/
  - Mapping: Hardcoded mapping of filenames to folder IDs
- Backend: Update startup to initialize documents
  - Source: backend/main.py
  - Update: @app.on_event("startup") to call initialize_test_documents()
  - Logic: Only run if ACTE-2024-001 folders are empty
- Data: Update mockData with document references
  - Source: src/data/mockData.ts
  - Update: ACTE-2024-001 case documents array with 7 documents
  - Update: Set correct filePath for each document

**Document Mapping:**
```python
# backend/scripts/initialize_test_documents.py
DOCUMENT_MAPPING = {
    "Geburtsurkunde.jpg": {
        "target_folder": "personal-data",
        "name": "Birth Certificate (Geburtsurkunde)",
        "type": "jpg"
    },
    "Email.eml": {
        "target_folder": "emails",
        "name": "BAMF Confirmation Email",
        "type": "eml"
    },
    "Sprachzeugnis-Zertifikat.pdf": {
        "target_folder": "certificates",
        "name": "German Language Certificate A2",
        "type": "pdf"
    },
    "Anmeldeformular.pdf": {
        "target_folder": "applications",
        "name": "Integration Course Application Form",
        "type": "pdf"
    },
    "Personalausweis.png": {
        "target_folder": "personal-data",
        "name": "ID Card (Personalausweis)",
        "type": "png"
    },
    "Aufenthalstitel.png": {
        "target_folder": "personal-data",
        "name": "Residence Permit (Aufenthaltstitel)",
        "type": "png"
    },
    "Notenspiegel.pdf": {
        "target_folder": "evidence",
        "name": "University Transcript (Notenspiegel)",
        "type": "pdf"
    }
}
```

**Initialization Script:**
```python
# backend/scripts/initialize_test_documents.py
import shutil
from pathlib import Path

def initialize_test_documents():
    source_dir = Path("root_docs")
    base_target_dir = Path("public/documents/ACTE-2024-001")

    for filename, config in DOCUMENT_MAPPING.items():
        source_file = source_dir / filename
        target_folder = base_target_dir / config["target_folder"]
        target_folder.mkdir(parents=True, exist_ok=True)
        target_file = target_folder / filename

        if not target_file.exists() and source_file.exists():
            shutil.copy2(source_file, target_file)
            print(f"Copied {filename} to {config['target_folder']}")
```

**Test Cases:**
- TC-S5-015-01: Run app startup, verify root_docs documents copied to ACTE-2024-001 folders
- TC-S5-015-02: Open ACTE-2024-001, verify 7 documents visible in correct folders
- TC-S5-015-03: Personal Data folder, verify contains 3 documents (Geburtsurkunde, Personalausweis, Aufenthalstitel)
- TC-S5-015-04: Emails folder, verify contains Email.eml
- TC-S5-015-05: Certificates folder, verify contains Sprachzeugnis-Zertifikat.pdf
- TC-S5-015-06: Applications & Forms folder, verify contains Anmeldeformular.pdf
- TC-S5-015-07: Additional Evidence folder, verify contains Notenspiegel.pdf
- TC-S5-015-08: Click Geburtsurkunde.jpg, verify image displays with German birth certificate
- TC-S5-015-09: Click Email.eml, verify email displays with Arabic text
- TC-S5-015-10: Click Anmeldeformular.pdf, verify PDF loads correctly
- TC-S5-015-11: Old irrelevant test documents removed, verify not visible in any case
- TC-S5-015-12: Document registry updated, verify manifest includes all 7 new documents
- TC-S5-015-13: Restart app, verify documents persist and remain visible
- TC-S5-015-14: Run validation on ACTE-2024-001, verify some required documents present

**Created:** 2026-01-09T16:00:00Z

---

## S5-016: Drag-and-Drop Document Management Across Folders

**Status:** proposed

**Description:**
Enable users to drag and drop documents from anywhere in the case tree (including home/root level) into specific folders. Documents can exist outside of folders initially and be organized by dragging them into the appropriate folders. This provides flexible document organization where users can upload documents first and categorize them later. The system supports:
- Documents at case root level (not in any folder)
- Drag document from root into a folder
- Drag document from one folder to another folder
- Visual drag indicators showing valid drop zones
- Update document registry when documents are moved

**Technical Requirements:**
- HTML5 drag and drop API for document items
- Drag source: Document items in tree
- Drop target: Folder items in tree
- Visual feedback during drag (hover state on folders)
- Update document metadata when moved (folderId change)
- Support documents at root level (folderId = null)
- Update document registry after move operation

**Changes Required:**
- Frontend: Draggable document items
  - Source: src/components/workspace/CaseTreeExplorer.tsx
  - Add: draggable={true} to document items
  - Add: onDragStart handler setting dataTransfer with document ID
- Frontend: Droppable folder items
  - Source: src/components/workspace/CaseTreeExplorer.tsx
  - Add: onDragOver handler (preventDefault to allow drop)
  - Add: onDrop handler receiving document ID and folder ID
  - Add: onDragEnter/onDragLeave for hover state styling
- Frontend: Root level document support
  - Source: src/types/case.ts
  - Update: Document interface folderId to be optional (folderId?: string | null)
  - Logic: Documents with folderId=null displayed at case root level
- Frontend: Visual drag indicators
  - Source: src/components/workspace/CaseTreeExplorer.tsx
  - Add: CSS class for drag-over state (border highlight, background color)
  - Add: Cursor style changes during drag (grabbing cursor)
  - Add: Drop zone visual (dashed border on valid drop targets)
- Frontend: Move document function
  - Source: src/contexts/AppContext.tsx
  - Add: moveDocument(documentId: string, sourceFolderId: string | null, targetFolderId: string) -> Promise<void>
  - Logic: Update document's folderId, call backend API to update registry
- Backend: Move document API endpoint
  - Source: backend/api/documents.py
  - Endpoint: PATCH /api/documents/move
  - Request: { documentId: string, sourceFolderId: string | null, targetFolderId: string }
  - Response: { success: boolean, document: Document }
- Backend: Update document registry on move
  - Source: backend/services/document_registry.py
  - Add: move_document(doc_id: string, new_folder_id: string) -> bool
  - Logic: Update manifest entry with new folderId
  - Logic: Move physical file if needed (optional for MVP)
- Frontend: Prevent invalid drops
  - Source: src/components/workspace/CaseTreeExplorer.tsx
  - Logic: Cannot drop document onto another document
  - Logic: Cannot drop folder onto document
  - Logic: Disable drop if source and target folder are the same
- Frontend: Toast notification on move
  - Source: src/components/workspace/CaseTreeExplorer.tsx
  - Add: Success toast "Document moved to {folderName}"
  - Add: Error toast if move fails "Failed to move document"

**Drag and Drop Implementation:**
```tsx
// src/components/workspace/CaseTreeExplorer.tsx

// Document item - draggable
<div
  draggable
  onDragStart={(e) => {
    e.dataTransfer.setData('documentId', document.id);
    e.dataTransfer.setData('sourceFolderId', document.folderId || '');
    e.dataTransfer.effectAllowed = 'move';
  }}
  className="document-item cursor-grab"
>
  {document.name}
</div>

// Folder item - drop target
<div
  onDragOver={(e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  }}
  onDragEnter={(e) => {
    e.currentTarget.classList.add('drag-over');
  }}
  onDragLeave={(e) => {
    e.currentTarget.classList.remove('drag-over');
  }}
  onDrop={(e) => {
    e.preventDefault();
    const documentId = e.dataTransfer.getData('documentId');
    const sourceFolderId = e.dataTransfer.getData('sourceFolderId') || null;
    const targetFolderId = folder.id;

    if (sourceFolderId !== targetFolderId) {
      moveDocument(documentId, sourceFolderId, targetFolderId);
    }

    e.currentTarget.classList.remove('drag-over');
  }}
  className="folder-item"
>
  {folder.name}
</div>
```

**CSS for Drag States:**
```css
.document-item {
  cursor: grab;
}

.document-item:active {
  cursor: grabbing;
}

.folder-item.drag-over {
  background-color: #e0f2fe;
  border: 2px dashed #0284c7;
}
```

**Test Cases:**
- TC-S5-016-01: Drag document from Personal Data folder onto Certificates folder, verify document moved
- TC-S5-016-02: Document displayed at case root level (no folder), verify visible in tree
- TC-S5-016-03: Drag root-level document into Personal Data folder, verify document moved into folder
- TC-S5-016-04: During drag, hover over folder, verify folder shows drag-over styling (border highlight)
- TC-S5-016-05: Drop document into folder, verify success toast "Document moved to Personal Data"
- TC-S5-016-06: Attempt to drop document onto another document, verify drop not allowed
- TC-S5-016-07: Drag document and drop on same folder, verify no action (no redundant move)
- TC-S5-016-08: Move document via drag-drop, verify document registry updated with new folderId
- TC-S5-016-09: Move document, refresh page, verify document persists in new folder location
- TC-S5-016-10: Drag cursor changes to grabbing during drag operation
- TC-S5-016-11: Cancel drag (drag out of window), verify document remains in original folder
- TC-S5-016-12: Move document, click it, verify DocumentViewer displays correct document
- TC-S5-016-13: Drag multiple documents sequentially, verify each moves correctly
- TC-S5-016-14: Upload document to root (folderId=null), verify appears outside folders in tree

**Created:** 2026-01-09T16:00:00Z

---

## Non-Functional Requirements

---

## NFR-S5-001: Multi-Language AI Response Accuracy

**Status:** proposed

**Description:**
Ensure the Gemini AI service maintains high accuracy when processing and responding to requests in multiple languages (German, English, Arabic). Cross-language operations (e.g., German query on English document, Arabic email translation to German) must preserve semantic meaning with ≥90% accuracy. The system should detect language automatically and handle language-specific text processing (RTL for Arabic, umlauts for German) correctly. Response times for multi-language operations must remain within acceptable limits (≤3 seconds for translation, ≤5 seconds for semantic search).

**Changes Required:**
- Backend: Language detection service
  - Source: backend/tools/language_detector.py
  - Method: detect_language() with ≥95% accuracy
  - Library: langdetect or Gemini API language detection
- Backend: Multi-language prompt engineering
  - Source: backend/services/gemini_service.py
  - Update: Prompts explicitly state source and target languages
  - Update: Include examples for cross-language matching
- Backend: Response validation for accuracy
  - Source: backend/tests/test_multilanguage.py
  - Tests: Cross-language translation accuracy tests
  - Tests: Semantic search accuracy across languages
- Backend: Performance benchmarks
  - Source: backend/tests/test_performance.py
  - Benchmark: Translation operations ≤3 seconds
  - Benchmark: Semantic search ≤5 seconds

**Test Cases:**
- TC-NFR-S5-001-01: German query "Reisepassnummer" on English doc with "passport number", verify correct match
- TC-NFR-S5-001-02: Translate Arabic email to German, verify semantic accuracy ≥90%
- TC-NFR-S5-001-03: Detect language of text samples (German, English, Arabic), verify ≥95% accuracy
- TC-NFR-S5-001-04: German text with umlauts (ä, ö, ü), verify preserved correctly in all operations
- TC-NFR-S5-001-05: Arabic RTL text, verify rendered correctly in UI and email viewer
- TC-NFR-S5-001-06: Cross-language translation response time, verify ≤3 seconds on average

**Created:** 2026-01-09T16:00:00Z

---

## NFR-S5-002: SHACL Validation Performance

**Status:** proposed

**Description:**
Client-side SHACL validation must execute quickly without blocking the UI. Form field validation should complete within 100ms per field. Full form validation (all fields) should complete within 500ms for forms with up to 20 fields. SHACL shape generation on the backend should complete within 1 second for complex forms. Validation error messages must be clear, specific, and reference the SHACL constraint that failed.

**Changes Required:**
- Frontend: Optimize validation functions
  - Source: src/components/workspace/FormViewer.tsx
  - Add: Debouncing for validation triggers (300ms delay)
  - Add: Validation caching to avoid re-validating unchanged fields
- Backend: SHACL generation performance
  - Source: backend/services/shacl_generator.py
  - Optimize: Pattern matching and schema.org lookups
  - Target: ≤1 second for 20-field forms
- Frontend: Async validation to prevent UI blocking
  - Source: src/components/workspace/FormViewer.tsx
  - Update: Use async validation with loading state
  - Update: Don't block form submission while validating

**Test Cases:**
- TC-NFR-S5-002-01: Validate single field, verify completes within 100ms
- TC-NFR-S5-002-02: Validate 20-field form, verify completes within 500ms
- TC-NFR-S5-002-03: Generate SHACL shape for 20-field form, verify ≤1 second
- TC-NFR-S5-002-04: Type in field, verify validation debounced (not triggered on every keystroke)
- TC-NFR-S5-002-05: Validation error message, verify includes specific SHACL constraint reference
- TC-NFR-S5-002-06: Validate field twice without changes, verify uses cached result (faster)

**Created:** 2026-01-09T16:00:00Z

---

## NFR-S5-003: Document Processing Scalability

**Status:** proposed

**Description:**
The system must handle document processing operations (anonymization, translation, search) efficiently for documents of varying sizes. Image files up to 15 MB must be processed without timeout. PDF files up to 100 pages must be translatable within 2 minutes. Email files with multiple attachments must parse within 5 seconds. The backend should implement timeout handling to prevent operations from hanging indefinitely. Memory usage during document processing should not exceed 500 MB per operation.

**Changes Required:**
- Backend: Timeout configuration
  - Source: backend/config.py
  - Add: ANONYMIZATION_TIMEOUT = 60 seconds
  - Add: TRANSLATION_TIMEOUT = 120 seconds
  - Add: SEARCH_TIMEOUT = 30 seconds
- Backend: Memory monitoring
  - Source: backend/services/resource_monitor.py (new file)
  - Methods: monitor_memory_usage() during document operations
  - Alert: Log warning if memory exceeds 500 MB
- Backend: Chunked processing for large files
  - Source: backend/services/pdf_translation_service.py
  - Update: Process PDF in batches of 10 pages at a time
  - Reason: Prevent memory overflow on large PDFs
- Backend: Progress indicators for long operations
  - Source: backend/api/translation.py
  - Add: WebSocket progress updates for translations
  - Format: { progress: 0.5, message: "Translating page 50 of 100" }

**Test Cases:**
- TC-NFR-S5-003-01: Anonymize 15 MB image, verify completes within 60 seconds
- TC-NFR-S5-003-02: Translate 100-page PDF, verify completes within 2 minutes
- TC-NFR-S5-003-03: Parse email with 5 attachments, verify completes within 5 seconds
- TC-NFR-S5-003-04: Operation exceeds timeout, verify graceful error message
- TC-NFR-S5-003-05: Monitor memory during 50-page PDF translation, verify ≤500 MB
- TC-NFR-S5-003-06: Large document operation, verify progress updates sent via WebSocket

**Created:** 2026-01-09T16:00:00Z

---

## Data Requirements

---

## D-S5-001: SHACL Property Shape Schema

**Status:** proposed

**Description:**
Define comprehensive SHACL property shape schema for form field validation with schema.org integration. Each form field must have a corresponding SHACL PropertyShape that includes semantic type (schema.org), data type (xsd:string, xsd:date), constraints (sh:pattern, sh:minCount, sh:maxCount), and validation messages. The schema supports all form field types (text, date, select, textarea) and provides validation patterns for common field types (email, phone, name, address).

**Changes Required:**
- Backend: SHACL property shape model
  - Source: backend/models/shacl_property_shape.py (new file)
  - Class: SHACLPropertyShape with fields:
    - sh_path: string (schema.org property)
    - sh_datatype: string (xsd type)
    - sh_pattern: Optional[string] (regex pattern)
    - sh_minCount: Optional[int]
    - sh_maxCount: Optional[int]
    - sh_name: string (human-readable name)
    - sh_description: string
    - sh_message: string (validation error message)
- Backend: Validation pattern library
  - Source: backend/schemas/validation_patterns.py (new file)
  - Constants: EMAIL_PATTERN, PHONE_PATTERN, NAME_PATTERN, DATE_PATTERN, ADDRESS_PATTERN
  - Each pattern includes regex and error message
- Frontend: TypeScript SHACL shape interface
  - Source: src/types/shacl.ts
  - Update: SHACLPropertyShape interface matching backend model
  - Add: ValidationPattern type with pattern and message

**SHACL Property Shape Example:**
```json
{
  "@context": {
    "sh": "http://www.w3.org/ns/shacl#",
    "schema": "http://schema.org/",
    "xsd": "http://www.w3.org/2001/XMLSchema#"
  },
  "@type": "sh:PropertyShape",
  "sh:path": "schema:email",
  "sh:datatype": "xsd:string",
  "sh:pattern": "^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$",
  "sh:name": "Email Address",
  "sh:description": "Contact email address for the applicant",
  "sh:message": "Email must be a valid email address containing @ and a domain",
  "sh:minCount": 1
}
```

**Test Cases:**
- TC-D-S5-001-01: Generate SHACL shape for email field, verify includes sh:pattern for email validation
- TC-D-S5-001-02: Verify sh:path uses schema.org vocabulary (schema:email, schema:name)
- TC-D-S5-001-03: Required field, verify sh:minCount = 1
- TC-D-S5-001-04: Optional field, verify sh:minCount not set or = 0
- TC-D-S5-001-05: Date field, verify sh:datatype = "xsd:date"
- TC-D-S5-001-06: Validation error, verify sh:message displayed in UI

**Created:** 2026-01-09T16:00:00Z

---

## D-S5-002: Document Registry Schema

**Status:** proposed

**Description:**
Define comprehensive document registry schema that tracks all documents, their metadata, renders, and folder locations. The registry persists across application restarts and provides the source of truth for the document tree structure. Schema includes document ID, case ID, folder ID, file path, upload timestamp, file hash for integrity checking, and array of renders. Each render has its own ID, type (anonymized, translated), file path, and creation timestamp.

**Changes Required:**
- Data: Document registry schema definition
  - Source: backend/schemas/document_registry_schema.json (new file)
  - Schema: JSON Schema defining DocumentRegistryEntry structure
  - Validation: Required fields, format validation, enum constraints
- Data: Document registry manifest format
  - Source: backend/data/document_manifest.json
  - Format:
    ```json
    {
      "version": "1.0",
      "schemaVersion": "1.0",
      "lastUpdated": "2026-01-09T16:00:00Z",
      "documents": [
        {
          "documentId": "doc_001",
          "caseId": "ACTE-2024-001",
          "folderId": "personal-data",
          "fileName": "Birth_Certificate.jpg",
          "filePath": "public/documents/ACTE-2024-001/personal-data/Birth_Certificate.jpg",
          "type": "jpg",
          "uploadedAt": "2026-01-08T10:00:00Z",
          "fileHash": "sha256:abc123def456...",
          "metadata": {
            "originalFileName": "Geburtsurkunde.jpg",
            "fileSize": 2048576,
            "mimeType": "image/jpeg"
          },
          "renders": [
            {
              "renderId": "render_001",
              "type": "anonymized",
              "filePath": "public/documents/ACTE-2024-001/personal-data/Birth_Certificate_anonymized.jpg",
              "createdAt": "2026-01-08T10:15:00Z"
            },
            {
              "renderId": "render_002",
              "type": "translated",
              "language": "en",
              "filePath": "public/documents/ACTE-2024-001/personal-data/Birth_Certificate_translated_en.jpg",
              "createdAt": "2026-01-08T10:20:00Z"
            }
          ]
        }
      ]
    }
    ```
- Backend: Manifest validation
  - Source: backend/services/document_registry.py
  - Method: validate_manifest(manifest: dict) -> ValidationResult
  - Logic: Validate against JSON schema, check for required fields

**Test Cases:**
- TC-D-S5-002-01: Load manifest, verify conforms to schema
- TC-D-S5-002-02: Document entry includes fileHash, verify integrity check works
- TC-D-S5-002-03: Document with 2 renders, verify renders array has 2 entries
- TC-D-S5-002-04: Render entry includes type and createdAt, verify fields present
- TC-D-S5-002-05: Translated render includes language field (e.g., "de", "en")
- TC-D-S5-002-06: Manifest lastUpdated field, verify updates after document operations

**Created:** 2026-01-09T16:00:00Z

---

## D-S5-003: Enhanced Case Context Schema (Integration Course)

**Status:** proposed

**Description:**
Comprehensive case context schema for German Integration Course Application (ACTE-2024-001) with researched requirements, regulations, and validation rules. This context includes 15+ required documents with specifications, 10+ regulation references, 20+ common issues with solutions, processing information, and validation rules. The context serves as the knowledge base for the AI validation agent and ensures accurate case guidance.

**Changes Required:**
- Data: Enhanced case context for ACTE-2024-001
  - Source: backend/data/contexts/cases/ACTE-2024-001/case.json
  - Content: Complete Integration Course context as defined in S5-013
  - Required: 15+ document specifications with criticality levels
  - Required: 10+ regulation references with URLs
  - Required: 20+ common issues with solutions
- Data: Template for Integration Course cases
  - Source: backend/data/contexts/templates/integration_course/case.json
  - Content: Same as ACTE-2024-001 but generic (no case-specific data)
  - Purpose: Used when creating new Integration Course cases
- Data: Asylum Application context template
  - Source: backend/data/contexts/templates/asylum_application/case.json
  - Content: Researched asylum requirements and regulations
- Data: Family Reunification context template
  - Source: backend/data/contexts/templates/family_reunification/case.json
  - Content: Researched family visa requirements

**Test Cases:**
- TC-D-S5-003-01: Load ACTE-2024-001 context, verify requiredDocuments array has ≥15 entries
- TC-D-S5-003-02: Verify regulations array has ≥10 entries with valid URLs
- TC-D-S5-003-03: Verify commonIssues array has ≥20 entries
- TC-D-S5-003-04: Each required document has criticality field ('critical' or 'optional')
- TC-D-S5-003-05: Load template, verify structure matches case context but without case-specific IDs
- TC-D-S5-003-06: Context schemaVersion field, verify is "2.0" (enhanced version)

**Created:** 2026-01-09T16:00:00Z

---
