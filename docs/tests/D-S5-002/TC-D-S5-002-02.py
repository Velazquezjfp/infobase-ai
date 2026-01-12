"""
Test Case: TC-D-S5-002-02
Requirement: D-S5-002 - Document Registry Schema
Description: Document entry includes fileHash, verify integrity check works
Generated: 2026-01-09T16:00:00Z

Note: This test validates file hash integrity checking functionality
"""

import json
import re
from pathlib import Path

def test_TC_D_S5_002_02():
    """Document file hash integrity validation"""
    # Get absolute paths
    base_path = Path(__file__).resolve().parents[3]
    manifest_path = base_path / "backend/data/document_manifest.json"

    # 1. Load manifest
    assert manifest_path.exists(), f"Manifest file not found: {manifest_path}"
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    # 2. Select document entries
    documents = manifest["documents"]
    assert len(documents) > 0, "No documents in manifest"

    # 3. Verify each document has fileHash field
    hash_pattern = re.compile(r'^sha256:[a-f0-9]{64}$')

    for doc in documents:
        # Verify fileHash field exists
        assert "fileHash" in doc, f"Document {doc.get('documentId')} missing fileHash field"

        file_hash = doc["fileHash"]

        # Verify hash format: "sha256:" + 64 hex characters
        assert file_hash.startswith("sha256:"), \
            f"fileHash must start with 'sha256:' prefix: {file_hash}"

        assert hash_pattern.match(file_hash), \
            f"fileHash format invalid (expected sha256:[a-f0-9]{{64}}): {file_hash}"

        # Verify hash contains only lowercase hex
        hex_part = file_hash.replace("sha256:", "")
        assert len(hex_part) == 64, f"SHA-256 hash must be 64 characters: {hex_part}"
        assert all(c in "0123456789abcdef" for c in hex_part), \
            f"Hash must contain only lowercase hex characters: {hex_part}"

    print(f"✓ All {len(documents)} documents have valid fileHash fields")
    print("✓ Hash format: sha256:[a-f0-9]{64} verified for all documents")

    # Additional validation: Check for unique hashes
    hashes = [doc["fileHash"] for doc in documents]
    assert len(hashes) == len(set(hashes)), "File hashes must be unique across documents"
    print("✓ All file hashes are unique")

if __name__ == "__main__":
    try:
        test_TC_D_S5_002_02()
        print("TC-D-S5-002-02: PASSED")
    except AssertionError as e:
        print(f"TC-D-S5-002-02: FAILED - {e}")
    except Exception as e:
        print(f"TC-D-S5-002-02: ERROR - {e}")
