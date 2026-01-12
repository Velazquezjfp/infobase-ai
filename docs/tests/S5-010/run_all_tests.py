#!/usr/bin/env python3
"""
Test Execution Script for S5-010: Optional Persistent Chat History
Runs all test cases and generates test-results.json
"""

import sys
import os
import json
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import all test functions
from docs.tests.S5_010.TC_S5_010_01 import test_TC_S5_010_01
from docs.tests.S5_010.TC_S5_010_02 import test_TC_S5_010_02
from docs.tests.S5_010.TC_S5_010_03 import test_TC_S5_010_03
from docs.tests.S5_010.TC_S5_010_04 import test_TC_S5_010_04
from docs.tests.S5_010.TC_S5_010_05 import test_TC_S5_010_05
from docs.tests.S5_010.TC_S5_010_06 import test_TC_S5_010_06
from docs.tests.S5_010.TC_S5_010_07 import test_TC_S5_010_07
from docs.tests.S5_010.TC_S5_010_08 import test_TC_S5_010_08
from docs.tests.S5_010.TC_S5_010_09 import test_TC_S5_010_09
from docs.tests.S5_010.TC_S5_010_10 import test_TC_S5_010_10
from docs.tests.S5_010.TC_S5_010_11 import test_TC_S5_010_11
from docs.tests.S5_010.TC_S5_010_12 import test_TC_S5_010_12

# Test definitions
TESTS = [
    {
        "testId": "TC-S5-010-01",
        "testName": "Feature flag disabled, verify one-shot mode works as before",
        "testType": "python",
        "function": test_TC_S5_010_01
    },
    {
        "testId": "TC-S5-010-02",
        "testName": "Feature flag enabled, send message, verify history stored in conversation_manager",
        "testType": "python",
        "function": test_TC_S5_010_02
    },
    {
        "testId": "TC-S5-010-03",
        "testName": "Send follow-up question 'What was the name again?', verify AI uses previous context",
        "testType": "python",
        "function": test_TC_S5_010_03
    },
    {
        "testId": "TC-S5-010-04",
        "testName": "Switch case, verify conversation history switches to new case",
        "testType": "python",
        "function": test_TC_S5_010_04
    },
    {
        "testId": "TC-S5-010-05",
        "testName": "Send 15 messages, verify only last 10 included in context window",
        "testType": "python",
        "function": test_TC_S5_010_05
    },
    {
        "testId": "TC-S5-010-06",
        "testName": "Long conversation approaches token limit, verify older messages truncated",
        "testType": "python",
        "function": test_TC_S5_010_06
    },
    {
        "testId": "TC-S5-010-07",
        "testName": "Click 'Clear History', verify conversation cleared and next message has no context",
        "testType": "python",
        "function": test_TC_S5_010_07
    },
    {
        "testId": "TC-S5-010-08",
        "testName": "Restart backend, verify all conversation history cleared (no persistence)",
        "testType": "python",
        "function": test_TC_S5_010_08
    },
    {
        "testId": "TC-S5-010-09",
        "testName": "Two different cases with separate conversations, verify history doesn't mix",
        "testType": "python",
        "function": test_TC_S5_010_09
    },
    {
        "testId": "TC-S5-010-10",
        "testName": "Estimate tokens for conversation, verify count is accurate (within 10%)",
        "testType": "python",
        "function": test_TC_S5_010_10
    },
    {
        "testId": "TC-S5-010-11",
        "testName": "User asks 'Translate it to French' (referring to previous doc), verify AI understands reference",
        "testType": "python",
        "function": test_TC_S5_010_11
    },
    {
        "testId": "TC-S5-010-12",
        "testName": "Disabled history, verify backend doesn't store messages in conversation_manager",
        "testType": "python",
        "function": test_TC_S5_010_12
    },
]


def run_test(test_def):
    """Run a single test and return results"""
    print(f"\nRunning {test_def['testId']}: {test_def['testName']}")

    start_time = time.time()
    timestamp = datetime.utcnow().isoformat() + "Z"

    result = {
        "testId": test_def["testId"],
        "testName": test_def["testName"],
        "testType": test_def["testType"],
        "timestamp": timestamp,
        "status": "failed",
        "executionTime": 0,
        "errorMessage": None,
        "stackTrace": None
    }

    try:
        test_def["function"]()
        result["status"] = "passed"
        print(f"✓ {test_def['testId']}: PASSED")
    except AssertionError as e:
        result["status"] = "failed"
        result["errorMessage"] = str(e)
        print(f"✗ {test_def['testId']}: FAILED - {e}")
    except Exception as e:
        result["status"] = "failed"
        result["errorMessage"] = str(e)
        result["stackTrace"] = str(e)
        print(f"✗ {test_def['testId']}: ERROR - {e}")
    finally:
        result["executionTime"] = round(time.time() - start_time, 3)

    return result


def main():
    """Run all tests and generate results JSON"""
    print("=" * 80)
    print("S5-010: Optional Persistent Chat History - Test Execution")
    print("=" * 80)

    execution_timestamp = datetime.utcnow().isoformat() + "Z"
    test_results = []

    # Run all tests
    for test_def in TESTS:
        result = run_test(test_def)
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
    print(f"Total:   {total}")
    print(f"Passed:  {passed}")
    print(f"Failed:  {failed}")
    print(f"Skipped: {skipped}")
    print(f"Manual:  {manual}")
    print(f"\nResults saved to: {output_file}")
    print("=" * 80)

    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
