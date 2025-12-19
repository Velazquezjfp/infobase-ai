# Sprint 1 Quick Reference Card

## Requirement IDs At-a-Glance

### Functional Requirements

| ID | Title | Priority | Effort |
|----|-------|----------|--------|
| F-001 | Document Assistant Agent - Backend WebSocket Service | P1 | High |
| F-002 | Document Context Management System | P1 | Medium |
| F-003 | Form Auto-Fill from Document Content | P2 | High |
| F-004 | AI-Powered Form Field Generator - Admin Interface | P3 | High |
| F-005 | Folder-Specific Form Management | P2 | Medium |
| F-006 | Replace Mock Documents with Text Files | P1 | Low |

### Non-Functional Requirements

| ID | Title | Priority | Effort |
|----|-------|----------|--------|
| NFR-001 | Real-Time AI Response Performance | P2 | Medium |
| NFR-002 | Modular Backend Architecture | P1 | Low |
| NFR-003 | Local Storage Without Database | P3 | Low |

### Data Requirements

| ID | Title | Priority | Effort |
|----|-------|----------|--------|
| D-001 | Hierarchical Context Data Schema | P1 | Medium |
| D-002 | Folder-Specific Form Schemas | P2 | Low |
| D-003 | Sample Document Text Content | P1 | Low |

## Key File Locations

### Frontend Files (Existing)
```
src/contexts/AppContext.tsx           - Global state (20+ properties)
src/components/workspace/
  ├── AIChatInterface.tsx              - Chat UI (lines 28-256)
  ├── FormViewer.tsx                   - Form display
  ├── AdminConfigPanel.tsx             - Admin config (5 tabs, line 472-538 for Forms)
  ├── DocumentViewer.tsx               - Document viewer
  └── CaseTreeExplorer.tsx             - File tree
src/types/case.ts                      - Type definitions
src/data/mockData.ts                   - Mock data and templates
```

### Backend Files (To Be Created)
```
backend/
├── main.py                            - FastAPI entry point
├── api/
│   ├── chat.py                        - WebSocket routes
│   └── admin.py                       - Admin endpoints
├── services/
│   ├── gemini_service.py              - Gemini API wrapper
│   ├── context_manager.py             - Context loading/merging
│   └── field_generator.py             - Field generation service
├── tools/
│   ├── form_parser.py                 - Form field extraction
│   └── document_processor.py          - Document utilities
├── data/contexts/
│   ├── case_types/
│   │   └── integration_course.json    - Case-level context
│   └── folders/
│       ├── personal_data.json         - Folder contexts (6 files)
│       └── ...
└── requirements.txt                   - Python dependencies
```

### Frontend Files (To Be Created)
```
src/types/websocket.ts                 - WebSocket message types
src/lib/
  ├── documentLoader.ts                - Document content loader
  └── localStorage.ts                  - Storage utilities
public/documents/
  ├── Birth_Certificate.txt            - Sample documents (6 files)
  └── ...
```

## API Endpoints

### WebSocket
- `ws://localhost:8000/ws/chat/{case_id}` - Real-time chat

### REST (Admin)
- `POST /api/admin/generate-field` - Generate form field from natural language

### Health
- `GET /health` - Service health check

## Message Types (WebSocket)

### Request
```typescript
interface ChatRequest {
  type: "message" | "command";
  content: string;
  caseId: string;
  folderId: string | null;
  documentContent?: string;
  formFields?: FormField[];
}
```

### Response
```typescript
interface ChatResponse {
  type: "message" | "form_update" | "error";
  content?: string;
  updates?: Record<string, string>;
  confidence?: Record<string, number>;
}
```

## Slash Commands

| Command | Purpose | Requirement |
|---------|---------|-------------|
| `/fillForm` | Extract data to form fields | F-003 |
| `/convert` | Convert document format | Future |
| `/translate` | Translate to German/English | Future |
| `/anonymize` | Remove PII from document | Future |
| `/search` | Search across documents | Future |
| `/validateCase` | Check case completeness | Future |

## Context Hierarchy

```
Case Context (integration_course.json)
  ├── regulations: BAMF regulations (§43 AufenthG, etc.)
  ├── requiredDocuments: Birth cert, passport, certificates
  └── validationRules: Age verification, document validity
    │
    └── Folder Context (personal_data.json, etc.)
        ├── expectedDocuments: Birth certificate, passport
        ├── validationCriteria: Name consistency, valid dates
        └── commonMistakes: Missing translations, expired docs
          │
          └── Document Content
              └── Selected document text
```

## Form Structure by Folder

### Personal Data Form (7 fields)
- name (text, required)
- birthDate (date, required)
- nationality (text, required)
- passportNumber (text, required)
- passportExpiry (date, required)
- placeOfBirth (text, required)
- currentAddress (textarea, required)

### Certificates Form (6 fields)
- certificateType (select: Language/Education/Professional, required)
- issuingInstitution (text, required)
- level (select: A1/A2/B1/B2/C1/C2, required)
- issueDate (date, required)
- expiryDate (date, optional)
- certificateNumber (text, optional)

### Integration Course Form (6 fields)
- courseProvider (text, required)
- courseType (select: Intensive/Evening/Weekend/Online, required)
- startDate (date, required)
- expectedEndDate (date, required)
- hoursPerWeek (text, required)
- courseLocation (text, required)

### Applications Form (4 fields)
- applicationDate (date, required)
- status (select: Draft/Submitted/Under Review/Approved/Rejected, required)
- reviewedBy (text, optional)
- notes (textarea, optional)

## Performance Targets (NFR-001)

