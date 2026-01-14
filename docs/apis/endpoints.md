# BAMF ACTE Companion - API Endpoints Reference

## Overview

This document provides detailed information about the BAMF ACTE Companion API endpoints, including both currently simulated operations and the planned future backend API.

**Current Status:** Backend API implementation has started using FastAPI. WebSocket-based AI chat and health check endpoints are now implemented. Other operations remain simulated client-side.

---

## Table of Contents

- [Health & System](#health--system)
- [Real-Time Communication](#real-time-communication)
- [Admin Operations](#admin-operations)
- [Authentication](#authentication)
- [Case Management](#case-management)
- [Document Operations](#document-operations)
- [Context API](#context-api)
- [Search API](#search-api)
- [File Operations](#file-operations)
- [AI Operations](#ai-operations)
- [Form Management](#form-management)
- [Search](#search)

---

## Health & System

### GET /health

Backend service health check endpoint.

**Current Implementation:** IMPLEMENTED in `backend/main.py`

**Source:** `backend/main.py:84-95`

**Authentication:** None (public endpoint)

**Success Response (200 OK):**
```json
{
  "status": "healthy"
}
```

**Example:**
```bash
curl -X GET http://localhost:8000/health
```

**Usage:**
- Monitoring and alerting systems
- Load balancer health checks
- Container orchestration readiness probes

---

### GET /

Backend API root information endpoint.

**Current Implementation:** IMPLEMENTED in `backend/main.py`

**Source:** `backend/main.py:98-111`

**Authentication:** None (public endpoint)

**Success Response (200 OK):**
```json
{
  "name": "BAMF AI Case Management API",
  "version": "0.1.0"
}
```

**Example:**
```bash
curl -X GET http://localhost:8000/
```

---

### GET /api/chat/health

Chat service health check with Gemini API status.

**Current Implementation:** IMPLEMENTED in `backend/api/chat.py`

**Source:** `backend/api/chat.py:343-360`

**Authentication:** None (public endpoint)

**Success Response (200 OK - Service Ready):**
```json
{
  "service": "chat",
  "status": "ready",
  "gemini_initialized": true
}
```

**Service Not Ready Response (503 Service Unavailable):**
```json
{
  "service": "chat",
  "status": "not_ready",
  "gemini_initialized": false
}
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/chat/health
```

**Usage:**
- Check if Gemini API key is configured
- Verify chat service initialization status
- Frontend can check before enabling chat features

---

### POST /api/chat/clear/{case_id}

Clear conversation history for a specific case (S5-010).

**Current Implementation:** IMPLEMENTED in `backend/api/chat.py`

**Source:** `backend/api/chat.py:550-610`

**Authentication:** None (public endpoint)

**Path Parameters:**
- `case_id` (required): Case identifier to clear history for (e.g., "ACTE-2024-001")

**Prerequisites:**
- `ENABLE_CHAT_HISTORY` must be enabled in backend configuration
- Default: disabled (can be enabled via environment variable)

**Success Response (200 OK):**
```json
{
  "success": true,
  "case_id": "ACTE-2024-001",
  "messages_cleared": 5,
  "message": "Successfully cleared 5 message(s) from conversation history"
}
```

**Feature Disabled Response (400 Bad Request):**
```json
{
  "success": false,
  "case_id": "ACTE-2024-001",
  "messages_cleared": 0,
  "message": "Chat history feature is disabled"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "success": false,
  "case_id": "ACTE-2024-001",
  "messages_cleared": 0,
  "error": "Error details"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/chat/clear/ACTE-2024-001
```

**Usage:**
- Clear stored conversation history when starting a new topic
- Reset conversation context without disconnecting WebSocket
- Privacy: Remove sensitive conversation data
- Requires `ENABLE_CHAT_HISTORY=true` in backend environment

**Note:** Conversation history is stored in-memory and cleared on application restart. This endpoint only works when the chat history feature is explicitly enabled.

---

### GET /api/admin/health

Admin service health check with feature availability.

**Current Implementation:** IMPLEMENTED in `backend/api/admin.py`

**Source:** `backend/api/admin.py:196-217`

**Authentication:** None (public endpoint)

**Success Response (200 OK):**
```json
{
  "service": "admin",
  "status": "ready",
  "features": {
    "field_generation": true
  }
}
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/admin/health
```

**Usage:**
- Check if admin service is available
- Verify field generation feature is enabled
- Monitoring and health checks

---

## Real-Time Communication

### WS /ws/chat/{case_id}

WebSocket endpoint for real-time, case-scoped AI chat communication with multilingual support.

**Current Implementation:** IMPLEMENTED in `backend/api/chat.py`

**Source:** `backend/api/chat.py:85-201`

**Authentication:** None (case-scoped isolation via URL parameter)

**Path Parameters:**
- `case_id` (required): Case identifier for context isolation (e.g., "ACTE-2024-001")

**Query Parameters:**
- `language` (optional): Language for AI responses and system messages. Default: 'de' (German)
  - Supported values: 'de' (German), 'en' (English)
  - Example: `ws://localhost:8000/ws/chat/ACTE-2024-001?language=en`
  - Affects: Welcome message translation and AI response language

**Connection Protocol:**

1. Client initiates WebSocket connection to `/ws/chat/{case_id}?language={lang}`
2. Server accepts connection and sends translated system message confirming connection
3. Bidirectional message exchange begins
4. Connection remains open until client disconnects or error occurs

**Message Protocol:**

#### Incoming Messages (Client to Server)

**Chat Message Format:**
```json
{
  "type": "chat",
  "content": "User message or question",
  "caseId": "ACTE-2024-001",
  "folderId": "personal-data",
  "documentContent": "Optional document text to analyze",
  "formSchema": [
    {
      "id": "name",
      "label": "Full Name",
      "type": "text",
      "required": true
    }
  ]
}
```

**Message Fields:**
- `type` (required): Message type - "chat" or "anonymize"
- `content` (required): User's message, question, or instruction
- `caseId` (optional): Case ID for context (should match URL parameter)
- `folderId` (optional): Folder ID for folder-specific context
- `documentContent` (optional): Document text to include in context
- `formSchema` (optional): Form field definitions for extraction requests
- `currentFormValues` (optional): Current form field values for suggestion mode (S5-002)
  - Format: `{"field_id": "current_value", ...}`
  - When provided, enables smart form extraction:
    - Empty fields: Filled automatically (direct update)
    - Non-empty fields with different values: Presented as suggestions requiring user approval
    - Identical values: Ignored
- `language` (optional): Language for AI responses. Default: 'de' (German)
  - Supported values: 'de', 'en'
  - Overrides the query parameter language setting for this specific message
- `stream` (optional): Enable streaming responses (default: true)

**Anonymization Message Format:**
```json
{
  "type": "anonymize",
  "filePath": "/path/to/document.jpg",
  "folderId": "optional-folder-id"
}
```

**Anonymization Message Fields:**
- `type` (required): Must be "anonymize"
- `filePath` (required): Path to the document file to anonymize
- `folderId` (optional): Folder ID for context

**Form Extraction Trigger:**
The AI automatically detects form filling requests when:
- `formSchema` is provided AND
- Message contains keywords: "fill", "extract", or "populate"

#### Outgoing Messages (Server to Client)

**System Message (Connection Confirmation):**

The welcome message is automatically translated based on the `language` query parameter. The case ID prefix is also localized:
- German (de): "ACTE" → "Akte"
- English (en): "ACTE" → "Case"

```json
{
  "type": "system",
  "content": "Verbunden mit KI-Assistent für Akte-2024-001",
  "timestamp": null
}
```

English example (language=en):
```json
{
  "type": "system",
  "content": "Connected to AI assistant for Case-2024-001",
  "timestamp": null
}
```

**Chat Response (AI Answer - Non-Streaming Mode):**
```json
{
  "type": "chat_response",
  "content": "AI-generated response text",
  "timestamp": null
}
```

**Chat Chunk (AI Answer - Streaming Mode):**
```json
{
  "type": "chat_chunk",
  "content": "Partial response text...",
  "is_complete": false,
  "timestamp": null
}
```

**Chat Chunk Completion (Streaming Mode Final Message):**
```json
{
  "type": "chat_chunk",
  "content": "",
  "is_complete": true,
  "timestamp": null
}
```

**Form Update (Field Extraction Results):**

When `currentFormValues` is NOT provided (legacy mode), all extracted values are sent as direct updates:
```json
{
  "type": "form_update",
  "updates": {
    "name": "Ahmad Ali",
    "birthDate": "1995-03-20",
    "countryOfOrigin": "Afghanistan"
  },
  "confidence": {
    "name": 0.95,
    "birthDate": 0.90,
    "countryOfOrigin": 0.92
  },
  "timestamp": null
}
```

When `currentFormValues` IS provided (suggestion mode - S5-002), only empty fields are sent as direct updates:
```json
{
  "type": "form_update",
  "updates": {
    "birthDate": "1995-03-20"
  },
  "confidence": {
    "birthDate": 0.90
  },
  "timestamp": null
}
```

**Form Suggestion (Suggestion Mode - S5-002):**

New message type sent when `currentFormValues` is provided and non-empty fields have different values. Requires user approval before applying:
```json
{
  "type": "form_suggestion",
  "suggestions": {
    "name": {
      "value": "Ahmad Ali",
      "confidence": 0.95,
      "current": "Ahmed Aly"
    },
    "countryOfOrigin": {
      "value": "Afghanistan",
      "confidence": 0.92,
      "current": "Syria"
    }
  },
  "timestamp": null
}
```

**Suggestion Fields:**
- `value`: AI-extracted value (suggested new value)
- `confidence`: Confidence score (0.0 to 1.0)
- `current`: Current value in the form (for comparison)

**Error Message:**
```json
{
  "type": "error",
  "message": "Error description",
  "timestamp": null
}
```

**Anonymization Complete Message:**
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

**Anonymization Confirmation Message:**
```json
{
  "type": "chat_response",
  "content": "Document anonymized successfully. Found and masked 5 PII fields. The anonymized version has been saved.",
  "timestamp": null
}
```

**Message Types Summary:**
- `system` - System notifications (connection status, etc.)
- `chat_response` - AI text responses to user queries (non-streaming mode)
- `chat_chunk` - Streaming AI response chunks with completion flag
- `form_update` - Extracted form field values with confidence scores (direct updates)
- `form_suggestion` - Suggested form field changes requiring user approval (S5-002)
- `anonymization_complete` - Document anonymization results with file paths and detection count
- `error` - Error notifications

**Context Loading:**

The WebSocket endpoint automatically loads case-specific context:

1. **Case-Level Context:** Loaded from `backend/data/contexts/cases/{case_id}/case.json`
   - Case type, regulations, required documents, validation rules

2. **Folder-Level Context (if folderId provided):** Loaded from `backend/data/contexts/cases/{case_id}/folders/{folder_id}.json`
   - Expected documents, validation criteria, common mistakes

3. **Document Content (if provided):** Included directly in the message

All contexts are merged and provided to the AI for context-aware responses.

**Case Isolation:**

Each WebSocket connection is strictly scoped to a single case:
- Connection manager maintains one connection per case ID
- Context is loaded only for the specified case
- No cross-case data access
- Switching cases requires a new WebSocket connection

**Error Handling:**

**API Key Not Configured:**
```json
{
  "type": "error",
  "message": "API key not configured",
  "timestamp": null
}
```
Connection is immediately closed after this error.

**Invalid Message Format:**
```json
{
  "type": "error",
  "message": "Invalid message format: expected JSON object",
  "timestamp": null
}
```

**Empty Message Content:**
```json
{
  "type": "error",
  "message": "Message content cannot be empty",
  "timestamp": null
}
```

**Form Extraction Failure:**
```json
{
  "type": "error",
  "message": "Failed to extract form fields: [error details]",
  "timestamp": null
}
```

**Connection Lifecycle:**

```
Client                          Server
  |                               |
  |-------- Connect -------------->|
  |<------ Accept & System Msg ----|
  |                               |
  |-------- Chat Message --------->|
  |                 [AI Processing]
  |<------ Chat Response ----------|
  |                               |
  |-- Form Extraction Request ---->|
  |              [AI Extraction]
  |<------ Form Update ------------|
  |<------ Chat Response ----------|
  |                               |
  |-------- Disconnect ----------->|
  |                               |
```

**Example Usage:**

**JavaScript/TypeScript Client:**
```javascript
const caseId = "ACTE-2024-001";
const ws = new WebSocket(`ws://localhost:8000/ws/chat/${caseId}`);

ws.onopen = () => {
  console.log("Connected to AI chat");
};

// Handle messages with streaming support
let currentStreamingMessage = "";

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  switch (message.type) {
    case "system":
      console.log("System:", message.content);
      break;

    case "chat_response":
      // Non-streaming mode: complete response
      console.log("AI:", message.content);
      break;

    case "chat_chunk":
      // Streaming mode: append chunks
      if (message.is_complete) {
        // Final chunk - streaming complete
        console.log("\n[Streaming complete]");
        currentStreamingMessage = "";
      } else {
        // Add chunk to current message
        currentStreamingMessage += message.content;
        process.stdout.write(message.content); // Print chunk without newline
      }
      break;

    case "form_update":
      console.log("Form updates:", message.updates);
      console.log("Confidence:", message.confidence);
      break;

    case "error":
      console.error("Error:", message.message);
      break;
  }
};

ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};

ws.onclose = () => {
  console.log("Disconnected from AI chat");
};

// Send a chat message with streaming (default)
function sendMessage(content) {
  ws.send(JSON.stringify({
    type: "chat",
    content: content,
    caseId: caseId,
    folderId: "personal-data",
    stream: true  // Enable streaming (default behavior)
  }));
}

// Send a chat message without streaming
function sendMessageNoStreaming(content) {
  ws.send(JSON.stringify({
    type: "chat",
    content: content,
    caseId: caseId,
    folderId: "personal-data",
    stream: false  // Disable streaming
  }));
}

// Request form field extraction
function extractFormFields(documentContent, formSchema) {
  ws.send(JSON.stringify({
    type: "chat",
    content: "Please extract and fill the form fields from this document",
    caseId: caseId,
    documentContent: documentContent,
    formSchema: formSchema
  }));
}
```

**Python Client:**
```python
import asyncio
import websockets
import json

async def chat_client():
    case_id = "ACTE-2024-001"
    uri = f"ws://localhost:8000/ws/chat/{case_id}"

    async with websockets.connect(uri) as websocket:
        # Wait for system message
        response = await websocket.recv()
        print(json.loads(response))

        # Send chat message
        await websocket.send(json.dumps({
            "type": "chat",
            "content": "What documents are required for this case?",
            "caseId": case_id,
            "folderId": "personal-data"
        }))

        # Receive response
        response = await websocket.recv()
        message = json.loads(response)
        print(f"AI: {message['content']}")

asyncio.run(chat_client())
```

**Multilingual Support Example (S5-014):**
```javascript
// Connect with English language preference
const ws = new WebSocket('ws://localhost:8000/ws/chat/ACTE-2024-001?language=en');

ws.onopen = () => {
  console.log('Connected');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  // First message: system welcome in English
  // { "type": "system", "content": "Connected to AI assistant for Case-2024-001" }

  console.log(message);
};

// Send chat message with language override (use German for this specific message)
ws.send(JSON.stringify({
  type: "chat",
  content: "Welche Dokumente werden für diesen Fall benötigt?",
  caseId: "ACTE-2024-001",
  language: "de"  // Override to German for this message
}));

// German connection example
const wsGerman = new WebSocket('ws://localhost:8000/ws/chat/ACTE-2024-001?language=de');
// Welcome message: "Verbunden mit KI-Assistent für Akte-2024-001"

// Default behavior (no language parameter = German)
const wsDefault = new WebSocket('ws://localhost:8000/ws/chat/ACTE-2024-001');
// Welcome message: "Verbunden mit KI-Assistent für Akte-2024-001"
```

**Form Extraction Example:**

**Basic Form Extraction (Legacy Mode):**
```javascript
const formSchema = [
  { id: "name", label: "Full Name", type: "text", required: true },
  { id: "birthDate", label: "Date of Birth", type: "date", required: true },
  { id: "countryOfOrigin", label: "Country", type: "text", required: true }
];

const documentContent = `
Birth Certificate
Name: Ahmad Ali
Date of Birth: March 20, 1995
Place of Birth: Kabul, Afghanistan
`;

ws.send(JSON.stringify({
  type: "chat",
  content: "Please extract the form fields from this document",
  caseId: "ACTE-2024-001",
  documentContent: documentContent,
  formSchema: formSchema
}));

// Expected responses:
// 1. form_update with extracted values
// 2. chat_response confirming extraction
```

**Form Extraction with Suggestion Mode (S5-002):**
```javascript
// When currentFormValues is provided, the system intelligently categorizes updates
const currentFormValues = {
  name: "Ahmed Aly",          // Non-empty, different from extracted
  birthDate: "",              // Empty, will be filled directly
  countryOfOrigin: "Syria"    // Non-empty, different from extracted
};

ws.send(JSON.stringify({
  type: "chat",
  content: "Please extract the form fields from this document",
  caseId: "ACTE-2024-001",
  documentContent: documentContent,
  formSchema: formSchema,
  currentFormValues: currentFormValues  // Enable suggestion mode
}));

// Expected responses:
// 1. form_update with direct updates (empty fields only):
//    { "updates": { "birthDate": "1995-03-20" } }
//
// 2. form_suggestion with suggestions (non-empty fields that differ):
//    {
//      "suggestions": {
//        "name": {
//          "value": "Ahmad Ali",
//          "confidence": 0.95,
//          "current": "Ahmed Aly"
//        },
//        "countryOfOrigin": {
//          "value": "Afghanistan",
//          "confidence": 0.92,
//          "current": "Syria"
//        }
//      }
//    }
//
// 3. chat_response with summary:
//    "I've extracted form data: 1 field filled, 2 suggestions available."
```

**Document Anonymization Example:**
```javascript
// Request anonymization of a document
ws.send(JSON.stringify({
  type: "anonymize",
  filePath: "/path/to/documents/ACTE-2024-001/personal-data/passport.jpg",
  folderId: "personal-data"
}));

// Expected responses:
// 1. anonymization_complete with result details
// 2. chat_response confirming the operation
```

**Anonymization Workflow:**

The WebSocket endpoint supports real-time document anonymization for image files:

1. **Client Request:**
   - Client sends `anonymize` message with `filePath` to document
   - Optionally includes `folderId` for context
   - Only image files (PNG, JPG, JPEG, etc.) are currently supported

2. **Server Processing:**
   - Validates file path is provided
   - Checks file format is supported (image files only)
   - Calls anonymization service to detect and mask PII
   - Creates anonymized version in same directory with "_anonymized" suffix

3. **Server Response:**
   - Sends `anonymization_complete` message with:
     - `originalPath`: Path to original document
     - `anonymizedPath`: Path to anonymized version (or null if failed)
     - `detectionsCount`: Number of PII fields detected and masked
     - `success`: Boolean indicating if operation succeeded
     - `error`: Error message if operation failed (null otherwise)
   - Sends follow-up `chat_response` with human-readable confirmation

4. **Supported File Formats:**
   - PNG (.png)
   - JPEG (.jpg, .jpeg)
   - Other image formats supported by anonymization service

5. **Error Cases:**
   - **No file path provided:** Returns error in `anonymization_complete`
   - **Unsupported format:** Returns error for non-image files
   - **Service failure:** Returns error with details from anonymization service

**Anonymization Response Examples:**

Success case:
```json
{
  "type": "anonymization_complete",
  "originalPath": "/public/documents/ACTE-2024-001/personal-data/passport.jpg",
  "anonymizedPath": "/public/documents/ACTE-2024-001/personal-data/passport_anonymized.jpg",
  "detectionsCount": 8,
  "success": true,
  "error": null,
  "timestamp": null
}
```

Failure case (unsupported format):
```json
{
  "type": "anonymization_complete",
  "originalPath": "/path/to/document.pdf",
  "anonymizedPath": null,
  "detectionsCount": 0,
  "success": false,
  "error": "Unsupported file format. Only image files (PNG, JPG, etc.) can be anonymized.",
  "timestamp": null
}
```

**Security Considerations:**

- No authentication currently implemented (planned for future)
- Case isolation enforced at connection level
- Input validation for all message fields
- Error messages don't expose sensitive information
- Connection rate limiting recommended (not yet implemented)

**Performance:**

- Single connection per case maintained by ConnectionManager
- AI responses use Google Gemini 2.5 Flash (optimized for speed)
- Context loaded once per message from filesystem
- **Streaming responses enabled by default (stream: true)**
  - Time-to-first-token: Typically 200-500ms
  - Total latency: 1-3 seconds for typical responses
  - Chunks delivered as generated for progressive UI updates
  - Better perceived performance compared to non-streaming mode
- Non-streaming mode available (stream: false) for simpler integration

**Streaming vs Non-Streaming Mode:**

**When to Use Streaming (stream: true, default):**
- Interactive chat interfaces where users benefit from progressive content
- Long responses where time-to-first-token matters
- Better perceived performance and user experience
- Real-time typing effect for AI responses
- Typical use case: conversational AI chat

**When to Use Non-Streaming (stream: false):**
- Simpler client-side implementation (single response handler)
- Processing responses as complete units (e.g., logging, caching)
- Form extraction (automatically non-streaming)
- Batch processing or automated workflows
- When progressive display is not needed

**Performance Comparison:**
- Streaming: First token in ~200-500ms, full response in 1-3s
- Non-streaming: Complete response in 1-3s (no progressive updates)
- Both modes have similar total latency
- Streaming provides better user experience through progressive rendering

**Known Limitations:**

- No authentication/authorization
- No message history persistence
- No typing indicators
- No read receipts
- One connection per case (reconnection required for case switch)
- No support for file uploads via WebSocket (use REST endpoints)
- Form extraction always uses non-streaming mode internally
- Anonymization only supports image files (PDF support planned for future)

---

## Admin Operations

### POST /api/admin/generate-field

Generate a SHACL-compliant form field specification from a natural language prompt.

**Current Implementation:** IMPLEMENTED in `backend/api/admin.py`

**Source:** `backend/api/admin.py:100-193`

**Authentication:** None (planned for future implementation)

**Description:**

This endpoint uses AI-powered natural language processing to generate form field specifications with semantic metadata. The service uses rule-based extraction for common patterns and falls back to AI (Gemini) for more complex or ambiguous requests.

**Request Body:**
```json
{
  "prompt": "Add a dropdown for marital status with options single, married, divorced"
}
```

**Request Constraints:**
- `prompt` (required): Natural language description (3-500 characters)

**Example Prompts:**
- "Add a text field for passport number"
- "Add dropdown for marital status with options single, married, divorced"
- "I need a required date field for visa expiry"
- "Create a textarea for additional notes"

**Supported Field Types:**
- `text`: Standard text input
- `date`: Date picker
- `select`: Dropdown with options
- `textarea`: Multi-line text

**Supported Languages:** English, German

**Success Response (200 OK):**
```json
{
  "field": {
    "id": "maritalStatus",
    "label": "Marital Status",
    "type": "select",
    "value": "",
    "options": ["single", "married", "divorced"],
    "required": false,
    "shaclMetadata": {
      "@context": {
        "sh": "http://www.w3.org/ns/shacl#",
        "schema": "http://schema.org/",
        "xsd": "http://www.w3.org/2001/XMLSchema#"
      },
      "@type": "sh:PropertyShape",
      "sh:path": "schema:maritalStatus",
      "sh:datatype": "xsd:string",
      "sh:name": "Marital Status",
      "sh:description": "The person's marital status",
      "sh:in": {
        "@list": ["single", "married", "divorced"]
      }
    }
  },
  "message": "Successfully generated 'Marital Status' field"
}
```

**Error Response (400 Bad Request - Invalid Input):**
```json
{
  "detail": {
    "error": "Field generation failed",
    "detail": "Prompt is too short or ambiguous"
  }
}
```

**Error Response (400 Bad Request - Validation Failed):**
```json
{
  "detail": {
    "error": "Generated field validation failed",
    "validation_errors": ["Field ID is missing", "Field type is invalid"]
  }
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "detail": {
    "error": "Internal server error",
    "detail": "Gemini API connection failed"
  }
}
```

**Example Usage:**

**cURL:**
```bash
curl -X POST http://localhost:8000/api/admin/generate-field \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Add a required text field for passport number"
  }'
```

**JavaScript/TypeScript:**
```javascript
const generateField = async (prompt) => {
  const response = await fetch('http://localhost:8000/api/admin/generate-field', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ prompt }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail.error);
  }

  return await response.json();
};

// Usage
const result = await generateField(
  "Add dropdown for education level with options high school, bachelor, master, doctorate"
);
console.log(result.field);
```

**Python:**
```python
import requests

def generate_field(prompt: str) -> dict:
    response = requests.post(
        "http://localhost:8000/api/admin/generate-field",
        json={"prompt": prompt}
    )

    if response.status_code != 200:
        raise Exception(f"Field generation failed: {response.json()}")

    return response.json()

# Usage
result = generate_field("Add a date field for visa expiry date")
print(result["field"])
```

**SHACL Metadata:**

The generated field includes SHACL (Shapes Constraint Language) metadata in JSON-LD format, which provides semantic meaning and validation constraints:

- `@context`: JSON-LD context with namespace prefixes
  - `sh`: SHACL namespace (http://www.w3.org/ns/shacl#)
  - `schema`: Schema.org namespace (http://schema.org/)
  - `xsd`: XML Schema Datatype namespace (http://www.w3.org/2001/XMLSchema#)

- `@type`: Always "sh:PropertyShape" for form fields

- `sh:path`: The semantic property path (e.g., "schema:name", "schema:birthDate")

- `sh:datatype`: XSD datatype defining the field's data type:
  - `xsd:string` for text and textarea fields
  - `xsd:date` for date fields
  - `xsd:string` with `sh:in` for select fields

- `sh:name`: Human-readable name for the field

- `sh:description`: Optional description of the field's purpose

- `sh:minCount`: Minimum cardinality (1 = required field)

- `sh:maxCount`: Maximum cardinality (1 = single value)

- `sh:in`: List of allowed values for select/enum fields (wrapped in JSON-LD @list)

**SHACL Benefits:**

1. **Semantic Interoperability**: Fields are linked to Schema.org vocabulary
2. **Machine-Readable Validation**: Constraints can be validated automatically
3. **Linked Data Integration**: Compatible with RDF and semantic web technologies
4. **Standard Compliance**: Uses W3C SHACL specification
5. **Future-Proof**: Supports advanced validation and reasoning

**Field Generation Process:**

1. **Prompt Analysis**: System analyzes the natural language prompt
2. **Rule-Based Extraction**: Common patterns are extracted using regex rules
3. **AI Fallback**: Complex prompts are sent to Gemini AI for interpretation
4. **Field Construction**: System builds the field specification
5. **SHACL Generation**: Semantic metadata is generated with proper namespaces
6. **Validation**: Generated field is validated against schema requirements
7. **Response**: Field specification with SHACL metadata is returned

**Use Cases:**

- **Dynamic Form Building**: Admin users can create form fields using natural language
- **Rapid Prototyping**: Quickly generate field specifications for testing
- **Form Templates**: Generate reusable field definitions for common use cases
- **Semantic Forms**: Build forms with semantic metadata for data integration
- **Multilingual Support**: Create fields with German or English prompts

**Known Limitations:**

- No authentication currently implemented (planned for future)
- Maximum prompt length: 500 characters
- Requires Gemini API key for complex prompts
- Generated field IDs are in camelCase format
- SHACL validation is performed but not enforced on the client side

**Performance:**

- Typical response time: 1-3 seconds (with AI)
- Rule-based extraction: < 100ms
- AI-based generation: 1-3 seconds depending on prompt complexity

**Security Considerations:**

- Input validation on prompt length and content
- Error messages don't expose sensitive information
- Rate limiting recommended (not yet implemented)
- Authentication planned for production use

---

### POST /api/admin/modify-form

Modify a form using natural language commands with automatic SHACL generation (S5-001).

**Current Implementation:** IMPLEMENTED in `backend/api/admin.py`

**Source:** `backend/api/admin.py:247-348`

**Authentication:** None (planned for future implementation)

**Description:**

This endpoint uses AI-powered natural language processing to modify form structures. It interprets natural language commands (add, remove, modify fields) and automatically generates SHACL metadata with Schema.org semantic types for each field.

**Request Body:**
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

**Request Constraints:**
- `command` (required): Natural language command (3-500 characters)
- `currentFields` (optional): Current form fields as array of field objects (default: empty array)
- `caseId` (optional): Case ID for the form (default: "UnknownCase")

**Supported Operations:**
- Add field: "Add an email field for contact email"
- Remove field: "Remove the phone number field"
- Add select field: "Add dropdown for marital status with options single, married, divorced"
- Add required field: "Add a required date field for birth date"

**Supported Field Types:**
- `text`: Standard text input (email, phone, name, etc.)
- `date`: Date picker
- `select`: Dropdown with options
- `textarea`: Multi-line text

**Automatic Semantic Type Inference:**

The system automatically infers Schema.org types from field labels:
- "email" → `schema:email` with email validation pattern
- "phone" → `schema:telephone` with phone validation pattern
- "name" → `schema:name` with name validation
- "birth date" → `schema:birthDate` with date validation
- "address" → `schema:address` with address validation

**Success Response (200 OK):**
```json
{
  "fields": [
    {
      "id": "name",
      "label": "Full Name",
      "type": "text",
      "value": "",
      "required": true,
      "shaclMetadata": {
        "@context": {
          "sh": "http://www.w3.org/ns/shacl#",
          "schema": "http://schema.org/",
          "xsd": "http://www.w3.org/2001/XMLSchema#"
        },
        "@type": "sh:PropertyShape",
        "sh:path": "schema:name",
        "sh:datatype": "xsd:string",
        "sh:name": "Full Name",
        "sh:description": "Person's full name",
        "sh:minCount": 1,
        "sh:maxCount": 1
      }
    },
    {
      "id": "contactEmail",
      "label": "Contact Email",
      "type": "text",
      "value": "",
      "required": false,
      "shaclMetadata": {
        "@context": {
          "sh": "http://www.w3.org/ns/shacl#",
          "schema": "http://schema.org/",
          "xsd": "http://www.w3.org/2001/XMLSchema#"
        },
        "@type": "sh:PropertyShape",
        "sh:path": "schema:email",
        "sh:datatype": "xsd:string",
        "sh:name": "Contact Email",
        "sh:description": "Contact email address",
        "sh:pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
      }
    }
  ],
  "shaclShape": {
    "@context": {
      "sh": "http://www.w3.org/ns/shacl#",
      "schema": "http://schema.org/",
      "xsd": "http://www.w3.org/2001/XMLSchema#",
      "acte": "http://bamf.example.de/acte#"
    },
    "@type": "sh:NodeShape",
    "sh:targetClass": "acte:IntegrationCourseApplication",
    "sh:property": [
      {
        "@type": "sh:PropertyShape",
        "sh:path": "schema:name",
        "sh:datatype": "xsd:string",
        "sh:name": "Full Name",
        "sh:minCount": 1,
        "sh:maxCount": 1
      },
      {
        "@type": "sh:PropertyShape",
        "sh:path": "schema:email",
        "sh:datatype": "xsd:string",
        "sh:name": "Contact Email",
        "sh:pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
      }
    ]
  },
  "modifications": [
    "Added field 'Contact Email' (email)"
  ],
  "message": "Form modified successfully"
}
```

**Error Response (400 Bad Request - Invalid Command):**
```json
{
  "error": "Form modification failed",
  "detail": "Unable to parse command: unclear operation"
}
```

**Error Response (400 Bad Request - Invalid Field Structure):**
```json
{
  "error": "Invalid field structure",
  "detail": "Field ID 'contactEmail' already exists"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "error": "Internal server error",
  "detail": "Gemini API connection failed"
}
```

**Example Usage:**

**cURL:**
```bash
curl -X POST http://localhost:8000/api/admin/modify-form \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

**JavaScript/TypeScript:**
```javascript
const modifyForm = async (command, currentFields, caseId) => {
  const response = await fetch('http://localhost:8000/api/admin/modify-form', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ command, currentFields, caseId }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || error.error);
  }

  return await response.json();
};

// Usage
const result = await modifyForm(
  "Add dropdown for marital status with options single, married, divorced",
  currentFields,
  "ACTE-2024-001"
);
console.log('Modifications:', result.modifications);
console.log('Updated fields:', result.fields);
```

**Python:**
```python
import requests

def modify_form(command: str, current_fields: list, case_id: str) -> dict:
    response = requests.post(
        "http://localhost:8000/api/admin/modify-form",
        json={
            "command": command,
            "currentFields": current_fields,
            "caseId": case_id
        }
    )

    if response.status_code != 200:
        raise Exception(f"Form modification failed: {response.json()}")

    return response.json()

# Usage
result = modify_form(
    "Add a required date field for birth date",
    current_fields,
    "ACTE-2024-001"
)
print(f"Modifications: {result['modifications']}")
print(f"Updated fields: {len(result['fields'])} fields")
```

**SHACL Shape Generation:**

The endpoint automatically generates a complete SHACL NodeShape for the entire form:

- `@context`: JSON-LD context with namespace prefixes
  - `sh`: SHACL namespace
  - `schema`: Schema.org namespace
  - `xsd`: XML Schema Datatype namespace
  - `acte`: BAMF ACTE custom namespace

- `@type`: Always "sh:NodeShape" for form definitions

- `sh:targetClass`: The semantic class the form validates (e.g., "acte:IntegrationCourseApplication")

- `sh:property`: Array of PropertyShapes, one for each form field

Each PropertyShape includes:
- `sh:path`: Semantic property path with Schema.org type
- `sh:datatype`: XSD datatype
- `sh:name`: Human-readable field name
- `sh:description`: Field description (auto-generated)
- `sh:pattern`: Validation regex pattern (for email, phone, etc.)
- `sh:minCount`: Minimum cardinality (1 for required fields)
- `sh:maxCount`: Maximum cardinality (1 for single-value fields)
- `sh:in`: List of allowed values (for select fields)

**Semantic Type Mappings:**

The SHACL generator service automatically maps field labels to Schema.org types:

| Field Label Contains | Schema.org Type | Validation Pattern |
|---------------------|----------------|-------------------|
| email | schema:email | Email regex |
| phone, telephone | schema:telephone | Phone regex |
| name (full/given/family) | schema:name/givenName/familyName | Name validation |
| birth date, date of birth | schema:birthDate | Date validation |
| address | schema:address | Address validation |
| postal code, zip | schema:postalCode | Postal code validation |
| nationality, country | schema:nationality | Country validation |
| gender | schema:gender | Gender validation |
| occupation, job | schema:jobTitle | Job validation |

**Modification Operations:**

The AI interprets commands and applies these operations:

1. **Add Field**: Creates new field with SHACL metadata
   - Infers field type from command
   - Assigns unique ID (camelCase format)
   - Generates semantic type and validation
   - Command examples: "Add email field", "Add dropdown for status"

2. **Remove Field**: Removes field by ID or label
   - Searches by exact ID or label match
   - Removes field and its SHACL metadata
   - Command examples: "Remove phone field", "Delete email"

3. **Modify Field**: Updates existing field properties
   - Changes label, type, options, or required status
   - Preserves field ID and value
   - Updates SHACL metadata accordingly
   - Command examples: "Make email required", "Change name to full name"

**Form Modification Process:**

1. **Command Parsing**: AI interprets the natural language command
2. **Operation Detection**: Identifies operation type (add/remove/modify)
3. **Field Generation**: Creates or modifies field specification
4. **Semantic Inference**: Maps field to Schema.org type
5. **SHACL Generation**: Generates PropertyShape with validation
6. **Form Integration**: Adds/removes/updates field in current fields
7. **NodeShape Generation**: Builds complete SHACL NodeShape for form
8. **Response Construction**: Returns updated fields, shape, and modifications

**Use Cases:**

- **Dynamic Form Building**: Administrators can modify forms using natural language
- **Rapid Prototyping**: Quickly add/remove fields during form design
- **Form Templates**: Create reusable form templates with semantic metadata
- **Semantic Forms**: Build forms with Schema.org types for data integration
- **Multilingual Support**: Commands work in German and English

**Known Limitations:**

- No authentication currently implemented (planned for future)
- Maximum command length: 500 characters
- Requires Gemini API key for AI processing
- Field IDs are auto-generated in camelCase format
- SHACL validation is performed but not enforced on the client side
- Cannot modify complex nested structures
- Single operation per command (cannot add multiple fields at once)

**Performance:**

- Typical response time: 1-3 seconds (with AI)
- AI-based command interpretation: 1-3 seconds
- SHACL generation: < 100ms

**Security Considerations:**

- Input validation on command length and field structure
- Error messages don't expose sensitive information
- Rate limiting recommended (not yet implemented)
- Authentication planned for production use
- No script injection validation (recommend adding)

---

## Authentication

### POST /auth/login

Authenticate user and receive access token.

**Current Implementation:** Simulated in `src/pages/Login.tsx` - stores username in context without validation.

**Authentication:** None (public endpoint)

**Request Body:**
```json
{
  "username": "bamf.officer@example.de",
  "password": "SecurePassword123!"
}
```

**Success Response (200 OK):**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "tokenType": "Bearer",
  "expiresIn": 3600,
  "refreshToken": "refresh_token_here",
  "user": {
    "id": "user-123",
    "username": "bamf.officer@example.de",
    "name": "Maria Schmidt",
    "role": "officer"
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "error": "UNAUTHORIZED",
  "message": "Invalid credentials provided"
}
```

**Example:**
```bash
curl -X POST https://api.bamf-acte.example.de/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"officer@example.de","password":"pass123"}'
```

```javascript
// React Query example (planned)
const { mutate: login } = useMutation({
  mutationFn: async (credentials) => {
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    });
    return response.json();
  }
});
```

---

### POST /auth/logout

Invalidate current access token.

**Current Implementation:** Simulated in `src/components/workspace/WorkspaceHeader.tsx` - clears context and redirects.

**Authentication:** Required (Bearer token)

**Success Response (204 No Content)**

**Example:**
```bash
curl -X POST https://api.bamf-acte.example.de/v1/auth/logout \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Case Management

### GET /cases

Retrieve list of cases accessible to the authenticated user.

**Current Implementation:** Simulated in `src/contexts/AppContext.tsx` - returns mock data from `sampleCases`.

**Source:** `src/contexts/AppContext.tsx`, `src/data/mockData.ts`

**Authentication:** Required (Bearer token)

**Query Parameters:**
- `status` (optional): Filter by case status (`open`, `pending`, `completed`)
- `search` (optional): Search cases by name or ID
- `limit` (optional): Maximum number of cases to return (default: 50, max: 100)
- `offset` (optional): Pagination offset (default: 0)

**Success Response (200 OK):**
```json
{
  "cases": [
    {
      "id": "ACTE-2024-001",
      "name": "German Integration Course Application",
      "createdAt": "2024-01-15",
      "status": "open",
      "folders": [
        {
          "id": "personal-data",
          "name": "Personal Data",
          "isExpanded": true,
          "documents": [
            {
              "id": "doc-1",
              "name": "Birth_Certificate.pdf",
              "type": "pdf",
              "size": "245 KB",
              "uploadedAt": "2024-01-15",
              "metadata": {
                "documentType": "Birth Certificate",
                "issuer": "Kabul Civil Registry",
                "language": "Dari"
              }
            }
          ],
          "subfolders": []
        }
      ]
    }
  ],
  "total": 3,
  "limit": 50,
  "offset": 0
}
```

**Example:**
```bash
curl -X GET "https://api.bamf-acte.example.de/v1/cases?status=open&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

```javascript
// React Query example (planned)
const { data: cases } = useQuery({
  queryKey: ['cases', { status: 'open' }],
  queryFn: async () => {
    const response = await fetch('/api/v1/cases?status=open', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.json();
  }
});
```

---

### POST /cases

Create a new case with specified template.

**Current Implementation:** Simulated in `src/components/workspace/NewCaseDialog.tsx` using `addNewCase` function.

**Source:** `src/components/workspace/NewCaseDialog.tsx`, `src/contexts/AppContext.tsx`

**Authentication:** Required (Bearer token)

**Request Body:**
```json
{
  "name": "German Integration Course Application - Ahmed Ali",
  "template": "integration"
}
```

**Template Options:**
- `standard` - Standard case template
- `asylum` - Asylum application template
- `familyReunification` - Family reunification template
- `integration` - Integration course template
- `citizenship` - Citizenship application template

**Success Response (201 Created):**
```json
{
  "id": "ACTE-2024-042",
  "name": "German Integration Course Application - Ahmed Ali",
  "createdAt": "2024-12-16",
  "status": "open",
  "folders": [
    {
      "id": "ACTE-2024-042-folder-0",
      "name": "Personal Data",
      "documents": [],
      "subfolders": [],
      "isExpanded": true
    },
    {
      "id": "ACTE-2024-042-folder-1",
      "name": "Certificates",
      "documents": [],
      "subfolders": [],
      "isExpanded": false
    }
  ]
}
```

**Example:**
```bash
curl -X POST https://api.bamf-acte.example.de/v1/cases \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Integration - John Doe","template":"integration"}'
```

---

### GET /cases/{caseId}

Retrieve detailed information about a specific case.

**Current Implementation:** Simulated in `src/contexts/AppContext.tsx` - finds case in `cases` array.

**Source:** `src/contexts/AppContext.tsx`

**Authentication:** Required (Bearer token)

**Path Parameters:**
- `caseId` (required): Case identifier (e.g., `ACTE-2024-001`)

**Success Response (200 OK):**
```json
{
  "id": "ACTE-2024-001",
  "name": "German Integration Course Application",
  "createdAt": "2024-01-15",
  "status": "open",
  "folders": [...]
}
```

**Error Response (404 Not Found):**
```json
{
  "error": "NOT_FOUND",
  "message": "Case with ID ACTE-2024-999 not found"
}
```

**Example:**
```bash
curl -X GET https://api.bamf-acte.example.de/v1/cases/ACTE-2024-001 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### PATCH /cases/{caseId}

Update case metadata (name, status, etc.).

**Current Implementation:** Partially simulated via context updates.

**Source:** `src/contexts/AppContext.tsx` (manual state updates)

**Authentication:** Required (Bearer token)

**Request Body:**
```json
{
  "name": "Updated Case Name",
  "status": "pending"
}
```

**Success Response (200 OK):**
```json
{
  "id": "ACTE-2024-001",
  "name": "Updated Case Name",
  "status": "pending",
  "createdAt": "2024-01-15",
  "folders": [...]
}
```

---

## Document Operations

### GET /cases/{caseId}/documents

Retrieve all documents in a case.

**Current Implementation:** Documents stored in case folders structure in `src/data/mockData.ts`.

**Source:** `src/data/mockData.ts` (mockCase.folders[].documents)

**Authentication:** Required (Bearer token)

**Query Parameters:**
- `folderId` (optional): Filter by specific folder ID

**Success Response (200 OK):**
```json
{
  "documents": [
    {
      "id": "doc-1",
      "name": "Birth_Certificate.pdf",
      "type": "pdf",
      "size": "245 KB",
      "uploadedAt": "2024-01-15",
      "metadata": {
        "documentType": "Birth Certificate",
        "issuer": "Kabul Civil Registry",
        "language": "Dari"
      }
    }
  ]
}
```

---

### POST /cases/{caseId}/documents

Upload a new document to a case.

**Current Implementation:** Simulated drag-and-drop in `src/components/workspace/CaseTreeExplorer.tsx` - shows toast notification only.

**Source:** `src/components/workspace/CaseTreeExplorer.tsx` (handleDrop function)

**Authentication:** Required (Bearer token)

**Request Body (multipart/form-data):**
- `file` (required): Binary file data
- `folderId` (required): Target folder ID
- `metadata` (optional): JSON object with document metadata

**Success Response (201 Created):**
```json
{
  "id": "doc-42",
  "name": "Certificate_A2.pdf",
  "type": "pdf",
  "size": "345 KB",
  "uploadedAt": "2024-12-16",
  "metadata": {
    "level": "A2",
    "institution": "Goethe Institut"
  }
}
```

**Example:**
```bash
curl -X POST https://api.bamf-acte.example.de/v1/cases/ACTE-2024-001/documents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/document.pdf" \
  -F "folderId=personal-data" \
  -F "metadata={\"documentType\":\"Passport\"}"
```

```javascript
// React example (planned)
const handleUpload = async (file, folderId) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('folderId', folderId);

  const response = await fetch(`/api/v1/cases/${caseId}/documents`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData
  });

  return response.json();
};
```

---

### GET /cases/{caseId}/documents/{documentId}

Retrieve document metadata and content.

**Current Implementation:** Simulated in `src/components/workspace/DocumentViewer.tsx` - displays mock content.

**Source:** `src/components/workspace/DocumentViewer.tsx`

**Authentication:** Required (Bearer token)

**Success Response (200 OK):**
```json
{
  "id": "doc-1",
  "name": "Birth_Certificate.pdf",
  "type": "pdf",
  "size": "245 KB",
  "uploadedAt": "2024-01-15",
  "metadata": {
    "documentType": "Birth Certificate",
    "issuer": "Kabul Civil Registry"
  },
  "content": "base64_encoded_content_or_url"
}
```

---

### DELETE /cases/{caseId}/documents/{documentId}

Remove document from case.

**Current Implementation:** Context menu option in `src/components/workspace/CaseTreeExplorer.tsx` - shows toast notification only.

**Source:** `src/components/workspace/CaseTreeExplorer.tsx` (context menu)

**Authentication:** Required (Bearer token)

**Success Response (204 No Content)**

**Example:**
```bash
curl -X DELETE https://api.bamf-acte.example.de/v1/cases/ACTE-2024-001/documents/doc-42 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## AI Operations

**Current Status:** AI operations are now implemented via the WebSocket chat endpoint (`/ws/chat/{case_id}`). Legacy REST endpoints for specific AI operations remain planned for backward compatibility.

**WebSocket-Based AI Operations:**
All AI functionality is available through the real-time chat interface:
- Natural language document analysis
- Form field extraction from documents
- Context-aware responses with case and folder isolation
- Powered by Google Gemini 2.5 Flash model

### Form Field Extraction via WebSocket

**Current Implementation:** IMPLEMENTED via WebSocket in `backend/api/chat.py` and `backend/tools/form_parser.py`

**Source:** `backend/api/chat.py:284-340`, `backend/tools/form_parser.py`

The AI can automatically extract structured data from documents and populate form fields. This feature is accessed through the WebSocket chat endpoint.

**How It Works:**

1. Client sends a chat message with:
   - `formSchema`: Array of form field definitions
   - `documentContent`: Document text to extract from
   - `content`: Message containing keywords "fill", "extract", or "populate"

2. Backend detects form extraction request and:
   - Builds a specialized extraction prompt using `build_extraction_prompt()`
   - Sends prompt to Gemini AI with document content
   - Parses AI response to extract field values
   - Validates extracted fields against schema

3. Backend sends two messages back:
   - `form_update` with extracted values and confidence scores
   - `chat_response` confirming the extraction

**Extraction Process:**

```
Document Text → AI Analysis → JSON Extraction → Validation → Form Update
```

**Form Schema Format:**

```json
[
  {
    "id": "fieldId",
    "label": "Field Label",
    "type": "text|date|select|textarea",
    "required": true|false,
    "options": ["option1", "option2"]
  }
]
```

**Extraction Features:**

- **Enhanced Multilingual Support:** Documents can be in German or English with explicit field mappings
  - German-English mappings: 'Vorname' → firstName, 'Nachname' → lastName, 'Geburtsdatum' → birthDate, 'Geburtsort' → placeOfBirth, 'Staatsangehörigkeit' → nationality, 'Passnummer' → passportNumber, 'Adresse' → address
  - AI extracts actual data values, not labels (e.g., from "Name: John Doe", extracts "John Doe" not "Name:")
  - Handles umlauts and special characters correctly (ä, ö, ü, ß)
- **Advanced Date Format Conversion:** Intelligent date parsing and normalization
  - Handles German format: DD.MM.YYYY (e.g., 15.05.1990 → 1990-05-15)
  - Supports multiple formats: DD/MM/YYYY, DD-MM-YYYY, and natural language dates
  - Validates date realism (years between 1900-2030 for birthdates)
  - Automatic conversion to ISO 8601 format (YYYY-MM-DD)
- **Fuzzy Select Field Matching:** Flexible matching for predefined option fields
  - Case-insensitive matching: 'EVENING' matches option 'Evening'
  - Partial word matching: 'weekend classes' matches option 'Weekend'
  - Word-based matching: 'intensive course' matches option 'Intensive'
  - Prioritizes exact matches, falls back to fuzzy matching
- **Enhanced Confidence Scoring:** Field-specific confidence based on validation
  - Date fields: 0.95 (valid ISO), 0.80 (converted format), 0.50 (questionable dates)
  - Select fields: 0.95 (exact match), 0.80 (fuzzy match), 0.40 (no match found)
  - Text fields: 0.90 (normal length), 0.60 (very short), 0.70 (very long)
  - Textarea fields: 0.85 (standard confidence)
- **Intelligent Field Mapping:** AI understands field semantics, not just labels
- **Partial Extraction:** Only returns fields where data was found with sufficient confidence
- **Type Validation:** Ensures extracted values match field type requirements

**Supported Field Types:**

- `text` - Free-form text fields
- `date` - Date values (auto-converted to YYYY-MM-DD)
- `select` - Single-choice fields (matched to closest option)
- `textarea` - Multi-line text fields

**Example Extraction Request:**

```javascript
// WebSocket message
{
  "type": "chat",
  "content": "Please fill the form from this document",
  "caseId": "ACTE-2024-001",
  "documentContent": `
    Birth Certificate
    Full Name: Ahmad Ali Hassan
    Date of Birth: 20 March 1995
    Place of Birth: Kabul, Afghanistan
    Father's Name: Hassan Ali
    Mother's Name: Fatima Hassan
  `,
  "formSchema": [
    { "id": "name", "label": "Full Name", "type": "text", "required": true },
    { "id": "birthDate", "label": "Date of Birth", "type": "date", "required": true },
    { "id": "countryOfOrigin", "label": "Country of Origin", "type": "text", "required": true },
    { "id": "fatherName", "label": "Father's Name", "type": "text", "required": false },
    { "id": "motherName", "label": "Mother's Name", "type": "text", "required": false }
  ]
}
```

**Example Extraction Response:**

```javascript
// Message 1: Form update
{
  "type": "form_update",
  "updates": {
    "name": "Ahmad Ali Hassan",
    "birthDate": "1995-03-20",
    "countryOfOrigin": "Afghanistan",
    "fatherName": "Hassan Ali",
    "motherName": "Fatima Hassan"
  },
  "confidence": {
    "name": 0.95,
    "birthDate": 0.92,
    "countryOfOrigin": 0.90,
    "fatherName": 0.88,
    "motherName": 0.88
  },
  "timestamp": null
}

// Message 2: Confirmation
{
  "type": "chat_response",
  "content": "I've extracted 5 fields from the document and updated the form.",
  "timestamp": null
}
```

**Confidence Scoring:**

The system provides field-specific confidence scores based on validation and matching quality:

- `0.90 - 1.00`: High confidence
  - Date fields with valid ISO format (0.95)
  - Text fields with normal length (0.90)
  - Select fields with exact case-insensitive match (0.95)
- `0.75 - 0.89`: Medium confidence
  - Date fields converted from other formats (0.80)
  - Textarea fields (0.85)
  - Select fields with fuzzy match (0.80)
- `0.50 - 0.74`: Low confidence
  - Text fields with very short (<2 chars) or very long (>200 chars) content (0.60-0.70)
  - Date fields with questionable format (0.50)
- `< 0.50`: Very low confidence
  - Select fields with no matching option (0.40)
  - Fields with this score may still be returned but require manual verification

Default confidence is 0.85 for fields without specific validation rules.

**Confidence Score Interpretation:**
- Scores ≥ 0.85: Generally safe for automatic form filling
- Scores 0.70-0.84: Recommended to highlight for user review
- Scores < 0.70: Require manual verification before use

**Error Handling:**

If extraction fails, an error message is sent:

```json
{
  "type": "error",
  "message": "Failed to extract form fields: Invalid JSON response from AI",
  "timestamp": null
}
```

**Form Schema Validation:**

The backend validates form schemas before extraction:

```python
# Required fields in each form field definition
{
  "id": str,      # Unique field identifier
  "label": str,   # Human-readable label
  "type": str     # Field type (text, date, select, textarea)
}
```

**Best Practices:**

1. **Provide Clear Field Labels:** Use descriptive labels that match document terminology
   - Include both English and German labels when possible
   - Labels should be semantically meaningful (e.g., "Full Name" or "Vollständiger Name")
2. **Include Field Context:** Add all relevant fields, even optional ones
   - More fields provide better context for the AI
   - Optional fields can be extracted when data is available
3. **Review Confidence Scores:** Implement UI highlighting based on confidence
   - Auto-accept fields with confidence ≥ 0.85
   - Highlight for review: confidence 0.70-0.84 (yellow/warning)
   - Require verification: confidence < 0.70 (red/error)
4. **Use Structured Documents:** Works best with well-formatted documents
   - Clear labels and values (e.g., "Name: John Doe")
   - Consistent formatting throughout
   - German documents with standard field labels work excellently
5. **Specify Select Options:** Provide all valid options for select fields
   - Include common variations if known (e.g., "Intensive" and "Intensive Course")
   - System will fuzzy match to closest option
   - Order doesn't matter (system finds best match)
6. **Handle Partial Results:** Not all fields may be extracted from every document
   - Only fields with sufficient confidence are returned
   - Missing fields may require manual input or additional documents
7. **Date Field Handling:** System automatically converts date formats
   - German format DD.MM.YYYY is fully supported
   - No need to pre-process dates before extraction
   - System validates date realism automatically
8. **Multilingual Documents:** Specify document language in context if known
   - System handles German and English automatically
   - Mixed-language documents are supported
   - Special characters (umlauts) preserved correctly

**Implementation Details:**

**Services Used:**
- `GeminiService` - AI model integration (Google Gemini 2.5 Flash)
- `ContextManager` - Case-specific context loading
- `form_parser` - Prompt building and result parsing

**Prompt Engineering:**

The extraction prompt includes 6 comprehensive sections:
1. **Field Extraction Rules:** General extraction guidelines and semantic matching
2. **Multilingual Document Handling:** German-English field mappings with examples
3. **Date Format Conversion:** Detailed date parsing and validation rules
4. **Select Field Matching:** Fuzzy matching strategies (case-insensitive, partial, word-based)
5. **Text Field Extraction:** Special character handling and whitespace management
6. **Output Format:** Strict JSON output requirements

Key prompt features:
- Explicit German-English field mapping examples
- Multiple date format conversion examples
- Clear fuzzy matching instructions for select fields
- Emphasis on extracting values, not labels
- Confidence-based field omission strategy

**Helper Functions:**

The form_parser module includes specialized helper functions:
- `_convert_to_iso_date()`: Multi-format date converter (DD.MM.YYYY, DD/MM/YYYY, DD-MM-YYYY → YYYY-MM-DD)
- `_match_select_option()`: Three-tier fuzzy matching (exact → partial → word-based)
- `_is_valid_iso_date()`: ISO 8601 date format validator with datetime parsing
- `parse_extraction_result()`: AI response parser with validation and confidence scoring
- `build_extraction_prompt()`: Comprehensive prompt builder with all instructions

**Performance:**

- Typical extraction time: 2-5 seconds
- Depends on document length and field count
- Gemini 2.5 Flash optimized for speed
- No caching (each request processed fresh)

**Limitations:**

- No OCR support (requires pre-extracted text from documents)
- No image analysis (text-based documents only)
- Primary language support: German and English (other languages may work but not tested)
- Complex nested form structures not supported (flat field lists only)
- Maximum ~10,000 characters document length for optimal performance
- Date format conversion limited to common European formats
- Fuzzy select matching requires options to be provided in form schema
- Very low confidence fields (< 0.40) are typically omitted from results

---

**Legacy REST Endpoints:**
The following REST endpoints are planned but not yet implemented. They will coexist with the WebSocket interface for clients that prefer request/response patterns over real-time communication.

### POST /ai/convert

Convert document to different format (PDF, JSON, XML, DOCX).

**Current Implementation:** Simulated in `src/components/workspace/AIChatInterface.tsx` via `/convert` slash command.

**Source:** `src/components/workspace/AIChatInterface.tsx` (line 70-72)

**Authentication:** Required (Bearer token)

**Request Body:**
```json
{
  "documentId": "doc-1",
  "targetFormat": "pdf"
}
```

**Target Formats:**
- `pdf` - Portable Document Format
- `json` - JSON structured data
- `xml` - XML structured data
- `docx` - Microsoft Word format

**Success Response (202 Accepted):**
```json
{
  "jobId": "job-12345",
  "status": "processing",
  "estimatedCompletion": "2024-12-16T10:05:00Z"
}
```

**Simulated Behavior:**
- Shows toast notification: "Document conversion in progress..."
- Returns success message after 1-1.5 second delay
- In real implementation, would create new document version

**Example:**
```bash
curl -X POST https://api.bamf-acte.example.de/v1/ai/convert \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"documentId":"doc-1","targetFormat":"pdf"}'
```

---

### POST /ai/translate

Translate document content to German.

**Current Implementation:** Simulated in `src/components/workspace/AIChatInterface.tsx` via `/translate` slash command.

**Source:** `src/components/workspace/AIChatInterface.tsx` (line 77-78)

**Authentication:** Required (Bearer token)

**Request Body:**
```json
{
  "documentId": "doc-1",
  "targetLanguage": "de"
}
```

**Success Response (202 Accepted):**
```json
{
  "jobId": "job-12346",
  "status": "processing",
  "estimatedCompletion": "2024-12-16T10:10:00Z"
}
```

**Simulated Behavior:**
- Returns message: "Translation to German initiated. The translated document will be added as a new rendition."
- In real implementation, would use AI translation service and create new document

**Example:**
```bash
curl -X POST https://api.bamf-acte.example.de/v1/ai/translate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"documentId":"doc-1","targetLanguage":"de"}'
```

---

### POST /ai/anonymize

Remove or redact personal data from document.

**Current Implementation:** Simulated in `src/components/workspace/AIChatInterface.tsx` via `/anonymize` slash command.

**Source:** `src/components/workspace/AIChatInterface.tsx` (line 79-80)

**Authentication:** Required (Bearer token)

**Request Body:**
```json
{
  "documentId": "doc-1",
  "redactionLevel": "standard"
}
```

**Redaction Levels:**
- `minimal` - Redact only critical PII (SSN, passport numbers)
- `standard` - Redact names, addresses, dates of birth (default)
- `maximum` - Redact all identifiable information

**Success Response (202 Accepted):**
```json
{
  "jobId": "job-12347",
  "status": "processing",
  "detectedPII": ["names", "addresses", "dates_of_birth"],
  "estimatedCompletion": "2024-12-16T10:08:00Z"
}
```

**Simulated Behavior:**
- Returns message about anonymization process starting
- In real implementation, would detect and redact PII using NLP

---

### POST /ai/extract-metadata

Extract structured metadata from document using AI.

**Current Implementation:** Simulated in `src/components/workspace/AIChatInterface.tsx` via `/extractMetadata` slash command.

**Source:** `src/components/workspace/AIChatInterface.tsx` (referenced in quickActions)

**Authentication:** Required (Bearer token)

**Request Body:**
```json
{
  "documentId": "doc-1"
}
```

**Success Response (200 OK):**
```json
{
  "metadata": {
    "documentType": "Birth Certificate",
    "issuer": "Kabul Civil Registry",
    "issuedDate": "1995-03-20",
    "expiryDate": null,
    "language": "Dari",
    "subject": {
      "name": "Ahmed Ali",
      "dateOfBirth": "1995-03-20",
      "placeOfBirth": "Kabul, Afghanistan"
    }
  },
  "confidence": 0.92
}
```

**Simulated Behavior:**
- In real implementation, would use OCR + NLP to extract structured data
- Confidence score indicates extraction accuracy

---

### POST /ai/validate-case

Check if case has all required documents and completeness.

**Current Implementation:** Simulated in `src/components/workspace/AIChatInterface.tsx` via `/validateCase` slash command.

**Source:** `src/components/workspace/AIChatInterface.tsx` (line 81-83)

**Authentication:** Required (Bearer token)

**Request Body:**
```json
{
  "caseId": "ACTE-2024-001"
}
```

**Success Response (200 OK):**
```json
{
  "valid": false,
  "missingDocuments": [
    "Integration course enrollment confirmation",
    "Language proficiency certificate"
  ],
  "completeness": 85.5,
  "recommendations": [
    "Upload integration course enrollment confirmation",
    "Verify all personal documents are translated to German",
    "Ensure passport scan is valid and not expired"
  ],
  "folderStatus": {
    "Personal Data": "complete",
    "Certificates": "partial",
    "Integration Course Documents": "empty",
    "Applications & Forms": "complete",
    "Additional Evidence": "complete"
  }
}
```

**Simulated Response:**
```
Case Validation Report

✅ Personal Data: Complete
✅ Certificates: 1 document found
⚠️ Integration Course Documents: Empty folder
✅ Applications & Forms: 1 draft form
✅ Additional Evidence: 1 document

Recommendation: Please upload integration course enrollment confirmation.
```

**Example:**
```bash
curl -X POST https://api.bamf-acte.example.de/v1/ai/validate-case \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"caseId":"ACTE-2024-001"}'
```

---

## Form Management

### GET /cases/{caseId}/forms

Retrieve application form data for a case.

**Current Implementation:** Simulated in `src/contexts/AppContext.tsx` via `formFields` state.

**Source:** `src/contexts/AppContext.tsx`, `src/data/mockData.ts` (initialFormFields)

**Authentication:** Required (Bearer token)

**Success Response (200 OK):**
```json
{
  "fields": [
    {
      "id": "name",
      "label": "Full Name",
      "type": "text",
      "value": "",
      "required": true
    },
    {
      "id": "birthDate",
      "label": "Date of Birth",
      "type": "date",
      "value": "",
      "required": true
    },
    {
      "id": "countryOfOrigin",
      "label": "Country of Origin",
      "type": "text",
      "value": "",
      "required": true
    },
    {
      "id": "coursePreference",
      "label": "Course Preference",
      "type": "select",
      "value": "",
      "options": [
        "Intensive Course",
        "Evening Course",
        "Weekend Course",
        "Online Course"
      ],
      "required": false
    },
    {
      "id": "reasonForApplication",
      "label": "Reason for Application",
      "type": "textarea",
      "value": "",
      "required": true
    }
  ]
}
```

**Example:**
```bash
curl -X GET https://api.bamf-acte.example.de/v1/cases/ACTE-2024-001/forms \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### PUT /cases/{caseId}/forms

Update application form data.

**Current Implementation:** Simulated in `src/components/workspace/FormViewer.tsx` via `updateFormField` context function.

**Source:** `src/components/workspace/FormViewer.tsx`, `src/contexts/AppContext.tsx`

**Authentication:** Required (Bearer token)

**Request Body:**
```json
{
  "fields": [
    {
      "id": "name",
      "label": "Full Name",
      "type": "text",
      "value": "Ahmed Ali Hassan",
      "required": true
    },
    {
      "id": "birthDate",
      "label": "Date of Birth",
      "type": "date",
      "value": "1995-03-20",
      "required": true
    }
  ]
}
```

**Success Response (200 OK):**
```json
{
  "fields": [...]
}
```

**Simulated Behavior:**
- Form fields update in real-time via context
- AI chat can auto-fill fields when extracting information from documents
- Save Draft button shows toast notification

---

## Document Registry Operations

The following endpoints provide access to the document registry system (S5-007), which tracks all uploaded documents, their metadata, renders (anonymized/translated versions), and folder locations. The registry persists across application restarts to ensure documents remain visible after container restarts.

### GET /api/documents/tree/{case_id}

Retrieve the complete document tree for a specific case, including all folders and documents organized in a hierarchical structure.

**Current Implementation:** IMPLEMENTED in `backend/api/documents.py`

**Source:** `backend/api/documents.py:68-151`

**Authentication:** None (planned for future implementation)

**Description:**

This endpoint retrieves the complete document tree from the document registry manifest. It is called by the frontend on app startup to load the document structure from the persisted manifest file.

**Path Parameters:**
- `case_id` (required): Case identifier (e.g., "ACTE-2024-001")

**Success Response (200 OK):**
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
          "metadata": {
            "documentType": "Birth Certificate",
            "issuer": "Kabul Civil Registry",
            "language": "Dari"
          },
          "caseId": "ACTE-2024-001",
          "folderId": "personal-data"
        }
      ],
      "subfolders": [],
      "isExpanded": true
    },
    {
      "id": "certificates",
      "name": "Certificates",
      "documents": [],
      "subfolders": [],
      "isExpanded": false
    }
  ],
  "rootDocuments": []
}
```

**Response Fields:**
- `folders`: Array of folder objects containing documents
  - `id`: Folder identifier
  - `name`: Human-readable folder name
  - `documents`: Array of document objects in this folder
  - `subfolders`: Array of nested subfolders (currently empty)
  - `isExpanded`: UI state for folder expansion (default: true)
- `rootDocuments`: Array of documents not in any folder

**Document Fields:**
- `id`: Unique document ID (UUID)
- `name`: Filename
- `type`: File extension (pdf, jpg, png, etc.)
- `size`: Human-readable file size (e.g., "245 KB")
- `uploadedAt`: ISO 8601 timestamp of upload
- `metadata`: Additional document metadata (type, issuer, language, etc.)
- `caseId`: Case ID this document belongs to
- `folderId`: Folder ID this document is in (null for root documents)

**Error Response (404 Not Found):**
```json
{
  "error": "Case not found",
  "detail": "No documents found for case ACTE-2024-999",
  "case_id": "ACTE-2024-999"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "error": "Failed to retrieve document tree",
  "detail": "Error loading manifest file",
  "case_id": "ACTE-2024-001"
}
```

**Example Usage:**

**cURL:**
```bash
curl -X GET http://localhost:8000/api/documents/tree/ACTE-2024-001
```

**JavaScript/TypeScript:**
```javascript
const getDocumentTree = async (caseId) => {
  const response = await fetch(
    `http://localhost:8000/api/documents/tree/${caseId}`
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || error.error);
  }

  return await response.json();
};

