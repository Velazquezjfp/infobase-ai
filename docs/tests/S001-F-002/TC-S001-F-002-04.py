"""TC-S001-F-002-04 — ollama-data named volume declared and mounted correctly."""
import pathlib

import pytest

PROJECT_ROOT = pathlib.Path(__file__).parents[3]
COMPOSE_FILE = PROJECT_ROOT / "docker-compose.yml"


def test_ollama_data_volume_declared_at_top_level():
    """docker-compose.yml declares ollama-data as a top-level named volume."""
    content = COMPOSE_FILE.read_text()
    # Top-level volumes section must include ollama-data
    assert "ollama-data:" in content, (
        "docker-compose.yml does not declare 'ollama-data' as a named volume."
    )


def test_ollama_data_volume_mounted_in_container():
    """ollama-data volume is mounted at /root/.ollama inside the ollama container."""
    content = COMPOSE_FILE.read_text()
    assert "/root/.ollama" in content, (
        "docker-compose.yml does not mount ollama-data at /root/.ollama."
    )
    assert "ollama-data:/root/.ollama" in content, (
        "ollama-data volume is not correctly mapped to /root/.ollama in the ollama service."
    )
