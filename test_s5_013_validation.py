#!/usr/bin/env python3
"""
Test script for S5-013: Enhanced Acte Context Research

This script tests the validation functionality against all existing case contexts
to ensure they meet schema v2.0 requirements.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.services.context_manager import ContextManager


def test_case_context_validation():
    """Test validation against all case contexts."""
    print("=" * 80)
    print("S5-013 Validation Test: Testing Case Context Validation")
    print("=" * 80)
    print()

    context_manager = ContextManager()

    # Test cases to validate
    test_cases = [
        ("ACTE-2024-001", "Integration Course - Real Case"),
        ("templates/integration_course", "Integration Course Template"),
        ("templates/asylum_application", "Asylum Application Template"),
        ("templates/family_reunification", "Family Reunification Template"),
    ]

    all_passed = True
    results = []

    for case_path, description in test_cases:
        print(f"\n{'─' * 80}")
        print(f"Testing: {description}")
        print(f"Path: {case_path}")
        print(f"{'─' * 80}")

        try:
            # Load the context
            if case_path.startswith("templates/"):
                case_type = case_path.split("/")[1]
                context_path = context_manager.templates_path / case_type / "case.json"
            else:
                context_path = context_manager.cases_path / case_path / "case.json"

            import json
            with open(context_path, 'r', encoding='utf-8') as f:
                context = json.load(f)

            # Validate the context
            result = context_manager.validate_case_context(context, check_urls=False)

            # Display results
            print(f"\n{result.get_summary()}")
            print()

            if result.stats:
                print("Statistics:")
                print(f"  • Case ID: {result.stats.get('case_id', 'N/A')}")
                print(f"  • Case Type: {result.stats.get('case_type', 'N/A')}")
                print(f"  • Documents: {result.stats.get('documents', 0)} total "
                      f"({result.stats.get('critical_documents', 0)} critical, "
                      f"{result.stats.get('optional_documents', 0)} optional)")
                print(f"  • Regulations: {result.stats.get('regulations', 0)} total "
                      f"({result.stats.get('regulations_valid', 0)} valid)")
                print(f"  • Common Issues: {result.stats.get('issues', 0)} total")
                if 'issues_by_severity' in result.stats:
                    severity_stats = result.stats['issues_by_severity']
                    print(f"    - Errors: {severity_stats.get('error', 0)}")
                    print(f"    - Warnings: {severity_stats.get('warning', 0)}")
                    print(f"    - Info: {severity_stats.get('info', 0)}")
                print(f"  • Validation Rules: {result.stats.get('validation_rules', 0)}")

            if result.errors:
                print(f"\n⚠️  Errors ({len(result.errors)}):")
                for error in result.errors[:5]:  # Show first 5 errors
                    print(f"  • {error}")
                if len(result.errors) > 5:
                    print(f"  ... and {len(result.errors) - 5} more error(s)")
                all_passed = False

            if result.warnings:
                print(f"\n⚠️  Warnings ({len(result.warnings)}):")
                for warning in result.warnings[:3]:  # Show first 3 warnings
                    print(f"  • {warning}")
                if len(result.warnings) > 3:
                    print(f"  ... and {len(result.warnings) - 3} more warning(s)")

            results.append({
                'case': description,
                'valid': result.valid,
                'errors': len(result.errors),
                'warnings': len(result.warnings)
            })

        except FileNotFoundError as e:
            print(f"❌ ERROR: File not found - {e}")
            all_passed = False
            results.append({
                'case': description,
                'valid': False,
                'errors': 1,
                'warnings': 0
            })
        except Exception as e:
            print(f"❌ ERROR: {type(e).__name__}: {e}")
            all_passed = False
            results.append({
                'case': description,
                'valid': False,
                'errors': 1,
                'warnings': 0
            })

    # Summary
    print(f"\n\n{'=' * 80}")
    print("VALIDATION SUMMARY")
    print(f"{'=' * 80}\n")

    for result in results:
        status = "✓ PASS" if result['valid'] else "✗ FAIL"
        print(f"{status} | {result['case']}")
        if result['errors'] > 0:
            print(f"       └─ {result['errors']} error(s), {result['warnings']} warning(s)")

    print()
    if all_passed:
        print("✅ All case contexts are valid!")
        return 0
    else:
        print("❌ Some case contexts have validation errors.")
        return 1


if __name__ == "__main__":
    exit_code = test_case_context_validation()
    sys.exit(exit_code)
