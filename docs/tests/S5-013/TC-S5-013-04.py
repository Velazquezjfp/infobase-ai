"""
Test Case: TC-S5-013-04
Requirement: S5-013 - Enhanced Acte Context Research
Description: Each regulation has reference, title, url, and summary fields
Generated: 2026-01-09T15:29:16Z
"""
import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).resolve().parents[3] / "backend"
sys.path.insert(0, str(backend_path))

from services.context_manager import ContextManager
from models.regulation import Regulation, validate_regulations_list


def test_TC_S5_013_04():
    """Each regulation has reference, title, url, and summary fields"""
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
            regulations = context.get('regulations', [])

            # Use regulation model validator
            is_valid, errors, stats = validate_regulations_list(regulations)

            assert is_valid, \
                f"{case_id}: Regulation validation failed: {', '.join(errors)}"

            # Verify all regulations have required fields
            for idx, reg_data in enumerate(regulations):
                regulation = Regulation.from_dict(reg_data)

                # Verify required fields are present and not empty
                assert regulation.id and regulation.id.strip(), \
                    f"{case_id}: Regulation {idx} has empty id"

                assert regulation.title and regulation.title.strip(), \
                    f"{case_id}: Regulation {idx} has empty title"

                assert regulation.url and regulation.url.strip(), \
                    f"{case_id}: Regulation {idx} has empty url"

                assert regulation.summary and regulation.summary.strip(), \
                    f"{case_id}: Regulation {idx} has empty summary"

                # Verify URL format
                assert regulation.url.startswith(('http://', 'https://')), \
                    f"{case_id}: Regulation {idx} url must start with http:// or https://"

                # Verify minimum content length
                assert len(regulation.summary) >= 20, \
                    f"{case_id}: Regulation {idx} summary too short (< 20 chars)"

                assert len(regulation.title) >= 5, \
                    f"{case_id}: Regulation {idx} title too short (< 5 chars)"

            results.append({
                'case_id': case_id,
                'case_name': case_name,
                'regulation_count': stats['count'],
                'valid': stats['valid'],
                'invalid': stats['invalid'],
                'status': 'PASS'
            })

            print(f"✓ {case_id} ({case_name}): {stats['valid']}/{stats['count']} regulations valid")

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
        results = test_TC_S5_013_04()
        print("\nTC-S5-013-04: PASSED")
        print(f"Validated regulation fields in {len(results)} case contexts successfully")
    except AssertionError as e:
        print(f"\nTC-S5-013-04: FAILED - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nTC-S5-013-04: ERROR - {e}")
        sys.exit(1)
