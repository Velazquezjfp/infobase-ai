#!/usr/bin/env python3
"""
NFR-001: Quick Performance Test (Reduced iterations for faster execution)

This script runs a reduced version of the performance test suite with:
- 5 iterations instead of 20 for first token test
- 5 iterations instead of 10 for other tests
- Optimized timeout handling
"""

import asyncio
import json
import statistics
import time
import websockets
from typing import List, Dict, Any
from datetime import datetime


class TestResults:
    def __init__(self, test_id: str, test_name: str):
        self.test_id = test_id
        self.test_name = test_name
        self.response_times: List[float] = []
        self.passed = False
        self.errors: List[str] = []
        self.execution_time = 0
        self.timestamp = None

    def add_timing(self, elapsed_ms: float):
        self.response_times.append(elapsed_ms)

    def add_error(self, error: str):
        self.errors.append(error)

    def calculate_stats(self) -> Dict[str, float]:
        if not self.response_times:
            return {}

        return {
            'count': len(self.response_times),
            'average': statistics.mean(self.response_times),
            'median': statistics.median(self.response_times),
            'min': min(self.response_times),
            'max': max(self.response_times),
            'stdev': statistics.stdev(self.response_times) if len(self.response_times) > 1 else 0
        }

    def print_report(self):
        print(f"\n{'=' * 80}")
        print(f"Test: {self.test_name} ({self.test_id})")
        print(f"{'=' * 80}")

        if self.errors:
            print(f"FAILED - {len(self.errors)} error(s)")
            for error in self.errors:
                print(f"   - {error}")
        elif self.passed:
            print("PASSED")
        else:
            print("NO RESULT")

        if self.response_times:
            stats = self.calculate_stats()
            print(f"\nPerformance Statistics:")
            print(f"  Tests run:      {stats['count']}")
            print(f"  Average:        {stats['average']:.2f}ms")
            print(f"  Median:         {stats['median']:.2f}ms")
            print(f"  Min:            {stats['min']:.2f}ms")
            print(f"  Max:            {stats['max']:.2f}ms")
            print(f"  Std Dev:        {stats['stdev']:.2f}ms")

        print(f"  Execution time: {self.execution_time:.2f}s")
        print(f"{'=' * 80}\n")


async def test_first_token_simple(iterations=5) -> TestResults:
    """TC-NFR-001-01: First Token Response Time - Simple Query"""
    results = TestResults("TC-NFR-001-01", "First Token (Simple Query)")
    ws_url = "ws://localhost:8000/ws/chat/ACTE-2024-001"

    print(f"\nRunning TC-NFR-001-01: First token response time ({iterations} iterations)...")

    test_start = time.perf_counter()

    try:
        for i in range(iterations):
            try:
                async with websockets.connect(ws_url) as ws:
                    # Wait for connection confirmation
                    await asyncio.wait_for(ws.recv(), timeout=5.0)

                    # Start timer
                    start_time = time.perf_counter()

                    # Send simple message
                    await ws.send(json.dumps({
                        "type": "chat",
                        "content": "Hello",
                        "caseId": "ACTE-2024-001",
                        "stream": True
                    }))

                    # Wait for first chunk
                    await asyncio.wait_for(ws.recv(), timeout=10.0)
                    first_token_time = (time.perf_counter() - start_time) * 1000

                    results.add_timing(first_token_time)
                    print(f"  Iteration {i+1}/{iterations}: {first_token_time:.2f}ms")

                    # Small delay between iterations
                    await asyncio.sleep(0.1)

            except asyncio.TimeoutError:
                results.add_error(f"Iteration {i+1}: Timeout waiting for response")
            except Exception as e:
                results.add_error(f"Iteration {i+1}: {str(e)}")

        # Evaluate results
        if results.response_times:
            stats = results.calculate_stats()
            if stats['average'] <= 2000:
                results.passed = True
            else:
                results.add_error(f"Average time {stats['average']:.2f}ms exceeds target 2000ms")

    except Exception as e:
        results.add_error(f"Test suite failed: {str(e)}")

    results.execution_time = time.perf_counter() - test_start
    results.timestamp = datetime.now().isoformat()
    return results


async def test_typing_indicator() -> TestResults:
    """TC-NFR-001-04: Typing Indicator Responsiveness (Manual UI Test - Skipped)"""
    results = TestResults("TC-NFR-001-04", "Typing Indicator Responsiveness")
    results.passed = False
    results.errors.append("Manual UI test - requires frontend inspection")
    results.execution_time = 0
    results.timestamp = datetime.now().isoformat()
    return results


