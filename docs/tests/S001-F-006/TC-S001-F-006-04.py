"""TC-S001-F-006-04 — drop on FileDropZone is ignored when feature is off.

Source-level verification (no frontend test runner — see TC-03):

  1. FileDropZone.uploadFiles short-circuits on !uploadEnabled before any
     iteration of the file list, so the network upload never fires.
  2. The notice surfaced is t('upload.notImplemented'), the i18n key
     introduced by this requirement.
  3. The same short-circuit guards FolderItem.handleDrop in CaseTreeExplorer.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DROP_ZONE = REPO_ROOT / "src" / "components" / "workspace" / "FileDropZone.tsx"
CASE_TREE = REPO_ROOT / "src" / "components" / "workspace" / "CaseTreeExplorer.tsx"
DE_LOCALE = REPO_ROOT / "src" / "i18n" / "locales" / "de.json"
EN_LOCALE = REPO_ROOT / "src" / "i18n" / "locales" / "en.json"


def test_upload_not_implemented_de():
    data = json.loads(DE_LOCALE.read_text(encoding="utf-8"))
    assert "upload" in data, "de.json missing 'upload' namespace"
    assert "notImplemented" in data["upload"]
    assert "deaktiviert" in data["upload"]["notImplemented"]


def test_upload_not_implemented_en():
    data = json.loads(EN_LOCALE.read_text(encoding="utf-8"))
    assert "upload" in data, "en.json missing 'upload' namespace"
    assert "notImplemented" in data["upload"]
    assert len(data["upload"]["notImplemented"]) > 0


def test_drop_zone_upload_files_short_circuits():
    src = DROP_ZONE.read_text(encoding="utf-8")
    # Locate uploadFiles function definition and confirm it returns early
    # on !uploadEnabled before the for-loop over files.
    fn_match = re.search(
        r"const uploadFiles = async \(files: File\[\]\) => \{(.*?)\n  \};",
        src,
        re.DOTALL,
    )
    assert fn_match, "uploadFiles function not found"
    body = fn_match.group(1)
    early_idx = body.find("if (!uploadEnabled)")
    loop_idx = body.find("for (const file of files)")
    assert early_idx != -1, "uploadFiles must guard on !uploadEnabled"
    assert loop_idx != -1, "uploadFiles still needs to iterate files in enabled path"
    assert early_idx < loop_idx, "Guard must short-circuit before the upload loop"
    assert "upload.notImplemented" in body, \
        "uploadFiles must surface upload.notImplemented when feature is off"


def test_folder_drop_short_circuits():
    src = CASE_TREE.read_text(encoding="utf-8")
    handle_drop = re.search(
        r"const handleDrop = async \(e: React\.DragEvent\) => \{(.*?)\n  \};",
        src,
        re.DOTALL,
    )
    assert handle_drop, "FolderItem.handleDrop not found in CaseTreeExplorer"
    body = handle_drop.group(1)
    assert "uploadEnabled" in body, "handleDrop must guard on uploadEnabled"
    assert "upload.notImplemented" in body
