"""
Test Case: TC-S5-013-03
Requirement: S5-013 - Enhanced Acte Context Research
Description: Verify regulations array contains at least 5 regulation references
Generated: 2026-01-09T15:29:16Z
"""
import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).resolve().parents[3] / "backend"
sys.path.insert(0, str(backend_path))

from services.context_manager import ContextManager

# Import regulation module without triggering backend module imports
import sys
import importlib.util
spec = importlib.util.spec_from_file_location(
    "regulation",
    str(backend_path / "models" / "regulation.py")
)
regulation_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(regulation_module)
Regulation = regulation_module.Regulation


def test_TC_S5_013_03():
    """Verify regulations array contains at least 5 regulation references"""
    context_manager = ContextManager()

    # Test all schema v2.0 contexts (use ACTE-2024-001 and templates)
    test_cases = [
        ("ACTE-2024-001", "Integration Course Case"),
        ("templates/integration_course", "Integration Course Template"),
        ("templates/asylum_application", "Asylum Application Template"),
        ("templates/family_reunification", "Family Reunification Template"),
    ]

    results = []

    for case_id, case_name in test_cases:
        try:
            context = context_manager.load_case_context(case_id)

            # Verify regulations field exists
            assert 'regulations' in context, \
                f"{case_id}: Missing 'regulations' field"

            regulations = context['regulations']

            # Verify it's a list
            assert isinstance(regulations, list), \
                f"{case_id}: 'regulations' must be a list"

            # Verify it has at least 5 regulation references
            reg_count = len(regulations)
            assert reg_count >= 5, \
                f"{case_id}: Expected ≥5 regulations, got {reg_count}"

            # Verify each regulation has required fields (id, title, url, summary)
            for idx, reg_data in enumerate(regulations):
                reg_id = reg_data.get('id', f'Regulation {idx}')

                # Use Regulation model to validate
                try:
                    regulation = Regulation.from_dict(reg_data)

                    # Verify regulation data
                    assert regulation.id, f"{case_id}: Regulation {idx} has empty id"
                    assert regulation.title, f"{case_id}: Regulation {idx} has empty title"
                    assert regulation.url, f"{case_id}: Regulation {idx} has empty url"
                    assert regulation.summary, f"{case_id}: Regulation {idx} has empty summary"

                except ValueError as e:
                    raise AssertionError(f"{case_id}: Regulation {idx} invalid: {e}")

            results.append({
                'case_id': case_id,
                'case_name': case_name,
                'regulation_count': reg_count,
                'status': 'PASS'
            })

            print(f"✓ {case_id} ({case_name}): {reg_count} regulations (≥5 required)")

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
        results = test_TC_S5_013_03()
        print("\nTC-S5-013-03: PASSED")
        print(f"Validated regulations in {len(results)} case contexts successfully")
    except AssertionError as e:
        print(f"\nTC-S5-013-03: FAILED - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nTC-S5-013-03: ERROR - {e}")
        sys.exit(1)
