# NFR-001 Performance Testing

This directory contains performance test scripts for **NFR-001: Real-Time AI Response Performance**.

## Files

- `test_nfr001_performance.py` - Main performance test script
- `run_performance_tests.sh` - Helper script to run tests and collect results
- `NFR-001_TEST_README.md` - This file

## Prerequisites

1. **Backend Running**: Backend must be running at `http://localhost:8000`
   ```bash
   cd backend
   python3 main.py
   ```

2. **Python Dependencies**:
   ```bash
   pip3 install websockets
   ```

3. **GEMINI_API_KEY**: Must be configured in `backend/.env`

## Running Tests

### Quick Start

```bash
./temp/run_performance_tests.sh
```

This script will:
- Check if backend is running
- Check Python dependencies
- Run all performance tests
- Display results
- Extract metrics from backend logs

### Manual Test Execution

```bash
python3 temp/test_nfr001_performance.py
```

## Tests Included

### TC-NFR-001-01: First Token Response Time (Simple Query)
- **Target**: Average ≤ 2000ms, 95th percentile ≤ 2500ms
- **Iterations**: 20
- **Test**: Send "Hello" message and measure time to first response chunk

### TC-NFR-001-02: Document Summary Performance
- **Target**: Complete response ≤ 10000ms
- **Iterations**: 10
- **Test**: Summarize 500-character document with streaming

### TC-NFR-001-03: Form Auto-Fill Performance
- **Target**: Complete extraction ≤ 5000ms
- **Iterations**: 10
- **Test**: Extract 7 fields from 2000-character document

### TC-NFR-001-06: No Performance Degradation
- **Target**: Degradation ≤ 10% over 10 sequential requests
- **Test**: Compare first 3 vs last 3 requests

## Expected Output

```
================================================================================
NFR-001: Real-Time AI Response Performance Test Suite
================================================================================
Started at: 2025-12-18 12:00:00
Backend URL: ws://localhost:8000

🧪 Running TC-NFR-001-01: First token response time (20 iterations)...
  Iteration 1/20: 1523.45ms
  Iteration 2/20: 1487.23ms
  ...

================================================================================
Test: TC-NFR-001-01: First Token (Simple Query)
================================================================================
✅ PASSED

Performance Statistics:
  Tests run:       20
  Average:         1550.32ms
  Median:          1542.11ms
  Min:             1401.23ms
  Max:             1678.90ms
  Std Dev:         65.43ms
  95th Percentile: 1654.32ms
================================================================================

...

Overall: 4 passed, 0 failed out of 4 tests

✅ ALL TESTS PASSED - NFR-001 requirements met!
```

## Interpreting Results

### Success Criteria

- ✅ **TC-NFR-001-01**: Average ≤ 2000ms, 95th ≤ 2500ms
- ✅ **TC-NFR-001-02**: Average ≤ 10000ms
- ✅ **TC-NFR-001-03**: Average ≤ 5000ms
- ✅ **TC-NFR-001-06**: Degradation ≤ 10%

### Backend Metrics

Check backend logs for detailed metrics:
```bash
# Look for log entries like:
First token received - latency: 1523.45ms, case_id: ACTE-2024-001
Response complete - latency: 3456.78ms, tokens: 150, case_id: ACTE-2024-001
Streaming complete - total_latency: 8234.56ms, first_token_latency: 1523.45ms, tokens: 350
```

## Troubleshooting

### Backend Not Running
```
❌ Backend is not running!
```
**Solution**: Start backend with `cd backend && python3 main.py`

### WebSocket Connection Failed
```
Test failed: [Errno 111] Connection refused
```
**Solution**: Verify backend is listening on port 8000

### Slow Response Times
If tests fail due to slow response times:
1. Check backend logs for errors
2. Verify GEMINI_API_KEY is valid
3. Check network connection
4. Monitor backend CPU/memory usage

### Import Errors
```
ModuleNotFoundError: No module named 'websockets'
```
**Solution**: `pip3 install websockets`

## Next Steps After Testing

1. **Update Test Status**: Mark tests as passed/failed in `docs/tests/non-functional/NFR-001-tests.md`
2. **Document Results**: Add actual timing results to test documentation
3. **Review Logs**: Check backend logs for any warnings or errors
4. **Optimize if Needed**: If tests fail, review streaming implementation

## Additional Tests

The complete NFR-001 test suite includes additional tests not automated here:
- TC-NFR-001-04: Typing Indicator Responsiveness (manual UI test)
- TC-NFR-001-05: Streaming UI Updates Frequency (manual UI test)
- Edge cases (large documents, cold start, etc.)
- Load testing (sustained load, burst load)
- Network condition tests (slow network, high latency)

See `docs/tests/non-functional/NFR-001-tests.md` for the complete test matrix.
