# BAMF ACTE Companion - API Changelog

## Overview

This document tracks all changes to the BAMF ACTE Companion API documentation and architecture. Since the application is currently a frontend-only prototype, this changelog documents the evolution of the API specification and simulated features.

**Current Status:** API specification is in planning phase. All endpoints documented are planned for future implementation.

---

## Version Format

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

---

## [Unreleased]

### Planned Features
- Authentication and authorization system
- Batch document upload endpoint
- Document comparison endpoint
- Case export/import endpoints
- Advanced search with filters and facets
- Document versioning and history
- Audit log API endpoints
- REST endpoints for legacy AI operations (convert, translate, anonymize)
- WebSocket streaming responses
- Message history persistence
- File upload via WebSocket

---

## [1.1.0] - 2025-12-18

### Added - Backend Implementation with WebSocket and AI Integration

This release marks the beginning of backend API implementation using FastAPI. Core AI functionality is now available through WebSocket communication with Google Gemini integration.

#### Backend Infrastructure

**Framework & Architecture:**
- FastAPI backend initialized (`backend/main.py`)
- Clean architecture with separation of concerns:
  - `backend/api/` - HTTP/WebSocket protocol handling
  - `backend/services/` - Business logic and AI integration
  - `backend/tools/` - Reusable stateless utility functions
  - `backend/data/` - Configuration files and context data
- CORS middleware configured for local development
- Lifecycle management (startup/shutdown events)
- Logging infrastructure

**Health Check Endpoints:**
- `GET /health` - Backend service health check
- `GET /` - API root information endpoint
- `GET /api/chat/health` - Chat service health with Gemini status

#### Real-Time Communication

**WebSocket Chat Endpoint:**
- `WS /ws/chat/{case_id}` - Real-time, case-scoped AI chat
  - Bidirectional message exchange
  - Connection manager for case isolation
  - Support for multiple message types
  - Automatic context loading per case

**Message Protocol:**

Incoming message types:
- `chat` - User messages and AI interaction requests

Outgoing message types:
- `system` - System notifications and connection status
- `chat_response` - AI-generated text responses
- `form_update` - Extracted form field values with confidence scores
- `error` - Error notifications and validation failures

**Case-Scoped Context:**
- Each WebSocket connection isolated to single case
- Automatic loading of case-level context from JSON files
- Optional folder-level context for specific document groups
- Complete case isolation (no cross-case data access)

#### AI Integration

**Google Gemini Service:**
- `GeminiService` class with singleton pattern (`backend/services/gemini_service.py`)
- Integration with Google Gemini 2.5 Flash model
- Environment-based API key configuration
- Configurable generation parameters (temperature, top_p, max_tokens)
- User-friendly error messages for quota/timeout issues

**Context Management:**
- `ContextManager` service for hierarchical context loading (`backend/services/context_manager.py`)
- Case-level context: regulations, required documents, validation rules
- Folder-level context: expected documents, validation criteria
- Context merging with precedence: Document > Folder > Case
- Template-based case creation support

**Context File Structure:**
```
backend/data/contexts/
├── cases/
│   └── {case_id}/
│       ├── case.json
│       └── folders/
│           └── {folder_id}.json
└── templates/
    └── {case_type}/
```

#### Form Field Extraction

**AI-Powered Data Extraction:**
- `form_parser` tool for document field extraction (`backend/tools/form_parser.py`)
- Intelligent field mapping with semantic understanding
- Date normalization to ISO 8601 format
- Multi-language document support
- Confidence scoring (0.0-1.0) for each extracted field

**Extraction Features:**
- Automatic detection via keywords: "fill", "extract", "populate"
- Validation against form schema before extraction
- Partial extraction (only found fields returned)
- Type-aware extraction (text, date, select, textarea)
- Structured prompt engineering for consistent results

**Form Schema Support:**
```json
{
  "id": "field_identifier",
  "label": "Field Label",
  "type": "text|date|select|textarea",
  "required": boolean,
  "options": ["array", "for", "select"]
}
```

**Extraction Workflow:**
1. Client sends chat message with `formSchema` and `documentContent`
2. Backend builds extraction prompt with field definitions
3. Gemini AI analyzes document and extracts values
4. Results parsed and validated against schema
5. Two responses sent: `form_update` + `chat_response`

#### Technical Details

**Dependencies Added:**
- FastAPI 0.104.1 - Web framework
- Uvicorn 0.24.0 - ASGI server
- google-generativeai 0.3.1 - Gemini API client
- Pydantic 2.5.2 - Data validation
- python-dotenv 1.0.0 - Environment configuration

