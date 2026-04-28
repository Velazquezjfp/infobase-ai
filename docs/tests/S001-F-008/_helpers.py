"""Shared helpers for S001-F-008 i18n localization tests."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOCALES_DIR = PROJECT_ROOT / "src" / "i18n" / "locales"
DE_PATH = LOCALES_DIR / "de.json"
EN_PATH = LOCALES_DIR / "en.json"
COVERAGE_SCRIPT = PROJECT_ROOT / "scripts" / "i18n-coverage.js"
I18NEXT_RUNNER = Path(__file__).parent / "_i18next_runner.mjs"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def remove_key(obj: dict, dotted: str) -> bool:
    """Remove a dotted key path from a nested dict; return True if removed."""
    parts = dotted.split(".")
    cur = obj
    for p in parts[:-1]:
        if not isinstance(cur, dict) or p not in cur:
            return False
        cur = cur[p]
    if isinstance(cur, dict) and parts[-1] in cur:
        del cur[parts[-1]]
        return True
    return False


def run_node(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["node", *args],
        cwd=str(cwd or PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


def run_coverage(de_path: Path, en_path: Path) -> subprocess.CompletedProcess:
    return run_node([str(COVERAGE_SCRIPT), str(de_path), str(en_path)])


def run_i18next(language: str, key: str, de_data: dict, en_data: dict, tmp_path: Path) -> subprocess.CompletedProcess:
    """Run a Node helper that loads given DE/EN resources into i18next and prints t(key)."""
    de_file = tmp_path / "de.json"
    en_file = tmp_path / "en.json"
    write_json(de_file, de_data)
    write_json(en_file, en_data)
    return run_node([str(I18NEXT_RUNNER), language, key, str(de_file), str(en_file)])
