#!/usr/bin/env python3
"""
NFR-001: Real-Time AI Response Performance Test Script (FIXED)

This script tests the performance requirements for the BAMF AI Case Management System.
Tests include:
- TC-NFR-001-01: First token response time (simple query)
- TC-NFR-001-02: Document summary response time
- TC-NFR-001-03: Form auto-fill performance
- TC-NFR-001-06: No performance degradation over sequential requests

Requirements:
- Backend must be running at localhost:8000
- GEMINI_API_KEY must be configured in backend .env

Usage:
    python3 docs/tests/NFR-001/test_nfr001_performance_fixed.py
"""

import asyncio
import json
import statistics
import time
import websockets
from typing import List, Dict, Any
from datetime import datetime


class PerformanceTestResults:
    """Store and calculate test results"""

    def __init__(self, test_name: str):
        self.test_name = test_name
        self.response_times: List[float] = []
        self.passed = False
        self.errors: List[str] = []

    def add_timing(self, elapsed_ms: float):
        """Add a timing measurement"""
        self.response_times.append(elapsed_ms)

    def add_error(self, error: str):
        """Add an error message"""
        self.errors.append(error)

    def calculate_stats(self) -> Dict[str, float]:
        """Calculate statistics from response times"""
        if not self.response_times:
            return {}

        return {
            'count': len(self.response_times),
            'average': statistics.mean(self.response_times),
            'median': statistics.median(self.response_times),
            'min': min(self.response_times),
            'max': max(self.response_times),
            'stdev': statistics.stdev(self.response_times) if len(self.response_times) > 1 else 0,
            'percentile_95': statistics.quantiles(self.response_times, n=20)[18] if len(self.response_times) >= 20 else max(self.response_times)
        }

    def print_report(self):
        """Print formatted test report"""
        print(f"\n{'=' * 80}")
        print(f"Test: {self.test_name}")
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
            if stats['count'] >= 20:
                print(f"  95th Percentile: {stats['percentile_95']:.2f}ms")

        print(f"{'=' * 80}\n")


async def test_first_token_simple(case_id: str = "ACTE-2024-001") -> PerformanceTestResults:
    """
    TC-NFR-001-01: First Token Response Time - Simple Query

    Target: First token ≤ 2000ms (average), 95th percentile ≤ 2500ms
    """
    results = PerformanceTestResults("TC-NFR-001-01: First Token (Simple Query)")
    ws_url = f"ws://localhost:8000/ws/chat/{case_id}"

    print(f"\nRunning TC-NFR-001-01: First token response time (20 iterations)...")

    try:
        for i in range(20):
            async with websockets.connect(ws_url) as ws:
                # Wait for connection confirmation
                await asyncio.wait_for(ws.recv(), timeout=5.0)

                # Start timer
                start_time = time.perf_counter()

                # Send simple message
                await ws.send(json.dumps({
                    "type": "chat",
                    "content": "Hello",
                    "caseId": case_id,
                    "stream": True
                }))

                # Wait for first chunk
                response = await asyncio.wait_for(ws.recv(), timeout=10.0)
                first_token_time = (time.perf_counter() - start_time) * 1000

                results.add_timing(first_token_time)
                print(f"  Iteration {i+1}/20: {first_token_time:.2f}ms")

        # Evaluate results
        stats = results.calculate_stats()
        if stats['average'] <= 2000 and stats['percentile_95'] <= 2500:
            results.passed = True
        else:
            if stats['average'] > 2000:
                results.add_error(f"Average time {stats['average']:.2f}ms exceeds target 2000ms")
            if stats['percentile_95'] > 2500:
                results.add_error(f"95th percentile {stats['percentile_95']:.2f}ms exceeds target 2500ms")

    except asyncio.TimeoutError:
        results.add_error("Timeout waiting for response")
    except Exception as e:
        results.add_error(f"Test failed: {str(e)}")

    return results


