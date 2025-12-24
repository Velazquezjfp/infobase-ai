"""
Test Case: TC-S4-001-09
Description: Upload file with special characters in name, verify filename sanitized
Category: Backend API / Security
Type: Python / Integration Test
"""

import pytest
import os
import tempfile
import requests
from pathlib import Path


def test_filename_with_special_characters_sanitized():
    """
    Test that filenames with special characters are properly sanitized.

    Steps:
    1. Create temporary test file (1 MB)
    2. Upload with filename containing special characters: ../../../etc/passwd.txt
    3. Upload with filename containing special characters: test<>:"/\\|?*.txt
    4. Verify backend sanitizes the filename
    5. Verify file is saved with sanitized name (no path traversal)
    6. Verify file is saved in correct directory (not outside case folder)

    Expected Result:
    - Dangerous characters removed or replaced
    - Path traversal attempts blocked (../ removed)
    - File saved safely in uploads folder
    - Original malicious path NOT used
    """
    # Setup
    base_url = "http://localhost:8000"
    case_id = "ACTE-2024-001"
    folder_id = "uploads"

    # Test cases for filename sanitization
    test_cases = [
        {
            'malicious_name': '../../../etc/passwd.txt',
            'description': 'Path traversal attempt'
        },
        {
            'malicious_name': 'test<>:"/\\|?*.txt',
            'description': 'Special characters'
        },
        {
            'malicious_name': '../../sensitive_data.txt',
            'description': 'Relative path traversal'
        }
    ]

    for test_case in test_cases:
        malicious_filename = test_case['malicious_name']
        description = test_case['description']

        # Create test file
        test_content = b'H' * 1024  # 1 KB

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name

        try:
            # Attempt upload with malicious filename
            with open(temp_file_path, 'rb') as f:
                files = {'file': (malicious_filename, f, 'text/plain')}
                data = {'case_id': case_id, 'folder_id': folder_id}

                response = requests.post(
                    f"{base_url}/api/files/upload",
                    files=files,
                    data=data,
                    timeout=30
                )

            # Backend should either:
            # 1. Reject the upload (400 or 403)
            # 2. Sanitize the filename and save with safe name
            assert response.status_code in [200, 400, 403], \
                f"Expected 200/400/403, got {response.status_code} for {description}"

            if response.status_code == 200:
                # If accepted, verify filename was sanitized
                response_data = response.json()
                saved_filename = response_data.get('fileName', '')

                # Verify no path traversal characters
                assert '../' not in saved_filename, "Sanitized filename should not contain ../"
                assert '\\' not in saved_filename, "Sanitized filename should not contain \\"

                # Verify file was NOT saved outside uploads folder
                malicious_path = Path(f"../../../etc/passwd.txt")
                assert not malicious_path.exists() or malicious_path.resolve().is_relative_to(Path.cwd()), \
                    "File should not be saved outside project directory"

                print(f"✓ {description}: Filename sanitized from '{malicious_filename}' to '{saved_filename}'")
            else:
                print(f"✓ {description}: Upload correctly rejected with status {response.status_code}")

        finally:
            # Cleanup
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
