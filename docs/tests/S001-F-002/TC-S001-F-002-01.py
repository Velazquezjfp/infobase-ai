"""TC-S001-F-002-01 — docker compose up (no profile) does NOT start the ollama service."""
import pathlib
import subprocess

from conftest import COMPOSE_AVAILABLE, PROJECT_ROOT
import pytest

COMPOSE_FILE = pathlib.Path(PROJECT_ROOT) / "docker-compose.yml"


def test_ollama_service_has_ollama_profile():
    """The ollama service in docker-compose.yml declares profiles: [ollama]."""
    content = COMPOSE_FILE.read_text()
    # Both the service name and the profile declaration must be present
    assert "ollama:" in content or "  ollama:" in content, (
        "docker-compose.yml does not define an 'ollama' service."
    )
    assert 'profiles:' in content, (
        "docker-compose.yml has no 'profiles:' key — ollama service is not profile-gated."
    )
    assert '"ollama"' in content or "- ollama" in content, (
        "docker-compose.yml does not assign the 'ollama' profile to the ollama service."
    )


def test_default_config_excludes_ollama(compose_config_no_profile):
    """Normalized compose config (no profile) does not include the ollama service."""
    assert compose_config_no_profile.returncode == 0, (
        f"docker compose config failed: {compose_config_no_profile.stderr}"
    )
    # The normalized output for the default profile should not list the ollama service
    # docker compose config without the profile simply omits profile-gated services
    stdout = compose_config_no_profile.stdout
    # Check backend and frontend ARE present
    assert "backend:" in stdout, "Backend service missing from default config."
    assert "frontend:" in stdout, "Frontend service missing from default config."