// Usage
const tree = await getDocumentTree('ACTE-2024-001');
console.log(`Loaded ${tree.folders.length} folders`);
tree.folders.forEach(folder => {
  console.log(`Folder: ${folder.name} (${folder.documents.length} documents)`);
});
```

**Python:**
```python
import requests

def get_document_tree(case_id: str) -> dict:
    response = requests.get(
        f'http://localhost:8000/api/documents/tree/{case_id}'
    )

    if response.status_code != 200:
        raise Exception(f"Failed to get document tree: {response.json()}")

    return response.json()

# Usage
tree = get_document_tree("ACTE-2024-001")
print(f"Loaded {len(tree['folders'])} folders")
for folder in tree['folders']:
    print(f"Folder: {folder['name']} ({len(folder['documents'])} documents)")
```

**Document Registry Integration:**

This endpoint reads from the document registry manifest (`backend/data/document_manifest.json`), which is the single source of truth for all document metadata. The manifest is automatically updated when:
- Files are uploaded via `POST /api/files/upload`
- Files are deleted via `DELETE /api/files/{case_id}/{folder_id}/{filename}`
- Application starts up and performs filesystem reconciliation

**Use Cases:**
- **Frontend initialization**: Load document tree on app startup
- **Case view**: Display all documents for a specific case
- **Document navigation**: Provide hierarchical folder structure
- **Container-compatible persistence**: Maintain document state across restarts

**Performance:**
- Typical response time: < 100ms
- Reads from manifest file (JSON)
- No filesystem scanning (uses cached registry)

**Known Limitations:**
- No authentication currently implemented (planned for future)
- No pagination (all documents returned at once)
- Subfolders currently not supported (flat folder structure)

---

### GET /api/documents/all

Retrieve all documents from the registry across all cases.

**Current Implementation:** IMPLEMENTED in `backend/api/documents.py`

**Source:** `backend/api/documents.py:154-200`

**Authentication:** None (planned for future implementation)

**Description:**

This endpoint retrieves all documents from the document registry across all cases. It is primarily used for administrative purposes or debugging.

**Success Response (200 OK):**
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
    },
    {
      "documentId": "doc-def456",
      "caseId": "ACTE-2024-001",
      "folderId": "personal-data",
      "fileName": "Passport_Scan_anonymized.jpg",
      "filePath": "public/documents/ACTE-2024-001/personal-data/Passport_Scan_anonymized.jpg",
      "uploadedAt": "2024-01-15T11:00:00Z",
      "fileHash": "sha256:def456...",
      "renders": [
        {
          "renderId": "render-xyz789",
          "type": "anonymized",
          "filePath": "public/documents/ACTE-2024-001/personal-data/Passport_Scan_anonymized.jpg",
          "createdAt": "2024-01-15T11:00:00Z"
        }
      ]
    }
  ]
}
```

