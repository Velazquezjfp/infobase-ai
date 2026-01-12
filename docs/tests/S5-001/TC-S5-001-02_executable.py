"""
Test Case: TC-S5-001-02
Requirement: S5-001 - Natural Language Form Field Modification with SHACL Validation
Description: Verify generated SHACL shape has sh:path="schema:email" and sh:pattern for email validation
Generated: 2026-01-09T16:30:00Z

This is an executable API test for the /api/admin/modify-form endpoint.
"""

import json
import sys
import subprocess
from datetime import datetime


def test_TC_S5_001_02():
    """Test SHACL shape generation for email field via API"""

    test_start = datetime.now()

    # Test configuration
    base_url = "http://localhost:8000"
    endpoint = "/api/admin/modify-form"
    url = f"{base_url}{endpoint}"

    # Test data
    payload = {
        "command": "Add an email field for contact email",
        "currentFields": [],
        "caseId": "test-case-S5-001-02"
    }

    print("=" * 80)
    print("TC-S5-001-02: SHACL Shape Generation for Email Field")
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

        # Step 3: Verify response includes shaclShape object
        print("\nStep 3: Verifying shaclShape exists...")
        assert "shaclShape" in response_data, "Response missing 'shaclShape' field"

        shacl_shape = response_data["shaclShape"]
        print(f"SHACL Shape type: {shacl_shape.get('@type')}")

        # Step 4: Verify SHACL shape has PropertyShape
        print("\nStep 4: Verifying SHACL PropertyShape...")
        assert "sh:property" in shacl_shape, "SHACL shape missing 'sh:property' field"

        property_shapes = shacl_shape["sh:property"]
        assert len(property_shapes) >= 1, "SHACL shape has no property shapes"

        # Find email property shape
        email_shape = property_shapes[0]  # Should be the first (and only) field
        print(f"Email PropertyShape: {json.dumps(email_shape, indent=2)}")

        # Step 5: Verify sh:path = "schema:email"
        print("\nStep 5: Verifying sh:path...")
        sh_path = email_shape.get("sh:path")
        assert sh_path == "schema:email", f"Expected 'schema:email', got '{sh_path}'"
        print(f"✓ sh:path = {sh_path}")

        # Step 6: Verify sh:pattern for email validation
        print("\nStep 6: Verifying sh:pattern...")
        sh_pattern = email_shape.get("sh:pattern")
        assert sh_pattern is not None, "sh:pattern is missing"

        # Email pattern should match the expected regex
        expected_pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
        assert sh_pattern == expected_pattern, f"Expected pattern '{expected_pattern}', got '{sh_pattern}'"
        print(f"✓ sh:pattern = {sh_pattern}")

        # Step 7: Verify sh:message
        print("\nStep 7: Verifying sh:message...")
        sh_message = email_shape.get("sh:message")
        assert sh_message is not None, "sh:message is missing"
        assert "email" in sh_message.lower() or "@" in sh_message, f"Message should mention email: {sh_message}"
        print(f"✓ sh:message = {sh_message}")

        # Step 8: Verify fields list includes new email field
        print("\nStep 8: Verifying fields list...")
        assert "fields" in response_data, "Response missing 'fields'"
        fields = response_data["fields"]
        assert len(fields) == 1, f"Expected 1 field, got {len(fields)}"

        email_field = fields[0]
        print(f"Email field: {json.dumps(email_field, indent=2)}")

        # Step 9: Verify semanticType = "schema:email"
        print("\nStep 9: Verifying semanticType...")
        semantic_type = email_field.get("semanticType")
        assert semantic_type == "schema:email", f"Expected 'schema:email', got '{semantic_type}'"
        print(f"✓ semanticType = {semantic_type}")

        # Step 10: Verify validationPattern
        print("\nStep 10: Verifying validationPattern...")
        validation_pattern = email_field.get("validationPattern")
        assert validation_pattern == expected_pattern, f"Expected pattern '{expected_pattern}', got '{validation_pattern}'"
        print(f"✓ validationPattern = {validation_pattern}")

        test_end = datetime.now()
        execution_time = (test_end - test_start).total_seconds()

        print()
        print("=" * 80)
        print("TC-S5-001-02: PASSED")
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
        print(f"TC-S5-001-02: FAILED - {error_msg}")
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
        print(f"TC-S5-001-02: ERROR - {error_msg}")
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
    result = test_TC_S5_001_02()
    sys.exit(0 if result["status"] == "passed" else 1)
