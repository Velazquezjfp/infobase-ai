"""
Test Case: TC-D-S5-001-04
Requirement: D-S5-001 - SHACL Property Shape Schema
Description: Optional field, verify sh:minCount not set or = 0
Generated: 2026-01-09T16:00:00Z

Note: This test validates SHACL cardinality constraints for optional fields
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.models.shacl_property_shape import (
    create_phone_shape,
    create_name_shape,
    SHACLPropertyShape
)


def test_TC_D_S5_001_04():
    """Optional field SHACL cardinality validation"""
    # Test optional fields using factory functions
    optional_fields = [
        ("middleName", create_name_shape("schema:additionalName", "Middle Name", required=False)),
        ("phone", create_phone_shape(required=False)),
        ("occupation", SHACLPropertyShape.create_for_field_type(
            "Occupation", "text", "schema:jobTitle", required=False
        )),
        ("additionalNotes", SHACLPropertyShape.create_for_field_type(
            "Additional Notes", "textarea", "schema:description", required=False
        )),
    ]

    for field_name, shape in optional_fields:
        # Step 1: Convert to JSON-LD
        jsonld = shape.to_jsonld()

        # Step 2: Check if sh:minCount present in shape
        if "sh:minCount" in jsonld:
            # If present, verify sh:minCount = 0 (not 1 or other value)
            assert jsonld["sh:minCount"] == 0, \
                f"If sh:minCount is present for optional field '{field_name}', it must be 0, got {jsonld['sh:minCount']}"
        # If sh:minCount not present, this is also valid (field is optional by default)

        # Step 3: Verify is_required() method returns False
        assert shape.is_required() is False, f"is_required() returned True for optional field '{field_name}'"

        # Step 4: Verify field can accept empty value
        is_valid, error = shape.validate_value("")
        assert is_valid is True, f"Optional field '{field_name}' should accept empty value, but got error: {error}"

        is_valid, error = shape.validate_value(None)
        assert is_valid is True, f"Optional field '{field_name}' should accept None value, but got error: {error}"

    print("All assertions passed - All optional fields correctly have sh:minCount not set or = 0")

if __name__ == "__main__":
    try:
        test_TC_D_S5_001_04()
        print("TC-D-S5-001-04: PASSED")
    except AssertionError as e:
        print(f"TC-D-S5-001-04: FAILED - {e}")
    except Exception as e:
        print(f"TC-D-S5-001-04: ERROR - {e}")
