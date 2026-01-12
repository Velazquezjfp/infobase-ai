"""
Test Case: TC-S5-007-08
Requirement: S5-007 - Container-Compatible File Persistence
Description: Check manifest file hash matches actual file, verify integrity validation
Generated: 2026-01-09T15:29:16Z
Updated: 2026-01-12
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))

from services.document_registry import (
    register_document,
    load_manifest,
    calculate_file_hash,
    verify_file_integrity,
    MANIFEST_PATH
)


def test_TC_S5_007_08():
    """Check manifest file hash matches actual file, verify integrity validation"""

    test_case_id = "ACTE-TEST-008"
    test_folder_id = "test-folder-08"
    test_file_name = "integrity_test.txt"
    test_docs_path = Path("public/documents")
    test_file_path = test_docs_path / test_case_id / test_folder_id / test_file_name

    manifest_backup = None
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, 'r') as f:
            manifest_backup = f.read()

    try:
        # Create test file with specific content
        test_file_path.parent.mkdir(parents=True, exist_ok=True)
        test_content = b"Specific content for hash verification in TC-S5-007-08"
        with open(test_file_path, 'wb') as f:
            f.write(test_content)

        # Calculate hash manually before registration
        expected_hash = calculate_file_hash(str(test_file_path))
        assert expected_hash.startswith('sha256:'), "Hash should start with 'sha256:'"

        # Register document
        entry = register_document(
            case_id=test_case_id,
            folder_id=test_folder_id,
            file_path=str(test_file_path),
            file_name=test_file_name
        )

        # Verify hash in entry matches calculated hash
        assert entry['fileHash'] == expected_hash, \
            f"Entry hash {entry['fileHash']} doesn't match expected {expected_hash}"

        # Load manifest and verify hash is stored correctly
        registry = load_manifest()
        doc_entry = None
        for doc in registry.documents:
            if doc.get('documentId') == entry['documentId']:
                doc_entry = doc
                break

        assert doc_entry is not None, "Document not found in manifest"
        assert doc_entry['fileHash'] == expected_hash, \
            "Hash in manifest doesn't match expected value"

        # Verify file integrity function
        integrity_valid = verify_file_integrity(doc_entry)
        assert integrity_valid, "File integrity verification should pass"

        # Test integrity check detects changes
        # Modify file content
        with open(test_file_path, 'wb') as f:
            f.write(b"Modified content - hash should not match")

        # Recalculate hash
        new_hash = calculate_file_hash(str(test_file_path))
        assert new_hash != expected_hash, "Hash should change when content changes"

        # Integrity check should now fail
        integrity_valid_after_change = verify_file_integrity(doc_entry)
        assert not integrity_valid_after_change, \
            "File integrity verification should fail after content change"

        print("TC-S5-007-08: PASSED - File hash integrity validation works correctly")

    finally:
        # Cleanup
        if test_file_path.exists():
            test_file_path.unlink()
        if test_file_path.parent.exists() and not list(test_file_path.parent.iterdir()):
            test_file_path.parent.rmdir()

        if manifest_backup:
            with open(MANIFEST_PATH, 'w') as f:
                f.write(manifest_backup)


if __name__ == "__main__":
    try:
        test_TC_S5_007_08()
        print("TC-S5-007-08: PASSED")
    except AssertionError as e:
        print(f"TC-S5-007-08: FAILED - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"TC-S5-007-08: ERROR - {e}")
        sys.exit(1)
