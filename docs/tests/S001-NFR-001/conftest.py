"""Shared fixtures for S001-NFR-001 Docker container tests."""
import json
import pathlib
import shutil
import subprocess
import time
import urllib.error
import urllib.request

import pytest

DOCKER_AVAILABLE = shutil.which("docker") is not None
IMAGE_TAG = "bamf-backend:test-nfr001"
PROJECT_ROOT = str(pathlib.Path(__file__).parents[3])


@pytest.fixture(scope="session")
def docker_build():
    """Build the image once per session. Yields the CompletedProcess result."""
    if not DOCKER_AVAILABLE:
        pytest.skip("Docker is not installed")
    result = subprocess.run(
        [
            "docker", "build", "-t", IMAGE_TAG,
            "--build-arg", "DOCKER_REGISTRY=docker.io",
            "--build-arg", "PIP_INDEX_URL=https://pypi.org/simple",
            "-f", "backend/Dockerfile", ".",
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    yield result
    subprocess.run(["docker", "rmi", "-f", IMAGE_TAG], capture_output=True, cwd=PROJECT_ROOT)


@pytest.fixture(scope="session")
def built_image(docker_build):
    """Skip if the session build failed; return the image tag."""
    if docker_build.returncode != 0:
        pytest.skip(f"Image build failed:\n{docker_build.stderr[-500:]}")
    return IMAGE_TAG


@pytest.fixture
def running_container(built_image):
    """Start a throwaway container on port 8001; yield the base URL; stop on teardown."""
    container_name = "bamf-test-nfr001-health"
    port = 8001
    subprocess.run(
        [
            "docker", "run", "-d",
            "--name", container_name,
            "-p", f"{port}:8000",
            "-e", "GEMINI_API_KEY=dummy",
            "-e", "LLM_BACKEND=external",
            built_image,
        ],
        capture_output=True,
        check=True,
        cwd=PROJECT_ROOT,
    )
    base_url = f"http://localhost:{port}"
    deadline = time.time() + 30
    ready = False
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{base_url}/health", timeout=2):
                ready = True
                break
        except (urllib.error.URLError, OSError):
            time.sleep(1)
    if not ready:
        subprocess.run(["docker", "stop", container_name], capture_output=True)
        subprocess.run(["docker", "rm", container_name], capture_output=True)
        pytest.fail("Container did not become ready within 30 s")
    yield base_url
    subprocess.run(["docker", "stop", container_name], capture_output=True)
    subprocess.run(["docker", "rm", container_name], capture_output=True)
