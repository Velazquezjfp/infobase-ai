"""TC-S001-F-004-03 — i18n keys for the frontend info toast.

Both locale files must contain the anonymization.notImplemented key with the
correct translated strings so the frontend can display the info toast.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DE_LOCALE = REPO_ROOT / "src" / "i18n" / "locales" / "de.json"
EN_LOCALE = REPO_ROOT / "src" / "i18n" / "locales" / "en.json"

DE_EXPECTED = "Die Anonymisierungsfunktion ist in dieser Demo-Umgebung noch nicht verfügbar."
EN_EXPECTED = "The anonymization feature is not yet available in this demo environment."


def test_de_locale_has_anonymization_not_implemented():
    data = json.loads(DE_LOCALE.read_text(encoding="utf-8"))
    assert "anonymization" in data, "de.json missing top-level 'anonymization' key"
    assert data["anonymization"]["notImplemented"] == DE_EXPECTED


def test_en_locale_has_anonymization_not_implemented():
    data = json.loads(EN_LOCALE.read_text(encoding="utf-8"))
    assert "anonymization" in data, "en.json missing top-level 'anonymization' key"
    assert data["anonymization"]["notImplemented"] == EN_EXPECTED
