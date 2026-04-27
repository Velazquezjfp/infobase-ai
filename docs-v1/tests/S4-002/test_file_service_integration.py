"""
Test Suite for S4-002: File Deletion - Service Integration Tests

This simplified test suite focuses on the file_service.py delete_file() function
and its security validation without requiring TestClient/httpx dependencies.

Test Coverage:
- File deletion functionality
- Security: Path traversal prevention
- Error handling (file not found, invalid paths)
- Folder preservation after deletion
"""

import pytest
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.services.file_service import (
    delete_file,
    create_folder_if_needed,
    save_uploaded_file,
    sanitize_filename
)

# Test constants
TEST_CASE_ID = "TEST-CASE-S4-002"
TEST_FOLDER_ID = "uploads"
TEST_FILENAME = "test_document.txt"
TEST_FILE_CONTENT = b"Test document content for S4-002 deletion tests."


@pytest.fixture
def test_file_setup():
    """
    Fixture to create a test file before each test.
    Cleans up after test completion.
    """
    test_dir = Path("public") / "documents" / TEST_CASE_ID / TEST_FOLDER_ID
    test_file_path = test_dir / TEST_FILENAME

    create_folder_if_needed(test_dir)
    save_uploaded_file(test_file_path, TEST_FILE_CONTENT)

    assert test_file_path.exists(), "Test file should exist"

    yield test_file_path

    # Cleanup
    if test_file_path.exists():
        test_file_path.unlink()

    # Remove test directories
    try:
        if test_dir.exists():
            test_dir.rmdir()
        case_dir = test_dir.parent
        if case_dir.exists():
            case_dir.rmdir()
    except OSError:
        pass


def test_delete_file_success(test_file_setup):
    """
    TC-S4-002-02: File deletion succeeds and file is removed from filesystem.

    Validates that delete_file() function:
    - Returns True on success
    - Physically removes file from filesystem
    - Handles the deletion gracefully
    """
    test_file_path = test_file_setup

    # Verify file exists before deletion
    assert test_file_path.exists(), "File must exist before deletion"

    # Delete the file
    result = delete_file(TEST_CASE_ID, TEST_FOLDER_ID, TEST_FILENAME)

    # Assertions
    assert result is True, "delete_file should return True on success"
    assert not test_file_path.exists(), "File should be deleted from filesystem"


def test_delete_file_not_found():
    """
    TC-S4-002-05: Attempting to delete non-existent file raises FileNotFoundError.

    Validates error handling when file doesn't exist.
    """
    non_existent_file = "non_existent_file_xyz.txt"

    with pytest.raises(FileNotFoundError, match="not found"):
        delete_file(TEST_CASE_ID, TEST_FOLDER_ID, non_existent_file)


def test_delete_file_path_traversal_in_filename():
    """
    TC-S4-002-06: Path traversal in filename is sanitized and prevented.

    Security test: Validates that ../ in filenames is sanitized.
    The sanitization removes ../ making it just "passwd" which then doesn't exist.
    """
    malicious_filename = "../../../etc/passwd"

    # Sanitization will strip ../ leaving just "passwd", which won't exist
    with pytest.raises((ValueError, FileNotFoundError)):
        delete_file(TEST_CASE_ID, TEST_FOLDER_ID, malicious_filename)


def test_delete_file_path_traversal_in_folder():
    """
    TC-S4-002-06: Path traversal in folder_id is rejected.

    Security test: Validates that ../ in folder_id raises ValueError.
    """
    malicious_folder = "../../../etc"

    with pytest.raises(ValueError, match="invalid characters"):
        delete_file(TEST_CASE_ID, malicious_folder, "any_file.txt")


def test_delete_file_absolute_path_in_case():
    """
    TC-S4-002-06: Absolute path in case_id is rejected.

    Security test: Validates that absolute paths in case_id raise ValueError.
    """
    malicious_case = "/etc/passwd"

    with pytest.raises(ValueError, match="invalid characters"):
        delete_file(malicious_case, TEST_FOLDER_ID, "any_file.txt")


def test_delete_last_file_folder_remains(test_file_setup):
    """
    TC-S4-002-07: Deleting last file in folder leaves folder structure intact.

    Validates that folder is not removed when its last file is deleted.
    """
    test_file_path = test_file_setup
    test_folder_path = test_file_path.parent

    # Verify only one file exists
    files_before = list(test_folder_path.glob("*"))
    assert len(files_before) == 1, f"Expected 1 file, found {len(files_before)}"

    # Delete the file
    result = delete_file(TEST_CASE_ID, TEST_FOLDER_ID, TEST_FILENAME)
    assert result is True

    # Verify file deleted but folder remains
    assert not test_file_path.exists(), "File should be deleted"
    assert test_folder_path.exists(), "Folder should still exist"
    assert test_folder_path.is_dir(), "Folder should be a directory"


def test_filename_sanitization():
    """
    Test that special characters in filenames are properly sanitized.

    Validates that sanitize_filename() handles:
    - Spaces (converted to underscores)
    - Path separators removed
    - Special characters removed
    """
    # Test space handling
    assert sanitize_filename("document with spaces.txt") == "document_with_spaces.txt"

    # Test path traversal removed
    sanitized = sanitize_filename("../../etc/passwd")
    assert ".." not in sanitized, "Path traversal should be removed"
    assert "/" not in sanitized, "Slashes should be removed"

    # Test special characters removed/replaced
    assert sanitize_filename("doc<>:file.txt") == "docfile.txt"


def test_delete_with_sanitized_filename(test_file_setup):
    """
    Test deletion with filename that requires sanitization.

    Validates that files with spaces can be deleted after sanitization.
    """
    # Create file with spaces in name
    test_dir = Path("public") / "documents" / TEST_CASE_ID / TEST_FOLDER_ID
    spaced_filename = "document with spaces.txt"
    sanitized_filename = "document_with_spaces.txt"
    test_file = test_dir / sanitized_filename

    save_uploaded_file(test_file, b"Test content")
    assert test_file.exists()

    # Delete using original filename (with spaces)
    result = delete_file(TEST_CASE_ID, TEST_FOLDER_ID, spaced_filename)
    assert result is True
    assert not test_file.exists(), "File should be deleted after sanitization"


def test_empty_case_id_rejected():
    """
    Test that empty case_id is rejected.

    Validates input validation.
    """
    with pytest.raises(ValueError, match="case_id cannot be empty"):
        delete_file("", TEST_FOLDER_ID, TEST_FILENAME)


def test_empty_folder_id_rejected():
    """
    Test that empty folder_id is rejected.

    Validates input validation.
    """
    with pytest.raises(ValueError, match="folder_id cannot be empty"):
        delete_file(TEST_CASE_ID, "", TEST_FILENAME)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
