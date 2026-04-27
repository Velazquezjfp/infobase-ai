# F-001: Document Assistant Agent - Backend WebSocket Service (Case-Scoped)

## Test Cases

### TC-F-001-01: Basic WebSocket Connection and Response

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Verify that the WebSocket connection can be established successfully and the AI agent responds to a simple greeting message within acceptable time limits.

**Preconditions:**
- Backend server running on localhost:8000
- GEMINI_API_KEY configured in .env file
- Frontend WebSocket client ready

**Test Steps:**
1. Establish WebSocket connection to `ws://localhost:8000/ws/chat/ACTE-2024-001`
2. Wait for connection confirmation
3. Send message: `{"type": "chat", "content": "Hello", "caseId": "ACTE-2024-001"}`
4. Start timer
5. Wait for response message
6. Record response time and content

**Expected Results:**
- WebSocket connection established successfully (status code 101)
- Response received within 3 seconds
- Response contains AI-generated greeting message
- Response format: `{"type": "chat_response", "content": "...", "timestamp": "..."}`

**Test Data:**
```json
{
  "type": "chat",
  "content": "Hello",
  "caseId": "ACTE-2024-001"
}
```

**Notes:**
- Monitor for WebSocket errors in browser console
- Check backend logs for Gemini API call timing

---

### TC-F-001-02: Document Summarization

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Verify that the AI agent can receive document content and provide an accurate summary when prompted with a question.

**Preconditions:**
- WebSocket connection established
- Test document with 500+ characters prepared
- Gemini API accessible

**Test Steps:**
1. Prepare document text (500 characters about integration course application)
2. Send message with document content and question: "What is this about?"
3. Wait for response
4. Validate response contains summary

**Expected Results:**
- Response received within 10 seconds
- Summary accurately reflects document content
- Summary is concise (under 200 words)
- Response includes key information from document

**Test Data:**
```json
{
  "type": "chat",
  "content": "What is this about?",
  "documentContent": "Application for Integration Course...[500 chars]",
  "caseId": "ACTE-2024-001"
}
```

**Notes:**
- Compare summary accuracy manually
- Verify German text in document is understood correctly

---

### TC-F-001-03: German to English Translation

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Validate the AI agent's ability to translate German document content into English upon request.

**Preconditions:**
- WebSocket connection active
- German text sample prepared

**Test Steps:**
1. Select document containing German text
2. Send command: "Translate to English"
3. Include German document content in message
4. Wait for translated response
5. Verify translation accuracy

**Expected Results:**
- Translation received within 5 seconds
- German text accurately translated to English
- Translation maintains original meaning
- Special characters (ä, ö, ü, ß) handled correctly

**Test Data:**
```json
{
  "type": "chat",
  "content": "Translate to English",
  "documentContent": "Geburtsurkunde: Ahmad Ali, Geboren: 15.05.1990 in Kabul, Afghanistan",
  "caseId": "ACTE-2024-001"
}
```

**Notes:**
- Manual verification of translation quality required
- Test with umlauts and special German characters

---

### TC-F-001-04: Form Field Auto-Fill via FormUpdateMessage

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Test the agent's ability to extract structured data from documents and send form field updates to the frontend.

**Preconditions:**
- WebSocket connection established
- Document containing name "John Doe" loaded
- Form schema with name field available in AppContext

**Test Steps:**
1. Load document with text: "Name: John Doe, Date of Birth: 15.05.1990"
2. Send instruction: "Fill the form"
3. Include current form schema in message
4. Wait for FormUpdateMessage response
5. Verify name field populated

**Expected Results:**
- FormUpdateMessage received within 5 seconds
- Response type: "form_update"
- Updates object contains: `{"name": "John Doe"}`
- Frontend formFields state updated with correct value

**Test Data:**
```json
{
  "type": "chat",
  "content": "Fill the form",
  "documentContent": "Name: John Doe\nDate of Birth: 15.05.1990",
  "formSchema": [{"id": "name", "label": "Full Name", "type": "text"}],
  "caseId": "ACTE-2024-001"
}
```

**Notes:**
- Test with various document formats
- Verify confidence scores for extracted values

---

### TC-F-001-05: Case Switching via WebSocket

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Test that switching cases requires establishing a new WebSocket connection to the new case's endpoint, and that context switches appropriately.

**Preconditions:**
- Multiple cases exist: ACTE-2024-001, ACTE-2024-002
- Backend WebSocket server running
- Each case has its own context

**Test Steps:**
1. Establish WebSocket connection to `ws://localhost:8000/ws/chat/ACTE-2024-001`
2. Send message: "What type of case is this?"
3. Verify response mentions Integration Course (from ACTE-2024-001 context)
4. Close connection to ACTE-2024-001
5. Establish new WebSocket connection to `ws://localhost:8000/ws/chat/ACTE-2024-002`
6. Send same message: "What type of case is this?"
7. Verify response mentions Asylum Application (from ACTE-2024-002 context)
8. Verify context switched completely

