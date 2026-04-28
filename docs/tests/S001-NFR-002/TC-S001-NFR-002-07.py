"""TC-S001-NFR-002-07 — VITE_API_BASE_URL is baked into the dist bundle.

Acceptance criterion: when built with --build-arg VITE_API_BASE_URL=https://backend.acme.test,
`grep -ro 'backend.acme.test' /app/dist` returns at least one match.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
_CUSTOM_URL = "https://backend.acme.test"
_BAKED_TAG = "bamf-frontend:baked-url-test"


def test_vite_api_base_url_baked():
    build = subprocess.run(
        [
            "docker", "build",
            "-t", _BAKED_TAG,
            "--build-arg", "DOCKER_REGISTRY=docker.io",
            "--build-arg", f"VITE_API_BASE_URL={_CUSTOM_URL}",
            "-f", "frontend/Dockerfile",
            ".",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert build.returncode == 0, f"docker build failed:\n{build.stderr[-2000:]}"

    try:
        result = subprocess.run(
            [
                "docker", "run", "--rm", _BAKED_TAG,
                "sh", "-c", "grep -ro 'backend.acme.test' /app/dist | head -1",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"docker run failed:\n{result.stderr}"
        match = result.stdout.strip()
        assert match, (
            f"Expected to find 'backend.acme.test' baked into /app/dist, but grep returned nothing"
        )
    finally:
        subprocess.run(["docker", "rmi", "-f", _BAKED_TAG], capture_output=True)
