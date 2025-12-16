# BAMF ACTE Companion - API Endpoints Reference

## Overview

This document provides detailed information about the BAMF ACTE Companion API endpoints, including both currently simulated operations and the planned future backend API.

**Current Status:** The application currently runs as a frontend-only prototype. All API operations described here are simulated client-side. This documentation serves as the blueprint for future backend implementation.

---

## Table of Contents

- [Authentication](#authentication)
- [Case Management](#case-management)
- [Document Operations](#document-operations)
- [AI Operations](#ai-operations)
- [Form Management](#form-management)
- [Search](#search)

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

All AI operations are asynchronous and return a job ID that can be polled for status.

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

**Last Updated:** 2025-12-16
**API Version:** 1.0.0 (Planned)
**Current Implementation:** Frontend-only simulation
