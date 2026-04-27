# NFR-001: Real-Time AI Response Performance

## Test Cases

### TC-NFR-001-01: First Token Response Time - Simple Query

**Type:** Performance
**Priority:** High
**Status:** Pending

**Description:**
Verify that the AI agent delivers the first token of response within 2 seconds for a simple "Hello" message.

**Preconditions:**
- WebSocket connection established
- Backend Gemini service configured with streaming
- Network latency < 100ms

**Test Steps:**
1. Establish WebSocket connection to backend
2. Send simple message: "Hello"
3. Start high-precision timer
4. Wait for first character/token of AI response
5. Stop timer when first content received
6. Record time
7. Repeat test 20 times
8. Calculate statistics (average, median, 95th percentile)

**Expected Results:**
- Average first token time: ≤ 2 seconds
- 95th percentile: ≤ 2.5 seconds
- Maximum time: ≤ 3 seconds
- Consistent performance across tests (low variance)
- No outliers >5 seconds

**Test Data:**
```json
{
  "type": "chat",
  "content": "Hello",
  "caseId": "ACTE-2024-001"
}
```

**Notes:**
- Measure from message send to first character received
- Exclude network latency if testing locally
- Use performance.now() for precise timing

---

### TC-NFR-001-02: Document Summary Response Time

**Type:** Performance
**Priority:** High
**Status:** Pending

**Description:**
Test that document summarization (500 char document + question) delivers first token within 2 seconds and completes within 10 seconds.

**Preconditions:**
- 500-character test document prepared
- Gemini API responsive
- Streaming enabled

**Test Steps:**
1. Prepare document with exactly 500 characters
2. Send summarization request: "Summarize this document"
3. Start timer
4. Measure time to first token
5. Measure time to complete response
6. Record word count of response
7. Repeat 10 times

**Expected Results:**
- First token time: ≤ 2 seconds
- Complete response time: ≤ 10 seconds
- Response length: ~100-200 words (1000 word target)
- Streaming visible (progressive updates)
- No timeouts or errors

**Test Data:**
```json
{
  "type": "chat",
  "content": "Summarize this document",
  "documentContent": "[500 character text about integration course]",
  "caseId": "ACTE-2024-001"
}
```

**Notes:**
- Test with realistic document content
- Verify summary quality not sacrificed for speed

---

### TC-NFR-001-03: Form Auto-Fill Performance

**Type:** Performance
**Priority:** High
**Status:** Pending

**Description:**
Validate that form auto-fill parsing a 2000-character document with 7 fields completes within 5 seconds.

**Preconditions:**
- 2000-character document prepared
- 7-field form schema defined
- Form parser tool operational

**Test Steps:**
1. Prepare birth certificate document (2000 chars exactly)
2. Define form with 7 fields: name, birthDate, placeOfBirth, nationality, passportNumber, passportExpiry, currentAddress
3. Send form fill request
4. Start timer
5. Wait for FormUpdateMessage
6. Stop timer on message received
7. Verify all fields extracted
8. Repeat 10 times

**Expected Results:**
- Average completion time: ≤ 5 seconds
- 95th percentile: ≤ 6 seconds
- All 7 fields extracted successfully
- Extraction accuracy > 95%
- No timeout errors

**Test Data:**
- Document: 2000 character birth certificate
- Fields: 7 mixed types (text, date, textarea)

**Notes:**
- Document should contain data for all 7 fields
- Measure end-to-end time including AI processing

---

### TC-NFR-001-04: Typing Indicator Responsiveness

**Type:** Performance
**Priority:** High
**Status:** Pending

**Description:**
Verify that the typing indicator displays immediately (<100ms) after the user sends a message.

**Preconditions:**
- Frontend typing indicator component implemented
- Indicator triggered on message send

**Test Steps:**
1. Prepare to send message
2. Start high-precision timer
3. Click send button
4. Measure time until typing indicator becomes visible
5. Verify indicator displays before AI response arrives
6. Repeat 20 times

**Expected Results:**
- Typing indicator visible within 100ms of send
- Indicator shows before first AI token
- Indicator remains until response complete
- No flicker or display issues
- Smooth user experience

**Test Data:**
N/A (UI timing test)

**Notes:**
- Use browser performance API
- Test on various devices/browsers

