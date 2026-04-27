"""
Test Case TC-S2-002-02: Create SHACLPropertyShape with required constraint,
verify sh:minCount = 1

This test verifies that a required field has sh:minCount set to 1.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../backend')))

from schemas.shacl import SHACLPropertyShape


def test_shacl_property_shape_required_constraint():
    """
    Test that a required field has sh:minCount = 1.
    """
    # Create a required PropertyShape
    shape = SHACLPropertyShape(
        sh_path="schema:birthDate",
        sh_datatype="xsd:date",
        sh_name="Birth Date",
        sh_min_count=1  # Required field
    )

    # Convert to JSON-LD
    jsonld = shape.to_jsonld()

    # Verify sh:minCount is present and equals 1
    assert "sh:minCount" in jsonld, "sh:minCount missing from required field"
    assert jsonld["sh:minCount"] == 1, \
        f"sh:minCount should be 1 for required field, got {jsonld['sh:minCount']}"

    # Test optional field (no minCount)
    optional_shape = SHACLPropertyShape(
        sh_path="schema:email",
        sh_datatype="xsd:string",
        sh_name="Email"
        # No sh_min_count specified
    )

    optional_jsonld = optional_shape.to_jsonld()

    # Verify sh:minCount is not present (or is None/0)
    assert "sh:minCount" not in optional_jsonld or optional_jsonld.get("sh:minCount") is None, \
        "Optional field should not have sh:minCount"

    print("✓ TC-S2-002-02 PASSED: Required constraint correctly sets sh:minCount = 1")
    return True


if __name__ == "__main__":
    try:
        test_shacl_property_shape_required_constraint()
        sys.exit(0)
    except AssertionError as e:
        print(f"✗ TC-S2-002-02 FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ TC-S2-002-02 ERROR: {e}")
        sys.exit(1)
