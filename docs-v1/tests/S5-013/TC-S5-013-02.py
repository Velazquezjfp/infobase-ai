"""
Test Case: TC-S5-013-02
Requirement: S5-013 - Enhanced Acte Context Research
Description: Verify each required document has criticality field ('critical' or 'optional')
Generated: 2026-01-09T15:29:16Z
"""
import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).resolve().parents[3] / "backend"
sys.path.insert(0, str(backend_path))

from services.context_manager import ContextManager


def test_TC_S5_013_02():
    """Verify each required document has criticality field ('critical' or 'optional')"""
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
            required_docs = context.get('requiredDocuments', [])

            critical_count = 0
            optional_count = 0

            for idx, doc in enumerate(required_docs):
                doc_name = doc.get('name', f'Document {idx}')

                # Verify criticality field exists
                assert 'criticality' in doc, \
                    f"{case_id}: Document '{doc_name}' missing 'criticality' field"

                criticality = doc['criticality']

                # Verify valid criticality values
                assert criticality in ['critical', 'optional'], \
                    f"{case_id}: Document '{doc_name}' has invalid criticality: '{criticality}' " \
                    f"(must be 'critical' or 'optional')"

                if criticality == 'critical':
                    critical_count += 1
                else:
                    optional_count += 1

            results.append({
                'case_id': case_id,
                'case_name': case_name,
                'total_documents': len(required_docs),
                'critical': critical_count,
                'optional': optional_count,
                'status': 'PASS'
            })

            print(f"✓ {case_id} ({case_name}): {critical_count} critical, {optional_count} optional documents")

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
        results = test_TC_S5_013_02()
        print("\nTC-S5-013-02: PASSED")
        print(f"Validated criticality fields in {len(results)} case contexts successfully")
    except AssertionError as e:
        print(f"\nTC-S5-013-02: FAILED - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nTC-S5-013-02: ERROR - {e}")
        sys.exit(1)
