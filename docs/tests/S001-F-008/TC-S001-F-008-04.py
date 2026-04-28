"""TC-S001-F-008-04 — English warning: removing a key from en.json makes
the coverage script exit 0 with a warning naming the missing key.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _helpers import DE_PATH, EN_PATH, load_json, remove_key, run_coverage, write_json  # noqa: E402


def test_coverage_warns_but_passes_when_en_missing_key(tmp_path):
    de = load_json(DE_PATH)
    en = load_json(EN_PATH)

    target_key = "common.save"
    assert remove_key(en, target_key), "fixture: common.save should exist in en.json"
    assert "save" in de.get("common", {}), "fixture: common.save should still exist in de.json"

    de_path = tmp_path / "de.json"
    en_path = tmp_path / "en.json"
    write_json(de_path, de)
    write_json(en_path, en)

    result = run_coverage(de_path, en_path)
    assert result.returncode == 0, (
        f"expected exit 0 (English warnings only), got {result.returncode}; "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )

    combined = result.stdout + result.stderr
    assert target_key in combined, (
        f"expected coverage script to warn about {target_key!r}, got: {combined!r}"
    )
    assert "warning" in combined.lower()
