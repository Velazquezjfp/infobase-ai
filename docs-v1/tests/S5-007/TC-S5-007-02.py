"""
Test Case: TC-S5-007-02
Requirement: S5-007 - Container-Compatible File Persistence
Description: Upload document, verify entry added to document_manifest.json
Generated: 2026-01-09T15:29:16Z
Updated: 2026-01-12
"""

import json
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))

from services.document_registry import (
    register_document,
    load_manifest,
    save_manifest,
    MANIFEST_PATH,
    DocumentRegistry
)
from datetime import datetime, timezone


def test_TC_S5_007_02():
    """Upload document, verify entry added to document_manifest.json"""

    # Setup
    test_case_id = "ACTE-TEST-002"
    test_folder_id = "test-folder-02"
    test_file_name = "test_doc_02.pdf"
    test_docs_path = Path("public/documents")
    test_file_path = test_docs_path / test_case_id / test_folder_id / test_file_name

    # Backup original manifest
    manifest_backup = None
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, 'r') as f:
            manifest_backup = f.read()

    try:
        # Create test file
        test_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(test_file_path, 'wb') as f:
            f.write(b"Test PDF content for TC-S5-007-02")

        # Get manifest count before upload
        registry_before = load_manifest()
        count_before = len(registry_before.documents)

        # Register document (simulating upload)
        entry = register_document(
            case_id=test_case_id,
            folder_id=test_folder_id,
            file_path=str(test_file_path),
            file_name=test_file_name
        )

        # Verify manifest file was updated
        assert MANIFEST_PATH.exists(), "Manifest file does not exist"

        # Read manifest file directly
        with open(MANIFEST_PATH, 'r') as f:
            manifest_data = json.load(f)

        # Verify structure
        assert 'version' in manifest_data, "Manifest missing 'version' field"
        assert 'schemaVersion' in manifest_data, "Manifest missing 'schemaVersion' field"
        assert 'lastUpdated' in manifest_data, "Manifest missing 'lastUpdated' field"
        assert 'documents' in manifest_data, "Manifest missing 'documents' field"

        # Verify document count increased
        count_after = len(manifest_data['documents'])
        assert count_after == count_before + 1, f"Document count should increase by 1 (was {count_before}, now {count_after})"

        # Verify the specific document entry exists in manifest
        found = False
        for doc in manifest_data['documents']:
            if (doc.get('caseId') == test_case_id and
                doc.get('folderId') == test_folder_id and
                doc.get('fileName') == test_file_name):
                found = True
                # Verify all required fields are present
                assert 'documentId' in doc, "Document entry missing 'documentId'"
                assert 'fileHash' in doc, "Document entry missing 'fileHash'"
                assert 'uploadedAt' in doc, "Document entry missing 'uploadedAt'"
                assert 'filePath' in doc, "Document entry missing 'filePath'"
                assert 'renders' in doc, "Document entry missing 'renders'"
                assert doc['fileHash'].startswith('sha256:'), "File hash should start with 'sha256:'"
                break

        assert found, f"Document entry not found in manifest file: {test_file_name}"

        print("TC-S5-007-02: PASSED - Document entry correctly added to manifest file")

    finally:
        # Cleanup
        if test_file_path.exists():
            test_file_path.unlink()
        if test_file_path.parent.exists() and not list(test_file_path.parent.iterdir()):
            test_file_path.parent.rmdir()

        # Restore original manifest
        if manifest_backup:
            with open(MANIFEST_PATH, 'w') as f:
                f.write(manifest_backup)


if __name__ == "__main__":
    try:
        test_TC_S5_007_02()
        print("TC-S5-007-02: PASSED")
    except AssertionError as e:
        print(f"TC-S5-007-02: FAILED - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"TC-S5-007-02: ERROR - {e}")
        sys.exit(1)
