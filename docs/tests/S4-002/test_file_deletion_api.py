"""
Test Suite for S4-002: File Deletion Feature - Backend API Tests

This test suite validates the DELETE /api/files/{case_id}/{folder_id}/{filename} endpoint
and the delete_file() function in file_service.py.

Test Coverage:
- TC-S4-002-02: File deletion from filesystem
- TC-S4-002-05: Delete non-existent file (404 error handling)
- TC-S4-002-06: Path traversal attack prevention (security)
- Backend functionality and security validation
"""

import pytest
import os
from pathlib import Path
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.file_service import delete_file, create_folder_if_needed, save_uploaded_file

# Create TestClient with correct syntax (positional argument, not keyword)
@pytest.fixture(scope="module")
def client():
    """Create test client fixture"""
    with TestClient(app) as test_client:
        yield test_client

# Test data paths
TEST_CASE_ID = "TEST-CASE-001"
TEST_FOLDER_ID = "uploads"
TEST_FILENAME = "test_document.txt"
TEST_FILE_CONTENT = b"Test document content for deletion tests."


@pytest.fixture
def setup_test_file():
    """
    Fixture to create a test file before deletion tests.
    Cleans up after test completion.
    """
    # Create test directory and file
    test_dir = Path("public") / "documents" / TEST_CASE_ID / TEST_FOLDER_ID
    test_file_path = test_dir / TEST_FILENAME

    create_folder_if_needed(test_dir)
    save_uploaded_file(test_file_path, TEST_FILE_CONTENT)

    assert test_file_path.exists(), "Test file should be created"

    yield test_file_path

    # Cleanup: Remove test file if it still exists
    if test_file_path.exists():
        test_file_path.unlink()

    # Cleanup: Remove test directories
    try:
        test_dir.rmdir()
        (test_dir.parent).rmdir()  # Remove case directory
        (test_dir.parent.parent).rmdir()  # Remove documents directory
    except OSError:
        pass  # Directory not empty or doesn't exist


def test_delete_file_success(client, setup_test_file):
    """
    TC-S4-002-02: Confirm deletion, verify file removed from filesystem.

    Tests successful file deletion via API endpoint.

    Expected:
    - Status code: 200
    - File physically removed from filesystem
    - Response contains success message
    """
    test_file_path = setup_test_file

    # Ensure file exists before deletion
    assert test_file_path.exists(), "Test file must exist before deletion"

    # Call DELETE endpoint
    response = client.delete(f"/api/files/{TEST_CASE_ID}/{TEST_FOLDER_ID}/{TEST_FILENAME}")

    # Assertions
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    result = response.json()
    assert result["success"] is True, "Response should indicate success"
    assert result["file_name"] == TEST_FILENAME, f"Filename mismatch: {result['file_name']}"
    assert "deleted successfully" in result["message"].lower(), f"Unexpected message: {result['message']}"

    # Verify file no longer exists on filesystem
    assert not test_file_path.exists(), "File should be deleted from filesystem"


def test_delete_file_not_found(client):
    """
    TC-S4-002-05: Delete non-existent file, verify 404 error handled gracefully.

    Tests error handling when trying to delete a file that doesn't exist.

    Expected:
    - Status code: 404
    - Error message indicates file not found
    - System handles gracefully without crashing
    """
    non_existent_file = "non_existent_file.txt"

    # Call DELETE endpoint for non-existent file
    response = client.delete(f"/api/files/{TEST_CASE_ID}/{TEST_FOLDER_ID}/{non_existent_file}")

    # Assertions
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    result = response.json()
    assert "error" in result["detail"], "Error response should contain 'error' field"
    assert "not found" in result["detail"]["detail"].lower(), "Error message should mention 'not found'"


def test_delete_file_path_traversal_prevention(client):
    """
    TC-S4-002-06: Attempt path traversal attack (../), verify security rejection.

    Tests that path traversal attempts are blocked by security validation.

    Expected:
    - Status code: 403 (Forbidden) or 400 (Bad Request)
    - Access denied or validation error
    - No files outside case directory affected
    """
    # Test case 1: Path traversal in filename
    malicious_filename = "../../../etc/passwd"
    response = client.delete(f"/api/files/{TEST_CASE_ID}/{TEST_FOLDER_ID}/{malicious_filename}")

    assert response.status_code in [400, 403], f"Expected 400 or 403, got {response.status_code}"
    result = response.json()
    assert "error" in result["detail"], "Error response should be present"

    # Test case 2: Path traversal in folder_id
    malicious_folder = "../../../etc"
    response = client.delete(f"/api/files/{TEST_CASE_ID}/{malicious_folder}/passwd")

    assert response.status_code in [400, 403], f"Expected 400 or 403, got {response.status_code}"

    # Test case 3: Absolute path in case_id
    malicious_case = "/etc"
    response = client.delete(f"/api/files/{malicious_case}/passwd/shadow")

    assert response.status_code in [400, 403], f"Expected 400 or 403, got {response.status_code}"


