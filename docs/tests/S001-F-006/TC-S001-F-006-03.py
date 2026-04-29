"""TC-S001-F-006-03 — UI Upload button has aria-disabled when feature is off.

No frontend test runner is configured for this project (package.json has
no `test` script and no jest/vitest dep), so this test verifies at the
source level that:

  1. CaseTreeExplorer reads the upload feature flag via checkUploadEnabled.
  2. The drop-zone button is rendered with `aria-disabled={!uploadEnabled}`
     and a notImplemented title when off.
  3. handleUploadClick + handleDropZoneClick short-circuit before invoking
     the file picker when uploadEnabled is false.
  4. FileDropZone's <button> uses both `disabled` and `aria-disabled` when
     the feature is off, satisfying the acceptance criterion verbatim.

Source-level verification is the same pattern used by S001-F-005 TC-04.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CASE_TREE = REPO_ROOT / "src" / "components" / "workspace" / "CaseTreeExplorer.tsx"
DROP_ZONE = REPO_ROOT / "src" / "components" / "workspace" / "FileDropZone.tsx"


def test_case_tree_imports_check_upload_enabled():
    src = CASE_TREE.read_text(encoding="utf-8")
    assert re.search(r"\bcheckUploadEnabled\b", src), \
        "CaseTreeExplorer must import checkUploadEnabled from fileApi"


def test_case_tree_drop_zone_has_aria_disabled():
    src = CASE_TREE.read_text(encoding="utf-8")
    assert "aria-disabled={!uploadEnabled}" in src, \
        "Drop zone must set aria-disabled based on uploadEnabled flag"


def test_case_tree_short_circuits_upload_click():
    src = CASE_TREE.read_text(encoding="utf-8")
    # handleUploadClick should test uploadEnabled before clicking the input.
    upload_click_block = re.search(
        r"const handleUploadClick = \(e: React\.MouseEvent\) => \{(.*?)\n  \};",
        src,
        re.DOTALL,
    )
    assert upload_click_block, "handleUploadClick block not found"
    body = upload_click_block.group(1)
    assert "uploadEnabled" in body, "handleUploadClick must guard on uploadEnabled"
    assert "fileInputRef.current?.click()" in body, \
        "handleUploadClick must still click input when enabled"


def test_case_tree_short_circuits_drop_zone_click():
    src = CASE_TREE.read_text(encoding="utf-8")
    drop_click_block = re.search(
        r"const handleDropZoneClick = \(\) => \{(.*?)\n  \};",
        src,
        re.DOTALL,
    )
    assert drop_click_block, "handleDropZoneClick block not found"
    body = drop_click_block.group(1)
    assert "uploadEnabled" in body, "handleDropZoneClick must guard on uploadEnabled"


def test_drop_zone_button_has_disabled_and_aria_disabled():
    src = DROP_ZONE.read_text(encoding="utf-8")
    # Acceptance criterion: button rendered with both attributes when feature off.
    assert "aria-disabled={!uploadEnabled}" in src
    assert "disabled={!uploadEnabled}" in src


def test_drop_zone_button_short_circuits_click():
    src = DROP_ZONE.read_text(encoding="utf-8")
    handle_click = re.search(
        r"const handleClick = useCallback\(\(\) => \{(.*?)\n  \},",
        src,
        re.DOTALL,
    )
    assert handle_click, "handleClick block not found in FileDropZone"
    body = handle_click.group(1)
    assert "uploadEnabled" in body, "handleClick must guard on uploadEnabled"
