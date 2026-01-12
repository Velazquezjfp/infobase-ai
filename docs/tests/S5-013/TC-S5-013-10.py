"""
Test Case: TC-S5-013-10
Requirement: S5-013 - Enhanced Acte Context Research
Description: Context schema version is tracked in case.json (schemaVersion field)
Generated: 2026-01-09T15:29:16Z
"""
import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).resolve().parents[3] / "backend"
sys.path.insert(0, str(backend_path))

from services.context_manager import ContextManager


def test_TC_S5_013_10():
    """Context schema version is tracked in case.json (schemaVersion field)"""
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

            # Verify schemaVersion field exists
            assert 'schemaVersion' in context, \
                f"{case_id}: Missing 'schemaVersion' field"

            schema_version = context['schemaVersion']

            # Verify it's the correct version
            assert schema_version == '2.0', \
                f"{case_id}: Expected schemaVersion '2.0', got '{schema_version}'"

            results.append({
                'case_id': case_id,
                'case_name': case_name,
                'schema_version': schema_version,
                'status': 'PASS'
            })

            print(f"✓ {case_id} ({case_name}): Schema version {schema_version}")

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
        results = test_TC_S5_013_10()
        print("\nTC-S5-013-10: PASSED")
        print(f"Validated schema version in {len(results)} case contexts successfully")
    except AssertionError as e:
        print(f"\nTC-S5-013-10: FAILED - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nTC-S5-013-10: ERROR - {e}")
        sys.exit(1)