---

### TC-NFR-001-05: Streaming UI Updates Frequency

**Type:** Performance
**Priority:** Medium
**Status:** Pending

**Description:**
Monitor streaming response to ensure UI updates at least every 500ms during AI response generation.

**Preconditions:**
- Streaming responses implemented
- Frontend handles partial content updates
- Long-form response expected

**Test Steps:**
1. Send request expecting long response (summary of 2000-char document)
2. Monitor WebSocket messages
3. Track timing of each content update
4. Calculate intervals between updates
5. Count total updates during response generation
6. Measure maximum gap between updates

**Expected Results:**
- UI updates at least every 500ms
- Average update interval: 200-400ms
- Maximum gap: ≤ 1 second
- Smooth streaming appearance
- No long pauses during generation
- Minimum 10 updates for 1000-word response

**Test Data:**
- Request producing 1000+ word response

**Notes:**
- Visual smoothness important for UX
- Too frequent updates (< 50ms) may cause flicker

---

### TC-NFR-001-06: No Performance Degradation - Sequential Requests

**Type:** Performance
**Priority:** High
**Status:** Pending

**Description:**
Test that sending 10 sequential requests shows no significant performance degradation over time.

**Preconditions:**
- Fresh backend session
- No rate limiting enabled
- Clean memory state

**Test Steps:**
1. Send 10 identical "Hello" messages sequentially
2. Measure response time for each
3. Calculate:
   - Average of first 3 requests
   - Average of last 3 requests
   - Overall average
   - Trend line
4. Check for memory leaks
5. Monitor backend resource usage

**Expected Results:**
- Response time increase ≤ 10% from first to last
- Average time consistent (±0.5 seconds)
- No memory leaks detected
- Backend memory stable
- CPU usage returns to baseline between requests
- No connection pool exhaustion

**Test Data:**
- 10 identical requests: `{"type": "chat", "content": "Hello"}`

**Notes:**
- Check garbage collection in backend
- Monitor connection pooling

---

## Edge Cases

### TC-NFR-001-E01: Large Document Summary Performance

**Type:** Performance
**Priority:** Medium
**Status:** Pending

**Description:**
Test performance with maximum size document (5000+ characters).

**Test Steps:**
1. Prepare 5000-character document
2. Request summary
3. Measure response times
4. Verify no timeout

**Expected Results:**
- First token: ≤ 3 seconds (relaxed for large doc)
- Complete response: ≤ 20 seconds
- No timeout errors
- Quality maintained

**Notes:**
- Document size limit for production: 10,000 chars

---

### TC-NFR-001-E02: Concurrent Requests Impact (Future)

**Type:** Performance
**Priority:** Low
**Status:** Deferred (POC single user)

**Description:**
Test performance impact of concurrent users (post-POC).

**Notes:**
- Deferred to multi-user phase
- Not required for POC

---

### TC-NFR-001-E03: Cold Start Performance

**Type:** Performance
**Priority:** Medium
**Status:** Pending

**Description:**
Measure first request after backend restart (cold start).

**Test Steps:**
1. Restart backend server
2. Wait for startup complete
3. Immediately send first request
4. Measure response time
5. Compare with warm requests

**Expected Results:**
- Cold start time: ≤ 5 seconds
- Warm up after first request
- Subsequent requests meet normal SLA
- User informed if initialization delay expected

---

## Performance Under Load

### TC-NFR-001-LOAD01: Sustained Load - 50 Sequential Requests

**Type:** Performance
**Priority:** Medium
**Status:** Pending

**Description:**
Test sustained performance over 50 sequential requests.

**Test Steps:**
1. Send 50 requests over 5 minutes (one every 6 seconds)
2. Measure each response time
3. Track backend metrics (CPU, memory, connections)
4. Identify any degradation patterns

**Expected Results:**
- All requests complete successfully
- Average response time stable
- No memory leaks over duration
- Backend remains responsive
- Error rate: 0%

**Notes:**
- Simulates active user session
- Monitor for resource exhaustion

---

### TC-NFR-001-LOAD02: Burst Load - 5 Rapid Requests

**Type:** Performance
**Priority:** Medium
**Status:** Pending

**Description:**
Test handling of burst: 5 requests sent within 1 second.

