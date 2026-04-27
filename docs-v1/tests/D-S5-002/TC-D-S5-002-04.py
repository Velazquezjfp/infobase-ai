"""
Test Case: TC-D-S5-002-04
Requirement: D-S5-002 - Document Registry Schema
Description: Render entry includes type and createdAt, verify fields present
Generated: 2026-01-09T16:00:00Z

Note: This test validates required fields in render entries
"""

import json
from pathlib import Path
from datetime import datetime

def test_TC_D_S5_002_04():
    """Render entry required fields validation"""
    # Get absolute paths
    base_path = Path(__file__).resolve().parents[3]
    manifest_path = base_path / "backend/data/document_manifest.json"

    # 1. Load manifest
    assert manifest_path.exists(), f"Manifest file not found: {manifest_path}"
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    documents = manifest["documents"]

    # 2. Find documents with renders
    docs_with_renders = [doc for doc in documents if len(doc.get("renders", [])) > 0]
    assert len(docs_with_renders) > 0, "No documents with renders found in manifest"

    # 3. Validate each render in each document
    valid_types = ["anonymized", "translated"]
    required_fields = ["renderId", "type", "filePath", "createdAt"]
    total_renders = 0

    for doc in docs_with_renders:
        renders = doc["renders"]
        for render in renders:
            total_renders += 1

            # a. Verify renderId field present and non-empty
            assert "renderId" in render, f"Render missing renderId in doc {doc['documentId']}"
            assert len(render["renderId"]) > 0, f"renderId is empty in doc {doc['documentId']}"

            # b. Verify type field present and valid value
            assert "type" in render, f"Render {render.get('renderId')} missing type field"
            assert render["type"] in valid_types, \
                f"Render {render['renderId']} has invalid type: {render['type']} (expected: {valid_types})"

            # c. Verify filePath field present and non-empty
            assert "filePath" in render, f"Render {render['renderId']} missing filePath"
            assert len(render["filePath"]) > 0, f"filePath is empty for render {render['renderId']}"

            # d. Verify createdAt field present and valid ISO 8601
            assert "createdAt" in render, f"Render {render['renderId']} missing createdAt"
            created_at = render["createdAt"]
            try:
                # Parse ISO 8601 timestamp
                datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except ValueError:
                raise AssertionError(f"Render {render['renderId']} has invalid ISO 8601 timestamp: {created_at}")

            # Verify all required fields present
            for field in required_fields:
                assert field in render, f"Render {render['renderId']} missing required field: {field}"

    print(f"✓ Validated {total_renders} renders across {len(docs_with_renders)} documents")
    print(f"✓ All renders have required fields: {', '.join(required_fields)}")
    print(f"✓ All render types are valid: {valid_types}")
    print("✓ All createdAt timestamps are valid ISO 8601 format")

if __name__ == "__main__":
    try:
        test_TC_D_S5_002_04()
        print("TC-D-S5-002-04: PASSED")
    except AssertionError as e:
        print(f"TC-D-S5-002-04: FAILED - {e}")
    except Exception as e:
        print(f"TC-D-S5-002-04: ERROR - {e}")