**Response Fields:**
- `success`: Boolean indicating successful retrieval
- `count`: Total number of documents
- `documents`: Array of all document registry entries with full metadata

**Document Registry Entry Fields:**
- `documentId`: Unique UUID for the document
- `caseId`: Case ID the document belongs to
- `folderId`: Folder ID within the case (null for root)
- `fileName`: Original filename
- `filePath`: Full file path relative to project root
- `uploadedAt`: ISO 8601 timestamp of initial upload
- `fileHash`: SHA-256 hash of file content for integrity verification
- `renders`: Array of rendered versions (anonymized, translated, etc.)

**Render Object Fields:**
- `renderId`: Unique UUID for the render
- `type`: Render type ("anonymized" or "translated")
- `filePath`: Path to the rendered file
- `createdAt`: ISO 8601 timestamp of render creation
- `language`: Target language (for translations only, optional)

**Error Response (500 Internal Server Error):**
```json
{
  "error": "Failed to retrieve documents",
  "detail": "Error loading manifest file"
}
```

**Example Usage:**

**cURL:**
```bash
curl -X GET http://localhost:8000/api/documents/all
```

**JavaScript/TypeScript:**
```javascript
const getAllDocuments = async () => {
  const response = await fetch('http://localhost:8000/api/documents/all');

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || error.error);
  }

  return await response.json();
};

// Usage
const result = await getAllDocuments();
console.log(`Total documents: ${result.count}`);
result.documents.forEach(doc => {
  console.log(`${doc.caseId}/${doc.folderId}/${doc.fileName}`);
  if (doc.renders.length > 0) {
    console.log(`  → ${doc.renders.length} render(s)`);
  }
});
```

