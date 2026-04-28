"""Shared fixtures for S001-NFR-003 Docker Compose orchestration tests."""
import json
import pathlib
import shutil
import subprocess
import time
import urllib.error
import urllib.request

import pytest

PROJECT_ROOT = str(pathlib.Path(__file__).parents[3])
COMPOSE_FILE = str(pathlib.Path(PROJECT_ROOT) / "docker-compose.yml")

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
    """Run a docker compose command from the project root."""
    return subprocess.run(
        ["docker", "compose", *args],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        **kwargs,
    )


@pytest.fixture(scope="session")
def compose_config():
    """Return the validated docker compose config output (session-scoped)."""
    if not COMPOSE_AVAILABLE:
        pytest.skip("docker compose is not available")
    result = _compose("config")
    return result


@pytest.fixture(scope="session")
def stack_up(tmp_path_factory):
    """Bring the stack up once for the session, tear it down after all tests."""
    if not COMPOSE_AVAILABLE:
        pytest.skip("docker compose is not available")

    _compose("down", "--remove-orphans")
    result = _compose("up", "-d", "--build")

    # Wait up to 90 s for both services to become healthy
    deadline = time.time() + 90
    backend_healthy = False
    frontend_healthy = False
    backend_logs = ""
    while time.time() < deadline and not (backend_healthy and frontend_healthy):
        ps = _compose("ps", "--format", "json")
        if ps.returncode == 0 and ps.stdout.strip():
            for line in ps.stdout.strip().splitlines():
                try:
                    svc = json.loads(line)
                    name = svc.get("Service", "")
                    health = svc.get("Health", "")
                    if name == "backend" and health == "healthy":
                        backend_healthy = True
                    if name == "frontend" and health == "healthy":
                        frontend_healthy = True
                except json.JSONDecodeError:
                    pass
        # Bail early if the backend container has already exited or is unhealthy
        # and capture its logs to include in skip/fail messages.
        if not backend_healthy:
            log_result = _compose("logs", "--no-color", "--tail=50", "backend")
            backend_logs = log_result.stdout + log_result.stderr
            # Known configuration error: LLM provider not configured for this env.
            if "LITELLM_PROXY_URL is required" in backend_logs or "ValueError" in backend_logs:
                break
        time.sleep(3)

    yield {
        "up_result": result,
        "backend_healthy": backend_healthy,
        "frontend_healthy": frontend_healthy,
        "backend_logs": backend_logs,
    }

    _compose("down", "--remove-orphans")
