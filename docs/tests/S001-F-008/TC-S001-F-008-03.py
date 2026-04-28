"""TC-S001-F-008-03 — German required: removing a key from de.json so it is
only present in en.json makes the coverage script exit 1 (German is the
source of truth).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _helpers import DE_PATH, EN_PATH, load_json, remove_key, run_coverage, write_json  # noqa: E402


def test_coverage_exits_1_when_de_missing_key(tmp_path):
    de = load_json(DE_PATH)
    en = load_json(EN_PATH)

    target_key = "common.save"
    assert remove_key(de, target_key), "fixture: common.save should exist in de.json"
    assert "save" in en.get("common", {}), "fixture: common.save should still exist in en.json"

    de_path = tmp_path / "de.json"
    en_path = tmp_path / "en.json"
    write_json(de_path, de)
    write_json(en_path, en)

    result = run_coverage(de_path, en_path)
    assert result.returncode == 1, (
        f"expected exit code 1 (German missing), got {result.returncode}; "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert target_key in result.stderr, (
        f"expected coverage script to mention {target_key!r} in stderr, got {result.stderr!r}"
    )