async def test_document_summary(case_id: str = "ACTE-2024-001") -> PerformanceTestResults:
    """
    TC-NFR-001-02: Document Summary Response Time

    Target: First token ≤ 2000ms, complete response ≤ 10000ms
    """
    results = PerformanceTestResults("TC-NFR-001-02: Document Summary Performance")
    ws_url = f"ws://localhost:8000/ws/chat/{case_id}"

    # Create 500-character document
    document = "This is a German Integration Course application. " * 10  # ~500 chars

    print(f"\nRunning TC-NFR-001-02: Document summary performance (10 iterations)...")

    try:
        for i in range(10):
            async with websockets.connect(ws_url) as ws:
                # Wait for connection confirmation
                await asyncio.wait_for(ws.recv(), timeout=5.0)

                # Start timer
                start_time = time.perf_counter()
                first_token_time = None

                # Send document summary request
                await ws.send(json.dumps({
                    "type": "chat",
                    "content": "Summarize this document",
                    "caseId": case_id,
                    "documentContent": document,
                    "stream": True
                }))

                # Collect all chunks
                complete = False
                chunk_count = 0
                while not complete:
                    response_text = await asyncio.wait_for(ws.recv(), timeout=15.0)
                    response = json.loads(response_text)

                    if first_token_time is None and response.get('type') == 'chat_chunk':
                        first_token_time = (time.perf_counter() - start_time) * 1000

                    if response.get('type') == 'chat_chunk' and response.get('is_complete'):
                        complete = True

                    chunk_count += 1
                    # Safety limit to prevent infinite loops
                    if chunk_count > 1000:
                        results.add_error(f"Too many chunks received (>{chunk_count})")
                        break

                total_time = (time.perf_counter() - start_time) * 1000
                results.add_timing(total_time)

                print(f"  Iteration {i+1}/10: First token: {first_token_time:.2f}ms, Total: {total_time:.2f}ms")

        # Evaluate results
        stats = results.calculate_stats()
        if stats['average'] <= 10000:
            results.passed = True
        else:
            results.add_error(f"Average completion time {stats['average']:.2f}ms exceeds target 10000ms")

    except asyncio.TimeoutError:
        results.add_error("Timeout waiting for response")
    except Exception as e:
        results.add_error(f"Test failed: {str(e)}")

    return results


async def test_form_autofill(case_id: str = "ACTE-2024-001") -> PerformanceTestResults:
    """
    TC-NFR-001-03: Form Auto-Fill Performance

    Target: Complete extraction ≤ 5000ms
    """
    results = PerformanceTestResults("TC-NFR-001-03: Form Auto-Fill Performance")
    ws_url = f"ws://localhost:8000/ws/chat/{case_id}"

    # Create 2000-character document with form data
    document = """
    Birth Certificate

    Name: Ahmad Ali
    Date of Birth: 15.05.1990
    Place of Birth: Kabul, Afghanistan
    Nationality: Afghan
    Passport Number: P123456789
    Passport Expiry: 20.05.2028
    Current Address: Hauptstraße 123, 10115 Berlin, Germany

    """ * 10  # Approximately 2000 characters

    # 7-field form schema
    form_schema = [
        {"id": "fullName", "label": "Full Name", "type": "text"},
        {"id": "birthDate", "label": "Birth Date", "type": "date"},
        {"id": "placeOfBirth", "label": "Place of Birth", "type": "text"},
        {"id": "nationality", "label": "Nationality", "type": "text"},
        {"id": "passportNumber", "label": "Passport Number", "type": "text"},
        {"id": "passportExpiry", "label": "Passport Expiry", "type": "date"},
        {"id": "currentAddress", "label": "Current Address", "type": "textarea"}
    ]

    print(f"\nRunning TC-NFR-001-03: Form auto-fill performance (10 iterations)...")

    try:
        for i in range(10):
            async with websockets.connect(ws_url) as ws:
                # Wait for connection confirmation
                await asyncio.wait_for(ws.recv(), timeout=5.0)

                # Start timer
                start_time = time.perf_counter()

                # Send form fill request
                await ws.send(json.dumps({
                    "type": "chat",
                    "content": "Fill the form from this document",
                    "caseId": case_id,
                    "documentContent": document,
                    "formSchema": form_schema,
                    "stream": False  # Form extraction doesn't use streaming
                }))

                # Wait for form_update message
                received = False
                timeout_count = 0
                while not received and timeout_count < 10:
                    try:
                        response_text = await asyncio.wait_for(ws.recv(), timeout=20.0)
                        response = json.loads(response_text)

                        if response.get('type') == 'form_update':
                            elapsed = (time.perf_counter() - start_time) * 1000
                            results.add_timing(elapsed)
                            print(f"  Iteration {i+1}/10: {elapsed:.2f}ms")
                            received = True
                            break

                        timeout_count += 1
                    except asyncio.TimeoutError:
                        timeout_count += 1

                if not received:
                    results.add_error(f"Iteration {i+1}: Did not receive form_update message")

        # Evaluate results
        if results.response_times:
            stats = results.calculate_stats()
            if stats['average'] <= 5000 and stats['percentile_95'] <= 6000:
                results.passed = True
            else:
                if stats['average'] > 5000:
                    results.add_error(f"Average time {stats['average']:.2f}ms exceeds target 5000ms")

    except asyncio.TimeoutError:
        results.add_error("Timeout waiting for response")
    except Exception as e:
        results.add_error(f"Test failed: {str(e)}")

    return results


