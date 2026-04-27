"""
Test Case: TC-D-S5-002-03
Requirement: D-S5-002 - Document Registry Schema
Description: Document with 2 renders, verify renders array has 2 entries
Generated: 2026-01-09T16:00:00Z

Note: This test validates renders array structure in document registry
"""

import json
from pathlib import Path

def test_TC_D_S5_002_03():
    """Document renders array validation"""
    # Get absolute paths
    base_path = Path(__file__).resolve().parents[3]
    manifest_path = base_path / "backend/data/document_manifest.json"

    # 1. Load manifest
    assert manifest_path.exists(), f"Manifest file not found: {manifest_path}"
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    documents = manifest["documents"]

    # 2. Find document with 2 renders (doc_001 should have 2 renders)
    doc_with_2_renders = None
    for doc in documents:
        if len(doc.get("renders", [])) == 2:
            doc_with_2_renders = doc
            break

    assert doc_with_2_renders is not None, "No document with 2 renders found in manifest"

    # 3. Extract renders array
    renders = doc_with_2_renders["renders"]

    # 4. Verify renders is an array
    assert isinstance(renders, list), "renders must be an array"

    # 5. Verify renders array length = 2
    assert len(renders) == 2, f"Expected 2 renders, found {len(renders)}"

    # 6. Verify each render entry has required fields
    required_fields = ["renderId", "type", "filePath", "createdAt"]
    render_ids = []

    for i, render in enumerate(renders):
        # a. Verify renderId present and unique
        assert "renderId" in render, f"Render {i} missing renderId"
        render_ids.append(render["renderId"])

        # b. Verify type field present
        assert "type" in render, f"Render {i} missing type field"
        assert render["type"] in ["anonymized", "translated"], \
            f"Render {i} has invalid type: {render['type']}"

        # c. Verify filePath present
        assert "filePath" in render, f"Render {i} missing filePath"
        assert len(render["filePath"]) > 0, f"Render {i} filePath is empty"

        # d. Verify createdAt present and valid format
        assert "createdAt" in render, f"Render {i} missing createdAt"
        assert "T" in render["createdAt"], f"Render {i} createdAt not ISO 8601 format"

    # Verify renderIds are unique within document
    assert len(render_ids) == len(set(render_ids)), "Render IDs must be unique within document"

    print(f"✓ Found document '{doc_with_2_renders['documentId']}' with 2 renders")
    print(f"✓ Render types: {[r['type'] for r in renders]}")
    print("✓ All render entries have required fields")
    print("✓ All render IDs are unique")

if __name__ == "__main__":
    try:
        test_TC_D_S5_002_03()
        print("TC-D-S5-002-03: PASSED")
    except AssertionError as e:
        print(f"TC-D-S5-002-03: FAILED - {e}")
    except Exception as e:
        print(f"TC-D-S5-002-03: ERROR - {e}")
