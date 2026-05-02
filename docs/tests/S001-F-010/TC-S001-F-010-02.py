"""
S001-F-010 TC-02 — handler logic verification via Node.

Spawns a Node subprocess that evaluates the same arrow function as a pure
function (independent of i18next) and asserts the four behavioural cases:
  - both args provided → defaultValue
  - only key (no second arg) → key
  - explicit undefined defaultValue → key
  - empty string defaultValue → '' (caller's choice; consistent with `??`)

Skips gracefully if Node isn't available.
"""

from __future__ import annotations

import json
import shutil
import subprocess

import pytest


NODE = shutil.which("node")


HANDLER_LITERAL = "(key, defaultValue) => defaultValue ?? key"


@pytest.mark.skipif(NODE is None, reason="node not on PATH")
def test_handler_logic_matrix():
    script = f"""
        const handler = {HANDLER_LITERAL};
        const cases = [
            ["both",    handler("foo.bar", "Friendly")],
            ["onlyKey", handler("foo.bar")],
            ["undef",   handler("foo.bar", undefined)],
            ["empty",   handler("foo.bar", "")],
        ];
        process.stdout.write(JSON.stringify(Object.fromEntries(cases)));
    """
    result = subprocess.run(
        [NODE, "-e", script],
        capture_output=True, text=True, timeout=15, check=False,
    )
    assert result.returncode == 0, f"node exited {result.returncode}: {result.stderr}"
    actual = json.loads(result.stdout)
    expected = {
        "both": "Friendly",
        "onlyKey": "foo.bar",
        "undef": "foo.bar",
        "empty": "",
    }
    assert actual == expected, f"Handler matrix mismatch.\nExpected: {expected}\nActual:   {actual}"