**Test Steps:**
1. Send 5 requests as fast as possible
2. Measure response time for each
3. Check request queuing
4. Verify all responses received

**Expected Results:**
- All 5 requests processed
- Response times: first ≤ 2s, others ≤ 4s (queued)
- No requests dropped
- Appropriate queuing behavior
- No backend crash

**Notes:**
- Tests Gemini API rate limiting handling
- Verify graceful queue management

---

## Network Conditions

### TC-NFR-001-NET01: Performance on Slow Network

**Type:** Performance
**Priority:** Medium
**Status:** Pending

**Description:**
Test streaming performance with simulated slow network (3G speed).

**Test Steps:**
1. Enable network throttling (3G: 400ms latency, 400kbps)
2. Send chat request
3. Measure first token and complete response times
4. Observe streaming behavior

**Expected Results:**
- First token arrives within adjusted time (4 seconds accounting for latency)
- Streaming still visible and functional
- No timeouts
- User experience acceptable
- Progress indicators help manage expectations

**Notes:**
- Use browser DevTools network throttling
- Test various network conditions

---

### TC-NFR-001-NET02: Performance on High Latency Network

**Type:** Performance
**Priority:** Low
**Status:** Pending

**Description:**
Test with high latency (500ms RTT) network.

**Test Steps:**
1. Simulate 500ms latency
2. Send requests
3. Measure performance impact

**Expected Results:**
- Latency impact understood and compensated
- WebSocket remains stable
- Streaming functional
- Timeout values appropriate

---

## Optimization Verification

### TC-NFR-001-OPT01: Connection Pooling Effectiveness

**Type:** Performance
**Priority:** Medium
**Status:** Pending

**Description:**
Verify Gemini API connection pooling improves performance.

**Test Steps:**
1. Measure first request time (new connection)
2. Measure second request time (pooled connection)
3. Calculate improvement
4. Verify connection reuse

**Expected Results:**
- Second request faster (pool reuse)
- Connection overhead reduced
- Pool size appropriate (1-3 for POC)
- Connections cleaned up properly

**Notes:**
- Monitor connection pool metrics
- Verify singleton pattern for Gemini client

---

### TC-NFR-001-OPT02: Streaming vs. Batch Comparison

**Type:** Performance
**Priority:** Low
**Status:** Pending

**Description:**
Compare streaming vs. batch response perception (if both modes available).

**Test Steps:**
1. Request with streaming enabled
2. Request with streaming disabled (batch)
3. Measure time to first content displayed
4. Assess perceived responsiveness

**Expected Results:**
- Streaming first content: ~2 seconds
- Batch first content: ~8-10 seconds
- Streaming perceived as significantly faster
- User preference for streaming

**Notes:**
- Streaming requirement validated
- Perceived performance often more important than actual

---

## Timeout Configuration

### TC-NFR-001-TIME01: Gemini API Timeout Setting

**Type:** Unit
**Priority:** High
**Status:** Pending

**Description:**
Verify Gemini API timeout set to 30 seconds as specified.

**Test Steps:**
1. Inspect gemini_service.py code
2. Verify request_timeout parameter
3. Trigger timeout scenario
4. Verify timeout occurs at 30 seconds

**Expected Results:**
- Timeout parameter: request_timeout=30
- Timeout error raised at 30 seconds
- Error handled gracefully
- User notified appropriately

**Notes:**
- 30 seconds allows complex operations
- Prevents indefinite hangs

---

### TC-NFR-001-TIME02: WebSocket Timeout Handling

**Type:** Integration
**Priority:** Medium
**Status:** Pending

**Description:**
Test WebSocket behavior when request exceeds timeout.

**Test Steps:**
1. Send request expected to take >30 seconds
2. Wait for timeout
3. Verify error handling
4. Check connection state

**Expected Results:**
- Timeout error after 30 seconds
- User notified: "Request timed out"
- WebSocket connection remains open
- User can retry
- No zombie requests

---

## Monitoring and Metrics

### TC-NFR-001-MON01: Response Timing Metrics Logging

**Type:** Unit
**Priority:** Medium
**Status:** Pending

**Description:**
Verify backend logs response timing metrics as specified.

