"""
Test Case: TC-S5-013-11
Requirement: S5-013 - Enhanced Acte Context Research
Description: Research sources documented in researchSources array
Generated: 2026-01-09T15:29:16Z
"""
import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).resolve().parents[3] / "backend"
sys.path.insert(0, str(backend_path))

from services.context_manager import ContextManager


def test_TC_S5_013_11():
    """Research sources documented in researchSources array"""
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

            # Verify processingInfo exists (includes timeline, costs, contact)
            assert 'processingInfo' in context, \
                f"{case_id}: Missing 'processingInfo' field"

            processing_info = context['processingInfo']

            # Verify processingInfo is a dict
            assert isinstance(processing_info, dict), \
                f"{case_id}: 'processingInfo' must be a dictionary"

            # Verify required sub-fields
            required_fields = ['timeline', 'costs', 'contact']
            for field in required_fields:
                assert field in processing_info, \
                    f"{case_id}: processingInfo missing '{field}' field"

                # Verify field is not empty
                value = processing_info[field]
                assert value, \
                    f"{case_id}: processingInfo.{field} is empty"

                # For dict fields, verify they have content
                if isinstance(value, dict):
                    assert len(value) > 0, \
                        f"{case_id}: processingInfo.{field} dict is empty"
                elif isinstance(value, str):
                    assert value.strip(), \
                        f"{case_id}: processingInfo.{field} string is empty"

            results.append({
                'case_id': case_id,
                'case_name': case_name,
                'has_timeline': 'timeline' in processing_info,
                'has_costs': 'costs' in processing_info,
                'has_contact': 'contact' in processing_info,
                'status': 'PASS'
            })

            print(f"✓ {case_id} ({case_name}): processingInfo with timeline, costs, contact")

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
        results = test_TC_S5_013_11()
        print("\nTC-S5-013-11: PASSED")
        print(f"Validated processingInfo in {len(results)} case contexts successfully")
    except AssertionError as e:
        print(f"\nTC-S5-013-11: FAILED - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nTC-S5-013-11: ERROR - {e}")
        sys.exit(1)
