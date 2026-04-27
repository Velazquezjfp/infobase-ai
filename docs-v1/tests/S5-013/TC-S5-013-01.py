"""
Test Case: TC-S5-013-01
Requirement: S5-013 - Enhanced Acte Context Research
Description: Load case context, verify requiredDocuments array has 10+ entries
Generated: 2026-01-09T15:29:16Z
"""
import sys
import json
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).resolve().parents[3] / "backend"
sys.path.insert(0, str(backend_path))

from services.context_manager import ContextManager


def test_TC_S5_013_01():
    """Load case context, verify requiredDocuments array has 10+ entries"""
    context_manager = ContextManager()

    # Test all schema v2.0 contexts
    test_cases = [
        ("ACTE-2024-001", "Integration Course"),
        ("ACTE-2024-002", "Asylum Application"),
        ("ACTE-2024-003", "Family Reunification"),
    ]

    results = []

    for case_id, case_name in test_cases:
        try:
            context = context_manager.load_case_context(case_id)

            # Verify requiredDocuments exists
            assert 'requiredDocuments' in context, \
                f"{case_id}: Missing 'requiredDocuments' field"

            required_docs = context['requiredDocuments']

            # Verify it's a list
            assert isinstance(required_docs, list), \
                f"{case_id}: 'requiredDocuments' must be a list"

            # Verify it has at least 10 entries
            doc_count = len(required_docs)
            assert doc_count >= 10, \
                f"{case_id}: Expected ≥10 required documents, got {doc_count}"

            results.append({
                'case_id': case_id,
                'case_name': case_name,
                'document_count': doc_count,
                'status': 'PASS'
            })

            print(f"✓ {case_id} ({case_name}): {doc_count} documents (≥10 required)")

        except AssertionError as e:
            results.append({
                'case_id': case_id,
                'case_name': case_name,
                'status': 'FAIL',
                'error': str(e)
            })
            raise
        except Exception as e:
            results.append({
                'case_id': case_id,
                'case_name': case_name,
                'status': 'ERROR',
                'error': str(e)
            })
            raise

    return results


if __name__ == "__main__":
    try:
        results = test_TC_S5_013_01()
        print("\nTC-S5-013-01: PASSED")
        print(f"Validated {len(results)} case contexts successfully")
    except AssertionError as e:
        print(f"\nTC-S5-013-01: FAILED - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nTC-S5-013-01: ERROR - {e}")
        sys.exit(1)
