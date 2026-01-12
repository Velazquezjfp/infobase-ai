"""
Test Case: TC-D-S5-001-02
Requirement: D-S5-001 - SHACL Property Shape Schema
Description: Verify sh:path uses schema.org vocabulary (schema:email, schema:name)
Generated: 2026-01-09T16:00:00Z

Note: This test validates proper schema.org vocabulary usage in SHACL shapes
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.models.shacl_property_shape import (
    create_email_shape,
    create_name_shape,
    create_date_shape,
    create_phone_shape,
    create_address_shape
)


def test_TC_D_S5_001_02():
    """Schema.org vocabulary usage validation"""
    # Test field mappings with factory functions
    test_shapes = [
        (create_email_shape(required=True), "schema:email", "Email Address"),
        (create_name_shape("schema:givenName", "First Name", required=True), "schema:givenName", "First Name"),
        (create_name_shape("schema:familyName", "Last Name", required=True), "schema:familyName", "Last Name"),
        (create_phone_shape(required=False), "schema:telephone", "Phone Number"),
        (create_address_shape(required=True), "schema:address", "Address"),
        (create_date_shape("schema:birthDate", "Birth Date", required=True), "schema:birthDate", "Birth Date"),
    ]

    expected_context = {
        "sh": "http://www.w3.org/ns/shacl#",
        "schema": "http://schema.org/",
        "xsd": "http://www.w3.org/2001/XMLSchema#"
    }

    for shape, expected_path, expected_name in test_shapes:
        # Step 1: Convert to JSON-LD
        jsonld = shape.to_jsonld()

        # Step 2: Verify sh:path starts with "schema:"
        assert jsonld["sh:path"].startswith("schema:"), \
            f"sh:path '{jsonld['sh:path']}' does not start with 'schema:'"

        # Step 3: Verify sh:path matches expected schema.org property
        assert jsonld["sh:path"] == expected_path, \
            f"Expected sh:path '{expected_path}', got '{jsonld['sh:path']}'"

        # Step 4: Verify @context includes schema.org namespace definition
        assert "@context" in jsonld, "@context not found in JSON-LD output"
        assert jsonld["@context"] == expected_context, \
            f"@context does not match expected namespaces"

        # Step 5: Verify no custom namespaces used (only sh, schema, xsd)
        for key in jsonld.keys():
            if key.startswith("@"):
                continue
            prefix = key.split(":")[0] if ":" in key else None
            if prefix:
                assert prefix in ["sh", "schema", "xsd"], \
                    f"Custom namespace '{prefix}' found, only 'sh', 'schema', 'xsd' allowed"

    print("All assertions passed - All shapes use schema.org vocabulary correctly")

if __name__ == "__main__":
    try:
        test_TC_D_S5_001_02()
        print("TC-D-S5-001-02: PASSED")
    except AssertionError as e:
        print(f"TC-D-S5-001-02: FAILED - {e}")
    except Exception as e:
        print(f"TC-D-S5-001-02: ERROR - {e}")