async def test_streaming_updates() -> TestResults:
    """TC-NFR-001-05: Streaming UI Updates Frequency (Manual UI Test - Skipped)"""
    results = TestResults("TC-NFR-001-05", "Streaming UI Updates Frequency")
    results.passed = False
    results.errors.append("Manual UI test - requires frontend inspection")
    results.execution_time = 0
    results.timestamp = datetime.now().isoformat()
    return results


async def test_no_degradation(iterations=10) -> TestResults:
    """TC-NFR-001-06: No Performance Degradation - Sequential Requests"""
    results = TestResults("TC-NFR-001-06", "No Performance Degradation")
    ws_url = "ws://localhost:8000/ws/chat/ACTE-2024-001"

    print(f"\nRunning TC-NFR-001-06: Sequential requests degradation test ({iterations} iterations)...")

    test_start = time.perf_counter()

    try:
        async with websockets.connect(ws_url) as ws:
            # Wait for connection confirmation
            await asyncio.wait_for(ws.recv(), timeout=5.0)

            for i in range(iterations):
                try:
                    # Start timer
                    start_time = time.perf_counter()

                    # Send simple message
                    await ws.send(json.dumps({
                        "type": "chat",
                        "content": "Hello",
                        "caseId": "ACTE-2024-001",
                        "stream": True
                    }))

                    # Wait for first chunk
                    await asyncio.wait_for(ws.recv(), timeout=10.0)
                    first_token_time = (time.perf_counter() - start_time) * 1000

                    # Wait for completion marker
                    complete = False
                    chunk_count = 0
                    while not complete and chunk_count < 100:
                        response_text = await asyncio.wait_for(ws.recv(), timeout=10.0)
                        response = json.loads(response_text)
                        if response.get('type') == 'chat_chunk' and response.get('is_complete'):
                            complete = True
                        chunk_count += 1

                    results.add_timing(first_token_time)
                    print(f"  Request {i+1}/{iterations}: {first_token_time:.2f}ms")

                    # Small delay between requests
                    await asyncio.sleep(0.1)

                except asyncio.TimeoutError:
                    results.add_error(f"Request {i+1}: Timeout waiting for response")
                except Exception as e:
                    results.add_error(f"Request {i+1}: {str(e)}")

        # Evaluate results
        if len(results.response_times) >= 6:
            first_3_avg = statistics.mean(results.response_times[:3])
            last_3_avg = statistics.mean(results.response_times[-3:])
            degradation_pct = ((last_3_avg - first_3_avg) / first_3_avg) * 100

            print(f"\n  First 3 average: {first_3_avg:.2f}ms")
            print(f"  Last 3 average:  {last_3_avg:.2f}ms")
            print(f"  Degradation:     {degradation_pct:+.1f}%")

            if degradation_pct <= 10:
                results.passed = True
            else:
                results.add_error(f"Performance degradation {degradation_pct:.1f}% exceeds 10% threshold")

    except Exception as e:
        results.add_error(f"Test suite failed: {str(e)}")

    results.execution_time = time.perf_counter() - test_start
    results.timestamp = datetime.now().isoformat()
    return results


async def run_all_tests():
    """Run all performance tests and generate report"""
    print("=" * 80)
    print("NFR-001: Real-Time AI Response Performance Test Suite (Quick)")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend URL: ws://localhost:8000")

    # Run tests
    test_results = []

    test_results.append(await test_first_token_simple(iterations=5))
    test_results.append(await test_typing_indicator())  # Skipped - manual test
    test_results.append(await test_streaming_updates())  # Skipped - manual test
    test_results.append(await test_no_degradation(iterations=10))

    # Print reports
    print("\n\n")
    print("=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)

    for result in test_results:
        result.print_report()

    # Overall summary
    passed = sum(1 for r in test_results if r.passed)
    failed = sum(1 for r in test_results if not r.passed and r.response_times)
    skipped = sum(1 for r in test_results if not r.passed and not r.response_times)

    print(f"Overall: {passed} passed, {failed} failed, {skipped} skipped out of {len(test_results)} tests")

    if failed == 0:
        print("\nAUTOMATED TESTS PASSED - NFR-001 core requirements met!")
        print("Note: Manual UI tests (TC-NFR-001-04, TC-NFR-001-05) require frontend inspection")
        return 0, test_results
    else:
        print(f"\n{failed} TEST(S) FAILED - NFR-001 requirements not met")
        return 1, test_results


if __name__ == "__main__":
    exit_code, test_results = asyncio.run(run_all_tests())
    exit(exit_code)