**Python:**
```python
import requests

def get_all_documents() -> dict:
    response = requests.get('http://localhost:8000/api/documents/all')

    if response.status_code != 200:
        raise Exception(f"Failed to get all documents: {response.json()}")

    return response.json()

# Usage
result = get_all_documents()
print(f"Total documents: {result['count']}")
for doc in result['documents']:
    print(f"{doc['caseId']}/{doc['folderId']}/{doc['fileName']}")
    if doc['renders']:
        print(f"  → {len(doc['renders'])} render(s)")
```

**Use Cases:**
- **Administrative dashboard**: View all documents across all cases
- **Debugging**: Inspect document registry state
- **Bulk operations**: Export or analyze all document metadata
- **Storage audit**: Check file hashes and integrity

**Performance:**
- Typical response time: < 200ms
- Reads from manifest file (JSON)
- Returns all documents (no filtering or pagination)

**Known Limitations:**
- No authentication (expose all documents)
- No pagination (performance issue with many documents)
- No filtering (returns all documents)
- Planned for admin use only

---

### GET /api/documents/health

Check the health status of the document registry service.

**Current Implementation:** IMPLEMENTED in `backend/api/documents.py`

**Source:** `backend/api/documents.py:203-260`

**Authentication:** None (public endpoint)

**Description:**

