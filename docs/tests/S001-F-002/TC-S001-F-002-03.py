"""TC-S001-F-002-03 — ollama service entrypoint includes model pull command."""
import pathlib

import pytest

PROJECT_ROOT = pathlib.Path(__file__).parents[3]
COMPOSE_FILE = PROJECT_ROOT / "docker-compose.yml"


def test_ollama_entrypoint_pulls_model():
    """The ollama service defines an entrypoint/command that runs ollama pull."""
    content = COMPOSE_FILE.read_text()
    assert "ollama pull" in content, (
        "docker-compose.yml ollama service does not contain 'ollama pull' — "
        "model will not be pulled on container start."
    )


def test_ollama_entrypoint_uses_model_env_var_with_default():
    """The ollama pull command references LITELLM_OLLAMA_MODEL with gemma3:12b default."""
    content = COMPOSE_FILE.read_text()
    assert "LITELLM_OLLAMA_MODEL:-gemma3:12b" in content or "LITELLM_OLLAMA_MODEL" in content, (
        "docker-compose.yml ollama entrypoint does not reference LITELLM_OLLAMA_MODEL."
    )
    assert "gemma3:12b" in content, (
        "docker-compose.yml ollama entrypoint does not fall back to 'gemma3:12b'."
    )


def test_ollama_entrypoint_starts_server():
    """The ollama service entrypoint starts the ollama server."""
    content = COMPOSE_FILE.read_text()
    assert "ollama serve" in content, (
        "docker-compose.yml ollama service does not start 'ollama serve' in its entrypoint."
    )
