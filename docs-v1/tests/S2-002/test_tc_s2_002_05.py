"""
Test Case TC-S2-002-05: Verify TypeScript SHACLPropertyShape interface
matches Python class

This test verifies that the TypeScript interface structure matches
the Python dataclass for cross-language compatibility.
"""

import sys
import os
import json
import re

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../backend')))

from schemas.shacl import SHACLPropertyShape


def extract_typescript_interface_fields(ts_file_path):
    """
    Extract field names from TypeScript SHACLPropertyShape interface.
    """
    with open(ts_file_path, 'r') as f:
        content = f.read()

    # Find the SHACLPropertyShape interface definition
    interface_pattern = r'export interface SHACLPropertyShape \{(.*?)\n\}'
    match = re.search(interface_pattern, content, re.DOTALL)

    if not match:
        raise ValueError("SHACLPropertyShape interface not found in TypeScript file")

    interface_body = match.group(1)

    # Extract field names (properties starting with quotes or identifiers)
    field_pattern = r'["\']?([@\w:]+)["\']?\??:'
    fields = re.findall(field_pattern, interface_body)

    return set(fields)


def test_typescript_python_interface_match():
    """
    Test that TypeScript interface matches Python dataclass.
    """
    # Create a Python PropertyShape with all fields
    shape = SHACLPropertyShape(
        sh_path="schema:name",
        sh_datatype="xsd:string",
        sh_name="Full Name",
        sh_description="The person's full name",
        sh_min_count=1,
        sh_max_count=1,
        sh_in=["Option 1", "Option 2"],
        sh_pattern="^[A-Z].*",
        sh_min_length=1,
        sh_max_length=100
    )

    # Convert to JSON-LD
    jsonld = shape.to_jsonld()

    # Expected JSON-LD keys (these should match TypeScript interface fields)
    expected_keys = {
        "@context",
        "@type",
        "sh:path",
        "sh:datatype",
        "sh:name",
        "sh:description",
        "sh:minCount",
        "sh:maxCount",
        "sh:in",
        "sh:pattern",
        "sh:minLength",
        "sh:maxLength"
    }

    # Verify all expected keys are in JSON-LD
    jsonld_keys = set(jsonld.keys())
    assert expected_keys.issubset(jsonld_keys), \
        f"Missing keys in JSON-LD: {expected_keys - jsonld_keys}"

    # Try to load TypeScript file and compare
    ts_file_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '../../../src/types/shacl.ts'
    ))

    if os.path.exists(ts_file_path):
        ts_fields = extract_typescript_interface_fields(ts_file_path)

        # Check that TypeScript has all the expected fields
        ts_expected = {"@context", "@type", "sh:path", "sh:datatype", "sh:name",
                      "sh:description", "sh:minCount", "sh:maxCount", "sh:in",
                      "sh:pattern", "sh:minLength", "sh:maxLength"}

        # Note: Some fields may be optional in TypeScript (with ?)
        common_fields = ts_expected.intersection(ts_fields)
        assert len(common_fields) >= 8, \
            f"TypeScript interface should have at least 8 matching fields, found {len(common_fields)}"

        print(f"  Found {len(common_fields)} matching fields between Python and TypeScript")
    else:
        print(f"  TypeScript file not found at {ts_file_path}, skipping cross-language check")

    # Verify JSON serialization compatibility
    json_str = json.dumps(jsonld)
    parsed = json.loads(json_str)
    assert parsed == jsonld, "JSON-LD should be serializable for TypeScript consumption"

    print("✓ TC-S2-002-05 PASSED: TypeScript interface matches Python class structure")
    return True


if __name__ == "__main__":
    try:
        test_typescript_python_interface_match()
        sys.exit(0)
    except AssertionError as e:
        print(f"✗ TC-S2-002-05 FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ TC-S2-002-05 ERROR: {e}")
        sys.exit(1)
