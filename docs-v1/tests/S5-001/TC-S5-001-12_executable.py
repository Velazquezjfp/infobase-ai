"""
Test Case: TC-S5-001-12
Requirement: S5-001 - Natural Language Form Field Modification with SHACL Validation
Description: Add date field, verify sh:datatype="xsd:date" and sh:pattern for ISO date format
Generated: 2026-01-09T16:30:00Z

This is an executable API test for the /api/admin/modify-form endpoint.
"""

import json
import sys
import subprocess
from datetime import datetime


def test_TC_S5_001_12():
    """Test date field creation with XSD datatype and ISO date pattern"""

    test_start = datetime.now()

    # Test configuration
    base_url = "http://localhost:8000"
    endpoint = "/api/admin/modify-form"
    url = f"{base_url}{endpoint}"

    # Test data
    payload = {
        "command": "Add a date field for birth date",
        "currentFields": [],
        "caseId": "test-case-S5-001-12"
    }

    headers = {
        "Content-Type": "application/json"
    }

    print("=" * 80)
    print("TC-S5-001-12: Date Field with XSD Datatype and ISO Date Pattern")
    print("=" * 80)
    print(f"Test started at: {test_start.isoformat()}")
    print(f"Endpoint: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()

    try:
        # Step 1: Send POST request using curl
        print("Step 1: Sending POST request...")
        curl_command = [
            "curl",
            "-s",
            "-X", "POST",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(payload),
            url
        ]

        result = subprocess.run(curl_command, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            raise Exception(f"curl command failed: {result.stderr}")

        response_text = result.stdout
        print(f"Response received (length: {len(response_text)} chars)")

        # Step 2: Parse response
        print("\nStep 2: Parsing response...")
        response_data = json.loads(response_text)

        print(f"Response keys: {list(response_data.keys())}")

        # Step 3: Verify response includes field with semanticType="schema:Date" or "schema:birthDate"
        print("\nStep 3: Verifying field semanticType...")
        assert "fields" in response_data, "Response missing 'fields'"
        fields = response_data["fields"]
        assert len(fields) == 1, f"Expected 1 field, got {len(fields)}"

        date_field = fields[0]
        print(f"Date field: {json.dumps(date_field, indent=2)}")

        semantic_type = date_field.get("semanticType")
        # Accept either schema:Date or schema:birthDate
        assert semantic_type in ["schema:Date", "schema:birthDate"], \
            f"Expected 'schema:Date' or 'schema:birthDate', got '{semantic_type}'"
        print(f"✓ semanticType = {semantic_type}")

        # Step 4: Verify SHACL PropertyShape includes sh:datatype = "xsd:date"
        print("\nStep 4: Verifying SHACL shape...")
        assert "shaclShape" in response_data, "Response missing 'shaclShape'"

        shacl_shape = response_data["shaclShape"]
        assert "sh:property" in shacl_shape, "SHACL shape missing 'sh:property'"

        property_shapes = shacl_shape["sh:property"]
        assert len(property_shapes) >= 1, "SHACL shape has no property shapes"

        date_shape = property_shapes[0]
        print(f"Date PropertyShape: {json.dumps(date_shape, indent=2)}")

        # Step 5: Verify sh:path
        print("\nStep 5: Verifying sh:path...")
        sh_path = date_shape.get("sh:path")
        # Accept either schema:Date or schema:birthDate
        assert sh_path in ["schema:Date", "schema:birthDate"], \
            f"Expected 'schema:Date' or 'schema:birthDate', got '{sh_path}'"
        print(f"✓ sh:path = {sh_path}")

        # Step 6: Verify sh:datatype = "xsd:date"
        print("\nStep 6: Verifying sh:datatype...")
        sh_datatype = date_shape.get("sh:datatype")
        assert sh_datatype == "xsd:date", f"Expected 'xsd:date', got '{sh_datatype}'"
        print(f"✓ sh:datatype = {sh_datatype}")

        # Step 7: Verify sh:pattern for ISO date format (YYYY-MM-DD)
        print("\nStep 7: Verifying sh:pattern...")
        sh_pattern = date_shape.get("sh:pattern")
        assert sh_pattern is not None, "sh:pattern is missing"

        # ISO date pattern should match YYYY-MM-DD
        expected_pattern = r"^\d{4}-\d{2}-\d{2}$"
        assert sh_pattern == expected_pattern, f"Expected pattern '{expected_pattern}', got '{sh_pattern}'"
        print(f"✓ sh:pattern = {sh_pattern}")

        # Step 8: Verify sh:message
        print("\nStep 8: Verifying sh:message...")
        sh_message = date_shape.get("sh:message")
        assert sh_message is not None, "sh:message is missing"
        print(f"✓ sh:message = {sh_message}")

        # Step 9: Verify validationPattern matches ISO date format
        print("\nStep 9: Verifying validationPattern...")
        validation_pattern = date_field.get("validationPattern")
        assert validation_pattern == expected_pattern, \
            f"Expected pattern '{expected_pattern}', got '{validation_pattern}'"
        print(f"✓ validationPattern = {validation_pattern}")

        # Step 10: Verify field type is "date"
        print("\nStep 10: Verifying field type...")
        field_type = date_field.get("type")
        assert field_type == "date", f"Expected type 'date', got '{field_type}'"
        print(f"✓ field type = {field_type}")

        test_end = datetime.now()
        execution_time = (test_end - test_start).total_seconds()

        print()
        print("=" * 80)
        print("TC-S5-001-12: PASSED")
        print(f"Execution time: {execution_time:.2f} seconds")
        print("=" * 80)

        return {
            "status": "passed",
            "execution_time": execution_time,
            "timestamp": test_end.isoformat(),
            "error_message": None,
            "stack_trace": None
        }

    except AssertionError as e:
        test_end = datetime.now()
        execution_time = (test_end - test_start).total_seconds()
        error_msg = str(e)

        print()
        print("=" * 80)
        print(f"TC-S5-001-12: FAILED - {error_msg}")
        print(f"Execution time: {execution_time:.2f} seconds")
        print("=" * 80)

        return {
            "status": "failed",
            "execution_time": execution_time,
            "timestamp": test_end.isoformat(),
            "error_message": error_msg,
            "stack_trace": None
        }

    except Exception as e:
        test_end = datetime.now()
        execution_time = (test_end - test_start).total_seconds()
        error_msg = str(e)

        import traceback
        stack_trace = traceback.format_exc()

        print()
        print("=" * 80)
        print(f"TC-S5-001-12: ERROR - {error_msg}")
        print(f"Stack trace:\n{stack_trace}")
        print(f"Execution time: {execution_time:.2f} seconds")
        print("=" * 80)

        return {
            "status": "failed",
            "execution_time": execution_time,
            "timestamp": test_end.isoformat(),
            "error_message": error_msg,
            "stack_trace": stack_trace
        }


if __name__ == "__main__":
    result = test_TC_S5_001_12()
    sys.exit(0 if result["status"] == "passed" else 1)
