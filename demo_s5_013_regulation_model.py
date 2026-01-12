#!/usr/bin/env python3
"""
Demonstration script for S5-013: Enhanced Acte Context Research

This script demonstrates how to use the Regulation model to access
regulation details from case contexts.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.services.context_manager import ContextManager
from backend.models.regulation import get_regulation_details, Regulation


def demo_regulation_model():
    """Demonstrate Regulation model usage."""
    print("=" * 80)
    print("S5-013 Demonstration: Using the Regulation Model")
    print("=" * 80)
    print()

    context_manager = ContextManager()

    # Load Integration Course case context
    print("Loading Integration Course case context (ACTE-2024-001)...")
    context = context_manager.load_case_context("ACTE-2024-001")
    print(f"✓ Loaded case: {context['name']}")
    print(f"  Case Type: {context['caseType']}")
    print(f"  Total Regulations: {len(context['regulations'])}")
    print()

    # Example 1: Get specific regulation by ID
    print("─" * 80)
    print("Example 1: Retrieving specific regulation by ID")
    print("─" * 80)

    regulation_id = "§43_AufenthG"
    print(f"\nSearching for regulation: {regulation_id}")

    regulation = get_regulation_details(context['regulations'], regulation_id)

    if regulation:
        print(f"\n✓ Found regulation!")
        print(f"  ID: {regulation.id}")
        print(f"  Title: {regulation.title}")
        print(f"  URL: {regulation.url}")
        print(f"\n  Summary:")
        print(f"  {regulation.summary[:150]}...")

        # Validate the regulation
        errors = regulation.validate()
        if errors:
            print(f"\n  ⚠️  Validation errors: {errors}")
        else:
            print(f"\n  ✓ Regulation data is valid")
    else:
        print(f"❌ Regulation {regulation_id} not found")

    # Example 2: List all regulations
    print("\n" + "─" * 80)
    print("Example 2: Listing all regulations in the context")
    print("─" * 80)
    print()

    for idx, reg_data in enumerate(context['regulations'][:5], 1):
        reg = Regulation.from_dict(reg_data)
        print(f"{idx}. {reg.id}")
        print(f"   {reg.title}")
        print()

    if len(context['regulations']) > 5:
        print(f"   ... and {len(context['regulations']) - 5} more regulations")

    # Example 3: Access regulation from different case types
    print("\n" + "─" * 80)
    print("Example 3: Regulations in different case types")
    print("─" * 80)
    print()

    case_types = [
        ("integration_course", "Integration Course"),
        ("asylum_application", "Asylum Application"),
        ("family_reunification", "Family Reunification"),
    ]

    for case_type_id, case_type_name in case_types:
        # Load template context
        import json
        template_path = context_manager.templates_path / case_type_id / "case.json"
        with open(template_path, 'r', encoding='utf-8') as f:
            template_context = json.load(f)

        regulations = template_context['regulations']
        print(f"{case_type_name}:")
        print(f"  • Total Regulations: {len(regulations)}")

        # Show first regulation
        first_reg = Regulation.from_dict(regulations[0])
        print(f"  • First Regulation: {first_reg.id} - {first_reg.title}")
        print()

    # Example 4: Convert regulation to dictionary
    print("─" * 80)
    print("Example 4: Converting Regulation to dictionary for JSON serialization")
    print("─" * 80)
    print()

    regulation = get_regulation_details(context['regulations'], "§44_AufenthG")
    if regulation:
        reg_dict = regulation.to_dict()
        print(f"Regulation as dictionary:")
        import json
        print(json.dumps(reg_dict, indent=2, ensure_ascii=False))

    print("\n" + "=" * 80)
    print("✅ Demonstration complete!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        demo_regulation_model()
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
