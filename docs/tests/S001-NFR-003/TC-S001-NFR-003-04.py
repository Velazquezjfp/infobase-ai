"""TC-S001-NFR-003-04 — LOG_LEVEL from .env is propagated into the backend container."""
from conftest import _compose, COMPOSE_AVAILABLE
import pytest


def test_log_level_env_propagated(stack_up):
    if not stack_up["backend_healthy"]:
        pytest.skip("Backend not healthy — skipping env-propagation test")

    result = _compose("exec", "backend", "env")
    assert result.returncode == 0, (
        f"docker compose exec backend env failed: {result.stderr}"
    )
    env_lines = result.stdout.splitlines()
    log_level_vars = [line for line in env_lines if line.startswith("LOG_LEVEL=")]
    assert log_level_vars, (
        "LOG_LEVEL not found in backend container environment.\n"
        f"All env vars:\n{result.stdout[:2000]}"
    )
    # Value must be one of the valid Python log levels
    value = log_level_vars[0].split("=", 1)[1].strip()
    assert value in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"), (
        f"LOG_LEVEL has unexpected value: {value!r}"
    )
