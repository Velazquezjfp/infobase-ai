"""Shared fixtures for S001-NFR-002 Docker tests.

Registers TC-*.py as test files so pytest collects them from this directory.
Provides session-scoped fixtures that build the image once and manage a single
container instance shared across TC-02, TC-03, TC-04, TC-05, TC-07, TC-08.
TC-01 and TC-06 drive their own build calls.
"""

from __future__ import annotations

import subprocess
import time
import urllib.request
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
IMAGE_TAG = "bamf-frontend:dev"
CONTAINER_NAME = "bamf-frontend-test"
HOST_PORT = 3000


def pytest_configure(config):
    config.addinivalue_line("python_files", "TC-*.py")


def _docker(*args, **kwargs):
    """Run a docker command via subprocess and return the CompletedProcess."""
    return subprocess.run(["docker", *args], capture_output=True, text=True, **kwargs)


@pytest.fixture(scope="session")
def built_image():
    """Build bamf-frontend:dev once for the session; clean up image on teardown."""
    result = _docker(
        "build",
        "-t", IMAGE_TAG,
        "--build-arg", "DOCKER_REGISTRY=docker.io",
        "--build-arg", "NPM_REGISTRY=https://registry.npmjs.org",
        "--build-arg", "VITE_API_BASE_URL=http://localhost:8000",
        "-f", "frontend/Dockerfile",
        ".",
        cwd=REPO_ROOT,
        timeout=600,
    )
    assert result.returncode == 0, (
        f"docker build failed (exit {result.returncode}):\n{result.stderr[-3000:]}"
    )
    yield IMAGE_TAG
    _docker("rmi", "-f", IMAGE_TAG)


@pytest.fixture(scope="session")
def running_container(built_image):
    """Start the container and wait up to 30 s for serve to respond; clean up after."""
    _docker("rm", "-f", CONTAINER_NAME)

    result = _docker(
        "run", "-d",
        "--name", CONTAINER_NAME,
        "-p", f"{HOST_PORT}:3000",
        built_image,
    )
    assert result.returncode == 0, f"docker run failed:\n{result.stderr}"

    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(
                f"http://localhost:{HOST_PORT}/", timeout=2
            ) as resp:
                if resp.status == 200:
                    break
        except Exception:
            time.sleep(1)
    else:
        pytest.fail("Container did not become healthy within 30 s")

    yield CONTAINER_NAME, HOST_PORT

    _docker("rm", "-f", CONTAINER_NAME)
