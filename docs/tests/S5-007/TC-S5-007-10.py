"""
Test Case: TC-S5-007-10
Requirement: S5-007 - Container-Compatible File Persistence
Description: GET /api/documents/tree/ACTE-2024-001, verify returns complete folder structure
Generated: 2026-01-09T15:29:16Z
Updated: 2026-01-12
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))

from services.document_registry import build_document_tree


def test_TC_S5_007_10():
    """GET /api/documents/tree/ACTE-2024-001, verify returns complete folder structure"""

    # Test with actual case ID from the system
    case_id = "ACTE-2024-001"

    try:
        # Call the document tree builder (same function used by API endpoint)
        tree = build_document_tree(case_id)

        # Verify tree structure
        assert isinstance(tree, dict), "Tree should be a dictionary"
        assert 'folders' in tree, "Tree should have 'folders' key"
        assert 'rootDocuments' in tree, "Tree should have 'rootDocuments' key"

        # Verify folders structure
        folders = tree['folders']
        assert isinstance(folders, list), "Folders should be a list"

        # If there are folders, verify their structure
        for folder in folders:
            assert 'id' in folder, "Folder should have 'id'"
            assert 'name' in folder, "Folder should have 'name'"
            assert 'documents' in folder, "Folder should have 'documents'"
            assert 'subfolders' in folder, "Folder should have 'subfolders'"
            assert 'isExpanded' in folder, "Folder should have 'isExpanded'"

            # Verify folder documents
            for doc in folder['documents']:
                assert 'documentId' in doc, "Document should have 'documentId'"
                assert 'fileName' in doc, "Document should have 'fileName'"
                assert 'caseId' in doc, "Document should have 'caseId'"
                assert doc['caseId'] == case_id, f"Document case ID should match {case_id}"

        # Verify root documents structure
        root_docs = tree['rootDocuments']
        assert isinstance(root_docs, list), "Root documents should be a list"

        for doc in root_docs:
            assert 'documentId' in doc, "Root document should have 'documentId'"
            assert 'fileName' in doc, "Root document should have 'fileName'"
            assert 'caseId' in doc, "Root document should have 'caseId'"
            assert doc['caseId'] == case_id, f"Root document case ID should match {case_id}"
            assert doc.get('folderId') is None, "Root document should not have folderId"

        # Verify the tree is consistent (all documents belong to the case)
        all_docs = []
        for folder in folders:
            all_docs.extend(folder['documents'])
        all_docs.extend(root_docs)

        for doc in all_docs:
            assert doc['caseId'] == case_id, \
                f"Document {doc['fileName']} belongs to wrong case {doc['caseId']}"

        print(f"TC-S5-007-10: PASSED - Document tree for {case_id} has valid structure")
        print(f"  - Folders: {len(folders)}")
        print(f"  - Root documents: {len(root_docs)}")
        print(f"  - Total documents: {len(all_docs)}")

    except Exception as e:
        print(f"TC-S5-007-10: ERROR - {e}")
        raise


if __name__ == "__main__":
    try:
        test_TC_S5_007_10()
        print("TC-S5-007-10: PASSED")
    except AssertionError as e:
        print(f"TC-S5-007-10: FAILED - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"TC-S5-007-10: ERROR - {e}")
        sys.exit(1)
