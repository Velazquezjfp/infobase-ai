"""
Test Case TC-S2-002-01: Create SHACLPropertyShape for text field,
verify @context includes SHACL namespace

This test verifies that a SHACLPropertyShape for a text field includes
the correct JSON-LD @context with SHACL namespace definitions.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../backend')))

from schemas.shacl import SHACLPropertyShape


def test_shacl_property_shape_text_field_context():
    """
    Test that a text field SHACLPropertyShape includes the correct @context.
    """
    # Create a PropertyShape for a text field
    shape = SHACLPropertyShape(
        sh_path="schema:name",
        sh_datatype="xsd:string",
        sh_name="Full Name"
    )

    # Convert to JSON-LD
    jsonld = shape.to_jsonld()

    # Verify @context exists
    assert "@context" in jsonld, "@context missing from JSON-LD output"

    context = jsonld["@context"]

    # Verify SHACL namespace
    assert "sh" in context, "SHACL namespace 'sh' missing from @context"
    assert context["sh"] == "http://www.w3.org/ns/shacl#", \
        f"Incorrect SHACL namespace URL: {context['sh']}"

    # Verify Schema.org namespace
    assert "schema" in context, "Schema.org namespace 'schema' missing from @context"
    assert context["schema"] == "http://schema.org/", \
        f"Incorrect Schema.org namespace URL: {context['schema']}"

    # Verify XSD namespace
    assert "xsd" in context, "XSD namespace 'xsd' missing from @context"
    assert context["xsd"] == "http://www.w3.org/2001/XMLSchema#", \
        f"Incorrect XSD namespace URL: {context['xsd']}"

    # Verify @type
    assert jsonld["@type"] == "sh:PropertyShape", \
        f"Incorrect @type: {jsonld['@type']}"

    # Verify basic properties
    assert jsonld["sh:path"] == "schema:name"
    assert jsonld["sh:datatype"] == "xsd:string"
    assert jsonld["sh:name"] == "Full Name"

    print("✓ TC-S2-002-01 PASSED: Text field PropertyShape has correct @context with SHACL namespace")
    return True


if __name__ == "__main__":
    try:
        test_shacl_property_shape_text_field_context()
        sys.exit(0)
    except AssertionError as e:
        print(f"✗ TC-S2-002-01 FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ TC-S2-002-01 ERROR: {e}")
        sys.exit(1)
