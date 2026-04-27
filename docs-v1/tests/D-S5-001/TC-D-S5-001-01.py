"""
Test Case: TC-D-S5-001-01
Requirement: D-S5-001 - SHACL Property Shape Schema
Description: Generate SHACL shape for email field, verify includes sh:pattern for email validation
Generated: 2026-01-09T16:00:00Z

Note: This test validates SHACL property shape generation with email validation pattern
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.models.shacl_property_shape import create_email_shape
from backend.schemas.validation_patterns import EMAIL_PATTERN


def test_TC_D_S5_001_01():
    """SHACL shape generation for email field with pattern validation"""
    # Step 1: Create email shape using factory method
    email_shape = create_email_shape(required=True)

    # Step 2: Convert to JSON-LD
    jsonld = email_shape.to_jsonld()

    # Step 3: Verify sh:path = "schema:email"
    assert jsonld["sh:path"] == "schema:email", f"Expected sh:path 'schema:email', got '{jsonld['sh:path']}'"

    # Step 4: Verify sh:datatype = "xsd:string"
    assert jsonld["sh:datatype"] == "xsd:string", f"Expected sh:datatype 'xsd:string', got '{jsonld['sh:datatype']}'"

    # Step 5: Verify sh:pattern with email regex
    expected_pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    assert jsonld.get("sh:pattern") == expected_pattern, \
        f"Expected sh:pattern '{expected_pattern}', got '{jsonld.get('sh:pattern')}'"

    # Step 6: Verify sh:message for validation errors
    expected_message = "Email must be a valid email address containing @ and a domain"
    assert jsonld["sh:message"] == expected_message, \
        f"Expected sh:message '{expected_message}', got '{jsonld['sh:message']}'"

    # Step 7: Verify sh:name = "Email Address"
    assert jsonld["sh:name"] == "Email Address", f"Expected sh:name 'Email Address', got '{jsonld['sh:name']}'"

    # Step 8: Verify @context includes required namespaces
    assert "@context" in jsonld, "@context not found in JSON-LD output"
    assert jsonld["@context"]["sh"] == "http://www.w3.org/ns/shacl#"
    assert jsonld["@context"]["schema"] == "http://schema.org/"
    assert jsonld["@context"]["xsd"] == "http://www.w3.org/2001/XMLSchema#"

    # Step 9: Verify @type = "sh:PropertyShape"
    assert jsonld["@type"] == "sh:PropertyShape"

    # Step 10: Verify pattern matches EMAIL_PATTERN from validation_patterns.py
    assert email_shape.sh_pattern == EMAIL_PATTERN["pattern"]

    print("All assertions passed")

if __name__ == "__main__":
    try:
        test_TC_D_S5_001_01()
        print("TC-D-S5-001-01: PASSED")
    except AssertionError as e:
        print(f"TC-D-S5-001-01: FAILED - {e}")
    except Exception as e:
        print(f"TC-D-S5-001-01: ERROR - {e}")
