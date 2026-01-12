"""
Test Case: TC-S5-007-12
Requirement: S5-007 - Container-Compatible File Persistence
Description: Simulate container restart, verify all documents persist and load correctly
Generated: 2026-01-09T15:29:16Z
Updated: 2026-01-12
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))

from services.document_registry import (
    register_document,
    load_manifest,
    scan_filesystem,
    reconcile,
    build_document_tree,
    MANIFEST_PATH
)


def test_TC_S5_007_12():
    """Simulate container restart, verify all documents persist and load correctly"""

    test_case_id = "ACTE-TEST-012"
    test_docs_path = Path("public/documents")

    # Create multiple documents simulating a real case
    test_docs = [
        ("personal-data", "birth_certificate.jpg"),
        ("personal-data", "passport.pdf"),
        ("education", "diploma.pdf"),
        ("education", "transcripts.pdf"),
        (None, "application_form.pdf"),  # Root document
    ]

    test_files = []

    manifest_backup = None
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, 'r') as f:
            manifest_backup = f.read()

    try:
        # Phase 1: Initial setup - create and register documents
        print("Phase 1: Creating and registering documents...")
        for folder_id, file_name in test_docs:
            if folder_id:
                file_path = test_docs_path / test_case_id / folder_id / file_name
            else:
                file_path = test_docs_path / test_case_id / file_name

            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'wb') as f:
                f.write(f"Content for {file_name} in container test".encode())

            test_files.append(file_path)

            register_document(
                case_id=test_case_id,
                folder_id=folder_id,
                file_path=str(file_path),
                file_name=file_name
            )

        # Capture state before "restart"
        registry_before = load_manifest()
        docs_before = [
            doc for doc in registry_before.documents
            if doc.get('caseId') == test_case_id
        ]
        count_before = len(docs_before)

        assert count_before == len(test_docs), \
            f"Expected {len(test_docs)} documents, found {count_before}"

        print(f"  - Registered {count_before} documents")

        # Phase 2: Simulate container restart
        print("Phase 2: Simulating container restart...")

        # 2a. Reload manifest (as app would on startup)
        registry_after_restart = load_manifest()

        # 2b. Scan filesystem
        filesystem_files = scan_filesystem(str(test_docs_path))

        # 2c. Reconcile
        reconcile_report = reconcile(registry_after_restart, filesystem_files)

        print(f"  - Reconciliation: {len(reconcile_report.added)} added, "
              f"{len(reconcile_report.missing)} missing, "
              f"{len(reconcile_report.integrity_failed)} integrity failed")

        # Phase 3: Verify persistence
        print("Phase 3: Verifying document persistence...")

        # All documents should still be in manifest
        registry_after = load_manifest()
        docs_after = [
            doc for doc in registry_after.documents
            if doc.get('caseId') == test_case_id
        ]
        count_after = len(docs_after)

        assert count_after == count_before, \
            f"Document count changed after restart: before={count_before}, after={count_after}"

        # Verify each document
        for folder_id, file_name in test_docs:
            found = any(
                doc.get('caseId') == test_case_id and
                doc.get('folderId') == folder_id and
                doc.get('fileName') == file_name
                for doc in docs_after
            )
            assert found, f"Document {file_name} not found after restart"

        # Verify document tree is correct
        tree = build_document_tree(test_case_id)

        # Should have 2 folders
        assert len(tree['folders']) == 2, "Should have 2 folders"

        # Should have 1 root document
        assert len(tree['rootDocuments']) == 1, "Should have 1 root document"

        # Total documents should match
        total_docs = sum(len(f['documents']) for f in tree['folders']) + len(tree['rootDocuments'])
        assert total_docs == len(test_docs), \
            f"Total documents mismatch: expected {len(test_docs)}, got {total_docs}"

        # Verify no reconciliation issues FOR OUR TEST FILES
        # Note: There may be missing files from other tests/production data
        # We only care that our test case documents are not missing
        test_missing = [
            path for path in reconcile_report.missing
            if test_case_id in path
        ]
        assert len(test_missing) == 0, \
            f"Test case files should not be missing: {test_missing}"

        print("  - All documents persisted correctly")
        print("  - Document tree structure preserved")
        print("TC-S5-007-12: PASSED - Container restart simulation successful")

    finally:
        # Cleanup
        for file_path in test_files:
            if file_path.exists():
                file_path.unlink()

        case_dir = test_docs_path / test_case_id
        if case_dir.exists():
            import shutil
            shutil.rmtree(case_dir, ignore_errors=True)

        if manifest_backup:
            with open(MANIFEST_PATH, 'w') as f:
                f.write(manifest_backup)


if __name__ == "__main__":
    try:
        test_TC_S5_007_12()
        print("TC-S5-007-12: PASSED")
    except AssertionError as e:
        print(f"TC-S5-007-12: FAILED - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"TC-S5-007-12: ERROR - {e}")
        sys.exit(1)
