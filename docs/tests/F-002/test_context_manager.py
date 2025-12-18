#!/usr/bin/env python3
"""
Test script for F-002 Context Manager implementation.

Tests all functionality of the ContextManager class including:
- Loading case context
- Loading folder context
- Merging contexts
- Case isolation

Usage:
    python temp/test_context_manager.py
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

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


def test_load_case_context():
    """Test TC-F-002-01: Load Case-Instance Context"""
    print_test("TC-F-002-01: Load Case-Instance Context")

    try:
        cm = ContextManager()
        context = cm.load_case_context("ACTE-2024-001")

        # Verify required fields
        assert "caseId" in context, "Missing caseId"
        assert context["caseId"] == "ACTE-2024-001", "Wrong caseId"
        print_success(f"Case ID correct: {context['caseId']}")

        assert "caseType" in context, "Missing caseType"
        assert context["caseType"] == "integration_course", "Wrong caseType"
        print_success(f"Case Type correct: {context['caseType']}")

        assert "name" in context, "Missing name"
        print_success(f"Case Name: {context['name']}")

        assert "regulations" in context, "Missing regulations"
        assert len(context["regulations"]) >= 5, "Not enough regulations"
        print_success(f"Regulations count: {len(context['regulations'])}")

        assert "requiredDocuments" in context, "Missing requiredDocuments"
        assert len(context["requiredDocuments"]) >= 10, "Not enough required documents"
        print_success(f"Required Documents count: {len(context['requiredDocuments'])}")

        assert "validationRules" in context, "Missing validationRules"
        assert len(context["validationRules"]) >= 8, "Not enough validation rules"
        print_success(f"Validation Rules count: {len(context['validationRules'])}")

        print_success("TC-F-002-01 PASSED")
        return True

    except Exception as e:
        print_error(f"TC-F-002-01 FAILED: {str(e)}")
        return False


def test_load_folder_context():
    """Test TC-F-002-02: Load Case-Specific Folder Context"""
    print_test("TC-F-002-02: Load Case-Specific Folder Context")

    try:
        cm = ContextManager()
        context = cm.load_folder_context("ACTE-2024-001", "personal-data")

        assert context is not None, "Context is None"

        # Verify required fields
        assert "folderId" in context, "Missing folderId"
        assert context["folderId"] == "personal-data", "Wrong folderId"
        print_success(f"Folder ID correct: {context['folderId']}")

        assert "folderName" in context, "Missing folderName"
        assert "Personal Data" in context["folderName"], "Wrong folder name"
        print_success(f"Folder Name: {context['folderName']}")

        assert "expectedDocuments" in context, "Missing expectedDocuments"
        expected_docs = context["expectedDocuments"]
        assert "birth_certificate" in expected_docs, "Missing birth_certificate"
        assert "passport" in expected_docs, "Missing passport"
        print_success(f"Expected Documents: {len(expected_docs)} types")

        assert "validationCriteria" in context, "Missing validationCriteria"
        assert len(context["validationCriteria"]) >= 3, "Not enough validation criteria"
        print_success(f"Validation Criteria count: {len(context['validationCriteria'])}")

        print_success("TC-F-002-02 PASSED")
        return True

    except Exception as e:
        print_error(f"TC-F-002-02 FAILED: {str(e)}")
        return False


def test_merge_contexts():
    """Test context merging with all three levels"""
    print_test("Context Merging Test")

    try:
        cm = ContextManager()

        # Load case and folder context
        case_ctx = cm.load_case_context("ACTE-2024-001")
        folder_ctx = cm.load_folder_context("ACTE-2024-001", "personal-data")
        doc_ctx = "Birth Certificate: Ahmad Ali, Born: 15.05.1990, Place: Kabul"

        # Merge contexts
        merged = cm.merge_contexts(case_ctx, folder_ctx, doc_ctx)

        assert merged is not None, "Merged context is None"
        assert len(merged) > 0, "Merged context is empty"

        # Verify all three levels are present
        assert "CASE CONTEXT" in merged, "Missing case context section"
        assert "FOLDER CONTEXT" in merged, "Missing folder context section"
        assert "DOCUMENT CONTENT" in merged, "Missing document content section"

        # Verify key information is present
        assert "ACTE-2024-001" in merged, "Case ID not in merged context"
        assert "Integration Course" in merged or "integration_course" in merged, "Case type not in merged context"
        assert "Personal Data" in merged, "Folder name not in merged context"
        assert "Ahmad Ali" in merged, "Document content not in merged context"

        print_success("All three context levels merged successfully")
        print_success(f"Merged context length: {len(merged)} characters")

        # Print sample of merged context
        print("\n--- Sample of Merged Context ---")
        print(merged[:500] + "...")

        print_success("Context Merging Test PASSED")
        return True

    except Exception as e:
        print_error(f"Context Merging Test FAILED: {str(e)}")
        return False


def test_case_isolation():
    """Test TC-F-002-09: Case Isolation Verification"""
    print_test("TC-F-002-09: Case Isolation Verification")

    try:
        cm = ContextManager()

        # Load context for ACTE-2024-001
        context1 = cm.load_case_context("ACTE-2024-001")
        print_success(f"Loaded case 1: {context1['caseId']}")

        # Verify it's an Integration Course
        assert context1["caseType"] == "integration_course", "Wrong case type for ACTE-2024-001"
        print_success(f"Case 1 type: {context1['caseType']}")

        # Try to load ACTE-2024-002 if it exists
        try:
            context2 = cm.load_case_context("ACTE-2024-002")
            print_success(f"Loaded case 2: {context2['caseId']}")

            # Verify contexts are different
            assert context1["caseId"] != context2["caseId"], "Case IDs should be different"
            assert context1["caseType"] != context2["caseType"], "Case types should be different"

            print_success("Cases are properly isolated with different contexts")

        except FileNotFoundError:
            print_success("ACTE-2024-002 not found (expected if not created yet)")

        print_success("TC-F-002-09 PASSED")
        return True

    except Exception as e:
        print_error(f"TC-F-002-09 FAILED: {str(e)}")
        return False


def test_error_handling():
    """Test error handling for missing files"""
    print_test("Error Handling Test")

    try:
        cm = ContextManager()

        # Test 1: Non-existent case
        try:
            cm.load_case_context("ACTE-9999-999")
            print_error("Should have raised FileNotFoundError for non-existent case")
            return False
        except FileNotFoundError:
            print_success("Correctly raised FileNotFoundError for non-existent case")

        # Test 2: Non-existent folder (should return None gracefully)
        folder_ctx = cm.load_folder_context("ACTE-2024-001", "non-existent-folder")
        assert folder_ctx is None, "Should return None for non-existent folder"
        print_success("Gracefully returned None for non-existent folder")

        print_success("Error Handling Test PASSED")
        return True

    except Exception as e:
        print_error(f"Error Handling Test FAILED: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("F-002 Context Manager Test Suite")
    print("=" * 70)

    results = []

    # Run tests
    results.append(("Load Case Context", test_load_case_context()))
    results.append(("Load Folder Context", test_load_folder_context()))
    results.append(("Merge Contexts", test_merge_contexts()))
    results.append(("Case Isolation", test_case_isolation()))
    results.append(("Error Handling", test_error_handling()))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:30} {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
