"""TC-S001-NFR-002-03 — static asset is served with status 200.

Acceptance criterion: GET /assets/<bundle>.js (or .css) returns 200.
"""

from __future__ import annotations

import subprocess
import urllib.request


def test_asset_served(running_container):
    container_name, port = running_container

    result = subprocess.run(
        ["docker", "exec", container_name, "sh", "-c", "ls /app/dist/assets | head -1"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"docker exec failed:\n{result.stderr}"
    asset_name = result.stdout.strip()
    assert asset_name, "No files found in /app/dist/assets — Vite build produced no assets"

    with urllib.request.urlopen(
        f"http://localhost:{port}/assets/{asset_name}", timeout=10
    ) as resp:
        assert resp.status == 200, f"Expected 200 for /assets/{asset_name}, got {resp.status}"
