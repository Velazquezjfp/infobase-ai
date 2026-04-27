"""
Test Case TC-S2-002-04: Validate JSON-LD context against JSON-LD specification

This test verifies that the JSON-LD context structure follows the JSON-LD
specification and includes all required namespaces.
"""

import sys
import os
import json

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../backend')))

from schemas.jsonld_context import SHACL_CONTEXT, SCHEMA_ORG_CONTEXT
from schemas.shacl import SHACLPropertyShape, SHACLNodeShape


def test_jsonld_context_structure():
    """
    Test that JSON-LD contexts follow the specification.
    """
    # Verify SHACL_CONTEXT structure
    assert isinstance(SHACL_CONTEXT, dict), "SHACL_CONTEXT should be a dictionary"

    required_namespaces = ["sh", "schema", "xsd"]
    for ns in required_namespaces:
        assert ns in SHACL_CONTEXT, f"Required namespace '{ns}' missing from SHACL_CONTEXT"
        assert isinstance(SHACL_CONTEXT[ns], str), f"Namespace '{ns}' value should be a string"
        assert SHACL_CONTEXT[ns].startswith("http"), \
            f"Namespace '{ns}' should be a valid HTTP(S) URL"

    # Verify SCHEMA_ORG_CONTEXT structure
    assert isinstance(SCHEMA_ORG_CONTEXT, dict), "SCHEMA_ORG_CONTEXT should be a dictionary"
    assert "schema" in SCHEMA_ORG_CONTEXT

    # Test PropertyShape JSON-LD structure
    shape = SHACLPropertyShape(
        sh_path="schema:name",
        sh_datatype="xsd:string",
        sh_name="Full Name"
    )

    jsonld = shape.to_jsonld()

    # Verify JSON-LD structure is valid JSON
    json_str = json.dumps(jsonld)
    parsed = json.loads(json_str)
    assert parsed == jsonld, "JSON-LD should be serializable and parseable"

    # Verify required JSON-LD keywords
    assert "@context" in jsonld, "@context is required in JSON-LD"
    assert "@type" in jsonld, "@type is required in JSON-LD"

    # Verify @type uses prefixed notation
    assert jsonld["@type"].startswith("sh:"), "@type should use namespace prefix"

    # Verify property names use prefixed notation
    for key in jsonld.keys():
        if key.startswith("sh:") or key.startswith("schema:") or key.startswith("xsd:"):
            # These should be valid prefixed names
            prefix = key.split(":")[0]
            assert prefix in jsonld["@context"], \
                f"Prefix '{prefix}' used but not defined in @context"

    # Test NodeShape JSON-LD structure
    node_shape = SHACLNodeShape(
        sh_target_class="schema:Person",
        sh_name="Person Form",
        sh_properties=[shape]
    )

    node_jsonld = node_shape.to_jsonld()

    # Verify NodeShape JSON-LD structure
    assert "@context" in node_jsonld
    assert "@type" in node_jsonld
    assert node_jsonld["@type"] == "sh:NodeShape"
    assert "sh:property" in node_jsonld
    assert isinstance(node_jsonld["sh:property"], list)

    print("✓ TC-S2-002-04 PASSED: JSON-LD context follows specification")
    return True


if __name__ == "__main__":
    try:
        test_jsonld_context_structure()
        sys.exit(0)
    except AssertionError as e:
        print(f"✗ TC-S2-002-04 FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ TC-S2-002-04 ERROR: {e}")
        sys.exit(1)
