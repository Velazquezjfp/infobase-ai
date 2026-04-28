"""TC-S001-NFR-004-02 — image builds.

`docker compose -f litellm/docker-compose.yml build` exits 0 and produces
an image tagged for the litellm service. Marked as an integration test
(requires Docker daemon).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
COMPOSE_FILE = REPO_ROOT / "litellm" / "docker-compose.yml"

pytestmark = pytest.mark.integration


def test_docker_compose_build():
    """docker compose build exits 0."""
    assert COMPOSE_FILE.exists(), f"docker-compose.yml missing at {COMPOSE_FILE}"
    result = subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE_FILE), "build"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, (
        f"docker compose build failed (rc={result.returncode}):\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
