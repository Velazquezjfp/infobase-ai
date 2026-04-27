"""
Test Case: TC-S5-007-11
Requirement: S5-007 - Container-Compatible File Persistence
Description: Upload document, delete from manifest only (not disk), restart, verify re-added to manifest
Generated: 2026-01-09T15:29:16Z
Updated: 2026-01-12
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))

from services.document_registry import (
    register_document,
    load_manifest,
    save_manifest,
    unregister_document,
    scan_filesystem,
    reconcile,
    MANIFEST_PATH,
    DocumentRegistry
)
from datetime import datetime, timezone


def test_TC_S5_007_11():
    """Upload document, delete from manifest only (not disk), restart, verify re-added to manifest"""

    test_case_id = "ACTE-TEST-011"
    test_folder_id = "test-folder-11"
    test_file_name = "orphan_after_unregister.pdf"
    test_docs_path = Path("public/documents")
    test_file_path = test_docs_path / test_case_id / test_folder_id / test_file_name

    manifest_backup = None
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, 'r') as f:
            manifest_backup = f.read()

    try:
        # Step 1: Create and register document
        test_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(test_file_path, 'wb') as f:
            f.write(b"Content for TC-S5-007-11 orphan test")

        entry = register_document(
            case_id=test_case_id,
            folder_id=test_folder_id,
            file_path=str(test_file_path),
            file_name=test_file_name
        )

        document_id = entry['documentId']

        # Verify document is in manifest
        registry_before = load_manifest()
        found_before = any(
            doc.get('documentId') == document_id
            for doc in registry_before.documents
        )
        assert found_before, "Document should be in manifest after registration"

        # Step 2: Remove document from manifest only (file stays on disk)
        success = unregister_document(document_id)
        assert success, "Unregister should succeed"

        # Verify file still exists on disk
        assert test_file_path.exists(), "File should still exist on disk"

        # Verify document removed from manifest
        registry_after_unregister = load_manifest()
        found_after_unregister = any(
            doc.get('documentId') == document_id
            for doc in registry_after_unregister.documents
        )
        assert not found_after_unregister, "Document should not be in manifest after unregister"

        # Step 3: Simulate app restart - scan and reconcile
        filesystem_files = scan_filesystem(str(test_docs_path))
        reconcile_report = reconcile(registry_after_unregister, filesystem_files)

        # Step 4: Verify file was re-detected as orphaned
        assert len(reconcile_report.added) > 0, "Orphaned file should be detected"
        assert any(test_file_name in path for path in reconcile_report.added), \
            f"Test file {test_file_name} should be in added list"

        # Step 5: Verify document is back in manifest (with new ID)
        registry_after_reconcile = load_manifest()
        found_after_reconcile = False
        new_doc_id = None

        for doc in registry_after_reconcile.documents:
            if (doc.get('caseId') == test_case_id and
                doc.get('folderId') == test_folder_id and
                doc.get('fileName') == test_file_name):
                found_after_reconcile = True
                new_doc_id = doc.get('documentId')
                assert doc.get('fileHash'), "Re-added document should have hash"
                assert doc.get('uploadedAt'), "Re-added document should have timestamp"
                break

        assert found_after_reconcile, "Orphaned file should be re-added to manifest"
        assert new_doc_id != document_id, "Re-added document should have new ID"

        print("TC-S5-007-11: PASSED - Orphaned file (manifest-only deletion) re-added on restart")

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
        test_TC_S5_007_11()
        print("TC-S5-007-11: PASSED")
    except AssertionError as e:
        print(f"TC-S5-007-11: FAILED - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"TC-S5-007-11: ERROR - {e}")
        sys.exit(1)
