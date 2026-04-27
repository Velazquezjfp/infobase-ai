"""
Test Case: TC-S4-001-04
Description: Drop multiple files, verify all valid files upload sequentially
Category: Backend API / Multiple Files
Type: Python / Integration Test
"""

import pytest
import os
import tempfile
import requests
from pathlib import Path


def test_upload_multiple_files_sequentially():
    """
    Test uploading multiple files to verify sequential handling.

    Steps:
    1. Create 3 temporary test files (1 MB, 3 MB, 5 MB)
    2. Upload each file sequentially to /api/files/upload
    3. Verify all uploads succeed with 200 status
    4. Verify all files exist in public/documents/{caseId}/uploads/
    5. Verify file sizes match originals

    Expected Result:
    - All 3 files upload successfully
    - Files are processed sequentially
    - All files saved in correct directory
    """
    # Setup
    base_url = "http://localhost:8000"
    case_id = "ACTE-2024-001"
    folder_id = "uploads"

    # Create 3 test files with different sizes
    test_files_config = [
        {'size': 1 * 1024 * 1024, 'name': 'test_file_1.txt', 'content': b'C'},
        {'size': 3 * 1024 * 1024, 'name': 'test_file_2.pdf', 'content': b'D'},
        {'size': 5 * 1024 * 1024, 'name': 'test_file_3.docx', 'content': b'E'},
    ]

    temp_files = []
    uploaded_files = []

    try:
        # Create temporary files
        for config in test_files_config:
            test_content = config['content'] * config['size']
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(config['name']).suffix) as temp_file:
                temp_file.write(test_content)
                temp_files.append({
                    'path': temp_file.name,
                    'name': config['name'],
                    'size': config['size']
                })

        # Upload files sequentially
        for file_info in temp_files:
            with open(file_info['path'], 'rb') as f:
                files = {'file': (file_info['name'], f, 'application/octet-stream')}
                data = {'case_id': case_id, 'folder_id': folder_id}

                response = requests.post(
                    f"{base_url}/api/files/upload",
                    files=files,
                    data=data,
                    timeout=30
                )

                # Verify each upload
                assert response.status_code == 200, \
                    f"Upload of {file_info['name']} failed: {response.status_code} - {response.text}"

                response_data = response.json()
                assert response_data.get('success') is True, f"Upload should be successful for {file_info['name']}"

                uploaded_files.append(file_info['name'])

        # Verify all files exist in correct location
        project_root = Path("/home/ayanm/projects/info-base/infobase-ai")
        for file_info in temp_files:
            expected_file_path = project_root / "public" / "documents" / case_id / folder_id / file_info['name']
            assert expected_file_path.exists(), f"File should exist at {expected_file_path}"
            assert expected_file_path.stat().st_size == file_info['size'], \
                f"File size should match original for {file_info['name']}"

        print(f"✓ Successfully uploaded {len(uploaded_files)} files sequentially")
        for fname in uploaded_files:
            print(f"  - {fname}")

    finally:
        # Cleanup temporary files
        for file_info in temp_files:
            if os.path.exists(file_info['path']):
                os.unlink(file_info['path'])
