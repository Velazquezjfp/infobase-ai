"""
Test Case: TC-S5-013-05
Requirement: S5-013 - Enhanced Acte Context Research
Description: Verify commonIssues array contains at least 10 common issues with solutions
Generated: 2026-01-09T15:29:16Z
"""
import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).resolve().parents[3] / "backend"
sys.path.insert(0, str(backend_path))

from services.context_manager import ContextManager


def test_TC_S5_013_05():
    """Verify commonIssues array contains at least 10 common issues with solutions"""
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

            # Verify commonIssues field exists
            assert 'commonIssues' in context, \
                f"{case_id}: Missing 'commonIssues' field"

            common_issues = context['commonIssues']

            # Verify it's a list
            assert isinstance(common_issues, list), \
                f"{case_id}: 'commonIssues' must be a list"

            # Verify it has at least 10 common issues
            issue_count = len(common_issues)
            assert issue_count >= 10, \
                f"{case_id}: Expected ≥10 common issues, got {issue_count}"

            # Verify each issue has required fields
            by_severity = {'error': 0, 'warning': 0, 'info': 0}

            for idx, issue in enumerate(common_issues):
                issue_name = issue.get('issue', f'Issue {idx}')

                # Check required fields
                required_fields = ['issue', 'severity', 'suggestion']
                for field in required_fields:
                    assert field in issue, \
                        f"{case_id}: Issue '{issue_name}' missing '{field}' field"

                    # Verify field is not empty
                    value = issue[field]
                    assert value and str(value).strip(), \
                        f"{case_id}: Issue '{issue_name}' has empty '{field}' field"

                # Verify valid severity
                severity = issue['severity']
                assert severity in ['error', 'warning', 'info'], \
                    f"{case_id}: Issue '{issue_name}' has invalid severity: '{severity}' " \
                    f"(must be 'error', 'warning', or 'info')"

                by_severity[severity] += 1

            results.append({
                'case_id': case_id,
                'case_name': case_name,
                'issue_count': issue_count,
                'by_severity': by_severity,
                'status': 'PASS'
            })

            print(f"✓ {case_id} ({case_name}): {issue_count} common issues " \
                  f"(errors: {by_severity['error']}, warnings: {by_severity['warning']}, info: {by_severity['info']})")

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
        results = test_TC_S5_013_05()
        print("\nTC-S5-013-05: PASSED")
        print(f"Validated common issues in {len(results)} case contexts successfully")
    except AssertionError as e:
        print(f"\nTC-S5-013-05: FAILED - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nTC-S5-013-05: ERROR - {e}")
        sys.exit(1)