This endpoint checks the health and availability of the document registry service, including manifest file status and storage directory availability.

**Success Response (200 OK - Service Ready):**
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

**Service Degraded Response (503 Service Unavailable - Manifest or Storage Issues):**
```json
{
  "service": "documents",
  "status": "degraded",
  "features": {
    "document_tree": true,
    "manifest_persistence": false,
    "filesystem_reconciliation": true
  },
  "manifest": {
    "loaded": false,
    "document_count": 0
  },
  "storage": {
    "available": false,
    "path": "/home/user/project/public/documents"
  }
}
```

**Response Fields:**
- `service`: Always "documents"
- `status`: Service status ("ready" or "degraded")
- `features`: Object listing available features
  - `document_tree`: Document tree endpoint availability
  - `manifest_persistence`: Whether manifest file loads successfully
  - `filesystem_reconciliation`: Whether reconciliation is enabled
- `manifest`: Manifest file status
  - `loaded`: Boolean indicating if manifest loaded successfully
  - `document_count`: Number of documents in manifest
- `storage`: Storage directory status
  - `available`: Boolean indicating if storage directory exists
  - `path`: Absolute path to documents directory

**Example Usage:**

**cURL:**
```bash
curl -X GET http://localhost:8000/api/documents/health
```

**JavaScript/TypeScript:**
```javascript
const checkDocumentServiceHealth = async () => {
  const response = await fetch('http://localhost:8000/api/documents/health');
  const health = await response.json();

  if (health.status === 'ready') {
    console.log(`Document service ready: ${health.manifest.document_count} documents`);
  } else {
    console.warn('Document service degraded');
    if (!health.manifest.loaded) console.error('Manifest failed to load');
    if (!health.storage.available) console.error('Storage directory not available');
  }

  return health;
};
```

