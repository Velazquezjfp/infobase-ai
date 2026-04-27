"""
Test Case: TC-S4-001-10
Description: Upload duplicate filename, verify handled (overwrite or rename)
Category: Backend API / File Management
Type: Python / Integration Test
"""

import pytest
import os
import tempfile
import requests
from pathlib import Path
import time


def test_duplicate_filename_handling():
    """
    Test uploading a file with the same name as an existing file.

    Steps:
    1. Upload a file named "duplicate_test.txt" with content "Version 1"
    2. Verify upload succeeds
    3. Upload another file with same name "duplicate_test.txt" but content "Version 2"
    4. Verify second upload succeeds (or returns specific handling status)
    5. Check if file was overwritten OR renamed (e.g., duplicate_test_1.txt)
    6. Verify behavior is consistent and safe

    Expected Result:
    - First upload succeeds
    - Second upload either:
      a) Overwrites the first file (content becomes "Version 2")
      b) Creates renamed file (duplicate_test_1.txt or similar)
    - No data corruption or file system errors
    """
    # Setup
    base_url = "http://localhost:8000"
    case_id = "ACTE-2024-001"
    folder_id = "uploads"
    test_filename = "duplicate_test.txt"

    # Create first file
    first_content = b'Version 1 content - original file'

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(first_content)
        first_file_path = temp_file.name

    # Create second file with same name
    second_content = b'Version 2 content - duplicate upload'

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(second_content)
        second_file_path = temp_file.name

    try:
        # Upload first file
        with open(first_file_path, 'rb') as f:
            files = {'file': (test_filename, f, 'text/plain')}
            data = {'case_id': case_id, 'folder_id': folder_id}

            response1 = requests.post(
                f"{base_url}/api/files/upload",
                files=files,
                data=data,
                timeout=30
            )

        assert response1.status_code == 200, f"First upload failed: {response1.status_code} - {response1.text}"

        time.sleep(0.5)  # Small delay to ensure different timestamps

        # Upload second file with same name
        with open(second_file_path, 'rb') as f:
            files = {'file': (test_filename, f, 'text/plain')}
            data = {'case_id': case_id, 'folder_id': folder_id}

            response2 = requests.post(
                f"{base_url}/api/files/upload",
                files=files,
                data=data,
                timeout=30
            )

        assert response2.status_code == 200, f"Second upload failed: {response2.status_code} - {response2.text}"

        # Check what happened with duplicate
        project_root = Path("/home/ayanm/projects/info-base/infobase-ai")
        uploads_folder = project_root / "public" / "documents" / case_id / folder_id

        # Strategy 1: Check if file was overwritten
        original_file_path = uploads_folder / test_filename
        if original_file_path.exists():
            with open(original_file_path, 'rb') as f:
                current_content = f.read()

            if current_content == second_content:
                print(f"✓ Duplicate handling: File was OVERWRITTEN (now contains Version 2)")
            elif current_content == first_content:
                # File wasn't overwritten, check for renamed version
                renamed_files = list(uploads_folder.glob(f"{Path(test_filename).stem}_*{Path(test_filename).suffix}"))
                if renamed_files:
                    print(f"✓ Duplicate handling: Original kept, duplicate renamed to {renamed_files[0].name}")
                else:
                    pytest.fail("Duplicate file uploaded but neither overwrite nor rename detected")
            else:
                pytest.fail(f"Unexpected file content: {current_content}")

        else:
            pytest.fail(f"Original file not found at {original_file_path}")

    finally:
        # Cleanup
        if os.path.exists(first_file_path):
            os.unlink(first_file_path)
        if os.path.exists(second_file_path):
            os.unlink(second_file_path)
