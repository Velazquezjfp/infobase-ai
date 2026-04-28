"""TC-S001-F-003-02 — i18n disclaimer: context.offlineNotice exists in both
de.json and en.json with the correct translations.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
LOCALES = REPO_ROOT / "src" / "i18n" / "locales"
DE_PATH = LOCALES / "de.json"
EN_PATH = LOCALES / "en.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_de_has_offline_notice():
    de = _load(DE_PATH)
    assert "context" in de, "de.json must have a top-level 'context' section"
    assert "offlineNotice" in de["context"], "de.json must have context.offlineNotice"
    assert de["context"]["offlineNotice"] == "Offline-Modus: Inhalt wird simuliert", (
        f"de offlineNotice mismatch: {de['context']['offlineNotice']!r}"
    )


def test_en_has_offline_notice():
    en = _load(EN_PATH)
    assert "context" in en, "en.json must have a top-level 'context' section"
    assert "offlineNotice" in en["context"], "en.json must have context.offlineNotice"
    assert en["context"]["offlineNotice"] == "Offline mode: content is simulated", (
        f"en offlineNotice mismatch: {en['context']['offlineNotice']!r}"
    )


def test_case_context_dialog_uses_offline_notice():
    """CaseContextDialog must reference t('context.offlineNotice') not an <a> tag."""
    dialog = REPO_ROOT / "src" / "components" / "workspace" / "CaseContextDialog.tsx"
    source = dialog.read_text(encoding="utf-8")

    assert "context.offlineNotice" in source, (
        "CaseContextDialog must use t('context.offlineNotice') for regulation URLs"
    )
    assert 'target="_blank"' not in source, (
        "CaseContextDialog must not contain target='_blank' — URLs must be inert"
    )
    assert 'ExternalLink' not in source, (
        "CaseContextDialog must not use ExternalLink icon after URL-link removal"
    )
