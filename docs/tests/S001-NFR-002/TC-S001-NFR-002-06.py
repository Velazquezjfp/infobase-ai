"""TC-S001-NFR-002-06 — invalid NPM_REGISTRY causes build failure.

Acceptance criterion: `docker build --build-arg NPM_REGISTRY=https://invalid.example.com/npm
-f frontend/Dockerfile .` fails (non-zero exit code) during npm ci.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
_INVALID_TAG = "bamf-frontend:invalid-registry-test"


def test_invalid_registry_fails_build():
    result = subprocess.run(
        [
            "docker", "build",
            "-t", _INVALID_TAG,
            "--build-arg", "DOCKER_REGISTRY=docker.io",
            "--build-arg", "NPM_REGISTRY=https://invalid.example.com/npm",
            "-f", "frontend/Dockerfile",
            ".",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    # Clean up any partial image that may have been tagged.
    subprocess.run(["docker", "rmi", "-f", _INVALID_TAG], capture_output=True)

    assert result.returncode != 0, (
        "Expected docker build to fail with invalid NPM_REGISTRY, but it exited 0"
    )
