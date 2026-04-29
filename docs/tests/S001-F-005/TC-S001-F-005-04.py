"""TC-S001-F-005-04 — frontend i18n key exists with correct German text.

Verifies that documentSearch.notImplemented is present in de.json
and contains the expected German notice text, which AIChatInterface
renders when it receives error="feature_disabled".
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DE_LOCALE = REPO_ROOT / "src" / "i18n" / "locales" / "de.json"
EN_LOCALE = REPO_ROOT / "src" / "i18n" / "locales" / "en.json"


def test_de_locale_has_not_implemented_key():
    data = json.loads(DE_LOCALE.read_text(encoding="utf-8"))
    key = data["documentSearch"]["notImplemented"]
    assert "Dokumentsuche" in key


def test_en_locale_has_not_implemented_key():
    data = json.loads(EN_LOCALE.read_text(encoding="utf-8"))
    key = data["documentSearch"]["notImplemented"]
    assert len(key) > 0