**Python:**
```python
import requests

def check_document_service_health():
    response = requests.get('http://localhost:8000/api/documents/health')
    health = response.json()

    if health['status'] == 'ready':
        print(f"Document service ready: {health['manifest']['document_count']} documents")
    else:
        print("Document service degraded")
        if not health['manifest']['loaded']:
            print("  Error: Manifest failed to load")
        if not health['storage']['available']:
            print("  Error: Storage directory not available")

    return health
```

**Health Status Values:**
- `ready`: Service is fully operational (manifest loads, storage directory exists)
- `degraded`: Service has issues (manifest corrupt or storage directory missing)

**Use Cases:**
- **Monitoring**: Health check probes for container orchestration
- **Load balancing**: Backend health checks for load balancers
- **Frontend validation**: Check service availability before loading documents
- **Debugging**: Verify manifest and storage configuration

**Performance:**
- Typical response time: < 50ms
- Lightweight operation (checks file/directory existence)

---

## Context API

**Current Status:** IMPLEMENTED - Provides document tree views and hierarchical context information.

The Context API (S5-011) provides endpoints for retrieving structured document tree views with hierarchical text representations. These endpoints support frontend debugging, tree visualization, and cascading context features.

### GET /api/context/tree/{case_id}

Get document tree view for a specific case with hierarchical text representation.

**Current Implementation:** IMPLEMENTED in `backend/api/context.py`

**Source:** `backend/api/context.py:35-126`

**Authentication:** None (planned for future implementation)

**Description:**

This endpoint returns a hierarchical text representation of the document tree for a case, formatted with ASCII tree characters (├── └──). The tree view includes all folders and documents, showing empty folders and providing folder display names from context files.

**Path Parameters:**

- `case_id` (required): Case identifier (e.g., "ACTE-2024-001")

**Features:**

- Cached for performance (regenerates on document changes via cache invalidation)
- Includes folder display names from context files
- Shows empty folders
- Lists all documents with their original filenames
- ASCII tree formatting with proper indentation

**Success Response (200 OK):**
```json
{
  "treeView": "Case ACTE-2024-001:\n├── Personal Data (5 documents)\n│   ├── Passport_Scan.pdf\n│   ├── Birth_Certificate.pdf\n│   └── Address_Proof.pdf\n├── Applications (2 documents)\n│   └── Integration_Application.pdf\n└── Evidence (3 documents)\n    ├── School_Transcripts.pdf\n    └── Language_Certificate.pdf",
  "folders": [
    "Personal Data",
    "Applications",
    "Evidence"
  ],
  "documentCount": 10
}
```

**Error Response (404 Not Found - Case Not Found):**
```json
{
  "detail": {
    "error": "Case not found",
    "case_id": "ACTE-2024-999"
  }
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "detail": {
    "error": "Failed to generate tree view",
    "detail": "<error details>",
    "case_id": "ACTE-2024-001"
  }
}
```

**Example Usage:**

**cURL:**
```bash
curl -X GET http://localhost:8000/api/context/tree/ACTE-2024-001
```

**JavaScript/TypeScript:**
```javascript
const getTreeView = async (caseId) => {
  const response = await fetch(
    `http://localhost:8000/api/context/tree/${caseId}`
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail?.error || 'Failed to get tree view');
  }

  return await response.json();
};

// Usage
try {
  const tree = await getTreeView('ACTE-2024-001');
  console.log('Tree View:\n' + tree.treeView);
  console.log(`Folders: ${tree.folders.join(', ')}`);
  console.log(`Total documents: ${tree.documentCount}`);
} catch (error) {
  console.error('Get tree view failed:', error.message);
}
```

**Python:**
```python
import requests

def get_tree_view(case_id: str):
    response = requests.get(
        f'http://localhost:8000/api/context/tree/{case_id}'
    )

    if response.status_code != 200:
        raise Exception(f"Get tree view failed: {response.json()}")

    return response.json()

# Usage
tree = get_tree_view("ACTE-2024-001")
print("Tree View:")
print(tree['treeView'])
print(f"\nFolders: {', '.join(tree['folders'])}")
print(f"Total documents: {tree['documentCount']}")
```

**Caching and Performance:**

The tree view is cached in memory for performance. The cache is automatically invalidated when:
- A file is uploaded (`POST /api/files/upload`)
- A file is deleted (`DELETE /api/files/{case_id}/{folder_id}/{filename}`)
- A render is deleted (`DELETE /api/files/renders/{case_id}/{document_id}/{render_id}`)

Cache invalidation ensures that the tree view always reflects the current state of the document structure.

**Use Cases:**

- **Frontend debugging:** Visualize document structure during development
- **Tree view display:** Render hierarchical tree in UI components
- **Manual verification:** Test document tree generation and folder structure
- **Context display:** Show users the complete document hierarchy for a case

**Performance:**

- First call: 100-300ms (generates and caches tree)
- Cached calls: < 50ms (returns cached tree)
- Cache invalidation: Automatic on document changes

---

## Search API

**Current Status:** IMPLEMENTED - Semantic search using natural language queries with Gemini AI.

The Search API (S5-003) provides intelligent document search capabilities using semantic understanding. It supports cross-language search, automatic language detection, PDF text extraction, and text highlighting with position information.

### POST /api/search/semantic

Perform semantic search on document content using natural language queries.

**Current Implementation:** IMPLEMENTED in `backend/api/search.py`

**Source:** `backend/api/search.py:103-266`

**Authentication:** None (planned for future implementation)

**Description:**

This endpoint analyzes document content and finds text passages that semantically match the user's natural language query. It uses Google Gemini AI for intelligent semantic matching and supports cross-language search where the query and document can be in different languages.

**Request Body (application/json):**

```json
{
  "query": "passport number",
  "documentContent": "Full text of document (for non-PDF)",
  "documentType": "pdf",
  "documentPath": "/path/to/document.pdf",
  "queryLanguage": "en",
  "documentLanguage": "de"
}
```

**Request Fields:**

- `query` (required): Natural language search query (minimum 1 character)
- `documentContent` (optional): Full text content of document (required for non-PDF documents)
- `documentType` (required): Type of document (pdf, txt, etc.)
- `documentPath` (optional): Path to PDF file (required for PDF documents)
- `queryLanguage` (optional): Query language ISO 639-1 code (auto-detected if not provided)
- `documentLanguage` (optional): Document language ISO 639-1 code (auto-detected if not provided)

**Features:**

- **Semantic Search:** Understands meaning, not just keywords
- **Cross-Language Support:** Search German documents with English queries (and vice versa)
- **Automatic Language Detection:** Detects query and document languages automatically
- **PDF Text Extraction:** Automatically extracts text from PDF files
- **Text Highlighting:** Returns exact character positions for matched text
- **Relevance Scoring:** Each match includes a relevance score (0.0-1.0)
- **Context Explanation:** Explains why each passage matched

**Success Response (200 OK):**
```json
{
  "highlights": [
    {
      "start": 125,
      "end": 145,
      "relevance": 0.95,
      "matchedText": "Passnummer: 123456789",
      "context": "Direct match: passport number field"
    },
    {
      "start": 450,
      "end": 475,
      "relevance": 0.75,
      "matchedText": "Reisepass-Nr. A98765432",
      "context": "Synonym match: travel document number"
    }
  ],
  "count": 2,
  "matchSummary": "Found 2 relevant passages (cross-language: English → German)",
  "queryLanguage": "en",
  "documentLanguage": "de",
  "isCrossLanguage": true
}
```

**Error Response (400 Bad Request - Missing Required Field):**
```json
{
  "detail": "documentPath is required for PDF documents"
}
```

**Error Response (404 Not Found - PDF Not Found):**
```json
{
  "detail": "PDF file not found: /path/to/document.pdf"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "detail": "Search failed: <error details>"
}
```

**Example Usage:**

**cURL (Text Document):**
```bash
curl -X POST http://localhost:8000/api/search/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "query": "birth date",
    "documentContent": "Name: John Doe\nGeburtsdatum: 15.05.1990\nGeburtsort: Berlin",
    "documentType": "txt",
    "queryLanguage": "en",
    "documentLanguage": "de"
  }'
```

**cURL (PDF Document):**
```bash
curl -X POST http://localhost:8000/api/search/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "query": "passport number",
    "documentType": "pdf",
    "documentPath": "public/documents/ACTE-2024-001/personal-data/Passport.pdf"
  }'
```

**JavaScript/TypeScript:**
```javascript
const semanticSearch = async (query, documentContent, documentType) => {
  const response = await fetch(
    'http://localhost:8000/api/search/semantic',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        documentContent,
        documentType
      })
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return await response.json();
};

// Usage
try {
  const results = await semanticSearch(
    'passport number',
    documentTextContent,
    'txt'
  );

  console.log(`Found ${results.count} matches`);
  results.highlights.forEach((highlight, index) => {
    console.log(`${index + 1}. ${highlight.matchedText}`);
    console.log(`   Relevance: ${highlight.relevance}`);
    console.log(`   Context: ${highlight.context}`);
  });
} catch (error) {
  console.error('Search failed:', error.message);
}
```

**Python:**
```python
import requests

def semantic_search(query: str, document_content: str = None, document_type: str = "txt", document_path: str = None):
    payload = {
        "query": query,
        "documentType": document_type
    }

    if document_type == "pdf":
        payload["documentPath"] = document_path
    else:
        payload["documentContent"] = document_content

    response = requests.post(
        'http://localhost:8000/api/search/semantic',
        json=payload
    )

    if response.status_code != 200:
        raise Exception(f"Search failed: {response.json()}")

    return response.json()

