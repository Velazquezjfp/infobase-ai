"""
Test Case: TC-S5-007-01
Requirement: S5-007 - Container-Compatible File Persistence
Description: Upload document, restart app, verify document visible in frontend
Generated: 2026-01-09T15:29:16Z
Updated: 2026-01-12
"""

import json
import os
import sys
import tempfile
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))

from services.document_registry import (
    register_document,
    load_manifest,
    save_manifest,
    scan_filesystem,
    reconcile,
    build_document_tree,
    MANIFEST_PATH
)


def test_TC_S5_007_01():
    """Upload document, restart app, verify document visible in frontend"""

    # Setup: Create test environment
    test_case_id = "ACTE-TEST-001"
    test_folder_id = "test-folder"
    test_file_name = "test_document.txt"
    test_docs_path = Path("public/documents")
    test_file_path = test_docs_path / test_case_id / test_folder_id / test_file_name

    # Backup original manifest
    manifest_backup = None
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, 'r') as f:
            manifest_backup = f.read()

    try:
        # Create test document file
        test_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(test_file_path, 'w') as f:
            f.write("Test content for TC-S5-007-01")

        # Step 1: Register document (simulating upload)
        entry = register_document(
            case_id=test_case_id,
            folder_id=test_folder_id,
            file_path=str(test_file_path),
            file_name=test_file_name
        )

        assert entry is not None, "Document registration failed"
        assert entry['documentId'], "Document ID not generated"
        assert entry['caseId'] == test_case_id, "Case ID mismatch"
        assert entry['folderId'] == test_folder_id, "Folder ID mismatch"
        assert entry['fileName'] == test_file_name, "File name mismatch"

        # Step 2: Simulate app restart by reloading manifest
        registry = load_manifest()

        # Step 3: Verify document is in manifest after "restart"
        found = False
        for doc in registry.documents:
            if (doc.get('caseId') == test_case_id and
                doc.get('folderId') == test_folder_id and
                doc.get('fileName') == test_file_name):
                found = True
                assert doc.get('documentId'), "Document ID missing after restart"
                assert doc.get('fileHash'), "File hash missing after restart"
                assert doc.get('uploadedAt'), "Upload timestamp missing after restart"
                break

        assert found, "Document not found in manifest after restart"

        # Step 4: Verify document tree API returns the document (frontend visibility)
        tree = build_document_tree(test_case_id)

        # Check if document appears in folder structure
        folder_found = False
        doc_found = False
        for folder in tree.get('folders', []):
            if folder['id'] == test_folder_id:
                folder_found = True
                for doc in folder.get('documents', []):
                    if doc.get('fileName') == test_file_name:
                        doc_found = True
                        break
                break

        assert folder_found, f"Folder {test_folder_id} not found in document tree"
        assert doc_found, f"Document {test_file_name} not found in folder"

        print("TC-S5-007-01: PASSED - Document persists and is visible after restart")

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
        elif MANIFEST_PATH.exists():
            # Load and remove test document
            registry = load_manifest()
            documents_list = [
                doc for doc in registry.documents
                if not (doc.get('caseId') == test_case_id and
                       doc.get('folderId') == test_folder_id and
                       doc.get('fileName') == test_file_name)
            ]
            from services.document_registry import DocumentRegistry
            from datetime import datetime, timezone
            updated_registry = DocumentRegistry(
                version=registry.version,
                schemaVersion=registry.schemaVersion,
                lastUpdated=datetime.now(timezone.utc).isoformat(),
                documents=documents_list
            )
            save_manifest(updated_registry)


if __name__ == "__main__":
    try:
        test_TC_S5_007_01()
        print("TC-S5-007-01: PASSED")
    except AssertionError as e:
        print(f"TC-S5-007-01: FAILED - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"TC-S5-007-01: ERROR - {e}")
        sys.exit(1)