**Expected Results:**
- Each WebSocket endpoint serves only its own case's context
- Cannot access ACTE-2024-002 context via ACTE-2024-001 endpoint
- AI responses reflect active case's context
- No context contamination between cases
- Clean context switch when changing WebSocket endpoints

**Test Data:**
```json
// Connection 1
ws://localhost:8000/ws/chat/ACTE-2024-001
{"type": "chat", "content": "What type of case is this?", "caseId": "ACTE-2024-001"}

// Connection 2
ws://localhost:8000/ws/chat/ACTE-2024-002
{"type": "chat", "content": "What type of case is this?", "caseId": "ACTE-2024-002"}
```

**Notes:**
- Critical test for case isolation at WebSocket level
- Verify backend maintains separate context per connection
- Each WebSocket URL must include case ID

---

### TC-F-001-06: WebSocket Connection Cleanup

**Type:** Unit
**Priority:** Medium
**Status:** Pending

**Description:**
Ensure proper cleanup when WebSocket connection is closed, preventing memory leaks and resource exhaustion.

**Preconditions:**
- WebSocket connection established and active
- Active conversation with message history

**Test Steps:**
1. Establish WebSocket connection
2. Send 3-5 messages and receive responses
3. Close connection (call `ws.close()`)
4. Monitor backend for cleanup
5. Check for memory leaks (Python garbage collection)
6. Attempt to send message after close

**Expected Results:**
- Connection closed cleanly without errors
- Backend releases resources (Gemini client connections)
- No memory leaks detected
- Attempt to send after close results in appropriate error
- Frontend handles disconnection gracefully

**Test Data:**
N/A

**Notes:**
- Use memory profiler to detect leaks
- Check WebSocket close code (1000 = normal closure)

---

### TC-F-001-06: Missing API Key Error Handling

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Verify graceful error handling when GEMINI_API_KEY is not configured or invalid.

**Preconditions:**
- Backend started without GEMINI_API_KEY in .env
- OR invalid API key configured

**Test Steps:**
1. Remove or comment out GEMINI_API_KEY from .env
2. Restart backend server
3. Attempt to establish WebSocket connection
4. Send chat message
5. Observe error response

**Expected Results:**
- Connection establishes but initialization fails
- Error message received: "API key not configured"
- Error response format: `{"type": "error", "message": "API key not configured"}`
- Backend logs error appropriately
- No application crash

**Test Data:**
```json
{
  "type": "chat",
  "content": "Hello",
  "caseId": "ACTE-2024-001"
}
```

**Notes:**
- Test both missing and invalid API keys
- Verify user-friendly error message

---

### TC-F-001-07: Rapid Message Handling

**Type:** Integration
**Priority:** Medium
**Status:** Pending

**Description:**
Test the system's ability to handle multiple rapid messages and maintain correct message ordering.

**Preconditions:**
- WebSocket connection established
- No rate limiting configured (POC phase)

**Test Steps:**
1. Connect to WebSocket
2. Send 3 messages in rapid succession (< 500ms apart):
   - Message 1: "What is your name?"
   - Message 2: "Summarize this document"
   - Message 3: "Translate to German"
3. Wait for all responses
4. Verify response order matches request order
5. Check all responses received

**Expected Results:**
- All 3 messages sent successfully
- All 3 responses received
- Response order matches request order (FIFO)
- No messages lost or duplicated
- Each response corresponds to correct request

**Test Data:**
```json
[
  {"type": "chat", "content": "What is your name?", "caseId": "ACTE-2024-001"},
  {"type": "chat", "content": "Summarize this document", "documentContent": "...", "caseId": "ACTE-2024-001"},
  {"type": "chat", "content": "Translate to German", "documentContent": "...", "caseId": "ACTE-2024-001"}
]
```

**Notes:**
- Monitor for race conditions
- Verify message IDs if implemented

---

## Edge Cases

### TC-F-001-E01: Empty Message Handling

**Type:** Unit
**Priority:** Low
**Status:** Pending

**Description:**
Test behavior when empty or whitespace-only messages are sent.

**Test Steps:**
1. Send message with empty string: `{"type": "chat", "content": ""}`
2. Send message with whitespace only: `{"type": "chat", "content": "   "}`
3. Verify appropriate error or default response

**Expected Results:**
- Error message: "Message content cannot be empty"
- OR default response: "How can I help you?"

---

### TC-F-001-E02: Very Long Document Content

**Type:** Performance
**Priority:** Medium
**Status:** Pending

**Description:**
Test handling of large documents exceeding typical size.

**Test Steps:**
1. Prepare document with 10,000+ characters
2. Send summarization request with large document
3. Monitor response time and accuracy
4. Check for timeouts or truncation

