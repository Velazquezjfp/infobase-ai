"""
Test Case: TC-S5-013-12
Requirement: S5-013 - Enhanced Acte Context Research
Description: Validate context against schema, verify all required fields present
Generated: 2026-01-09T15:29:16Z
"""
import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).resolve().parents[3] / "backend"
sys.path.insert(0, str(backend_path))

from services.context_manager import ContextManager


def test_TC_S5_013_12():
    """Validate context against schema, verify all required fields present"""
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

            # Use validate_case_context method from context_manager
            validation_result = context_manager.validate_case_context(context, check_urls=False)

            # Verify validation passes
            if not validation_result.valid:
                error_msg = f"{case_id}: Context validation failed:\n"
                for error in validation_result.errors:
                    error_msg += f"  - {error}\n"
                raise AssertionError(error_msg.rstrip())

            # Log any warnings
            if validation_result.warnings:
                print(f"⚠ {case_id} warnings:")
                for warning in validation_result.warnings:
                    print(f"  - {warning}")

            results.append({
                'case_id': case_id,
                'case_name': case_name,
                'valid': validation_result.valid,
                'errors': len(validation_result.errors),
                'warnings': len(validation_result.warnings),
                'stats': validation_result.stats,
                'status': 'PASS'
            })

            print(f"✓ {case_id} ({case_name}): {validation_result.get_summary()}")

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
        results = test_TC_S5_013_12()
        print("\nTC-S5-013-12: PASSED")
        print(f"Validated schema compliance in {len(results)} case contexts successfully")
    except AssertionError as e:
        print(f"\nTC-S5-013-12: FAILED - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nTC-S5-013-12: ERROR - {e}")
        sys.exit(1)
