"""
Test Case TC-S2-002-06: Import SHACL schemas in field_generator service,
verify no import errors

This test verifies that SHACL schema modules can be imported by other
services without errors, ensuring proper package structure.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../backend')))


def test_shacl_imports():
    """
    Test that SHACL schemas can be imported without errors.
    """
    # Test individual module imports
    try:
        from schemas import shacl
        print("  ✓ schemas.shacl module imported successfully")
    except ImportError as e:
        raise AssertionError(f"Failed to import schemas.shacl: {e}")

    try:
        from schemas import jsonld_context
        print("  ✓ schemas.jsonld_context module imported successfully")
    except ImportError as e:
        raise AssertionError(f"Failed to import schemas.jsonld_context: {e}")

    # Test package-level imports
    try:
        from schemas import (
            SHACLPropertyShape,
            SHACLNodeShape,
            SHACL_CONTEXT,
            build_field_context
        )
        print("  ✓ Package-level imports successful")
    except ImportError as e:
        raise AssertionError(f"Failed to import from schemas package: {e}")

    # Verify classes are accessible
    assert hasattr(SHACLPropertyShape, 'to_jsonld'), \
        "SHACLPropertyShape should have to_jsonld method"
    assert hasattr(SHACLNodeShape, 'to_jsonld'), \
        "SHACLNodeShape should have to_jsonld method"

    # Test that helper functions work
    try:
        context = build_field_context("text", "Test Field", required=True)
        assert "@context" in context, "build_field_context should return valid context"
        print("  ✓ build_field_context helper function works")
    except Exception as e:
        raise AssertionError(f"build_field_context failed: {e}")

    # Test imports in a simulated field_generator context
    try:
        # Simulate field_generator service imports
        from schemas.shacl import SHACLPropertyShape
        from schemas.jsonld_context import (
            get_xsd_datatype,
            get_schema_org_property,
            build_field_context
        )

        # Create a sample field using the imports
        shape = SHACLPropertyShape(
            sh_path="schema:name",
            sh_datatype=get_xsd_datatype("text"),
            sh_name="Full Name",
            sh_min_count=1
        )

        jsonld = shape.to_jsonld()
        assert jsonld["@type"] == "sh:PropertyShape"

        print("  ✓ Simulated field_generator imports work correctly")
    except Exception as e:
        raise AssertionError(f"Simulated field_generator import failed: {e}")

    # Verify __all__ exports
    import schemas
    assert hasattr(schemas, '__all__'), "schemas package should have __all__ defined"
    assert 'SHACLPropertyShape' in schemas.__all__, \
        "SHACLPropertyShape should be in __all__"
    assert 'build_field_context' in schemas.__all__, \
        "build_field_context should be in __all__"

    print("✓ TC-S2-002-06 PASSED: SHACL schemas can be imported in field_generator service")
    return True


if __name__ == "__main__":
    try:
        test_shacl_imports()
        sys.exit(0)
    except AssertionError as e:
        print(f"✗ TC-S2-002-06 FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ TC-S2-002-06 ERROR: {e}")
        sys.exit(1)
