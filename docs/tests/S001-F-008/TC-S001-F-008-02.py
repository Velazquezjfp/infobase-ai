"""TC-S001-F-008-02 — missing-everywhere fallback: with `chat.foo` absent in
both locales, t("chat.foo") returns the bare string "chat.foo" and i18next
emits no console.error.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _helpers import DE_PATH, EN_PATH, load_json, run_i18next  # noqa: E402


def test_returns_key_when_missing_everywhere(tmp_path):
    de = load_json(DE_PATH)
    en = load_json(EN_PATH)

    assert "foo" not in de.get("chat", {}), "fixture assumption: chat.foo absent in de.json"
    assert "foo" not in en.get("chat", {}), "fixture assumption: chat.foo absent in en.json"

    result = run_i18next("en", "chat.foo", de, en, tmp_path)
    assert result.returncode == 0, f"runner failed: {result.stderr}"
    assert result.stdout == "chat.foo", (
        f"expected bare key 'chat.foo', got {result.stdout!r}"
    )
    assert "undefined" not in result.stdout
    assert result.stderr.strip() == "", (
        f"i18next must not emit error output for missing keys, got: {result.stderr!r}"
    )