**Test Steps:**
1. Send various requests
2. Check backend logs
3. Verify logged metrics

**Expected Results:**
- Logs include:
  - Response start time
  - Response end time
  - Token count
  - Latency (ms)
- Structured logging format
- Metrics usable for monitoring

**Notes:**
- Enables performance monitoring in production
- Foundation for alerting

---

## Automated Test Implementation

### Performance Test Script (Python)

**File:** `backend/tests/performance/test_response_times.py`

```python
import pytest
import time
import statistics
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture
def ws_client():
    client = TestClient(app)
    return client

def test_first_token_response_time(ws_client):
    """Test first token arrives within 2 seconds"""
    response_times = []

    for _ in range(20):
        start = time.perf_counter()

        with ws_client.websocket_connect("/ws/chat/ACTE-2024-001") as ws:
            ws.send_json({"type": "chat", "content": "Hello"})
            first_data = ws.receive_json()

        first_token_time = time.perf_counter() - start
        response_times.append(first_token_time)

    avg_time = statistics.mean(response_times)
    percentile_95 = statistics.quantiles(response_times, n=20)[18]

    assert avg_time <= 2.0, f"Average first token time {avg_time}s exceeds 2s"
    assert percentile_95 <= 2.5, f"95th percentile {percentile_95}s exceeds 2.5s"

def test_document_summary_performance(ws_client):
    """Test document summary completes within 10 seconds"""
    document = "A" * 500  # 500 character document

    start = time.perf_counter()

    with ws_client.websocket_connect("/ws/chat/ACTE-2024-001") as ws:
        ws.send_json({
            "type": "chat",
            "content": "Summarize this document",
            "documentContent": document
        })

        # Wait for complete response
        response = ws.receive_json()
        while response.get("type") == "stream_chunk":
            response = ws.receive_json()

    total_time = time.perf_counter() - start

    assert total_time <= 10.0, f"Summary took {total_time}s, exceeds 10s limit"

def test_form_autofill_performance(ws_client):
    """Test form auto-fill completes within 5 seconds"""
    document = "Name: John Doe\n" * 100  # 2000+ characters
    form_fields = [
        {"id": "name", "type": "text"},
        {"id": "birthDate", "type": "date"},
        # ... 5 more fields
    ]

    start = time.perf_counter()

    with ws_client.websocket_connect("/ws/chat/ACTE-2024-001") as ws:
        ws.send_json({
            "type": "chat",
            "content": "/fillForm",
            "documentContent": document,
            "formFields": form_fields
        })

        response = ws.receive_json()

    elapsed = time.perf_counter() - start

    assert elapsed <= 5.0, f"Form fill took {elapsed}s, exceeds 5s limit"
    assert response["type"] == "form_update"
```

---

## Test Summary

| Category | Total Tests | High Priority | Medium Priority | Low Priority |
|----------|-------------|---------------|-----------------|--------------|
| Performance | 6 | 5 | 1 | 0 |
| Edge Cases | 3 | 0 | 2 | 1 |
| Load Testing | 2 | 0 | 2 | 0 |
| Network | 2 | 0 | 1 | 1 |
| Optimization | 2 | 0 | 1 | 1 |
| Timeout | 2 | 1 | 1 | 0 |
| Monitoring | 1 | 0 | 1 | 0 |
| **Total** | **18** | **6** | **9** | **3** |

---

## Performance Benchmarks Summary

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| First token (simple) | ≤ 2s | WebSocket receive timing |
| First token (with doc) | ≤ 2s | With 500-char document |
| Full summary | ≤ 10s | 1000-word response complete |
| Form auto-fill | ≤ 5s | 2000-char doc, 7 fields |
| Typing indicator | ≤ 100ms | UI update timing |
| Streaming interval | every 500ms | Update frequency |
| Sequential degradation | ≤ 10% | 10 requests comparison |

---

## Test Execution Checklist

- [ ] Streaming responses implemented
- [ ] Connection pooling configured
- [ ] Timeout parameters set (30s)
- [ ] Response metrics logging active
- [ ] Performance monitoring tools ready
- [ ] Test environment matches production specs
- [ ] Baseline measurements recorded
- [ ] All performance tests passing
- [ ] Optimization opportunities identified
- [ ] Results documented and reviewed
