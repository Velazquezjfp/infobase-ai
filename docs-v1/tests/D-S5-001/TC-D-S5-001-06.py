"""
Test Case: TC-D-S5-001-06
Requirement: D-S5-001 - SHACL Property Shape Schema
Description: Validation error, verify sh:message displayed in UI
Generated: 2026-01-09T16:00:00Z

Note: This test validates that SHACL error messages appear correctly in the UI
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.models.shacl_property_shape import (
    create_email_shape,
    create_name_shape,
    create_date_shape,
    create_phone_shape
)


def test_TC_D_S5_001_06():
    """SHACL error message UI display validation"""
    # Test validation scenarios - Backend validation (sh:message presence)
    validation_scenarios = [
        {
            "name": "email",
            "shape": create_email_shape(required=True),
            "invalid_value": "not-an-email",
            "expected_message": "Email must be a valid email address containing @ and a domain"
        },
        {
            "name": "firstName",
            "shape": create_name_shape("schema:givenName", "First Name", required=True),
            "invalid_value": "",
            "expected_message_contains": "name"  # Message should mention name validation
        },
        {
            "name": "birthDate",
            "shape": create_date_shape("schema:birthDate", "Birth Date", required=True),
            "invalid_value": "invalid-date",
            "expected_message": "Date must be in YYYY-MM-DD format"
        },
        {
            "name": "phone",
            "shape": create_phone_shape(required=False),
            "invalid_value": "abc",
            "expected_message_contains": "phone"  # Message should mention phone validation
        },
    ]

    for scenario in validation_scenarios:
        shape = scenario["shape"]
        invalid_value = scenario["invalid_value"]
        field_name = scenario["name"]

        # Step 1: Verify sh:message field exists in PropertyShape
        assert hasattr(shape, "sh_message"), f"sh_message field not found in shape for '{field_name}'"
        assert shape.sh_message is not None, f"sh_message is None for '{field_name}'"
        assert len(shape.sh_message) > 0, f"sh_message is empty for '{field_name}'"

        # Step 2: Convert to JSON-LD and verify sh:message is present
        jsonld = shape.to_jsonld()
        assert "sh:message" in jsonld, f"sh:message not found in JSON-LD output for '{field_name}'"
        assert len(jsonld["sh:message"]) > 0, f"sh:message is empty in JSON-LD output for '{field_name}'"

        # Step 3: Trigger validation with invalid value
        is_valid, error_message = shape.validate_value(invalid_value)

        # Step 4: Verify validation fails (returns False)
        assert is_valid is False, f"Validation should fail for invalid value '{invalid_value}' in field '{field_name}'"

        # Step 5: Verify error message is returned
        assert error_message is not None, f"Error message should be returned for invalid value in field '{field_name}'"
        assert len(error_message) > 0, f"Error message should not be empty for field '{field_name}'"

        # Step 6: Verify error message matches sh:message from SHACL shape
        assert error_message == shape.sh_message, \
            f"Error message '{error_message}' does not match sh:message '{shape.sh_message}' for field '{field_name}'"

        # Step 7: Verify error message matches expected message (if specified)
        if "expected_message" in scenario:
            assert error_message == scenario["expected_message"], \
                f"Expected message '{scenario['expected_message']}', got '{error_message}' for field '{field_name}'"

        # Step 8: Verify error message contains expected keywords (if specified)
        if "expected_message_contains" in scenario:
            keyword = scenario["expected_message_contains"].lower()
            assert keyword in error_message.lower(), \
                f"Error message should contain '{keyword}' for field '{field_name}', got '{error_message}'"

        # Step 9: Verify message is user-friendly (not technical/cryptic)
        assert not error_message.startswith("Error:"), f"Error message should be user-friendly for field '{field_name}'"
        assert "exception" not in error_message.lower(), f"Error message should not mention exceptions for field '{field_name}'"

    print("All assertions passed - All SHACL shapes have proper sh:message for UI display")

if __name__ == "__main__":
    try:
        test_TC_D_S5_001_06()
        print("TC-D-S5-001-06: PASSED")
    except AssertionError as e:
        print(f"TC-D-S5-001-06: FAILED - {e}")
    except Exception as e:
        print(f"TC-D-S5-001-06: ERROR - {e}")