**Expected Results:**
- Response received within 30 seconds (extended timeout)
- Summary still accurate despite document size
- No content truncation without warning
- OR appropriate error if document too large

---

### TC-F-001-E03: Special Characters in Content

**Type:** Unit
**Priority:** Medium
**Status:** Pending

**Description:**
Verify handling of special characters, emojis, and non-Latin scripts.

**Test Steps:**
1. Send message with emojis: "This is great! 😊"
2. Send message with Arabic script
3. Send message with special characters: `<>&"'`
4. Verify all characters preserved correctly

**Expected Results:**
- All special characters preserved in response
- No encoding errors or character corruption
- JSON escaping handled correctly

---

## Error Handling Tests

### TC-F-001-ERR01: Network Interruption

**Type:** Integration
**Priority:** High
**Status:** Pending

**Description:**
Simulate network interruption during active conversation.

**Test Steps:**
1. Establish connection and send message
2. Simulate network disconnection (disable WiFi)
3. Attempt to send another message
4. Restore network
5. Attempt to reconnect

**Expected Results:**
- Frontend detects disconnection
- User notified of connection loss
- Reconnection attempt successful
- No data loss for completed messages

---

### TC-F-001-ERR02: Gemini API Rate Limit

**Type:** Integration
**Priority:** Medium
**Status:** Pending

**Description:**
Handle Gemini API rate limit errors gracefully.

**Test Steps:**
1. Send messages rapidly to trigger rate limit
2. Observe API error response
3. Verify error handling and user notification

**Expected Results:**
- Error caught and logged
- User receives friendly error: "Service temporarily busy, please try again"
- No application crash
- Retry mechanism suggested

---

### TC-F-001-ERR03: Invalid JSON Message Format

**Type:** Unit
**Priority:** Medium
**Status:** Pending

**Description:**
Test backend validation of WebSocket message format.

**Test Steps:**
1. Send malformed JSON: `{invalid json}`
2. Send JSON missing required fields: `{"type": "chat"}`
3. Send JSON with wrong field types: `{"type": 123}`

**Expected Results:**
- Validation error returned for each case
- Error message describes validation failure
- Connection remains open for retry
- Backend logs validation errors

---

## Performance Tests

### TC-F-001-PERF01: Response Time Under Load

**Type:** Performance
**Priority:** Medium
**Status:** Pending

**Description:**
Measure response times across multiple sequential requests.

**Test Steps:**
1. Send 10 sequential messages
2. Measure response time for each
3. Calculate average, min, max response times
4. Verify no performance degradation

**Expected Results:**
- Average response time < 3 seconds
- No significant increase in response time for later messages
- All responses complete successfully

---

### TC-F-001-PERF02: Concurrent Connections (Future)

**Type:** Performance
**Priority:** Low
**Status:** Deferred (Not required for POC)

**Description:**
Test handling of multiple concurrent WebSocket connections.

**Notes:**
- Deferred to post-POC phase
- Single user assumption for POC

---

## Automated Test Implementation

### Backend Unit Tests (Python/pytest)

**File:** `backend/tests/test_websocket_chat.py`

```python
import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_websocket_connection(client):
    with client.websocket_connect("/ws/chat/ACTE-2024-001") as websocket:
        websocket.send_json({"type": "chat", "content": "Hello"})
        data = websocket.receive_json()
        assert data["type"] == "chat_response"
        assert "content" in data
```

### Frontend Integration Tests (Playwright)

**File:** `tests/e2e/websocket-chat.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test('AI chat responds to messages', async ({ page }) => {
  await page.goto('http://localhost:5173');

  // Open AI chat interface
  await page.click('[data-testid="ai-chat-toggle"]');

  // Send message
  await page.fill('[data-testid="chat-input"]', 'Hello');
  await page.click('[data-testid="chat-send"]');

  // Wait for response
  await page.waitForSelector('[data-testid="ai-response"]', { timeout: 5000 });

  const response = await page.textContent('[data-testid="ai-response"]');
  expect(response).toBeTruthy();
  expect(response.length).toBeGreaterThan(0);
});
```

---

## Test Summary

| Category | Total Tests | High Priority | Medium Priority | Low Priority |
|----------|-------------|---------------|-----------------|--------------|
| Integration | 4 | 4 | 0 | 0 |
| Unit | 2 | 1 | 1 | 0 |
| Performance | 1 | 0 | 1 | 0 |
| Edge Cases | 3 | 0 | 2 | 1 |
| Error Handling | 3 | 1 | 2 | 0 |
| **Total** | **13** | **6** | **6** | **1** |

---

## Test Execution Checklist

- [ ] All preconditions met (server running, API key configured)
- [ ] Test data files created and accessible
- [ ] Automated tests written and passing
- [ ] Manual test procedures documented
- [ ] Performance benchmarks recorded
- [ ] Error handling verified
- [ ] Test results documented
- [ ] Known issues logged