**AI Model Configuration:**
- Model: gemini-2.5-flash (fast, cost-effective, latest)
- Temperature: 0.7
- Top P: 0.8
- Top K: 40
- Max Output Tokens: 2048

**Performance Characteristics:**
- WebSocket connection per case maintained by ConnectionManager
- Context loaded per message from filesystem (no caching)
- Typical AI response time: 1-3 seconds
- Form extraction: 2-5 seconds depending on complexity

#### Known Limitations

**Not Yet Implemented:**
- Authentication/authorization system
- Case management REST endpoints
- Document storage and retrieval
- Persistent message history
- WebSocket message streaming
- Connection rate limiting
- OCR support for images
- File uploads via WebSocket

**Current Constraints:**
- No authentication (case isolation only)
- Single connection per case (no concurrent)
- Text-only document processing
- Maximum ~10,000 character document length
- Frontend still using mock data (integration pending)

#### Migration Impact

**Non-Breaking Changes:**
- All new functionality (no existing APIs affected)
- Frontend integration not yet required
- Backward compatible with existing simulated operations

**Frontend Integration Required:**
- Update `AIChatInterface.tsx` to use WebSocket
- Replace simulated AI operations with real backend calls
- Add WebSocket connection management
- Handle new message types (form_update, system, error)
- Implement confidence score display for form extraction

#### Documentation Updates

**New Documentation:**
- WebSocket endpoint comprehensive documentation
- Message protocol specification
- Form extraction guide with examples
- Context management architecture
- Health check endpoint documentation

**Updated Files:**
- `docs/apis/.last-sync.json` - Added backend file tracking
- `docs/apis/endpoints.md` - Added WebSocket and health endpoints
- `docs/apis/api-changelog.md` - Version 1.1.0 changelog
- API status changed: "planned" → "partial_implementation"

#### Configuration Required

**Environment Variables:**
```bash
GEMINI_API_KEY=your_google_gemini_api_key_here
```

**Running the Backend:**
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**WebSocket Test:**
```bash
# Using wscat
wscat -c ws://localhost:8000/ws/chat/ACTE-2024-001
```

---

## [1.0.0] - 2025-12-16

### Added - Initial API Documentation

#### Documentation Structure
- Created comprehensive API documentation in `docs/apis/` directory
- Added OpenAPI 3.0 specification (YAML and JSON formats)
- Created detailed endpoint reference with examples
- Documented authentication architecture
- Added this changelog

#### API Endpoints (Planned)

**Authentication**
- `POST /auth/login` - User authentication with JWT tokens
- `POST /auth/logout` - Invalidate access token
- `POST /auth/refresh` - Refresh expired access token

**Case Management**
- `GET /cases` - List cases with filtering and pagination
- `POST /cases` - Create new case from template
- `GET /cases/{caseId}` - Get case details
- `PATCH /cases/{caseId}` - Update case metadata

**Document Operations**
- `GET /cases/{caseId}/documents` - List case documents
- `POST /cases/{caseId}/documents` - Upload document
- `GET /cases/{caseId}/documents/{documentId}` - Get document
- `DELETE /cases/{caseId}/documents/{documentId}` - Delete document

**AI Operations**
- `POST /ai/convert` - Convert document format
- `POST /ai/translate` - Translate document to German
- `POST /ai/anonymize` - Redact personal information
- `POST /ai/extract-metadata` - Extract structured metadata
- `POST /ai/validate-case` - Check case completeness

**Form Management**
- `GET /cases/{caseId}/forms` - Get application form data
- `PUT /cases/{caseId}/forms` - Update form data

**Search**
- `GET /search` - Full-text search across documents

#### Current Implementation (Simulated)

**Source Files:**
- `src/pages/Login.tsx` - Simulated login (no validation)
- `src/contexts/AppContext.tsx` - State management with mock data
- `src/data/mockData.ts` - Mock case, document, and form data
- `src/components/workspace/AIChatInterface.tsx` - Simulated AI operations via slash commands
- `src/components/workspace/CaseTreeExplorer.tsx` - Simulated document upload
- `src/components/workspace/FormViewer.tsx` - Form state management
- `src/components/workspace/DocumentViewer.tsx` - Document display

**Simulated Features:**
- User authentication (username only, no password)
- Case browsing and switching
- Document tree navigation
- AI chat with slash commands:
  - `/convert` - Document format conversion
  - `/translate` - Translation to German
  - `/anonymize` - PII redaction
  - `/search` - Document search
  - `/validateCase` - Case completeness check
  - `/generateEmail` - Email generation
  - `/extractMetadata` - Metadata extraction
- Form auto-fill from AI chat
- Context-aware folder highlighting