# Usage - Text document
results = semantic_search(
    query="birth date",
    document_content="Name: John\nGeburtsdatum: 15.05.1990",
    document_type="txt"
)

print(f"Found {results['count']} matches")
for highlight in results['highlights']:
    print(f"- {highlight['matchedText']} (relevance: {highlight['relevance']})")

# Usage - PDF document
pdf_results = semantic_search(
    query="passport number",
    document_type="pdf",
    document_path="public/documents/ACTE-2024-001/personal-data/Passport.pdf"
)
```

**Cross-Language Search Examples:**

1. **English query → German document:**
   - Query: "passport number"
   - Matches: "Reisepassnummer", "Passnummer", "Pass-Nr."

2. **German query → English document:**
   - Query: "Geburtsdatum"
   - Matches: "date of birth", "birth date", "DOB"

3. **Mixed-language documents:**
   - Automatically detects primary document language
   - Searches across both languages intelligently

**Language Detection:**

If `queryLanguage` or `documentLanguage` are not provided, the service automatically detects them using linguistic analysis. Supported languages:
- German (de)
- English (en)

**Use Cases:**

- **Document search:** Find specific information in documents regardless of language
- **Data extraction:** Locate and extract specific fields from documents
- **Cross-language compliance:** Search German documents with English queries
- **Quality assurance:** Verify document completeness by searching for required fields

**Performance:**

- Text document search: 1-3 seconds
- PDF document search: 2-5 seconds (includes PDF extraction time)
- Cross-language search: Same performance (no additional overhead)

---

### GET /api/search/health

Search service health check with capability information.

**Current Implementation:** IMPLEMENTED in `backend/api/search.py`

**Source:** `backend/api/search.py:269-286`

**Authentication:** None (public endpoint)

**Success Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "semantic_search",
  "gemini_initialized": true,
  "pdf_support": true,
  "cross_language_support": true
}
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/search/health
```

**Usage:**
- Verify search service is initialized and ready
- Check Gemini AI integration status
- Confirm PDF extraction capability
- Validate cross-language search support

---

## File Operations

### POST /api/files/upload

Upload a file to a specific case folder with size validation and security checks.

**Current Implementation:** IMPLEMENTED in `backend/api/files.py`

**Source:** `backend/api/files.py:67-217`

**Authentication:** None (planned for future implementation)

**Description:**

This endpoint handles file uploads to case-scoped storage with comprehensive security features including filename sanitization, path traversal prevention, and file size validation. Files are stored in the `public/documents/{case_id}/{folder_id}/` directory structure.

**Request Body (multipart/form-data):**

- `file` (required): Binary file data to upload
- `case_id` (required): Case identifier (e.g., "ACTE-2024-001")
- `folder_id` (optional): Target folder ID within the case (default: "uploads")
- `rename_to` (optional): Alternative filename for duplicate handling

**Request Constraints:**

- Maximum file size: 15 MB (15,728,640 bytes)
- File must not be empty (0 bytes)
- case_id and folder_id must be alphanumeric with hyphens/underscores only
- Filename is automatically sanitized to remove unsafe characters

**Security Features:**

- **Path Traversal Prevention:** No `../` or absolute paths allowed in case_id, folder_id, or filename
- **Filename Sanitization:** Removes special characters, null bytes, and path separators
- **Case Path Validation:** Validates case_id and folder_id format (alphanumeric, hyphens, underscores)
- **Size Validation:** Enforces 15 MB limit to prevent resource exhaustion
- **Automatic Folder Creation:** Creates target directory structure if it doesn't exist

**Success Response (200 OK):**
```json
{
  "success": true,
  "file_path": "documents/ACTE-2024-001/uploads/document.pdf",
  "file_name": "document.pdf",
  "size": 2458624,
  "message": "File 'document.pdf' uploaded successfully"
}
```

**Error Response (400 Bad Request - Invalid Path):**
```json
{
  "error": "Validation failed",
  "detail": "case_id contains invalid characters: '../'",
  "file_name": "document.pdf"
}
```

**Error Response (413 Payload Too Large - File Too Large):**
```json
{
  "error": "File too large",
  "detail": "File exceeds 15.0 MB size limit. File size: 18.45 MB",
  "file_name": "large_file.pdf"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "error": "File system error",
  "detail": "Failed to save file. Please try again or contact support.",
  "file_name": "document.pdf"
}
```

**Example Usage:**

**cURL:**
```bash
curl -X POST http://localhost:8000/api/files/upload \
  -F "file=@/path/to/document.pdf" \
  -F "case_id=ACTE-2024-001" \
  -F "folder_id=uploads"
```

**cURL with duplicate handling:**
```bash
curl -X POST http://localhost:8000/api/files/upload \
  -F "file=@/path/to/document.pdf" \
  -F "case_id=ACTE-2024-001" \
  -F "folder_id=uploads" \
  -F "rename_to=document_2.pdf"
```

**JavaScript/TypeScript:**
```javascript
const uploadFile = async (file, caseId, folderId = 'uploads', renameTo = null) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('case_id', caseId);
  formData.append('folder_id', folderId);

  if (renameTo) {
    formData.append('rename_to', renameTo);
  }

  const response = await fetch('http://localhost:8000/api/files/upload', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || error.error);
  }

  return await response.json();
};

// Usage
try {
  const result = await uploadFile(
    fileInputElement.files[0],
    'ACTE-2024-001',
    'evidence'
  );
  console.log('Uploaded:', result.file_path);
} catch (error) {
  console.error('Upload failed:', error.message);
}
```

**Python:**
```python
import requests

def upload_file(file_path: str, case_id: str, folder_id: str = "uploads", rename_to: str = None):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {
            'case_id': case_id,
            'folder_id': folder_id
        }

        if rename_to:
            data['rename_to'] = rename_to

        response = requests.post(
            'http://localhost:8000/api/files/upload',
            files=files,
            data=data
        )

        if response.status_code != 200:
            raise Exception(f"Upload failed: {response.json()}")

        return response.json()

# Usage
result = upload_file("document.pdf", "ACTE-2024-001", "uploads")
print(f"Uploaded to: {result['file_path']}")
```

**Storage Structure:**

Files are stored in the following directory structure:
```
public/
  documents/
    ACTE-2024-001/
      uploads/
        document.pdf
        test_file.txt
      evidence/
        passport_scan.jpg
      personal-data/
        birth_certificate.pdf
```

**Document Registry Integration (S5-007):**

Upon successful file upload, the endpoint automatically registers the document in the document registry manifest (`backend/data/document_manifest.json`). This ensures:
- Document persists across container restarts
- Document appears in `GET /api/documents/tree/{case_id}` responses
- Document metadata is tracked (upload time, file hash, etc.)
- Document can have renders (anonymized, translated versions) associated with it

The registration process:
1. File is saved to filesystem
2. File hash (SHA-256) is calculated
3. Document entry is created in manifest with unique UUID
4. Manifest is persisted to disk

If registration fails (e.g., manifest corruption), the file upload still succeeds. The error is logged, and the document will be discovered during the next filesystem reconciliation on application startup.

**Tree Cache Invalidation (S5-011):**

After successful file upload, the endpoint automatically invalidates the document tree cache for the case. This ensures that the `GET /api/context/tree/{case_id}` endpoint returns updated tree views that include the newly uploaded file.

**Duplicate File Handling:**

When a file with the same name already exists:

1. Client should first call `GET /api/files/exists/{case_id}/{folder_id}/{filename}` to check for duplicates
2. If file exists, the exists endpoint returns a `suggested_name` (e.g., "document_1.pdf")
3. Client can then:
   - Use the `rename_to` parameter with the suggested name to upload with a unique name
   - Prompt user to overwrite (upload without `rename_to` to replace existing file)
   - Cancel the upload

**Filename Sanitization Rules:**

The service automatically sanitizes filenames using these rules:
- Removes null bytes and path separators (`/`, `\`)
- Removes parent directory references (`..`)
- Replaces spaces with underscores
- Removes special characters (keeps only alphanumeric, hyphens, dots, underscores)
- Ensures filename starts with alphanumeric character
- Limits filename length to 255 characters (preserves extension)

Examples:
- `my document.pdf` → `my_document.pdf`
- `../../etc/passwd` → `etc_passwd`
- `file<>:*?.txt` → `file.txt`

**Use Cases:**

- **Drag-and-drop file upload:** Frontend can use this endpoint for drag-and-drop functionality
- **Evidence upload:** Upload supporting documents to case folders
- **Document submission:** Applicants can submit required documents
- **Batch uploads:** Multiple files can be uploaded sequentially with progress tracking

**Known Limitations:**

- No authentication currently implemented (planned for future)
- Maximum file size: 15 MB (configurable in backend/services/file_service.py)
- No virus scanning (recommended for production)
- No file type validation (accepts all file types)
- Overwrites existing files with same name (unless `rename_to` is used)

**Performance:**

- Typical upload time: < 1 second for files under 5 MB
- Network-dependent for larger files
- Atomic write operation ensures no partial files

---

### DELETE /api/files/{case_id}/{folder_id}/{filename}

Delete a file from a specific case folder with security validation.

**Current Implementation:** IMPLEMENTED in `backend/api/files.py`

**Source:** `backend/api/files.py:220-347`

**Authentication:** None (planned for future implementation)

**Description:**

This endpoint handles file deletion with comprehensive security checks including path traversal prevention and case directory validation. The resolved file path is verified to stay within the expected case directory to prevent unauthorized access.

**Path Parameters:**

- `case_id` (required): Case identifier (e.g., "ACTE-2024-001")
- `folder_id` (required): Folder identifier (e.g., "uploads", "evidence")
- `filename` (required): Name of the file to delete

**Security Features:**

- **Path Traversal Prevention:** Validates resolved path stays within case directory
- **Case Path Validation:** Ensures case_id and folder_id contain only safe characters
- **Filename Sanitization:** Removes unsafe characters before deletion
- **Directory Validation:** Ensures target is a file, not a directory
- **Existence Check:** Verifies file exists before attempting deletion

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "File 'document.pdf' deleted successfully",
  "file_name": "document.pdf"
}
```

**Error Response (400 Bad Request - Invalid Path):**
```json
{
  "error": "Validation failed",
  "detail": "folder_id contains invalid characters: '../'",
  "file_name": "document.pdf"
}
```

**Error Response (403 Forbidden - Path Traversal Attempt):**
```json
{
  "error": "Access denied",
  "detail": "Access denied: Invalid file path",
  "file_name": "document.pdf"
}
```

**Error Response (404 Not Found):**
```json
{
  "error": "File not found",
  "detail": "File not found: document.pdf",
  "file_name": "document.pdf"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "error": "File system error",
  "detail": "Failed to delete file. Please try again or contact support.",
  "file_name": "document.pdf"
}
```

**Example Usage:**

**cURL:**
```bash
curl -X DELETE http://localhost:8000/api/files/ACTE-2024-001/uploads/document.pdf
```

**JavaScript/TypeScript:**
```javascript
const deleteFile = async (caseId, folderId, filename) => {
  const response = await fetch(
    `http://localhost:8000/api/files/${caseId}/${folderId}/${filename}`,
    { method: 'DELETE' }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || error.error);
  }

  return await response.json();
};

// Usage
try {
  const result = await deleteFile('ACTE-2024-001', 'uploads', 'document.pdf');
  console.log(result.message);
} catch (error) {
  console.error('Delete failed:', error.message);
}
```

**Python:**
```python
import requests

def delete_file(case_id: str, folder_id: str, filename: str):
    response = requests.delete(
        f'http://localhost:8000/api/files/{case_id}/{folder_id}/{filename}'
    )

    if response.status_code != 200:
        raise Exception(f"Delete failed: {response.json()}")

    return response.json()

# Usage
result = delete_file("ACTE-2024-001", "uploads", "document.pdf")
print(result['message'])
```

**Security Considerations:**

1. **Path Resolution Validation:** The endpoint resolves the file path and verifies it stays within the case directory:
   ```
   Expected: /public/documents/ACTE-2024-001/
   Resolved: /public/documents/ACTE-2024-001/uploads/document.pdf
   ✓ Path is valid (within case directory)
   ```

2. **Prevented Attack Examples:**
   ```
   DELETE /api/files/ACTE-2024-001/../ACTE-2024-002/uploads/file.pdf
   → 403 Forbidden: "folder_id contains invalid characters"

   DELETE /api/files/ACTE-2024-001/uploads/../../etc/passwd
   → 403 Forbidden: "Access denied: Invalid file path"
   ```

3. **Directory Protection:** Attempting to delete a directory returns an error

**Document Registry Unregistration (S5-007):**

Upon successful file deletion, the endpoint automatically unregisters the document from the document registry manifest. This ensures:
- Document no longer appears in `GET /api/documents/tree/{case_id}` responses
- Document metadata is removed from manifest
- Document renders (anonymized versions, etc.) are also unregistered
- Manifest is persisted to disk

**Tree Cache Invalidation (S5-011):**

After successful file deletion, the endpoint automatically invalidates the document tree cache for the case. This ensures that the `GET /api/context/tree/{case_id}` endpoint returns updated tree views without the deleted file.

The unregistration process:
1. Document is located in manifest by case_id, folder_id, and filename
2. File is deleted from filesystem
3. Document entry is removed from manifest (including all renders)
4. Manifest is persisted to disk

If the document is not found in the registry (orphaned file), a warning is logged but deletion proceeds normally. If unregistration fails (e.g., manifest corruption), the file deletion still succeeds. The error is logged, and the orphaned entry will be cleaned up during the next filesystem reconciliation.

**Use Cases:**

- **File cleanup:** Remove outdated or incorrect uploads
- **Privacy compliance:** Delete files when no longer needed
- **Storage management:** Free up disk space by removing unnecessary files
- **User corrections:** Allow users to remove files they uploaded by mistake

**Known Limitations:**

- No authentication currently implemented (planned for future)
- No trash/recycle bin (deletion is permanent)
- No cascading delete (must delete files individually)
- Recommended for "uploads" folder only (system folders may affect case functionality)

**Performance:**

- Typical deletion time: < 100ms
- Synchronous operation (returns after deletion completes)

---

### GET /api/files/exists/{case_id}/{folder_id}/{filename}

Check if a file already exists in a specific case folder (duplicate detection).

**Current Implementation:** IMPLEMENTED in `backend/api/files.py`

**Source:** `backend/api/files.py:364-442`

**Authentication:** None (planned for future implementation)

**Description:**

This endpoint checks for file existence and provides a suggested unique filename if the file already exists. It's designed to be called before upload to detect duplicates and allow users to make informed decisions about renaming or overwriting.

**Path Parameters:**

- `case_id` (required): Case identifier (e.g., "ACTE-2024-001")
- `folder_id` (required): Folder identifier (e.g., "uploads")
- `filename` (required): Name of the file to check

**Success Response (200 OK - File Exists):**
```json
{
  "exists": true,
  "file_name": "document.pdf",
  "suggested_name": "document_1.pdf"
}
```

**Success Response (200 OK - File Does Not Exist):**
```json
{
  "exists": false,
  "file_name": "new_document.pdf",
  "suggested_name": null
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Validation failed",
  "detail": "case_id contains invalid characters: '../'",
  "file_name": "document.pdf"
}
```

**Example Usage:**

**cURL:**
```bash
curl -X GET http://localhost:8000/api/files/exists/ACTE-2024-001/uploads/document.pdf
```

**JavaScript/TypeScript:**
```javascript
const checkFileExists = async (caseId, folderId, filename) => {
  const response = await fetch(
    `http://localhost:8000/api/files/exists/${caseId}/${folderId}/${filename}`
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || error.error);
  }

  return await response.json();
};

