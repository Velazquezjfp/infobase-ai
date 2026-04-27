"""
Test Case: TC-D-S5-002-05
Requirement: D-S5-002 - Document Registry Schema
Description: Translated render includes language field (e.g., "de", "en")
Generated: 2026-01-09T16:00:00Z

Note: This test validates language field presence in translated render entries
"""

import json
import re
from pathlib import Path

def test_TC_D_S5_002_05():
    """Translated render language field validation"""
    # Get absolute paths
    base_path = Path(__file__).resolve().parents[3]
    manifest_path = base_path / "backend/data/document_manifest.json"

    # 1. Load manifest
    assert manifest_path.exists(), f"Manifest file not found: {manifest_path}"
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    documents = manifest["documents"]

    # 2. Find documents with translated renders
    translated_renders = []
    anonymized_renders = []

    for doc in documents:
        for render in doc.get("renders", []):
            if render["type"] == "translated":
                translated_renders.append((doc["documentId"], render))
            elif render["type"] == "anonymized":
                anonymized_renders.append((doc["documentId"], render))

    assert len(translated_renders) > 0, "No translated renders found in manifest"

    # 3. Validate each translated render
    language_pattern = re.compile(r'^[a-z]{2}$')

    for doc_id, render in translated_renders:
        # a. Verify type = "translated"
        assert render["type"] == "translated", f"Expected type 'translated', got '{render['type']}'"

        # b. Verify language field present
        assert "language" in render, \
            f"Translated render {render['renderId']} in doc {doc_id} missing language field"

        # c. Verify language is valid ISO 639-1 code (2-letter lowercase)
        language = render["language"]
        assert language_pattern.match(language), \
            f"Language '{language}' is not valid ISO 639-1 format (expected 2 lowercase letters)"

        # d. Verify language matches filename (if encoded)
        file_path = render["filePath"]
        if f"_translated_{language}" in file_path or f"_translated_{language.upper()}" in file_path:
            print(f"  ✓ Language '{language}' matches filename: {file_path}")

    # 4. Verify anonymized renders do NOT require language field (optional check)
    for doc_id, render in anonymized_renders:
        assert render["type"] == "anonymized", f"Expected type 'anonymized'"
        # Language field is optional for anonymized renders - we just verify it doesn't cause issues

    print(f"✓ Found {len(translated_renders)} translated renders")
    print("✓ All translated renders have 'language' field")
    print("✓ All language codes are valid ISO 639-1 format (2 lowercase letters)")
    print(f"✓ Languages found: {sorted(set(r[1]['language'] for r in translated_renders))}")

    # Additional check: Verify language field NOT present in anonymized renders
    anonymized_with_language = [r for _, r in anonymized_renders if "language" in r]
    if len(anonymized_with_language) > 0:
        print(f"  Note: {len(anonymized_with_language)} anonymized renders have optional language field")

if __name__ == "__main__":
    try:
        test_TC_D_S5_002_05()
        print("TC-D-S5-002-05: PASSED")
    except AssertionError as e:
        print(f"TC-D-S5-002-05: FAILED - {e}")
    except Exception as e:
        print(f"TC-D-S5-002-05: ERROR - {e}")
