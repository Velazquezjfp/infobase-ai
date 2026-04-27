"""
Test Case: TC-S4-001-08
Description: Verify uploaded file appears in case document tree under "uploads" folder
Category: Backend API / Document Tree
Type: Python / Integration Test
"""

import pytest
import os
import tempfile
import requests
from pathlib import Path


def test_uploaded_file_appears_in_uploads_folder():
    """
    Test that uploaded file is correctly saved in uploads folder structure.

    Steps:
    1. Create a temporary test file (2 MB)
    2. POST to /api/files/upload with file, caseId, folderId=uploads
    3. Verify response status 200 and success=True
    4. Verify file exists at public/documents/{caseId}/uploads/{fileName}
    5. Verify uploads folder structure exists
    6. (UI test would verify file appears in CaseTreeExplorer under uploads folder)

    Expected Result:
    - File saved in correct uploads folder path
    - File is accessible in filesystem
    - Uploads folder is created if it doesn't exist
    - In UI: File would appear in case tree under "uploads" folder

    Note: UI verification requires Playwright automation
    """
    # Setup
    base_url = "http://localhost:8000"
    case_id = "ACTE-2024-001"
    folder_id = "uploads"

    # Create test file
    test_file_size = 2 * 1024 * 1024  # 2 MB
    test_content = b'G' * test_file_size

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        temp_file.write(test_content)
        temp_file_path = temp_file.name
        test_file_name = "test_document_upload.pdf"

    try:
        # Upload file
        with open(temp_file_path, 'rb') as f:
            files = {'file': (test_file_name, f, 'application/pdf')}
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

        # Verify file exists in uploads folder
        project_root = Path("/home/ayanm/projects/info-base/infobase-ai")
        uploads_folder_path = project_root / "public" / "documents" / case_id / folder_id
        assert uploads_folder_path.exists(), f"Uploads folder should exist at {uploads_folder_path}"
        assert uploads_folder_path.is_dir(), "Uploads path should be a directory"

        expected_file_path = uploads_folder_path / test_file_name
        assert expected_file_path.exists(), f"Uploaded file should exist at {expected_file_path}"
        assert expected_file_path.is_file(), "Uploaded path should be a file"

        # Verify file size
        assert expected_file_path.stat().st_size == test_file_size, "File size should match original"

        print(f"✓ File {test_file_name} successfully uploaded to uploads folder")
        print(f"  Path: {expected_file_path}")

    finally:
        # Cleanup
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
