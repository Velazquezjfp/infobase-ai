# BAMF ACTE Companion - API Documentation

## Overview

This directory contains API documentation for the BAMF ACTE Companion application. The application uses a hybrid architecture with a React/TypeScript frontend and a FastAPI Python backend.

## Current Architecture

**Status:** Hybrid Application with Backend API

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Browser                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Frontend   │
                    │   (Vite)    │
                    │ Port: 5173  │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    ┌───▼────┐      ┌─────▼─────┐     ┌──────▼──────┐
    │ Backend │      │ WebSocket │     │ Anonymize   │
    │(FastAPI)│◀────▶│   Chat    │     │  Service    │
    │Port:8000│      │           │     │ Port: 5000  │
    └─────────┘      └───────────┘     │ (External)  │
                                       └─────────────┘
```

### Backend Services

| Service | Location | Description |
|---------|----------|-------------|
| **GeminiService** | `backend/services/gemini_service.py` | AI integration with Google Gemini API |
| **ContextManager** | `backend/services/context_manager.py` | Case/folder context management |
| **ConversationManager** | `backend/services/conversation_manager.py` | Chat history management (optional, S5-010) |
| **FieldGenerator** | `backend/services/field_generator.py` | NLP-powered form field generation |
| **FileService** | `backend/services/file_service.py` | File upload, deletion, validation |
| **AnonymizationService** | `backend/services/anonymization_service.py` | PII detection client (calls external service) |
| **ValidationService** | `backend/services/validation_service.py` | AI-powered case validation for submission (S5-005) |

### Implemented API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `WS` | `/ws/chat/{case_id}?language={lang}` | Real-time AI chat with streaming and multilingual support (S5-014) |
| `GET` | `/health` | Backend health check |
| `GET` | `/` | Backend info |
| `POST` | `/api/admin/generate-field` | Generate form field from NLP |
| `GET` | `/api/admin/health` | Admin service health |
| `POST` | `/api/files/upload` | Upload file (15 MB limit) |
| `DELETE` | `/api/files/{case_id}/{folder_id}/{filename}` | Delete file |
| `GET` | `/api/files/exists/{case_id}/{folder_id}/{filename}` | Check file exists |
| `GET` | `/api/files/health` | File service health |
| `GET` | `/api/chat/health` | Chat service health |
| `POST` | `/api/chat/clear/{case_id}` | Clear conversation history (S5-010) |
| `GET` | `/api/context/tree/{case_id}` | Get document tree view for case (S5-011) |
| `GET` | `/api/custom-context/{case_id}` | Get custom context rules for a case (S5-017) |
| `POST` | `/api/custom-context/{case_id}/rule` | Add a validation rule (S5-017) |
| `POST` | `/api/custom-context/{case_id}/document` | Add a required document (S5-017) |
| `DELETE` | `/api/custom-context/{case_id}/{rule_id}` | Remove a custom rule (S5-017) |
| `POST` | `/api/validation/case/{case_id}` | AI-powered case validation for submission (S5-005) |
| `GET` | `/api/validation/health` | Validation service health |

### External Dependencies

- **Anonymization Service** (port 5000): External PII detection and masking service
  - Endpoint: `http://localhost:5000/ai-analysis`
  - Required for `/anonymize` command functionality

## Running the Application

```bash
# Start all services (frontend + backend)
./start.sh

# Services will be available at:
# - Frontend: http://localhost:5173
# - Backend:  http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

**Note:** The anonymization service (port 5000) must be started separately.

## Documentation Structure

### 1. **openapi.yaml / openapi.json**
OpenAPI 3.0 specifications documenting the implemented and planned API endpoints.

### 2. **endpoints.md**
Detailed endpoint reference including:
- Implemented backend API endpoints
- WebSocket protocol for AI chat
- Request/response formats with examples

### 3. **authentication.md**
Authentication and authorization documentation:
- Current: Simple client-side username storage
- Planned: Token-based authentication strategy

### 4. **api-changelog.md**
Chronological record of API changes and feature implementations.

### 5. **.last-sync.json**
Internal tracking file for documentation synchronization with codebase changes.

## API Operations

### Implemented (Backend)

| Operation | Endpoint | Status |
|-----------|----------|--------|
| AI Chat | `WS /ws/chat/{case_id}` | Implemented |
| Anonymize Document | `WS message type: anonymize` | Implemented |
| Generate Form Field | `POST /api/admin/generate-field` | Implemented |
| Upload File | `POST /api/files/upload` | Implemented |
| Delete File | `DELETE /api/files/{case_id}/{folder_id}/{filename}` | Implemented |

### Simulated (Frontend Mock)

| Operation | Location | Notes |
|-----------|----------|-------|
| `/convert` | AIChatInterface.tsx | Document format conversion |
| `/translate` | AIChatInterface.tsx | Document translation |
| `/search` | AIChatInterface.tsx | Case document search |
| `/validateCase` | AIChatInterface.tsx | Missing document check |
| Authentication | Login.tsx | Simple username storage |
| Case Management | AppContext.tsx | CRUD operations |

## Technology Stack

### Frontend
- React 18.3 with TypeScript 5.8
- Vite 5.4 (dev server)
- React Router 6.30
- @tanstack/react-query 5.83
- shadcn/ui components

### Backend
- Python 3.12
- FastAPI 0.104.1
- Uvicorn 0.24.0
- Google Generative AI (Gemini)
- WebSockets 12.0
- Pydantic 2.5.2

## Development Notes

### Environment Setup
1. Create `backend/.env` with required configuration:
   ```
   GEMINI_API_KEY=your_key
   ENABLE_CHAT_HISTORY=false  # Optional: Enable conversation history (S5-010)
   ```
2. Run `./start.sh` to start both services
3. Ensure anonymization service is running on port 5000 if needed

### Configuration Options (backend/.env or environment variables)
- `GEMINI_API_KEY` (required): Google Gemini API key for AI integration
- `ENABLE_CHAT_HISTORY` (optional, default: false): Enable conversation history management
- `MAX_CONVERSATION_HISTORY` (optional, default: 10): Maximum messages per case
- `LOG_LEVEL` (optional, default: INFO): Logging level

### API Integration Status
- React Query client configured in `App.tsx`
- Type definitions in `src/types/case.ts` and `src/types/file.ts`
- File API client in `src/lib/fileApi.ts`
- Some frontend operations still use mock data (see Simulated operations above)

## Related Documentation

- [Code Graph](/docs/code-graph/code-graph.json) - Application structure analysis
- [Implementation Plan](/docs/implementation_plan.md) - Sprint planning
- [Requirements](/docs/requirements/) - Feature specifications

---

**Last Updated:** 2026-01-16
**Documentation Version:** 2.2.0
**Application Version:** 0.0.0
