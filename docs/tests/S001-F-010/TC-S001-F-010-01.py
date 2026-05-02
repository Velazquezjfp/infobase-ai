"""
S001-F-010 TC-01 — i18n config source-code shape.

Asserts the new parseMissingKeyHandler signature is in place and the old buggy
form is gone. This is the load-bearing fix for the operator-reported leaks
(`formFields.Passnummer`, `documents.renders.*`).
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = REPO_ROOT / "src" / "i18n" / "config.ts"


def test_new_handler_shape_is_present():
    text = CONFIG_PATH.read_text(encoding="utf-8")
    pattern = re.compile(
        r"parseMissingKeyHandler:\s*\(key:\s*string,\s*defaultValue\?:\s*string\)\s*=>\s*defaultValue\s*\?\?\s*key",
    )
    assert pattern.search(text), (
        "Expected the new parseMissingKeyHandler shape "
        "`(key: string, defaultValue?: string) => defaultValue ?? key` in "
        f"{CONFIG_PATH}, but did not find it."
    )


def test_old_buggy_handler_shape_is_gone():
    text = CONFIG_PATH.read_text(encoding="utf-8")
    # The old form returned only the key — that's the bug.
    old_pattern = re.compile(r"parseMissingKeyHandler:\s*\(key:\s*string\)\s*=>\s*key")
    assert not old_pattern.search(text), (
        "Old buggy parseMissingKeyHandler shape `(key: string) => key` is still "
        f"present in {CONFIG_PATH}; the leak fix has not landed."
    )