**Technology Stack:**
- React 18.3 with TypeScript 5.8
- Vite 5.4 for build tooling
- React Router 6.30 for routing
- @tanstack/react-query 5.83 (configured but not yet used)
- shadcn/ui components
- Client-side state via React Context

#### Data Models

**Core Types** (`src/types/case.ts`):
```typescript
type DocumentType = 'pdf' | 'xml' | 'json' | 'docx';
type CaseStatus = 'open' | 'pending' | 'completed';
type FormFieldType = 'text' | 'date' | 'select' | 'textarea';
type ChatRole = 'user' | 'assistant';

interface Document {
  id: string;
  name: string;
  type: DocumentType;
  size: string;
  uploadedAt: string;
  metadata?: Record<string, any>;
  content?: string;
}

interface Folder {
  id: string;
  name: string;
  documents: Document[];
  subfolders: Folder[];
  isExpanded?: boolean;
}

interface Case {
  id: string;
  name: string;
  createdAt: string;
  status: CaseStatus;
  folders: Folder[];
}

interface FormField {
  id: string;
  label: string;
  type: FormFieldType;
  value: string;
  options?: string[];
  required?: boolean;
}

interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  timestamp: string;
  command?: string;
}
```

#### Authentication Architecture

**Current:** Simple username storage in React Context
- No password validation
- No token management
- No session persistence
- No role-based access control

**Planned:** JWT-based authentication
- Access tokens (1 hour expiration)
- Refresh tokens (7 days expiration)
- Role-based permissions (admin, officer, viewer)
- Granular permission system
- HttpOnly cookie storage
- Automatic token refresh

#### Security Considerations

**Planned Security Features:**
- HTTPS-only communication
- Password hashing (bcrypt/Argon2)
- Rate limiting (5 login attempts per 15 minutes)
- CSRF protection
- Token blacklist for logout
- Content Security Policy
- Audit logging

---

## [0.0.0] - 2024-12-16

### Initial Prototype

- Created frontend-only prototype application
- Implemented UI components with shadcn/ui
- Created mock data structures
- Simulated AI chat interface
- Basic case and document management UI
- Drag-and-drop document upload (UI only)

---

## Migration Notes

### From Prototype to Production API

When implementing the real backend API, the following changes will be required:

#### Frontend Changes
1. Replace `src/contexts/AppContext.tsx` state management with React Query calls
2. Update `src/pages/Login.tsx` to call `/api/v1/auth/login`
3. Add authentication token management (localStorage + auto-refresh)
4. Replace all `setTimeout` simulations with actual API calls
5. Update `src/components/workspace/AIChatInterface.tsx` to call AI endpoints
6. Implement proper error handling and loading states
7. Add retry logic for failed requests

#### Backend Implementation Required
1. Set up API server (Node.js/Python/Java based on requirements)
2. Implement authentication endpoints with JWT
3. Create case management CRUD endpoints
4. Implement file upload and storage system
5. Integrate AI services for document processing
6. Set up database for persistent storage
7. Implement search indexing (Elasticsearch/PostgreSQL full-text)
8. Add rate limiting and security middleware
9. Set up logging and monitoring

#### Breaking Changes from Simulation
- Case IDs will come from backend (not generated client-side)
- Document uploads will be real multipart/form-data
- AI operations will be asynchronous (job queue pattern)
- Authentication required for all protected endpoints
- Error responses will follow standard format

---

## Deprecation Policy

When the API is implemented:
- Deprecated endpoints will be marked 6 months before removal
- Breaking changes will always result in a new major version
- All deprecations will be documented in this changelog
- Migration guides will be provided for breaking changes

---

## Versioning Strategy

### API Versioning
- URL path versioning: `/v1/`, `/v2/`, etc.
- Version specified in OpenAPI spec `info.version`
- Each major version supported for minimum 12 months after successor release

### Documentation Versioning
- Documentation version tracks API specification version
- Git tags for each version release
- Documentation archived for previous versions

---

## Related Documentation

- [OpenAPI Specification](/docs/apis/openapi.yaml)
- [Endpoint Reference](/docs/apis/endpoints.md)
- [Authentication Guide](/docs/apis/authentication.md)
- [Architecture Overview](/docs/apis/README.md)

---

## Questions & Support

For questions about the API or to report issues with this documentation:
- Email: api@bamf.example.de
- Internal Wiki: [BAMF Development Portal](https://internal.bamf.example.de)

---

**Changelog Maintained By:** BAMF Development Team
**Last Updated:** 2025-12-16
**Format:** [Keep a Changelog](https://keepachangelog.com/)
