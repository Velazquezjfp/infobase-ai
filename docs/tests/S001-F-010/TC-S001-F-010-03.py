"""
S001-F-010 TC-03 — build sanity.

Confirms the i18n config edit did not break the SPA build. `npm run build`
must exit 0; the dist/ directory must contain the bundled JS.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
NPM = shutil.which("npm")


@pytest.mark.skipif(NPM is None, reason="npm not on PATH")
def test_npm_run_build_succeeds():
    result = subprocess.run(
        [NPM, "run", "build"],
        cwd=str(REPO_ROOT),
        capture_output=True, text=True, timeout=300, check=False,
    )
    assert result.returncode == 0, (
        f"`npm run build` exited {result.returncode}.\n"
        f"stdout (last 800 chars):\n{result.stdout[-800:]}\n"
        f"stderr (last 800 chars):\n{result.stderr[-800:]}"
    )

    dist = REPO_ROOT / "dist"
    assert dist.is_dir(), "dist/ directory missing after build"
    assets = list((dist / "assets").glob("*.js"))
    assert assets, "no JS bundles in dist/assets/ after build"
