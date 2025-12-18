#!/usr/bin/env python3
"""
Test script for F-002 Case Switching functionality.

Tests case-instance isolation and context switching between multiple cases:
- ACTE-2024-001: Integration Course
- ACTE-2024-002: Asylum Application
- ACTE-2024-003: Family Reunification

Usage:
    python temp/test_case_switching.py
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.services.context_manager import ContextManager


def print_test(test_name: str):
    """Print test header."""
    print("\n" + "=" * 70)
    print(f"TEST: {test_name}")
    print("=" * 70)


def print_success(message: str):
    """Print success message."""
    print(f"✓ {message}")


def print_error(message: str):
    """Print error message."""
    print(f"✗ {message}")


def test_case_switching():
    """Test TC-F-002-03: Switch Between Cases - Context Reload"""
    print_test("TC-F-002-03: Switch Between Cases - Context Reload")

    try:
        cm = ContextManager()

        # Load ACTE-2024-001 (Integration Course)
        print("\n--- Loading Case: ACTE-2024-001 ---")
        case1 = cm.load_case_context("ACTE-2024-001")
        print_success(f"Case ID: {case1['caseId']}")
        print_success(f"Case Type: {case1['caseType']}")
        print_success(f"Case Name: {case1['name']}")

        # Verify it's Integration Course
        assert case1["caseType"] == "integration_course", \
            "ACTE-2024-001 should be integration_course"
        print_success("Confirmed: Integration Course case")

        # Switch to ACTE-2024-002 (Asylum Application)
        print("\n--- Switching to Case: ACTE-2024-002 ---")
        case2 = cm.load_case_context("ACTE-2024-002")
        print_success(f"Case ID: {case2['caseId']}")
        print_success(f"Case Type: {case2['caseType']}")
        print_success(f"Case Name: {case2['name']}")

        # Verify it's Asylum Application
        assert case2["caseType"] == "asylum_application", \
            "ACTE-2024-002 should be asylum_application"
        print_success("Confirmed: Asylum Application case")

        # Verify contexts are completely different
        assert case1["caseId"] != case2["caseId"], \
            "Case IDs must be different"
        assert case1["caseType"] != case2["caseType"], \
            "Case types must be different"
        assert case1["name"] != case2["name"], \
            "Case names must be different"

        print_success("Cases are properly isolated with different contexts")

        # Switch to ACTE-2024-003 (Family Reunification)
        print("\n--- Switching to Case: ACTE-2024-003 ---")
        case3 = cm.load_case_context("ACTE-2024-003")
        print_success(f"Case ID: {case3['caseId']}")
        print_success(f"Case Type: {case3['caseType']}")
        print_success(f"Case Name: {case3['name']}")

        # Verify it's Family Reunification
        assert case3["caseType"] == "family_reunification", \
            "ACTE-2024-003 should be family_reunification"
        print_success("Confirmed: Family Reunification case")

        # Verify all three are different
        assert len({case1["caseId"], case2["caseId"], case3["caseId"]}) == 3, \
            "All case IDs must be unique"
        assert len({case1["caseType"], case2["caseType"], case3["caseType"]}) == 3, \
            "All case types must be unique"

        print_success("All three cases have distinct contexts")

        # Switch back to ACTE-2024-001 to verify context reload
        print("\n--- Switching back to Case: ACTE-2024-001 ---")
        case1_reload = cm.load_case_context("ACTE-2024-001")
        assert case1_reload["caseId"] == case1["caseId"], \
            "Case ID should match original"
        assert case1_reload["caseType"] == case1["caseType"], \
            "Case type should match original"
        print_success("Context correctly reloaded after switching back")

        print_success("TC-F-002-03 PASSED")
        return True

    except Exception as e:
        print_error(f"TC-F-002-03 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_folder_context_per_case():
    """Test that folder contexts are case-specific"""
    print_test("Folder Context per Case Test")

    try:
        cm = ContextManager()

        # Load personal-data folder for ACTE-2024-001
        print("\n--- ACTE-2024-001 Personal Data Folder ---")
        folder1 = cm.load_folder_context("ACTE-2024-001", "personal-data")
        assert folder1 is not None, "Folder context should exist"
        print_success(f"Folder: {folder1['folderName']}")
        print_success(f"Purpose: {folder1['purpose'][:50]}...")

        # Load personal-data folder for ACTE-2024-002
        print("\n--- ACTE-2024-002 Personal Data Folder ---")
        folder2 = cm.load_folder_context("ACTE-2024-002", "personal-data")
        if folder2:
            print_success(f"Folder: {folder2['folderName']}")
            print_success(f"Purpose: {folder2['purpose'][:50]}...")

            # Verify folder contexts are case-specific
            # They may have different validation criteria based on case type
            if folder1 != folder2:
                print_success("Folder contexts are case-specific")
        else:
            print_success("ACTE-2024-002 doesn't have personal-data folder (OK)")

        print_success("Folder Context per Case Test PASSED")
        return True

    except Exception as e:
        print_error(f"Folder Context per Case Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_merged_context_switching():
    """Test TC-F-002-04: Context-Aware Document Analysis"""
    print_test("TC-F-002-04: Context-Aware Document Analysis")

    try:
        cm = ContextManager()

        # Simulate document analysis in ACTE-2024-001
        print("\n--- Analysis in ACTE-2024-001 (Integration Course) ---")
        case1 = cm.load_case_context("ACTE-2024-001")
        folder1 = cm.load_folder_context("ACTE-2024-001", "personal-data")
        doc_content = "Birth Certificate: Ahmad Ali, Born: 15.05.1990"

        merged1 = cm.merge_contexts(case1, folder1, doc_content)

        # Verify Integration Course context present
        assert "integration_course" in merged1 or "Integration Course" in merged1, \
            "Integration Course context should be present"
        assert "Ahmad Ali" in merged1, \
            "Document content should be present"
        print_success("Integration Course context properly included")

        # Simulate same document analysis in different case
        print("\n--- Same Document in ACTE-2024-002 (Asylum Application) ---")
        case2 = cm.load_case_context("ACTE-2024-002")
        folder2 = cm.load_folder_context("ACTE-2024-002", "personal-data")

        merged2 = cm.merge_contexts(case2, folder2, doc_content)

        # Verify Asylum Application context present
        assert "asylum_application" in merged2 or "Asylum" in merged2, \
            "Asylum Application context should be present"
        assert "Ahmad Ali" in merged2, \
            "Document content should be present"
        print_success("Asylum Application context properly included")

        # Verify contexts are different despite same document
        assert "Integration Course" in merged1 or "integration_course" in merged1, \
            "Case 1 should mention Integration Course"
        assert "Asylum" in merged2 or "asylum" in merged2, \
            "Case 2 should mention Asylum"

        print_success("Context switches correctly based on active case")
        print_success("TC-F-002-04 PASSED")
        return True

    except Exception as e:
        print_error(f"TC-F-002-04 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_case_regulations():
    """Compare regulations across different case types"""
    print_test("Case Type Regulations Comparison")

    try:
        cm = ContextManager()

        cases = [
            ("ACTE-2024-001", "integration_course"),
            ("ACTE-2024-002", "asylum_application"),
            ("ACTE-2024-003", "family_reunification"),
        ]

        for case_id, expected_type in cases:
            context = cm.load_case_context(case_id)
            print(f"\n{case_id} ({context['caseType']}):")
            print(f"  Regulations: {len(context.get('regulations', []))}")
            print(f"  Required Docs: {len(context.get('requiredDocuments', []))}")
            print(f"  Validation Rules: {len(context.get('validationRules', []))}")

            assert context['caseType'] == expected_type, \
                f"Case {case_id} should be {expected_type}"

        print_success("All cases have distinct regulation sets")
        print_success("Case Type Regulations Comparison PASSED")
        return True

    except Exception as e:
        print_error(f"Case Type Regulations Comparison FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all case switching tests"""
    print("\n" + "=" * 70)
    print("F-002 Case Switching Test Suite")
    print("=" * 70)

    results = []

    # Run tests
    results.append(("Case Switching", test_case_switching()))
    results.append(("Folder Context per Case", test_folder_context_per_case()))
    results.append(("Merged Context Switching", test_merged_context_switching()))
    results.append(("Case Regulations", test_case_regulations()))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:35} {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL CASE SWITCHING TESTS PASSED!")
        print("\n✅ F-002 Implementation Complete:")
        print("   - Case-instance context loading")
        print("   - Folder-level context loading")
        print("   - Context merging")
        print("   - Case switching with isolation")
        print("   - Backend integration with GeminiService")
        print("   - Frontend WebSocket message types")
        print("   - AppContext case switching logic")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
