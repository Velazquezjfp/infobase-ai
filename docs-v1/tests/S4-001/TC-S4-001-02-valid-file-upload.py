"""
Test Case: TC-S4-001-02
Description: Drop 5 MB file, verify upload completes and file appears in uploads folder
Category: Backend API / File Upload
Type: Python / Integration Test
"""

import pytest
import os
import tempfile
import requests
from pathlib import Path


def test_upload_valid_5mb_file():
    """
    Test uploading a valid 5 MB file to the uploads folder.

    Steps:
    1. Create a temporary 5 MB test file
    2. POST to /api/files/upload with file, caseId, folderId=uploads
    3. Verify response status 200
    4. Verify response contains success=True, filePath, fileName
    5. Verify file exists in public/documents/{caseId}/uploads/
    6. Verify file size matches original

    Expected Result:
    - Upload succeeds with 200 status
    - File saved in correct directory
    - File integrity preserved
    """
    # Setup
    base_url = "http://localhost:8000"
    case_id = "ACTE-2024-001"
    folder_id = "uploads"

    # Create 5 MB test file
    test_file_size = 5 * 1024 * 1024  # 5 MB
    test_content = b'A' * test_file_size

    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
        temp_file.write(test_content)
        temp_file_path = temp_file.name
        temp_file_name = Path(temp_file_path).name

    try:
        # Upload file
        with open(temp_file_path, 'rb') as f:
            files = {'file': (temp_file_name, f, 'text/plain')}
            data = {'case_id': case_id, 'folder_id': folder_id}

            response = requests.post(
                f"{base_url}/api/files/upload",
                files=files,
                data=data,
                timeout=30
            )

        # Assertions
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        response_data = response.json()
        assert response_data.get('success') is True, "Upload should be successful"
        assert 'file_path' in response_data, "Response should contain file_path"
        assert 'file_name' in response_data, "Response should contain file_name"

        # Verify file exists in correct location
        saved_filename = response_data['file_name']
        # Use absolute path from project root
        project_root = Path("/home/ayanm/projects/info-base/infobase-ai")
        expected_file_path = project_root / "public" / response_data['file_path']
        assert expected_file_path.exists(), f"File should exist at {expected_file_path}"

        # Verify file size
        assert expected_file_path.stat().st_size == test_file_size, "File size should match original"

        print(f"✓ Successfully uploaded {saved_filename} (5 MB) to {expected_file_path}")

    finally:
        # Cleanup
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
