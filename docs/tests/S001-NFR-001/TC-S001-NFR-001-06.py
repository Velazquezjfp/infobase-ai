"""TC-S001-NFR-001-06 — PIP_INDEX_URL ARG is consumed; invalid PyPI index causes build failure."""
import subprocess
import shutil
import pytest

PROJECT_ROOT = str(__import__("pathlib").Path(__file__).parents[3])


def test_invalid_pip_index_fails_build():
    if not shutil.which("docker"):
        pytest.skip("Docker is not installed")
    result = subprocess.run(
        [
            "docker", "build",
            "--build-arg", "DOCKER_REGISTRY=docker.io",
            "--build-arg", "PIP_INDEX_URL=https://invalid.example.com/pypi/simple",
            "-f", "backend/Dockerfile",
            "--no-cache",
            ".",
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    assert result.returncode != 0, (
        "Expected build to fail with an unreachable pip index, but it exited 0"
    )
