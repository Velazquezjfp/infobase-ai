"""Shared fixtures for S001-F-002 Ollama Compose profile tests."""
import pathlib
import shutil
import subprocess

import pytest

PROJECT_ROOT = str(pathlib.Path(__file__).parents[3])
COMPOSE_FILE = pathlib.Path(PROJECT_ROOT) / "docker-compose.yml"

DOCKER_AVAILABLE = shutil.which("docker") is not None
COMPOSE_AVAILABLE = DOCKER_AVAILABLE and (
    subprocess.run(
        ["docker", "compose", "version"],
        capture_output=True,
    ).returncode == 0
    if DOCKER_AVAILABLE
    else False
)


def _compose(*args, **kwargs):
    return subprocess.run(
        ["docker", "compose", *args],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        **kwargs,
    )


@pytest.fixture(scope="session")
def compose_config():
    if not COMPOSE_AVAILABLE:
        pytest.skip("docker compose is not available")
    return subprocess.run(
        ["docker", "compose", "--profile", "ollama", "config"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )


@pytest.fixture(scope="session")
def compose_config_no_profile():
    if not COMPOSE_AVAILABLE:
        pytest.skip("docker compose is not available")
    return _compose("config")
