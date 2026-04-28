"""TC-S001-F-003-05 — missing-key fallback: when context.offlineNotice is
absent from a locale file, the UI renders the key string itself rather than
throwing an error (per S001-F-008 fallback behaviour).

This test loads de.json without the context.offlineNotice key and verifies
that the i18next fallback chain returns the key name, not an exception.
It reuses the _i18next_runner.mjs helper from S001-F-008.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

LOCALES_DIR = REPO_ROOT / "src" / "i18n" / "locales"
I18NEXT_RUNNER = REPO_ROOT / "docs" / "tests" / "S001-F-008" / "_i18next_runner.mjs"

import subprocess


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _run_i18next(language: str, key: str, de_data: dict, en_data: dict, tmp_path: Path):
    de_file = tmp_path / "de.json"
    en_file = tmp_path / "en.json"
    _write(de_file, de_data)
    _write(en_file, en_data)
    return subprocess.run(
        ["node", str(I18NEXT_RUNNER), language, key, str(de_file), str(en_file)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


def test_missing_offline_notice_returns_key_name(tmp_path):
    """When context.offlineNotice is missing from both locales, t() returns the key."""
    de = _load(LOCALES_DIR / "de.json")
    en = _load(LOCALES_DIR / "en.json")

    # Remove context.offlineNotice from both to simulate a missing-key scenario
    if "context" in de and "offlineNotice" in de["context"]:
        del de["context"]["offlineNotice"]
    if "context" in en and "offlineNotice" in en["context"]:
        del en["context"]["offlineNotice"]

    if not I18NEXT_RUNNER.exists():
        # If the runner helper is not available, fall back to checking
        # that the locale files themselves validate cleanly (no throw on load)
        import pytest
        pytest.skip("_i18next_runner.mjs not available; skipping Node-based test")

    result = _run_i18next("de", "context.offlineNotice", de, en, tmp_path)
    assert result.returncode == 0, f"i18next runner failed: {result.stderr}"
    # i18next returns the key itself when no translation is found
    assert result.stdout == "context.offlineNotice", (
        f"Expected key name fallback, got: {result.stdout!r}"
    )


def test_present_offline_notice_not_key_name(tmp_path):
    """When context.offlineNotice is present in de.json, t() returns the German string."""
    de = _load(LOCALES_DIR / "de.json")
    en = _load(LOCALES_DIR / "en.json")

    if not I18NEXT_RUNNER.exists():
        import pytest
        pytest.skip("_i18next_runner.mjs not available; skipping Node-based test")

    result = _run_i18next("de", "context.offlineNotice", de, en, tmp_path)
    assert result.returncode == 0, f"i18next runner failed: {result.stderr}"
    assert result.stdout == "Offline-Modus: Inhalt wird simuliert", (
        f"Expected German translation, got: {result.stdout!r}"
    )
