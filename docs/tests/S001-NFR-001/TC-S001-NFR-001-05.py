"""TC-S001-NFR-001-05 — DOCKER_REGISTRY ARG is consumed; invalid registry causes build failure."""
import subprocess
import shutil
import pytest

PROJECT_ROOT = str(__import__("pathlib").Path(__file__).parents[3])


def test_invalid_registry_fails_build():
    if not shutil.which("docker"):
        pytest.skip("Docker is not installed")
    result = subprocess.run(
        [
            "docker", "build",
            "--build-arg", "DOCKER_REGISTRY=invalid.registry.example.com",
            "-f", "backend/Dockerfile",
            "--no-cache",
            ".",
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    assert result.returncode != 0, (
        "Expected build to fail with an unreachable registry, but it exited 0"
    )
