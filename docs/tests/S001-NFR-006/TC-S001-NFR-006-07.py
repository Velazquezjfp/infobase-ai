"""
S001-NFR-006 TC-07 — meta regression test.

Sanity-check that NFR-005's e2e test still passes after this requirement's
edits. This guards against an accidental regression in the chat / form-fill
chain caused by the path-resolution helper.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

REPO_ROOT = Path(__file__).resolve().parents[3]
VENV_PY = REPO_ROOT / "backend" / "venv" / "bin" / "python3"
VERIFY_E2E = REPO_ROOT / "temp" / "verify-e2e.py"


def test_nfr005_e2e_still_green():
    if not VENV_PY.exists():
        pytest.skip("backend/venv not available; skipping e2e regression check")
    if not VERIFY_E2E.exists():
        pytest.skip("temp/verify-e2e.py not present; skipping")

    result = subprocess.run(
        [str(VENV_PY), str(VERIFY_E2E)],
        capture_output=True, text=True, timeout=180,
        cwd=str(REPO_ROOT),
    )
    if result.returncode != 0:
        pytest.fail(
            f"NFR-005 verify-e2e.py regressed (rc={result.returncode}).\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    assert "OK: e2e chat path traversed" in result.stdout, (
        f"e2e completed but success marker not found in stdout:\n{result.stdout}"
    )