// Usage with duplicate handling
const handleUpload = async (file, caseId, folderId) => {
  // Check if file exists
  const existsResult = await checkFileExists(caseId, folderId, file.name);

  if (existsResult.exists) {
    // Prompt user for action
    const action = confirm(
      `File "${file.name}" already exists. Click OK to rename to "${existsResult.suggested_name}" or Cancel to overwrite.`
    );

    if (action) {
      // Upload with suggested name
      return uploadFile(file, caseId, folderId, existsResult.suggested_name);
    } else {
      // Upload to overwrite
      return uploadFile(file, caseId, folderId);
    }
  } else {
    // File doesn't exist, upload normally
    return uploadFile(file, caseId, folderId);
  }
};
```

**Python:**
```python
import requests

def check_file_exists(case_id: str, folder_id: str, filename: str):
    response = requests.get(
        f'http://localhost:8000/api/files/exists/{case_id}/{folder_id}/{filename}'
    )

    if response.status_code != 200:
        raise Exception(f"Check failed: {response.json()}")

    return response.json()

# Usage
result = check_file_exists("ACTE-2024-001", "uploads", "document.pdf")
if result['exists']:
    print(f"File exists! Suggested name: {result['suggested_name']}")
else:
    print("File does not exist, safe to upload")
```

**Unique Filename Generation:**

If a file exists, the service generates a unique filename by appending a numeric suffix:

- `document.pdf` exists → suggests `document_1.pdf`
- `document_1.pdf` exists → suggests `document_2.pdf`
- `document_2.pdf` exists → suggests `document_3.pdf`
- ...continues up to `document_999.pdf`

The service preserves the file extension and inserts the suffix before it.

**Typical Workflow:**

1. **User selects file for upload**
2. **Client calls exists endpoint** to check for duplicate
3. **If file exists:**
   - Display dialog: "File already exists. Rename, Overwrite, or Cancel?"
   - If rename: Use suggested_name in upload request's `rename_to` parameter
   - If overwrite: Upload without `rename_to` parameter
   - If cancel: Abort upload
4. **If file doesn't exist:** Proceed with upload normally

**Use Cases:**

- **Duplicate prevention:** Warn users before overwriting existing files
- **Batch upload validation:** Check multiple files before starting uploads
- **File versioning:** Automatically create numbered versions of files
- **User experience:** Provide clear feedback about file conflicts

**Performance:**

- Typical check time: < 50ms
- Lightweight operation (only checks file existence, doesn't read content)

---

### DELETE /api/files/renders/{case_id}/{document_id}/{render_id}

Delete a specific document render (anonymized, translated, etc.) from a document (S5-006).

**Current Implementation:** IMPLEMENTED in `backend/api/files.py`

**Source:** `backend/api/files.py:496-565`

**Authentication:** None (planned for future implementation)

**Description:**

This endpoint deletes a specific render (alternative version) of a document, such as an anonymized version or translated version. Renders are tracked in the document registry and linked to their parent document. Deleting a render removes both the file and the registry entry.

**Path Parameters:**

- `case_id` (required): Case identifier (e.g., "ACTE-2024-001")
- `document_id` (required): Parent document ID (UUID from document registry)
- `render_id` (required): Render ID to delete (UUID from document registry)

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Render deleted successfully",
  "render_id": "550e8400-e29b-41d4-a716-446655440002",
  "document_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

**Error Response (404 Not Found - Render Not Found):**
```json
{
  "detail": "Render 550e8400-e29b-41d4-a716-446655440002 not found or could not be deleted"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "detail": "Failed to delete render: <error details>"
}
```

**Example Usage:**

**cURL:**
```bash
curl -X DELETE \
  http://localhost:8000/api/files/renders/ACTE-2024-001/550e8400-e29b-41d4-a716-446655440001/550e8400-e29b-41d4-a716-446655440002
```

**JavaScript/TypeScript:**
```javascript
const deleteRender = async (caseId, documentId, renderId) => {
  const response = await fetch(
    `http://localhost:8000/api/files/renders/${caseId}/${documentId}/${renderId}`,
    { method: 'DELETE' }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return await response.json();
};

// Usage
try {
  const result = await deleteRender(
    'ACTE-2024-001',
    '550e8400-e29b-41d4-a716-446655440001',
    '550e8400-e29b-41d4-a716-446655440002'
  );
  console.log(result.message);
} catch (error) {
  console.error('Delete render failed:', error.message);
}
```

**Python:**
```python
import requests

def delete_render(case_id: str, document_id: str, render_id: str):
    response = requests.delete(
        f'http://localhost:8000/api/files/renders/{case_id}/{document_id}/{render_id}'
    )

    if response.status_code != 200:
        raise Exception(f"Delete render failed: {response.json()}")

    return response.json()

# Usage
result = delete_render(
    "ACTE-2024-001",
    "550e8400-e29b-41d4-a716-446655440001",
    "550e8400-e29b-41d4-a716-446655440002"
)
print(result['message'])
```

**Document Registry Integration:**

When a render is deleted:
1. The render entry is removed from the parent document's `renders` array in the document registry
2. The render file is deleted from the filesystem
3. The document registry manifest is persisted to disk
4. The document tree cache is invalidated to reflect the change

**Tree Cache Invalidation (S5-011):**

After successful render deletion, the endpoint automatically invalidates the document tree cache for the case. This ensures that the `GET /api/context/tree/{case_id}` endpoint returns updated tree views without the deleted render.

**Use Cases:**

- **Remove anonymized versions:** Delete anonymized document renders when no longer needed
- **Clean up translations:** Remove translated document versions after approval or rejection
- **Storage management:** Free up storage space by deleting unnecessary renders
- **Privacy compliance:** Remove renders containing sensitive data

---

### GET /api/files/health

File service health check endpoint.

**Current Implementation:** IMPLEMENTED in `backend/api/files.py`

**Source:** `backend/api/files.py:445-476`

**Authentication:** None (public endpoint)

**Description:**

This endpoint checks the health and availability of the file upload service, including storage availability and configuration settings. It can be used by monitoring systems, load balancers, and frontend applications to verify service readiness.

**Success Response (200 OK - Service Ready):**
```json
{
  "service": "files",
  "status": "ready",
  "features": {
    "upload": true,
    "max_file_size_mb": 15,
    "storage_path": "public/documents/"
  },
  "storage": {
    "available": true,
    "path": "/home/ayanm/projects/info-base/infobase-ai/public/documents"
  }
}
```

**Service Degraded Response (503 Service Unavailable - Storage Not Available):**
```json
{
  "service": "files",
  "status": "degraded",
  "features": {
    "upload": true,
    "max_file_size_mb": 15,
    "storage_path": "public/documents/"
  },
  "storage": {
    "available": false,
    "path": "/home/ayanm/projects/info-base/infobase-ai/public/documents"
  }
}
```

**Example Usage:**

**cURL:**
```bash
curl -X GET http://localhost:8000/api/files/health
```

**JavaScript/TypeScript:**
```javascript
const checkFileServiceHealth = async () => {
  const response = await fetch('http://localhost:8000/api/files/health');
  const health = await response.json();

  if (health.status === 'ready') {
    console.log('File service is ready');
    console.log(`Max file size: ${health.features.max_file_size_mb} MB`);
  } else {
    console.warn('File service is degraded');
  }

  return health;
};
```

**Python:**
```python
import requests

def check_file_service_health():
    response = requests.get('http://localhost:8000/api/files/health')
    health = response.json()

    if health['status'] == 'ready':
        print(f"File service ready. Max size: {health['features']['max_file_size_mb']} MB")
    else:
        print("File service degraded")

    return health
```

**Health Status Values:**

- `ready`: Service is fully operational, storage directory exists
- `degraded`: Service is running but storage directory is missing or inaccessible

**Use Cases:**

- **Monitoring:** Health check probes for container orchestration (Kubernetes, Docker)
- **Load balancing:** Backend health checks for load balancers
- **Frontend validation:** Check service availability before enabling upload features
- **Configuration verification:** Confirm max file size and storage path settings

**Performance:**

- Typical response time: < 50ms
- Lightweight operation (only checks directory existence)

---

## Search

### GET /search

Full-text search across all documents in accessible cases.

**Current Implementation:** Simulated in `src/components/workspace/AIChatInterface.tsx` via `/search` slash command.

**Source:** `src/components/workspace/AIChatInterface.tsx` (line 73-76)

**Authentication:** Required (Bearer token)

**Query Parameters:**
- `q` (required): Search query string
- `caseId` (optional): Limit search to specific case
- `documentType` (optional): Filter by document type (`pdf`, `xml`, `json`, `docx`)

**Success Response (200 OK):**
```json
{
  "results": [
    {
      "documentId": "doc-1",
      "documentName": "Birth_Certificate.pdf",
      "caseId": "ACTE-2024-001",
      "caseName": "German Integration Course Application",
      "matches": 2,
      "snippets": [
        "...born on March 20, 1995 in <mark>Kabul</mark>, Afghanistan...",
        "...issued by <mark>Kabul</mark> Civil Registry on..."
      ]
    },
    {
      "documentId": "doc-5",
      "documentName": "School_Transcripts.pdf",
      "caseId": "ACTE-2024-001",
      "caseName": "German Integration Course Application",
      "matches": 1,
      "snippets": [
        "...<mark>Kabul</mark> University, Faculty of Engineering..."
      ]
    }
  ],
  "total": 3,
  "query": "Kabul"
}
```

**Simulated Response:**
```
Searching for "Kabul" across all documents...

Found 3 matches:
• Birth_Certificate.pdf (2 occurrences)
• Passport_Scan.pdf (1 occurrence)
• School_Transcripts.pdf (highlighted)
```

**Simulated Behavior:**
- Highlights matching folder in case tree (`setHighlightedFolder('personal-data')`)
- In real implementation, would use full-text search index

**Example:**
```bash
curl -X GET "https://api.bamf-acte.example.de/v1/search?q=Kabul&caseId=ACTE-2024-001" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

```javascript
// React Query example (planned)
const { data: searchResults } = useQuery({
  queryKey: ['search', searchQuery],
  queryFn: async () => {
    const response = await fetch(`/api/v1/search?q=${encodeURIComponent(searchQuery)}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.json();
  },
  enabled: searchQuery.length > 0
});
```

---

## Additional Simulated Operations

These operations are simulated via the AI chat interface but don't have explicit API endpoints planned yet:

### AI Chat Commands

**Source:** `src/components/workspace/AIChatInterface.tsx`

#### Natural Language Form Filling

When user provides information in natural language, the AI extracts and auto-fills form fields:

```
User: "The applicant's name is Ahmed Ali and he was born in 1995"

AI Response: "I've updated the form with the name 'Ahmed Ali' and birth year 1995.
Please verify the exact date in the form."
```

**Implementation:**
- Pattern matching on chat messages (line 86-105)
- Calls `updateFormField()` to populate form
- Switches view to form mode via `setViewMode('form')`

#### Context-Aware Assistance

```
User: "Show me the certificates"

AI Response: "I've highlighted the Certificates folder in the case tree.
Click on it to view the available certificates."
```

**Implementation:**
- Calls `setHighlightedFolder('certificates')` to highlight folder
- Provides contextual navigation hints

---

## Error Handling

All endpoints use standard HTTP status codes and return consistent error responses:

**Error Response Format:**
```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {
    "field": "Additional context about the error"
  }
}
```

**Common Status Codes:**
- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `202 Accepted` - Async operation accepted
- `204 No Content` - Successful request with no response body
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict (e.g., duplicate)
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

---

## Rate Limiting

**Planned:** API endpoints will implement rate limiting:
- 1000 requests per hour per user
- 100 requests per minute per user
- Document upload: 50 files per hour

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 997
X-RateLimit-Reset: 1702729200
```

---

## Pagination

List endpoints support pagination using `limit` and `offset` parameters:

**Request:**
```
GET /cases?limit=20&offset=40
```

**Response:**
```json
{
  "cases": [...],
  "total": 156,
  "limit": 20,
  "offset": 40,
  "hasMore": true
}
```

---

## Versioning

The API uses URL path versioning: `/v1/`, `/v2/`, etc.

Breaking changes will result in a new version. Non-breaking changes (additions) will be deployed to existing versions.

---

**Last Updated:** 2025-12-24
**API Version:** 1.6.0 (Partial Implementation)
**Current Implementation:** Backend with WebSocket + AI + Streaming + Enhanced Form Extraction + Admin API + Document Anonymization + File Management, Frontend simulations for other operations
