"""TC-S001-F-008-01 — happy path: with UI in `en` and `chat.placeholder`
missing from en.json, t() returns the German translation from de.json.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _helpers import DE_PATH, EN_PATH, load_json, remove_key, run_i18next  # noqa: E402


def test_en_falls_back_to_de_when_key_missing(tmp_path):
    de = load_json(DE_PATH)
    en = load_json(EN_PATH)

    expected_german = de["chat"]["placeholder"]
    assert expected_german, "de.json must define chat.placeholder for this test"

    assert remove_key(en, "chat.placeholder"), "test fixture: chat.placeholder should exist in en.json"
    assert "placeholder" not in en.get("chat", {}), "fixture failed to remove chat.placeholder from en"

    result = run_i18next("en", "chat.placeholder", de, en, tmp_path)
    assert result.returncode == 0, f"runner failed: {result.stderr}"
    assert result.stdout == expected_german, (
        f"expected German fallback {expected_german!r}, got {result.stdout!r}"
    )
