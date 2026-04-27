"""
Test Case: TC-S4-001-03
Description: Drop 20 MB file, verify error message "File exceeds 15 MB limit"
Category: Backend API / Validation
Type: Python / Integration Test
"""

import pytest
import os
import tempfile
import requests
from pathlib import Path


def test_reject_oversized_20mb_file():
    """
    Test that files exceeding 15 MB limit are rejected with appropriate error.

    Steps:
    1. Create a temporary 20 MB test file (exceeds 15 MB limit)
    2. POST to /api/files/upload with file, caseId, folderId=uploads
    3. Verify response status 413 (Payload Too Large)
    4. Verify error message contains "File exceeds 15 MB limit" or similar
    5. Verify file is NOT saved in public/documents/{caseId}/uploads/

    Expected Result:
    - Upload fails with 413 status code
    - Clear error message about size limit
    - No file saved to filesystem
    """
    # Setup
    base_url = "http://localhost:8000"
    case_id = "ACTE-2024-001"
    folder_id = "uploads"

    # Create 20 MB test file (exceeds 15 MB limit)
    test_file_size = 20 * 1024 * 1024  # 20 MB
    test_content = b'B' * test_file_size

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        temp_file.write(test_content)
        temp_file_path = temp_file.name
        temp_file_name = Path(temp_file_path).name

    try:
        # Attempt to upload oversized file
        with open(temp_file_path, 'rb') as f:
            files = {'file': (temp_file_name, f, 'application/pdf')}
            data = {'case_id': case_id, 'folder_id': folder_id}

            response = requests.post(
                f"{base_url}/api/files/upload",
                files=files,
                data=data,
                timeout=30
            )

        # Assertions
        assert response.status_code == 413, f"Expected 413 (Payload Too Large), got {response.status_code}"

        response_data = response.json()
        # Response may have 'detail' as string or dict with 'detail' key
        if isinstance(response_data.get('detail'), dict):
            error_message = response_data['detail'].get('detail', '')
        else:
            error_message = response_data.get('detail', '')

        # Also check error field
        if not error_message:
            error_message = str(response_data)

        assert '15' in error_message and 'MB' in error_message, \
            f"Error message should mention 15 MB limit. Got: {error_message}"

        # Verify file was NOT saved
        project_root = Path("/home/ayanm/projects/info-base/infobase-ai")
        expected_file_path = project_root / "public" / "documents" / case_id / folder_id / temp_file_name
        assert not expected_file_path.exists(), f"Oversized file should NOT be saved at {expected_file_path}"

        print(f"✓ Correctly rejected oversized file {temp_file_name} (20 MB) with 413 status")

    finally:
        # Cleanup
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
