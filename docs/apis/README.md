# BAMF ACTE Companion - API Documentation

## Overview

This directory contains API documentation for the BAMF ACTE Companion application. The application is a Vite + React + TypeScript frontend application with shadcn/ui components.

## Current Architecture

**Status:** Frontend-Only Application with Simulated APIs

The BAMF ACTE Companion is currently a **frontend-only prototype** that simulates AI and backend functionality using:
- Mock data patterns (see `src/data/mockData.ts`)
- Simulated async operations with setTimeout
- Client-side state management via React Context
- @tanstack/react-query setup (ready for future API integration)

### Key Components

- **State Management:** AppContext (`src/contexts/AppContext.tsx`)
- **Mock Data:** `src/data/mockData.ts`
- **AI Simulation:** `src/components/workspace/AIChatInterface.tsx`
- **Query Client:** Configured in `src/App.tsx` (ready for future use)

## Documentation Structure

### 1. **openapi.yaml / openapi.json**
OpenAPI 3.0 specifications documenting the **planned future API** that will replace the current simulated operations.

### 2. **endpoints.md**
Detailed endpoint reference including:
- Current simulated AI operations (slash commands)
- Planned future backend API endpoints
- Request/response formats
- Usage examples

### 3. **authentication.md**
Authentication and authorization documentation:
- Current: Simple client-side username storage
- Planned: Token-based authentication strategy

### 4. **api-changelog.md**
Chronological record of API documentation changes and architectural evolution.

### 5. **.last-sync.json**
Internal tracking file for documentation synchronization with codebase changes.

## Simulated API Operations

The application currently simulates these operations via the AI chat interface:

### Document Operations
- `/convert` - Convert document formats (PDF, JSON, XML)
- `/translate` - Translate documents to German
- `/anonymize` - Redact personal data from documents
- `/extractMetadata` - Extract document metadata

### Search & Discovery
- `/search` - Search across case documents
- `/validateCase` - Check for missing required documents

### Case Management
- `/addDocument` - Upload new document to case
- `/switchCase` - Switch between cases
- `/changeActeName` - Rename case

### Communication
- `/generateEmail` - Generate notification emails
- `/transcribe` - Extract text from documents

All these operations are **simulated client-side** and will be replaced with actual API calls in future iterations.

## Future API Architecture

The documentation in this directory describes the **target API architecture** that will:

1. Replace simulated operations with real backend endpoints
2. Integrate with BAMF systems for document processing
3. Provide secure authentication and authorization
4. Support real-time AI operations via WebSocket or Server-Sent Events
5. Handle file uploads and conversions on the server

## Technology Stack

### Current
- React 18.3
- TypeScript 5.8
- Vite 5.4
- React Router 6.30
- @tanstack/react-query 5.83 (configured, not yet used for API calls)
- shadcn/ui components

### Planned Backend (for API implementation)
To be determined based on BAMF infrastructure requirements.

## Development Notes

When transitioning from simulated to real APIs:
1. Replace mock data imports with API service calls
2. Utilize the configured QueryClient for data fetching
3. Replace setTimeout simulations with actual async API calls
4. Implement proper error handling and loading states
5. Add API authentication headers to all requests

## Related Documentation

- [Code Graph](/docs/code-graph/code-graph.json) - Application structure analysis
- [Types Definition](/src/types/case.ts) - TypeScript interfaces for Case, Document, Folder, etc.
- [Mock Data](/src/data/mockData.ts) - Current data structures and simulated responses

---

**Last Updated:** 2025-12-16
**Documentation Version:** 1.0.0
**Application Version:** 0.0.0