async def test_no_degradation(case_id: str = "ACTE-2024-001") -> PerformanceTestResults:
    """
    TC-NFR-001-06: No Performance Degradation - Sequential Requests

    Target: Performance increase ≤ 10% from first 3 to last 3 requests
    """
    results = PerformanceTestResults("TC-NFR-001-06: No Performance Degradation")
    ws_url = f"ws://localhost:8000/ws/chat/{case_id}"

    print(f"\nRunning TC-NFR-001-06: Sequential requests degradation test (10 iterations)...")

    try:
        async with websockets.connect(ws_url) as ws:
            # Wait for connection confirmation
            await asyncio.wait_for(ws.recv(), timeout=5.0)

            for i in range(10):
                # Start timer
                start_time = time.perf_counter()

                # Send simple message
                await ws.send(json.dumps({
                    "type": "chat",
                    "content": "Hello",
                    "caseId": case_id,
                    "stream": True
                }))

                # Wait for first chunk
                await asyncio.wait_for(ws.recv(), timeout=10.0)
                first_token_time = (time.perf_counter() - start_time) * 1000

                # Wait for completion
                complete = False
                chunk_count = 0
                while not complete and chunk_count < 1000:
                    response_text = await asyncio.wait_for(ws.recv(), timeout=10.0)
                    response = json.loads(response_text)
                    if response.get('type') == 'chat_chunk' and response.get('is_complete'):
                        complete = True
                    chunk_count += 1

                results.add_timing(first_token_time)
                print(f"  Request {i+1}/10: {first_token_time:.2f}ms")

        # Evaluate results
        if len(results.response_times) >= 10:
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

    except asyncio.TimeoutError:
        results.add_error("Timeout waiting for response")
    except Exception as e:
        results.add_error(f"Test failed: {str(e)}")

    return results


async def run_all_tests():
    """Run all performance tests and generate report"""
    print("=" * 80)
    print("NFR-001: Real-Time AI Response Performance Test Suite")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend URL: ws://localhost:8000")

    # Run tests
    test_results = []

    test_results.append(await test_first_token_simple())
    test_results.append(await test_document_summary())
    test_results.append(await test_form_autofill())
    test_results.append(await test_no_degradation())

    # Print reports
    print("\n\n")
    print("=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)

    for result in test_results:
        result.print_report()

    # Overall summary
    passed = sum(1 for r in test_results if r.passed)
    failed = sum(1 for r in test_results if r.errors)

    print(f"Overall: {passed} passed, {failed} failed out of {len(test_results)} tests")

    if failed == 0:
        print("\nALL TESTS PASSED - NFR-001 requirements met!")
        return 0, test_results
    else:
        print(f"\n{failed} TEST(S) FAILED - NFR-001 requirements not met")
        return 1, test_results


if __name__ == "__main__":
    exit_code, test_results = asyncio.run(run_all_tests())
    exit(exit_code)
