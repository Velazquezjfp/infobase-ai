"""
Test Case: TC-S5-007-03
Requirement: S5-007 - Container-Compatible File Persistence
Description: Manually add file to documents folder, restart app, verify file detected and added to manifest
Generated: 2026-01-09T15:29:16Z
Updated: 2026-01-12
"""

import json
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))

from services.document_registry import (
    load_manifest,
    save_manifest,
    scan_filesystem,
    reconcile,
    MANIFEST_PATH,
    DocumentRegistry
)
from datetime import datetime, timezone


def test_TC_S5_007_03():
    """Manually add file to documents folder, restart app, verify file detected and added to manifest"""

    # Setup
    test_case_id = "ACTE-TEST-003"
    test_folder_id = "test-folder-03"
    test_file_name = "orphan_file.jpg"
    test_docs_path = Path("public/documents")
    test_file_path = test_docs_path / test_case_id / test_folder_id / test_file_name

    # Backup original manifest
    manifest_backup = None
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, 'r') as f:
            manifest_backup = f.read()

    try:
        # Manually create file in documents folder (simulating direct filesystem addition)
        test_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(test_file_path, 'wb') as f:
            f.write(b"Orphaned image file content for TC-S5-007-03")

        # Verify file is NOT in manifest initially
        registry_before = load_manifest()
        found_before = any(
            doc.get('caseId') == test_case_id and
            doc.get('folderId') == test_folder_id and
            doc.get('fileName') == test_file_name
            for doc in registry_before.documents
        )
        assert not found_before, "File should not be in manifest initially"

        # Simulate app restart: scan filesystem and reconcile
        filesystem_files = scan_filesystem(str(test_docs_path))
        reconcile_report = reconcile(registry_before, filesystem_files)

        # Verify file was detected as orphaned and added
        assert len(reconcile_report.added) > 0, "No orphaned files were detected"
        assert any(test_file_name in path for path in reconcile_report.added), \
            f"Test file {test_file_name} was not detected as orphaned"

        # Load manifest after reconciliation
        registry_after = load_manifest()

        # Verify file is now in manifest
        found_after = False
        for doc in registry_after.documents:
            if (doc.get('caseId') == test_case_id and
                doc.get('folderId') == test_folder_id and
                doc.get('fileName') == test_file_name):
                found_after = True
                # Verify all required fields were auto-generated
                assert doc.get('documentId'), "Document ID not generated for orphaned file"
                assert doc.get('fileHash'), "File hash not calculated for orphaned file"
                assert doc.get('uploadedAt'), "Upload timestamp not set for orphaned file"
                assert doc.get('filePath') == str(test_file_path), "File path incorrect"
                assert isinstance(doc.get('renders', []), list), "Renders field should be empty list"
                break

        assert found_after, "Orphaned file was not added to manifest after reconciliation"

        print("TC-S5-007-03: PASSED - Orphaned file detected and added to manifest")

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
        test_TC_S5_007_03()
        print("TC-S5-007-03: PASSED")
    except AssertionError as e:
        print(f"TC-S5-007-03: FAILED - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"TC-S5-007-03: ERROR - {e}")
        sys.exit(1)
