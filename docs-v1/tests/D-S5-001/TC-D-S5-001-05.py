"""
Test Case: TC-D-S5-001-05
Requirement: D-S5-001 - SHACL Property Shape Schema
Description: Date field, verify sh:datatype = "xsd:date"
Generated: 2026-01-09T16:00:00Z

Note: This test validates SHACL datatype constraints for date fields
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.models.shacl_property_shape import create_date_shape
from backend.schemas.validation_patterns import DATE_PATTERN


def test_TC_D_S5_001_05():
    """Date field SHACL datatype validation"""
    # Test date fields using create_date_shape factory
    date_fields = [
        ("birthDate", "schema:birthDate", "Birth Date"),
        ("startDate", "schema:startDate", "Start Date"),
        ("expiryDate", "schema:expires", "Expiry Date"),
        ("applicationDate", "schema:applicationDate", "Application Date"),
    ]

    expected_pattern = r"^\d{4}-\d{2}-\d{2}$"

    for field_name, schema_path, display_name in date_fields:
        # Step 1: Create date shape
        shape = create_date_shape(schema_path, display_name, required=True)

        # Step 2: Convert to JSON-LD
        jsonld = shape.to_jsonld()

        # Step 3: Verify sh:datatype = "xsd:date"
        assert jsonld["sh:datatype"] == "xsd:date", \
            f"Expected sh:datatype 'xsd:date' for date field '{field_name}', got '{jsonld['sh:datatype']}'"

        # Step 4: Verify sh:datatype is NOT "xsd:string" or other type
        assert jsonld["sh:datatype"] != "xsd:string", \
            f"Date field '{field_name}' should use 'xsd:date', not 'xsd:string'"

        # Step 5: Verify sh:pattern includes YYYY-MM-DD format validation
        assert "sh:pattern" in jsonld, f"sh:pattern not found in date field '{field_name}'"
        assert jsonld["sh:pattern"] == expected_pattern, \
            f"Expected pattern '{expected_pattern}' for date field '{field_name}', got '{jsonld['sh:pattern']}'"

        # Step 6: Verify @context defines xsd namespace
        assert "@context" in jsonld, "@context not found in JSON-LD output"
        assert "xsd" in jsonld["@context"], "xsd namespace not defined in @context"
        assert jsonld["@context"]["xsd"] == "http://www.w3.org/2001/XMLSchema#"

        # Step 7: Verify sh:message mentions date format
        assert "sh:message" in jsonld, f"sh:message not found in date field '{field_name}'"
        message_lower = jsonld["sh:message"].lower()
        assert "date" in message_lower or "yyyy" in message_lower, \
            f"Date field '{field_name}' sh:message should mention date format: {jsonld['sh:message']}"

        # Step 8: Verify pattern matches DATE_PATTERN from validation_patterns.py
        assert shape.sh_pattern == DATE_PATTERN["pattern"], \
            f"Date pattern should match DATE_PATTERN constant"

    print("All assertions passed - All date fields use xsd:date datatype with YYYY-MM-DD pattern")

if __name__ == "__main__":
    try:
        test_TC_D_S5_001_05()
        print("TC-D-S5-001-05: PASSED")
    except AssertionError as e:
        print(f"TC-D-S5-001-05: FAILED - {e}")
    except Exception as e:
        print(f"TC-D-S5-001-05: ERROR - {e}")