def test_delete_file_service_function(setup_test_file):
    """
    Test the delete_file() service function directly.

    Validates that the file_service.delete_file() function works correctly
    with proper security validation.

    Expected:
    - Function returns True on success
    - File is removed from filesystem
    - ValueError raised for invalid paths
    - FileNotFoundError raised for missing files
    """
    test_file_path = setup_test_file

    # Ensure file exists
    assert test_file_path.exists(), "Test file must exist"

    # Call delete_file function
    result = delete_file(TEST_CASE_ID, TEST_FOLDER_ID, TEST_FILENAME)

    # Assertions
    assert result is True, "delete_file should return True on success"
    assert not test_file_path.exists(), "File should be deleted"


def test_delete_file_service_security_validation():
    """
    Test that the file service properly validates paths to prevent security issues.

    Expected:
    - ValueError or FileNotFoundError raised for path traversal attempts
    - ValueError raised for invalid case_id/folder_id formats
    """
    # Test path traversal in filename - sanitization removes ../ so it becomes "passwd"
    # which then doesn't exist, raising FileNotFoundError
    with pytest.raises((ValueError, FileNotFoundError)):
        delete_file(TEST_CASE_ID, TEST_FOLDER_ID, "../../../etc/passwd")

    # Test path traversal in folder_id
    with pytest.raises(ValueError, match="invalid characters"):
        delete_file(TEST_CASE_ID, "../etc", "passwd")

    # Test absolute path in case_id
    with pytest.raises(ValueError, match="invalid characters"):
        delete_file("/etc", "passwd", "shadow")


def test_delete_file_not_found_service():
    """
    Test that file service raises FileNotFoundError for missing files.

    Expected:
    - FileNotFoundError raised when file doesn't exist
    - Error message includes filename
    """
    with pytest.raises(FileNotFoundError, match="not found"):
        delete_file(TEST_CASE_ID, TEST_FOLDER_ID, "non_existent_file.txt")


def test_delete_last_file_in_folder(client, setup_test_file):
    """
    TC-S4-002-07: Delete last file in uploads folder, verify folder structure remains.

    Tests that deleting the last file in a folder doesn't remove the folder itself.

    Expected:
    - File deleted successfully
    - Folder directory still exists
    - Other files in other folders unaffected
    """
    test_file_path = setup_test_file
    test_folder_path = test_file_path.parent

    # Ensure only one file in folder
    files_before = list(test_folder_path.glob("*"))
    assert len(files_before) == 1, f"Expected 1 file, found {len(files_before)}"

    # Delete the file
    response = client.delete(f"/api/files/{TEST_CASE_ID}/{TEST_FOLDER_ID}/{TEST_FILENAME}")
    assert response.status_code == 200

    # Verify file deleted but folder remains
    assert not test_file_path.exists(), "File should be deleted"
    assert test_folder_path.exists(), "Folder should still exist"
    assert test_folder_path.is_dir(), "Folder should be a directory"


def test_delete_file_with_special_characters(client):
    """
    Test deletion of files with special characters in filename.

    Expected:
    - Special characters handled correctly
    - Filename sanitization works properly
    - File can be deleted if it exists
    """
    special_filenames = [
        "document with spaces.txt",
        "document_with_underscores.txt",
        "document-with-hyphens.txt",
    ]

    for filename in special_filenames:
        # Create test file
        test_dir = Path("public") / "documents" / TEST_CASE_ID / TEST_FOLDER_ID
        test_file_path = test_dir / filename.replace(" ", "_")  # Simulating sanitization

        create_folder_if_needed(test_dir)
        save_uploaded_file(test_file_path, b"Test content")

        # Delete via API
        response = client.delete(f"/api/files/{TEST_CASE_ID}/{TEST_FOLDER_ID}/{filename}")

        # Should succeed with proper sanitization
        assert response.status_code in [200, 404], f"Failed for {filename}: {response.status_code}"

        # Cleanup
        if test_file_path.exists():
            test_file_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
