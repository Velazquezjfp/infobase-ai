"""
Test Case: TC-D-S5-002-01
Requirement: D-S5-002 - Document Registry Schema
Description: Load manifest, verify conforms to schema
Generated: 2026-01-09T16:00:00Z

Note: This test validates document registry manifest against JSON schema
"""

import json
import os
from pathlib import Path
from jsonschema import validate, ValidationError

def test_TC_D_S5_002_01():
    """Document manifest schema validation"""
    # Get absolute paths
    base_path = Path(__file__).resolve().parents[3]
    schema_path = base_path / "backend/schemas/document_registry_schema.json"
    manifest_path = base_path / "backend/data/document_manifest.json"

    # 1. Load JSON schema
    assert schema_path.exists(), f"Schema file not found: {schema_path}"
    with open(schema_path, 'r') as f:
        schema = json.load(f)

    # 2. Load manifest
    assert manifest_path.exists(), f"Manifest file not found: {manifest_path}"
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    # 3. Validate manifest against schema
    try:
        validate(instance=manifest, schema=schema)
    except ValidationError as e:
        raise AssertionError(f"Manifest validation failed: {e.message}")

    # 4. Verify required top-level fields present
    required_fields = ["version", "schemaVersion", "lastUpdated", "documents"]
    for field in required_fields:
        assert field in manifest, f"Required field '{field}' missing from manifest"

    # 5. Verify field types
    assert isinstance(manifest["version"], str), "version must be string"
    assert isinstance(manifest["schemaVersion"], str), "schemaVersion must be string"
    assert isinstance(manifest["lastUpdated"], str), "lastUpdated must be string"
    assert isinstance(manifest["documents"], list), "documents must be array"

    # 6. Verify documents array contains valid entries
    assert len(manifest["documents"]) > 0, "documents array should not be empty"

    # Verify each document has required fields
    for doc in manifest["documents"]:
        required_doc_fields = ["documentId", "caseId", "fileName", "filePath",
                               "uploadedAt", "fileHash", "renders"]
        for field in required_doc_fields:
            assert field in doc, f"Document missing required field: {field}"

    print("✓ Manifest conforms to JSON Schema")
    print(f"✓ Version: {manifest['version']}, Schema Version: {manifest['schemaVersion']}")
    print(f"✓ Total documents: {len(manifest['documents'])}")

if __name__ == "__main__":
    try:
        test_TC_D_S5_002_01()
        print("TC-D-S5-002-01: PASSED")
    except AssertionError as e:
        print(f"TC-D-S5-002-01: FAILED - {e}")
    except Exception as e:
        print(f"TC-D-S5-002-01: ERROR - {e}")
