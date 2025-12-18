# BAMF ACTE Companion - API Endpoints Reference

## Overview

This document provides detailed information about the BAMF ACTE Companion API endpoints, including both currently simulated operations and the planned future backend API.

**Current Status:** Backend API implementation has started using FastAPI. WebSocket-based AI chat and health check endpoints are now implemented. Other operations remain simulated client-side.

---

## Table of Contents

- [Health & System](#health--system)
- [Real-Time Communication](#real-time-communication)
- [Authentication](#authentication)
- [Case Management](#case-management)
- [Document Operations](#document-operations)
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

## Real-Time Communication

### WS /ws/chat/{case_id}

WebSocket endpoint for real-time, case-scoped AI chat communication.

**Current Implementation:** IMPLEMENTED in `backend/api/chat.py`

**Source:** `backend/api/chat.py:82-201`

**Authentication:** None (case-scoped isolation via URL parameter)

**Path Parameters:**
- `case_id` (required): Case identifier for context isolation (e.g., "ACTE-2024-001")

**Connection Protocol:**

1. Client initiates WebSocket connection to `/ws/chat/{case_id}`
2. Server accepts connection and sends system message confirming connection
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
- `type` (required): Message type - currently only "chat" is supported
- `content` (required): User's message, question, or instruction
- `caseId` (optional): Case ID for context (should match URL parameter)
- `folderId` (optional): Folder ID for folder-specific context
- `documentContent` (optional): Document text to include in context
- `formSchema` (optional): Form field definitions for extraction requests
- `stream` (optional): Enable streaming responses (default: true)

**Form Extraction Trigger:**
The AI automatically detects form filling requests when:
- `formSchema` is provided AND
- Message contains keywords: "fill", "extract", or "populate"

#### Outgoing Messages (Server to Client)

**System Message (Connection Confirmation):**
```json
{
  "type": "system",
  "content": "Connected to AI assistant for case ACTE-2024-001",
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

**Error Message:**
```json
{
  "type": "error",
  "message": "Error description",
  "timestamp": null
}
```

**Message Types Summary:**
- `system` - System notifications (connection status, etc.)
- `chat_response` - AI text responses to user queries (non-streaming mode)
- `chat_chunk` - Streaming AI response chunks with completion flag
- `form_update` - Extracted form field values with confidence scores
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

**Form Extraction Example:**
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

**Last Updated:** 2025-12-18
**API Version:** 1.3.0 (Partial Implementation)
**Current Implementation:** Backend with WebSocket + AI + Streaming + Enhanced Form Extraction, Frontend simulations for other operations
