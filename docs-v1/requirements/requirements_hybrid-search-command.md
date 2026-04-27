# Requirements: Hybrid Search & RAG Slash Commands

## Feature ID: IDIRS-001

## Overview

Two new slash commands for the BAMF ACTE Companion that integrate with the IDIRS OpenSearch API to provide:

1. `/Dokumentsuche` - Hybrid document search (BM25 + kNN) with entity filters
2. `/Dokumente-abfragen` - RAG-based document querying with AI confidence analysis

## Dependencies

- IDIRS OpenSearch API running at configurable `IDIRS_BASE_URL` (default: `http://localhost:8010`)
- Gemini AI Service (existing) for RAG confidence analysis

## Functional Requirements

### FR-001: `/Dokumentsuche` Command

- **Input format**: `/Dokumentsuche [key=value ...] "query"`
- Accepts optional entity filters as `key=value` pairs (e.g. `referenznummer=AKTE-2024-001`)
- Accepts a quoted semantic search query
- Proxies to IDIRS `POST /search` endpoint
- Displays results as a markdown table with document name, type, owner, and relevance score
- Shows "No results found" message when no matches

### FR-002: `/Dokumente-abfragen` Command

- **Input format**: `/Dokumente-abfragen docId1 [docId2...] "question"`
- Accepts one or more document IDs
- Accepts a quoted question
- Proxies to IDIRS `POST /rag` endpoint for each document
- Uses GeminiService to analyze RAG chunks and generate confidence-rated answer
- Confidence calculation: average of non-zero chunk scores (zero-score filler chunks excluded)
- Displays AI analysis with confidence percentage and disclaimer

### FR-003: Confidence Disclaimers

- **Score >= 80%** (configurable via `RAG_CONFIDENCE_THRESHOLD`): Green indicator, "answer well-supported by document evidence"
- **Score < 80%**: Yellow indicator, "answer uncertain, manual document review recommended"

### FR-004: Autocomplete Integration

- Both commands appear in the slash command autocomplete dropdown
- Placeholder hints shown when command is typed without arguments
- Autocomplete suppressed when user is typing arguments

### FR-005: i18n Support

- All user-facing strings available in German (de) and English (en)
- Command descriptions, result labels, error messages, and disclaimers translated
- Language follows current app locale setting

## Non-Functional Requirements

### NFR-001: Backend Proxy Pattern

- Backend proxies IDIRS calls (not direct frontend-to-IDIRS)
- Configurable via environment variables: `IDIRS_BASE_URL`, `IDIRS_TIMEOUT`, `RAG_CONFIDENCE_THRESHOLD`
- Proper error handling for IDIRS connectivity issues (timeout, connection refused)

### NFR-002: REST Pattern

- Uses REST fetch (like `/Aktenkontext`), not WebSocket
- Loading indicator shown during API calls

## API Endpoints

### `POST /api/idirs/search`
- Request: `{ query, entity_filters?, doc_type_filter?, top_k? }`
- Response: IDIRS search results with scores

### `POST /api/idirs/rag`
- Request: `{ doc_ids: string[], question, top_k?, language? }`
- Response: `{ analysis, confidence, is_high_confidence, disclaimer, doc_ids, chunk_count }`

## Configuration

| Variable | Default | Description |
|---|---|---|
| `IDIRS_BASE_URL` | `http://localhost:8010` | IDIRS API base URL |
| `IDIRS_TIMEOUT` | `30` | Request timeout in seconds |
| `RAG_CONFIDENCE_THRESHOLD` | `0.80` | Confidence threshold for high/low classification |
