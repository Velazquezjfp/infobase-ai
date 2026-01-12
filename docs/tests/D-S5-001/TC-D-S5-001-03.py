"""
Test Case: TC-D-S5-001-03
Requirement: D-S5-001 - SHACL Property Shape Schema
Description: Required field, verify sh:minCount = 1
Generated: 2026-01-09T16:00:00Z

Note: This test validates SHACL cardinality constraints for required fields
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.models.shacl_property_shape import (
    create_email_shape,
    create_name_shape,
    create_date_shape,
    create_address_shape
)


def test_TC_D_S5_001_03():
    """Required field SHACL cardinality validation"""
    # Test required fields using factory functions
    required_fields = [
        ("firstName", create_name_shape("schema:givenName", "First Name", required=True)),
        ("lastName", create_name_shape("schema:familyName", "Last Name", required=True)),
        ("email", create_email_shape(required=True)),
        ("birthDate", create_date_shape("schema:birthDate", "Birth Date", required=True)),
        ("address", create_address_shape(required=True)),
    ]

    for field_name, shape in required_fields:
        # Step 1: Convert to JSON-LD
        jsonld = shape.to_jsonld()

        # Step 2: Verify sh:minCount present in shape
        assert "sh:minCount" in jsonld, f"sh:minCount not found in required field '{field_name}'"

        # Step 3: Verify sh:minCount = 1
        assert jsonld["sh:minCount"] == 1, \
            f"Expected sh:minCount = 1 for required field '{field_name}', got {jsonld['sh:minCount']}"

        # Step 4: Verify shape has sh:message
        assert "sh:message" in jsonld, f"sh:message not found in required field '{field_name}'"
        assert len(jsonld["sh:message"]) > 0, f"sh:message is empty for required field '{field_name}'"

        # Step 5: Verify is_required() method returns True
        assert shape.is_required() is True, f"is_required() returned False for required field '{field_name}'"

        # Step 6: Verify sh:minCount is not 0 or other value
        assert jsonld["sh:minCount"] != 0, f"sh:minCount should not be 0 for required field '{field_name}'"

    print("All assertions passed - All required fields have sh:minCount = 1")

if __name__ == "__main__":
    try:
        test_TC_D_S5_001_03()
        print("TC-D-S5-001-03: PASSED")
    except AssertionError as e:
        print(f"TC-D-S5-001-03: FAILED - {e}")
    except Exception as e:
        print(f"TC-D-S5-001-03: ERROR - {e}")
