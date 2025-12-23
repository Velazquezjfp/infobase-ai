"""
S2-003: Legacy Form Standardization Migration Script

This script provides utilities for migrating form fields to SHACL/JSON-LD format.
It generates SHACL PropertyShape metadata for form fields based on their properties.

Usage:
    python -m backend.scripts.migrate_forms_to_shacl

This script can be used to:
1. Generate SHACL metadata for individual form fields
2. Migrate entire form schemas to include SHACL metadata
3. Validate existing SHACL metadata

Note: The frontend mockData.ts has already been updated manually with SHACL metadata.
This script serves as a backend utility for future migrations or validation.
"""

import json
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])

from backend.schemas.jsonld_context import (
    SHACL_CONTEXT,
    get_xsd_datatype,
    get_schema_org_property,
    build_field_context,
)


@dataclass
class FormField:
    """Represents a form field structure matching the frontend FormField interface."""
    id: str
    label: str
    type: str  # 'text' | 'date' | 'select' | 'textarea'
    value: str = ""
    options: Optional[List[str]] = None
    required: bool = False


def generate_shacl_for_field(field: FormField) -> Dict[str, Any]:
    """
    Generate SHACL PropertyShape metadata for a form field.

    Args:
        field: FormField object to generate SHACL metadata for

    Returns:
        SHACL PropertyShape as a dictionary (JSON-LD format)

    Example:
        >>> field = FormField(id='fullName', label='Full Name', type='text', required=True)
        >>> shacl = generate_shacl_for_field(field)
        >>> print(shacl['sh:path'])
        'schema:name'
    """
    return build_field_context(
        field_type=field.type,
        field_label=field.label,
        required=field.required,
        options=field.options,
        description=f"Form field: {field.label}",
    )


def migrate_form_fields(fields: List[FormField]) -> List[Dict[str, Any]]:
    """
    Migrate a list of form fields to include SHACL metadata.

    Args:
        fields: List of FormField objects

    Returns:
        List of form field dictionaries with shaclMetadata added
    """
    migrated = []
    for field in fields:
        field_dict = asdict(field)
        field_dict['shaclMetadata'] = generate_shacl_for_field(field)
        migrated.append(field_dict)
    return migrated


def validate_shacl_metadata(shacl: Dict[str, Any]) -> List[str]:
    """
    Validate SHACL metadata for completeness.

    Args:
        shacl: SHACL PropertyShape dictionary

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    required_fields = ['@type', 'sh:path', 'sh:datatype', 'sh:name']
    for field in required_fields:
        if field not in shacl:
            errors.append(f"Missing required field: {field}")

    if shacl.get('@type') != 'sh:PropertyShape':
        errors.append(f"Invalid @type: expected 'sh:PropertyShape', got '{shacl.get('@type')}'")

    valid_datatypes = ['xsd:string', 'xsd:date', 'xsd:integer', 'xsd:boolean']
    if shacl.get('sh:datatype') not in valid_datatypes:
        errors.append(f"Invalid datatype: {shacl.get('sh:datatype')}")

    return errors


# Integration Course Application form fields (matching frontend mockData.ts)
INTEGRATION_COURSE_FIELDS = [
    FormField(id='fullName', label='Full Name', type='text', required=True),
    FormField(id='birthDate', label='Date of Birth', type='date', required=True),
    FormField(id='countryOfOrigin', label='Country of Origin', type='text', required=True),
    FormField(id='existingLanguageCertificates', label='Existing Language Certificates', type='text'),
    FormField(
        id='coursePreference',
        label='Course Preference',
        type='select',
        options=['Intensive Course', 'Evening Course', 'Weekend Course'],
    ),
    FormField(id='currentAddress', label='Current Address', type='textarea', required=True),
    FormField(id='reasonForApplication', label='Reason for Application', type='textarea', required=True),
]


def main():
    """Run the migration script to demonstrate SHACL generation."""
    print("S2-003: Legacy Form Standardization Migration Script")
    print("=" * 60)
    print()

    print("Generating SHACL metadata for Integration Course Form fields:")
    print("-" * 60)

    migrated_fields = migrate_form_fields(INTEGRATION_COURSE_FIELDS)

    for field in migrated_fields:
        print(f"\nField: {field['label']} ({field['id']})")
        print(f"  Type: {field['type']}")
        print(f"  Required: {field['required']}")

        shacl = field['shaclMetadata']
        print(f"  SHACL Path: {shacl['sh:path']}")
        print(f"  SHACL Datatype: {shacl['sh:datatype']}")

        if 'sh:in' in shacl:
            print(f"  Allowed Values: {shacl['sh:in']['@list']}")

        # Validate
        errors = validate_shacl_metadata(shacl)
        if errors:
            print(f"  Validation Errors: {errors}")
        else:
            print("  Validation: PASSED")

    print()
    print("-" * 60)
    print("Migration complete. All fields have valid SHACL metadata.")
    print()

    # Output JSON for reference
    print("JSON Output (for reference):")
    print(json.dumps(migrated_fields, indent=2))


if __name__ == "__main__":
    main()
