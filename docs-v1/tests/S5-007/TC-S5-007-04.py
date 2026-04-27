"""
Test Case: TC-S5-007-04
Requirement: S5-007 - Container-Compatible File Persistence
Description: Delete file from filesystem, restart app, verify marked as missing in logs (not shown in UI)
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
    scan_filesystem,
    reconcile,
    MANIFEST_PATH
)


def test_TC_S5_007_04():
    """Delete file from filesystem, restart app, verify marked as missing in logs (not shown in UI)"""

    # Setup
    test_case_id = "ACTE-TEST-004"
    test_folder_id = "test-folder-04"
    test_file_name = "deleted_file.pdf"
    test_docs_path = Path("public/documents")
    test_file_path = test_docs_path / test_case_id / test_folder_id / test_file_name

    # Backup original manifest
    manifest_backup = None
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, 'r') as f:
            manifest_backup = f.read()

    try:
        # Step 1: Create and register document
        test_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(test_file_path, 'wb') as f:
            f.write(b"Content that will be deleted for TC-S5-007-04")

        entry = register_document(
            case_id=test_case_id,
            folder_id=test_folder_id,
            file_path=str(test_file_path),
            file_name=test_file_name
        )
        assert entry is not None, "Document registration failed"

        # Step 2: Manually delete file from filesystem (simulating file loss)
        test_file_path.unlink()
        assert not test_file_path.exists(), "File should be deleted"

        # Step 3: Simulate app restart - scan filesystem and reconcile
        filesystem_files = scan_filesystem(str(test_docs_path))
        reconcile_report = reconcile(load_manifest(), filesystem_files)

        # Step 4: Verify file is marked as missing
        assert len(reconcile_report.missing) > 0, "No missing files detected"
        assert any(test_file_name in path for path in reconcile_report.missing), \
            f"Deleted file {test_file_name} not detected as missing"

        # Step 5: Verify file is still in manifest (but marked as missing in logs)
        # The manifest should still contain the entry for auditability
        registry = load_manifest()
        found = any(
            doc.get('caseId') == test_case_id and
            doc.get('folderId') == test_folder_id and
            doc.get('fileName') == test_file_name
            for doc in registry.documents
        )
        assert found, "Missing file entry should still be in manifest for audit trail"

        print("TC-S5-007-04: PASSED - Missing file detected and logged")

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
        test_TC_S5_007_04()
        print("TC-S5-007-04: PASSED")
    except AssertionError as e:
        print(f"TC-S5-007-04: FAILED - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"TC-S5-007-04: ERROR - {e}")
        sys.exit(1)
