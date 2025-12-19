# BAMF ACTE Companion

AI-powered case management system for BAMF asylum case processing with context-aware document analysis and intelligent form filling.

## Project Status

### Implementation Progress

According to [docs/implementation_plan.md](docs/implementation_plan.md):

- ✅ **Phase 1: Foundation** - Complete
  - Backend modular architecture (NFR-002)
  - Hierarchical context data schema (D-001)
  - Case-type form schemas (D-002)
  - Sample document text content (D-003)

- ✅ **Phase 2: Core Infrastructure** - Complete
  - Document Assistant Agent with WebSocket (F-001)
  - Document Context Management System (F-002)
  - Text file document loading (F-006)
  - Local storage without database (NFR-003)

- ✅ **Phase 3: Feature Implementation** - Complete
  - Case-level form management (F-005)
  - Form auto-fill from documents (F-003)
  - Real-time AI response performance (NFR-001)

- ❌ **Phase 4: Admin Features** - NOT IMPLEMENTED
  - AI-Powered Form Field Generator (F-004) - Missing

### Known Limitations and Missing Features

1. **Phase 4 Admin Features**: AI-powered form field generator for admins is not implemented
2. **PDF Processing**: Only text files (.txt) are currently supported, PDF parsing not implemented
3. **Document Type Support**: Limited to text files; DOCX, XML, JSON viewers are placeholder UI only
4. **Multi-Case Testing**: Further testing needed to ensure proper isolation between different case types
5. **Production Deployment**: No deployment configuration or production environment setup
6. **Error Recovery**: Limited error handling for edge cases and network failures
7. **Authentication**: Simple name-based login; no real authentication/authorization system
8. **Internationalization**: UI is in English; no German localization despite BAMF context

## Quick Start

### Prerequisites