| Operation | Target | Measurement |
|-----------|--------|-------------|
| First token | < 2 seconds | Time to first WebSocket message chunk |
| Document summary | < 10 seconds | Full response for 1000-word document |
| Form auto-fill | < 5 seconds | Parse 2000-char doc with 7 fields |
| Document load | < 500ms | Fetch and display text file |
| WebSocket connect | < 1 second | Connection establishment time |

## Technology Stack

### Frontend
- React 18 + TypeScript 5
- Vite 5
- shadcn/ui components
- Tailwind CSS
- WebSocket API (native)
- localStorage API (native)

### Backend
- Python 3.10+
- FastAPI 0.104+
- websockets 12.0
- google-generativeai 0.3+
- python-dotenv 1.0
- uvicorn 0.24+

### External Services
- Google Gemini API (gemini-pro or gemini-1.5-flash)

## Environment Variables

```bash
# .env file
GEMINI_API_KEY=your_gemini_api_key_here
```

## Development Commands

### Frontend
```bash
npm install              # Install dependencies
npm run dev             # Start dev server (port 5173)
npm run build           # Build for production
npm run type-check      # TypeScript validation
```

### Backend
```bash
python -m venv venv                    # Create virtual environment
source venv/bin/activate               # Activate (Linux/Mac)
pip install -r requirements.txt        # Install dependencies
uvicorn main:app --reload --port 8000  # Start dev server
python -m pytest                       # Run tests
pylint backend/                        # Code quality check
mypy backend/                          # Type checking
```

## Testing Quick Commands

### Test WebSocket Connection
```bash
# Install websocat: https://github.com/vi/websocat
websocat ws://localhost:8000/ws/chat/ACTE-2024-001
# Type: {"type":"message","content":"Hello"}
```

### Test Document Loading
```javascript
// Browser console
fetch('/documents/Birth_Certificate.txt')
  .then(r => r.text())
  .then(console.log)
```

### Test LocalStorage
```javascript
// Browser console
localStorage.setItem('bamf_test', JSON.stringify({hello: 'world'}))
JSON.parse(localStorage.getItem('bamf_test'))
localStorage.clear()
```

## Common Patterns

### Adding New Form Field
1. Define in appropriate form array (`src/data/mockData.ts`)
2. Add to FormField type if new field type needed (`src/types/case.ts`)
3. Update FormViewer if new rendering logic needed
4. Update form parser to recognize new field

### Adding New Context Rule
1. Edit appropriate JSON file in `backend/data/contexts/`
2. Follow schema structure (see D-001)
3. Restart backend to reload contexts
4. Test agent responses include new context

### Adding New WebSocket Message Type
1. Define interface in `src/types/websocket.ts`
2. Handle in backend `chat.py` route
3. Handle in frontend `AIChatInterface.tsx` onMessage
4. Update tests for new message type

## Troubleshooting

### WebSocket Won't Connect
- Check backend is running on port 8000
- Verify CORS settings in `main.py`
- Check browser console for errors
- Try `ws://` not `wss://` for local dev

### Gemini API Errors
- Verify GEMINI_API_KEY in .env
- Check API quota/billing in Google Cloud Console
- Review error messages in backend logs
- Try smaller prompts if hitting token limits

### Form Auto-Fill Not Working
- Check document content loaded (not null)
- Verify formFields passed in WebSocket message
- Check backend logs for parsing errors
- Test with simpler document text

### LocalStorage Full
- Check current usage: `localStorage.length`
- Clear old data: `localStorage.clear()`
- Reduce stored data size
- Implement data compression

## Folder ID Mappings

```typescript
{
  "personal-data": "Personal Data",
  "certificates": "Certificates",
  "integration-docs": "Integration Course Documents",
  "applications": "Applications & Forms",
  "emails": "Emails",
  "evidence": "Additional Evidence"
}
```

## Sample Test Cases (Copy-Paste Ready)

### TC-F-001-01: Basic Chat
1. Start backend and frontend
2. Open chat interface
3. Send message: "Hello"
4. Verify response within 3 seconds

### TC-F-003-01: Form Auto-Fill
1. Click Birth_Certificate.txt in Personal Data folder
2. Send command: "/fillForm"
3. Verify name field populated with extracted name
4. Check birthDate field has ISO format date

### TC-F-005-01: Folder Form Switching
1. Click Personal Data folder
2. Verify form shows name, birthDate, nationality fields
3. Click Certificates folder
4. Verify form shows certificateType, level, issuingInstitution fields

## Git Commit Message Format

```
<requirement-id>: <imperative-mood-summary>

<optional-body>

Addresses: <requirement-id>
Test cases: <test-case-ids>
```

Examples:
```
F-001: Implement WebSocket chat endpoint

- Add FastAPI WebSocket route at /ws/chat/{case_id}
- Integrate GeminiService for message processing
- Add connection lifecycle management

Addresses: F-001
Test cases: TC-F-001-01, TC-F-001-02, TC-F-001-03
```

```
D-001: Create hierarchical context JSON files

- Add integration_course.json with BAMF regulations
- Create 6 folder-specific context files
- Document schema in comments

Addresses: D-001
Test cases: TC-D-001-01, TC-D-001-05
```

## Status Tracking

Update requirement status in `requirements.md`:
- `proposed` → `in_progress` (when starting work)
- `in_progress` → `completed` (when all test cases pass)
- Add `implemented_date` field when marking complete
- Add notes about any deviations from spec

---

**This quick reference is current as of Sprint 1 requirements v1.0**
**For detailed specifications, see `requirements.md`**
**For implementation order, see `sprint1-implementation-plan.md`**
