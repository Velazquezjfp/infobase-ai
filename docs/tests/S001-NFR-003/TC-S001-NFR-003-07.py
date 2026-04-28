"""TC-S001-NFR-003-07 — ollama service is not started without --profile ollama."""
import json
from conftest import _compose, COMPOSE_AVAILABLE
import pytest


def test_ollama_not_started_without_profile(stack_up):
    """docker compose ps should not list an ollama service when profile is not set."""
    ps = _compose("ps", "--format", "json")
    assert ps.returncode == 0, f"docker compose ps failed: {ps.stderr}"

    services = []
    for line in ps.stdout.strip().splitlines():
        try:
            svc = json.loads(line)
            services.append(svc.get("Service", ""))
        except json.JSONDecodeError:
            pass

    assert "ollama" not in services, (
        "ollama service is running but should be inactive without --profile ollama. "
        f"Running services: {services}"
    )
