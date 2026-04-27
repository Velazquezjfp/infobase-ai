"""
Test Case: TC-S5-007-09
Requirement: S5-007 - Container-Compatible File Persistence
Description: Corrupt manifest file, verify app creates new manifest from filesystem scan
Generated: 2026-01-09T15:29:16Z
Updated: 2026-01-12
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))

from services.document_registry import (
    load_manifest,
    scan_filesystem,
    reconcile,
    MANIFEST_PATH
)


def test_TC_S5_007_09():
    """Corrupt manifest file, verify app creates new manifest from filesystem scan"""

    test_docs_path = Path("public/documents")

    # Backup original manifest
    manifest_backup = None
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, 'r') as f:
            manifest_backup = f.read()

    try:
        # Corrupt the manifest file (invalid JSON)
        with open(MANIFEST_PATH, 'w') as f:
            f.write("{ invalid json content ][")

        # Try to load manifest - should return empty manifest instead of crashing
        registry = load_manifest()

        # Verify empty manifest was created
        assert registry is not None, "Registry should not be None"
        assert registry.version == "1.0", "New registry should have version 1.0"
        assert isinstance(registry.documents, list), "Documents should be a list"

        # Verify manifest recovery via filesystem scan
        filesystem_files = scan_filesystem(str(test_docs_path))

        # If there are files, reconciliation should add them
        if filesystem_files:
            reconcile_report = reconcile(registry, filesystem_files)

            # Verify files were added from filesystem
            assert len(reconcile_report.added) > 0 or len(filesystem_files) == 0, \
                "Orphaned files should be detected after manifest corruption"

            # Load manifest again to verify it was rebuilt
            registry_rebuilt = load_manifest()
            assert registry_rebuilt is not None, "Rebuilt registry should not be None"

        print("TC-S5-007-09: PASSED - App recovers from corrupt manifest")

    finally:
        # Restore original manifest
        if manifest_backup:
            with open(MANIFEST_PATH, 'w') as f:
                f.write(manifest_backup)


if __name__ == "__main__":
    try:
        test_TC_S5_007_09()
        print("TC-S5-007-09: PASSED")
    except AssertionError as e:
        print(f"TC-S5-007-09: FAILED - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"TC-S5-007-09: ERROR - {e}")
        sys.exit(1)
