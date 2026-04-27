#!/usr/bin/env python3
"""
Generate test-results.json for S5-010 by running all test cases
"""

import subprocess
import json
import time
import os
from datetime import datetime

# Test case definitions
TEST_CASES = [
    {
        "testId": "TC-S5-010-01",
        "testName": "Feature flag disabled, verify one-shot mode works as before",
        "testType": "python",
        "file": "TC-S5-010-01.py"
    },
    {
        "testId": "TC-S5-010-02",
        "testName": "Feature flag enabled, send message, verify history stored in conversation_manager",
        "testType": "python",
        "file": "TC-S5-010-02.py"
    },
    {
        "testId": "TC-S5-010-03",
        "testName": "Send follow-up question 'What was the name again?', verify AI uses previous context",
        "testType": "python",
        "file": "TC-S5-010-03.py"
    },
    {
        "testId": "TC-S5-010-04",
        "testName": "Switch case, verify conversation history switches to new case",
        "testType": "python",
        "file": "TC-S5-010-04.py"
    },
    {
        "testId": "TC-S5-010-05",
        "testName": "Send 15 messages, verify only last 10 included in context window",
        "testType": "python",
        "file": "TC-S5-010-05.py"
    },
    {
        "testId": "TC-S5-010-06",
        "testName": "Long conversation approaches token limit, verify older messages truncated",
        "testType": "python",
        "file": "TC-S5-010-06.py"
    },
    {
        "testId": "TC-S5-010-07",
        "testName": "Click 'Clear History', verify conversation cleared and next message has no context",
        "testType": "python",
        "file": "TC-S5-010-07.py"
    },
    {
        "testId": "TC-S5-010-08",
        "testName": "Restart backend, verify all conversation history cleared (no persistence)",
        "testType": "python",
        "file": "TC-S5-010-08.py"
    },
    {
        "testId": "TC-S5-010-09",
        "testName": "Two different cases with separate conversations, verify history doesn't mix",
        "testType": "python",
        "file": "TC-S5-010-09.py"
    },
    {
        "testId": "TC-S5-010-10",
        "testName": "Estimate tokens for conversation, verify count is accurate (within 10%)",
        "testType": "python",
        "file": "TC-S5-010-10.py"
    },
    {
        "testId": "TC-S5-010-11",
        "testName": "User asks 'Translate it to French' (referring to previous doc), verify AI understands reference",
        "testType": "python",
        "file": "TC-S5-010-11.py"
    },
    {
        "testId": "TC-S5-010-12",
        "testName": "Disabled history, verify backend doesn't store messages in conversation_manager",
        "testType": "python",
        "file": "TC-S5-010-12.py"
    },
]


def run_test(test_case):
    """Run a single test case and capture results"""
    test_file = os.path.join(os.path.dirname(__file__), test_case["file"])

    print(f"\nRunning {test_case['testId']}: {test_case['testName'][:60]}...")

    start_time = time.time()
    timestamp = datetime.utcnow().isoformat() + "Z"

    result = {
        "testId": test_case["testId"],
        "testName": test_case["testName"],
        "testType": test_case["testType"],
        "timestamp": timestamp,
        "status": "failed",
        "executionTime": 0,
        "errorMessage": None,
        "stackTrace": None
    }

    try:
        # Run test file
        proc = subprocess.run(
            ["python", test_file],
            capture_output=True,
            text=True,
            timeout=30
        )

        execution_time = round(time.time() - start_time, 3)
        result["executionTime"] = execution_time

        if proc.returncode == 0:
            result["status"] = "passed"
            print(f"  ✓ PASSED ({execution_time}s)")
        else:
            result["status"] = "failed"
            error_msg = proc.stderr if proc.stderr else proc.stdout
            result["errorMessage"] = error_msg.strip()
            result["stackTrace"] = error_msg.strip()
            print(f"  ✗ FAILED ({execution_time}s)")
            print(f"  Error: {error_msg[:200]}")

    except subprocess.TimeoutExpired:
        result["status"] = "failed"
        result["errorMessage"] = "Test execution timeout (30s)"
        result["executionTime"] = 30.0
        print(f"  ✗ TIMEOUT")

    except Exception as e:
        result["status"] = "failed"
        result["errorMessage"] = str(e)
        result["stackTrace"] = str(e)
        result["executionTime"] = round(time.time() - start_time, 3)
        print(f"  ✗ ERROR: {e}")

    return result


def main():
    """Run all tests and generate test-results.json"""
    print("=" * 80)
    print("S5-010: Optional Persistent Chat History - Test Execution")
    print("=" * 80)

    execution_timestamp = datetime.utcnow().isoformat() + "Z"
    test_results = []

    # Run all tests
    for test_case in TEST_CASES:
        result = run_test(test_case)
        test_results.append(result)

    # Calculate summary
    total = len(test_results)
    passed = sum(1 for r in test_results if r["status"] == "passed")
    failed = sum(1 for r in test_results if r["status"] == "failed")
    skipped = sum(1 for r in test_results if r["status"] == "skipped")
    manual = sum(1 for r in test_results if r["status"] == "manual")

    summary = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "manual": manual
    }

    # Create results object
    results = {
        "requirementId": "S5-010",
        "executionTimestamp": execution_timestamp,
        "summary": summary,
        "testCases": test_results
    }

    # Write to file
    output_file = os.path.join(os.path.dirname(__file__), "test-results.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Print summary
    print("\n" + "=" * 80)
    print("Test Execution Summary")
    print("=" * 80)
    print(f"Total Tests:   {total}")
    print(f"Passed:        {passed}")
    print(f"Failed:        {failed}")
    print(f"Skipped:       {skipped}")
    print(f"Manual:        {manual}")
    print(f"\nPass Rate:     {(passed/total*100):.1f}%")
    print(f"\nResults saved to: {output_file}")
    print("=" * 80)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(main())
