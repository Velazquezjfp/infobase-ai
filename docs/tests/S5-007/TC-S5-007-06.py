"""
Test Case: TC-S5-007-06
Requirement: S5-007 - Container-Compatible File Persistence
Description: Multiple documents across cases, verify all loaded correctly on startup
Generated: 2026-01-09T15:29:16Z
Updated: 2026-01-12
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))

from services.document_registry import (
    register_document,
    load_manifest,
    build_document_tree,
    MANIFEST_PATH
)


def test_TC_S5_007_06():
    """Multiple documents across cases, verify all loaded correctly on startup"""

    test_docs = [
        ("ACTE-TEST-006-A", "folder-a", "doc_a1.pdf"),
        ("ACTE-TEST-006-A", "folder-a", "doc_a2.txt"),
        ("ACTE-TEST-006-A", "folder-b", "doc_a3.jpg"),
        ("ACTE-TEST-006-B", "folder-c", "doc_b1.pdf"),
        ("ACTE-TEST-006-B", None, "doc_b2.txt"),  # Root document
    ]

    test_docs_path = Path("public/documents")
    test_files = []

    # Backup manifest
    manifest_backup = None
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, 'r') as f:
            manifest_backup = f.read()

    try:
        # Create and register multiple documents
        for case_id, folder_id, file_name in test_docs:
            if folder_id:
                file_path = test_docs_path / case_id / folder_id / file_name
            else:
                file_path = test_docs_path / case_id / file_name

            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(f"Content for {file_name}")

            test_files.append(file_path)

            register_document(
                case_id=case_id,
                folder_id=folder_id,
                file_path=str(file_path),
                file_name=file_name
            )

        # Simulate startup: reload manifest
        registry = load_manifest()

        # Verify all documents are loaded
        assert len(registry.documents) >= len(test_docs), \
            f"Expected at least {len(test_docs)} documents in manifest"

        # Verify each document exists in manifest
        for case_id, folder_id, file_name in test_docs:
            found = any(
                doc.get('caseId') == case_id and
                doc.get('folderId') == folder_id and
                doc.get('fileName') == file_name
                for doc in registry.documents
            )
            assert found, f"Document {file_name} not found in manifest"

        # Verify document trees for both cases
        tree_a = build_document_tree("ACTE-TEST-006-A")
        tree_b = build_document_tree("ACTE-TEST-006-B")

        # Case A should have 2 folders and 3 documents total
        assert len(tree_a['folders']) == 2, "Case A should have 2 folders"
        total_docs_a = sum(len(f['documents']) for f in tree_a['folders']) + len(tree_a['rootDocuments'])
        assert total_docs_a == 3, f"Case A should have 3 documents, found {total_docs_a}"

        # Case B should have 1 folder and 1 root document
        assert len(tree_b['folders']) == 1, "Case B should have 1 folder"
        assert len(tree_b['rootDocuments']) == 1, "Case B should have 1 root document"

        print("TC-S5-007-06: PASSED - Multiple documents across cases loaded correctly")

    finally:
        # Cleanup files
        for file_path in test_files:
            if file_path.exists():
                file_path.unlink()

        # Clean up directories
        for case_id in ["ACTE-TEST-006-A", "ACTE-TEST-006-B"]:
            case_dir = test_docs_path / case_id
            if case_dir.exists():
                import shutil
                shutil.rmtree(case_dir, ignore_errors=True)

        # Restore manifest
        if manifest_backup:
            with open(MANIFEST_PATH, 'w') as f:
                f.write(manifest_backup)


if __name__ == "__main__":
    try:
        test_TC_S5_007_06()
        print("TC-S5-007-06: PASSED")
    except AssertionError as e:
        print(f"TC-S5-007-06: FAILED - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"TC-S5-007-06: ERROR - {e}")
        sys.exit(1)
