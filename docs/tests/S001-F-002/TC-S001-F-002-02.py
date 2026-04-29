"""TC-S001-F-002-02 — docker compose --profile ollama config includes the ollama service."""
from conftest import COMPOSE_AVAILABLE
import pytest


def test_profile_config_includes_ollama(compose_config):
    """Normalized compose config with --profiles ollama includes the ollama service."""
    assert compose_config.returncode == 0, (
        f"docker compose config --profiles ollama failed: {compose_config.stderr}"
    )
    stdout = compose_config.stdout
    assert "ollama:" in stdout or "  ollama:" in stdout, (
        "Normalized config with ollama profile does not include the 'ollama' service."
    )


def test_profile_config_includes_backend_and_frontend(compose_config):
    """With the ollama profile, backend and frontend are still present."""
    stdout = compose_config.stdout
    assert "backend:" in stdout, "backend service missing from ollama-profile config."
    assert "frontend:" in stdout, "frontend service missing from ollama-profile config."
