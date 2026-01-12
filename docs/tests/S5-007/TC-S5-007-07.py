"""
Test Case: TC-S5-007-07
Requirement: S5-007 - Container-Compatible File Persistence
Description: Document with renders, restart app, verify render structure preserved
Generated: 2026-01-09T15:29:16Z
Updated: 2026-01-12
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))

from services.document_registry import (
    register_document,
    load_manifest,
    save_manifest,
    MANIFEST_PATH,
    DocumentRegistry
)
from datetime import datetime, timezone


def test_TC_S5_007_07():
    """Document with renders, restart app, verify render structure preserved"""

    test_case_id = "ACTE-TEST-007"
    test_folder_id = "test-folder-07"
    test_file_name = "doc_with_renders.pdf"
    test_docs_path = Path("public/documents")
    test_file_path = test_docs_path / test_case_id / test_folder_id / test_file_name

    manifest_backup = None
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, 'r') as f:
            manifest_backup = f.read()

    try:
        # Create and register main document
        test_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(test_file_path, 'wb') as f:
            f.write(b"Main document with renders for TC-S5-007-07")

        entry = register_document(
            case_id=test_case_id,
            folder_id=test_folder_id,
            file_path=str(test_file_path),
            file_name=test_file_name
        )

        # Add renders to the document
        test_renders = [
            {
                "renderId": "render_001",
                "type": "anonymized",
                "filePath": f"{test_file_path.parent}/anonymized_{test_file_name}",
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "language": None
            },
            {
                "renderId": "render_002",
                "type": "translated",
                "filePath": f"{test_file_path.parent}/translated_de_{test_file_name}",
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "language": "de"
            }
        ]

        # Update document in manifest with renders
        registry = load_manifest()
        documents_list = list(registry.documents)

        for doc in documents_list:
            if doc.get('documentId') == entry['documentId']:
                doc['renders'] = test_renders
                break

        updated_registry = DocumentRegistry(
            version=registry.version,
            schemaVersion=registry.schemaVersion,
            lastUpdated=datetime.now(timezone.utc).isoformat(),
            documents=documents_list
        )
        save_manifest(updated_registry)

        # Simulate app restart: reload manifest
        registry_after_restart = load_manifest()

        # Find the document and verify renders are preserved
        found = False
        for doc in registry_after_restart.documents:
            if doc.get('documentId') == entry['documentId']:
                found = True
                renders = doc.get('renders', [])

                assert len(renders) == 2, f"Expected 2 renders, found {len(renders)}"

                # Verify first render (anonymized)
                assert renders[0]['renderId'] == "render_001", "Render 1 ID mismatch"
                assert renders[0]['type'] == "anonymized", "Render 1 type should be anonymized"
                assert renders[0]['language'] is None, "Render 1 language should be None"

                # Verify second render (translated)
                assert renders[1]['renderId'] == "render_002", "Render 2 ID mismatch"
                assert renders[1]['type'] == "translated", "Render 2 type should be translated"
                assert renders[1]['language'] == "de", "Render 2 language should be 'de'"

                # Verify all renders have required fields
                for render in renders:
                    assert 'renderId' in render, "Render missing renderId"
                    assert 'type' in render, "Render missing type"
                    assert 'filePath' in render, "Render missing filePath"
                    assert 'createdAt' in render, "Render missing createdAt"

                break

        assert found, "Document with renders not found after restart"

        print("TC-S5-007-07: PASSED - Render structure preserved after restart")

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
        test_TC_S5_007_07()
        print("TC-S5-007-07: PASSED")
    except AssertionError as e:
        print(f"TC-S5-007-07: FAILED - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"TC-S5-007-07: ERROR - {e}")
        sys.exit(1)
