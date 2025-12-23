"""
Test Case TC-S2-002-03: Create SHACLPropertyShape for date field,
verify sh:datatype = xsd:date

This test verifies that a date field has the correct XSD datatype.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../backend')))

from schemas.shacl import SHACLPropertyShape
from schemas.jsonld_context import get_xsd_datatype


def test_shacl_property_shape_date_datatype():
    """
    Test that a date field has sh:datatype = xsd:date.
    """
    # Create a PropertyShape for a date field
    shape = SHACLPropertyShape(
        sh_path="schema:birthDate",
        sh_datatype="xsd:date",
        sh_name="Birth Date",
        sh_min_count=1
    )

    # Convert to JSON-LD
    jsonld = shape.to_jsonld()

    # Verify sh:datatype is xsd:date
    assert "sh:datatype" in jsonld, "sh:datatype missing from JSON-LD output"
    assert jsonld["sh:datatype"] == "xsd:date", \
        f"Incorrect datatype for date field: {jsonld['sh:datatype']}, expected xsd:date"

    # Test helper function
    date_datatype = get_xsd_datatype("date")
    assert date_datatype == "xsd:date", \
        f"get_xsd_datatype('date') returned {date_datatype}, expected xsd:date"

    # Test other field types for completeness
    assert get_xsd_datatype("text") == "xsd:string"
    assert get_xsd_datatype("select") == "xsd:string"
    assert get_xsd_datatype("textarea") == "xsd:string"
    assert get_xsd_datatype("number") == "xsd:integer"

    print("✓ TC-S2-002-03 PASSED: Date field has correct sh:datatype = xsd:date")
    return True


if __name__ == "__main__":
    try:
        test_shacl_property_shape_date_datatype()
        sys.exit(0)
    except AssertionError as e:
        print(f"✗ TC-S2-002-03 FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ TC-S2-002-03 ERROR: {e}")
        sys.exit(1)