- **Node.js 16+** and npm ([install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating))
- **Python 3.8+** ([download here](https://www.python.org/downloads/))
- **Google Gemini API key** ([get one free here](https://aistudio.google.com/app/apikey))

### Installation and Startup

#### Option 1: Automated Startup (Recommended)

```bash
# 1. Clone the repository
git clone <YOUR_GIT_URL>
cd bamf-acte-companion

# 2. Configure environment
echo "GEMINI_API_KEY=your_api_key_here" > backend/.env

# 3. Start everything with one command
./start.sh
```

The startup script automatically:
- Checks for required dependencies (Node.js, npm, Python)
- Installs npm packages if needed
- Creates Python virtual environment if it doesn't exist
- Installs Python dependencies
- Starts backend on port 8000
- Starts frontend on port 5173
- Handles graceful shutdown with Ctrl+C

#### Option 2: Manual Setup

**Terminal 1 - Backend:**
```bash
# Create virtual environment (first time only)
python3 -m venv backend/venv

# Activate virtual environment
source backend/venv/bin/activate  # On Windows: backend\venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Create .env file with your API key
echo "GEMINI_API_KEY=your_api_key_here" > backend/.env

# Start backend (run from project root)
PYTHONPATH="${PWD}:${PYTHONPATH}" python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
# Install dependencies (first time only)
npm install

# Start frontend
npm run dev
```

### Access the Application

Once both services are running:

- **Frontend Application**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (interactive Swagger UI)
- **Health Check**: http://localhost:8000/health

**Default Login**: Enter any name to access the workspace (no authentication required)

## Project Architecture

### Technology Stack

**Frontend:**
- React 18 + TypeScript
- Vite (build tool and dev server)
- shadcn/ui component library
- Tailwind CSS
- TanStack Query (data fetching)
- React Router (routing)
- WebSocket (real-time communication)

**Backend:**
- FastAPI (Python web framework)
- Google Gemini API (AI/LLM integration)
- Uvicorn (ASGI server)
- WebSockets (real-time communication)
- Pydantic (data validation)

### Directory Structure

```
bamf-acte-companion/
├── src/                           # Frontend React application
│   ├── components/
│   │   └── workspace/            # Main workspace components
│   │       ├── AIChatInterface.tsx       # AI chat with streaming
│   │       ├── WorkspaceHeader.tsx       # Top navigation bar
│   │       ├── CaseTreeExplorer.tsx      # Document tree sidebar
│   │       ├── DocumentViewer.tsx        # Document display
│   │       ├── FormViewer.tsx            # Case form display
│   │       └── AdminConfigPanel.tsx      # Admin configuration
│   ├── contexts/
│   │   └── AppContext.tsx        # Global app state + WebSocket
│   ├── pages/
│   │   ├── Index.tsx             # Landing/login page
│   │   ├── Workspace.tsx         # Main workspace layout
│   │   └── NotFound.tsx          # 404 page
│   ├── types/
│   │   ├── case.ts               # Case, Document, Folder types
│   │   └── websocket.ts          # WebSocket message types
│   ├── data/
│   │   └── mockData.ts           # Sample data and commands
│   └── lib/
│       └── utils.ts              # Utility functions
│
├── backend/                       # Python FastAPI backend
│   ├── main.py                   # Application entry point
│   ├── requirements.txt          # Python dependencies
│   ├── api/
│   │   └── chat.py              # WebSocket chat endpoint
│   ├── services/
│   │   ├── gemini_service.py    # Gemini AI integration
│   │   └── context_manager.py   # Case context management
│   ├── tools/
│   │   └── form_parser.py       # Form field extraction
│   ├── data/
│   │   └── contexts/            # Case-specific context data
│   │       ├── cases/           # Active case contexts
│   │       │   ├── ACTE-2024-001/  # German Integration Course
│   │       │   ├── ACTE-2024-002/  # Asylum Application
│   │       │   └── ACTE-2024-003/  # Family Reunification
│   │       └── templates/       # Templates for new cases
│   └── venv/                    # Python virtual environment
│
├── docs/                         # Documentation
│   ├── code-graph/              # Architecture documentation
│   │   └── code-graph.json     # Complete system architecture
│   ├── requirements/            # Project requirements
│   │   ├── requirements.md     # Detailed requirements
│   │   ├── implementation_plan.md  # Sprint implementation plan
│   │   └── quick-reference.md  # Quick reference guide
│   ├── apis/                    # API documentation
│   └── tests/                   # Test documentation
│
├── public/
│   └── documents/               # Case document storage
│       ├── ACTE-2024-001/      # Case-specific documents
│       └── templates/          # Document templates
│
├── start.sh                     # Automated startup script
└── package.json                 # Node.js dependencies

```

### Key Features

**Case Management:**
- Multi-case workspace with case switching
- Case-instance scoped data (complete isolation between cases)
- Template-based case creation
- Hierarchical folder structure per case

**AI-Powered Features:**
- Context-aware AI assistant using Google Gemini
- Real-time streaming responses via WebSocket
- Document content analysis and Q&A
- Automatic form field extraction from documents
- Case and folder-specific context injection

**Document Processing:**
- Document tree explorer with drag-and-drop upload
- Text file content loading and display
- Document metadata and type icons
- Case-scoped document storage

**Form Management:**
- Case-level persistent forms
- Auto-fill from document content
- Multiple field types: text, date, select, textarea
- Form data persists across folder navigation

## Development Guide

### Available Commands

**Frontend:**
```bash
npm install              # Install dependencies
npm run dev             # Start dev server (port 5173)
npm run build           # Build for production
npm run build:dev       # Build in development mode
npm run preview         # Preview production build
npm run lint            # Run ESLint
```

**Backend:**
```bash
# Activate venv (from project root)
source backend/venv/bin/activate

# Run backend (from project root)
PYTHONPATH="${PWD}:${PYTHONPATH}" python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Install/update dependencies
pip install -r backend/requirements.txt

# List installed packages
pip list
```

**Startup Script:**
```bash
./start.sh              # Start both frontend and backend
chmod +x start.sh       # Make executable (if needed)
```

### Environment Configuration

Create `backend/.env`:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

**Security Note:** The `.env` file is gitignored. Never commit API keys to the repository.

### WebSocket Communication

The frontend connects to the backend via WebSocket:
- **Endpoint**: `ws://localhost:8000/ws/chat/{caseId}`
- **Protocol**: JSON messages
- **Features**: Streaming responses, form updates, error handling

**Message Types:**
- `chat` - User chat message
- `chat_response` - AI response (non-streaming)
- `chat_chunk` - AI response chunk (streaming)
- `form_update` - Form field updates from extraction
- `system` - System notifications
- `error` - Error messages

### Case-Instance Architecture

All data is scoped to specific case instances (ACTEs):

| Component | Scope | Path Pattern |
|-----------|-------|--------------|
| Context | Per case | `backend/data/contexts/cases/{caseId}/` |
| Documents | Per case | `public/documents/{caseId}/{folderId}/` |
| Forms | Per case | `sampleCaseFormData[caseId]` |
| Folders | Per case | Defined in case folder structure |

**Key Principles:**
- Complete isolation between cases
- Dynamic case creation from templates
- Context switches entirely when changing cases
- No cross-case data contamination

## Troubleshooting

### Connection Error

If frontend shows "Connection Error" or cannot reach backend:

```bash
# Check if backend is running
ps aux | grep uvicorn

# Check backend logs (from project root)
source backend/venv/bin/activate
PYTHONPATH="${PWD}:${PYTHONPATH}" python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Verify .env file exists
cat backend/.env
```

### Port Already in Use

```bash
# Find and kill process on port 5173 (frontend)
lsof -ti:5173 | xargs kill -9

# Find and kill process on port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Alternative: kill by name
pkill -f "vite"
pkill -f "uvicorn"
```

### Python Virtual Environment Issues

```bash
# Remove and recreate venv (from project root)
rm -rf backend/venv
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt
```

### Module Import Errors

```bash
# Ensure project root is in Python path
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# Run backend from project root
source backend/venv/bin/activate
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### API Key Issues

```bash
# Verify .env file location and format
cat backend/.env
# Should show: GEMINI_API_KEY=AIza...

# Test Gemini API key
curl -X GET "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro?key=YOUR_KEY"
```

### WebSocket Connection Failed

Check CORS configuration in `backend/main.py`:
```python
allow_origins=[
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Alternative port
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]
```

### Document Loading Issues

```bash
# Verify document files exist
ls -la public/documents/ACTE-2024-001/

# Check file permissions
chmod 644 public/documents/ACTE-2024-001/*/*.txt
```

## Testing

### Manual Testing Checklist

- [ ] Frontend starts on port 5173
- [ ] Backend starts on port 8000
- [ ] Login with any name works
- [ ] WebSocket connection establishes
- [ ] Case switching works
- [ ] Document tree loads for each case
- [ ] Text file content displays
- [ ] AI chat responds to messages
- [ ] Form fields update from chat
- [ ] Form data persists across folder navigation

### API Testing

Access interactive API docs at http://localhost:8000/docs

Test endpoints:
- GET `/health` - Health check
- GET `/` - Root endpoint
- GET `/api/chat/health` - Chat service health
- WebSocket `/ws/chat/{case_id}` - Chat endpoint

## Documentation

- **Architecture**: [docs/code-graph/code-graph.json](docs/code-graph/code-graph.json)
- **Requirements**: [docs/requirements/requirements.md](docs/requirements/requirements.md)
- **Implementation Plan**: [docs/implementation_plan.md](docs/implementation_plan.md)
- **Quick Reference**: [docs/requirements/quick-reference.md](docs/requirements/quick-reference.md)
- **API Documentation**: Available at http://localhost:8000/docs when running

## Future Work

Based on the implementation plan and current gaps:

### Phase 4 (Not Implemented)
- **F-004**: AI-Powered Form Field Generator for admins
  - Natural language form field creation
  - JSON-LD metadata for fields
  - Admin API endpoint for field generation

### Additional Improvements Needed
1. **PDF Processing**: Implement PDF parsing and text extraction
2. **Document Type Support**: Add DOCX, XML, JSON file processing
3. **Multi-Case Testing**: Comprehensive testing across different case types
4. **Authentication System**: Real user authentication and authorization
5. **Production Deployment**: Docker, CI/CD, environment configuration
6. **Error Handling**: Comprehensive error recovery and user feedback
7. **Internationalization**: German localization for BAMF context
8. **Performance**: Caching, optimization for large documents
9. **Testing Suite**: Automated tests for frontend and backend
10. **Monitoring**: Logging, metrics, alerting for production

## Contributing

This project follows:
- Clean architecture with separation of concerns
- Type-safe TypeScript for frontend
- Python type hints for backend
- WebSocket for real-time communication
- Case-instance scoped data architecture

## License

Proprietary - BAMF Internal Use Only

## Support

For issues or questions:
- Check [Troubleshooting](#troubleshooting) section
- Review [Documentation](#documentation)
- Examine backend logs: Look for errors in the uvicorn output
- Check browser console for frontend errors
- Verify GEMINI_API_KEY is set in `backend/.env`
- Ensure you're running commands from the project root directory
