"""TC-S001-F-002-05 — ollama service does NOT bind port 11434 on the host."""
import pathlib
import re

import pytest

PROJECT_ROOT = pathlib.Path(__file__).parents[3]
COMPOSE_FILE = PROJECT_ROOT / "docker-compose.yml"


def test_ollama_service_has_no_host_port_binding():
    """The ollama service must not bind port 11434 on the host interface."""
    content = COMPOSE_FILE.read_text()

    # Parse only the ollama service block (between 'ollama:' and next top-level key)
    ollama_block_match = re.search(
        r"^\s{2}ollama:(.+?)(?=^\s{2}\w|\Z)",
        content,
        re.MULTILINE | re.DOTALL,
    )
    assert ollama_block_match, "Could not locate 'ollama:' service block in docker-compose.yml."

    ollama_block = ollama_block_match.group(1)

    # A host port binding looks like "11434:11434" or similar inside a ports: section
    host_port_pattern = re.compile(r'"?[\d.]*:?11434:11434"?')
    assert not host_port_pattern.search(ollama_block), (
        "The ollama service binds port 11434 on the host, which would conflict "
        "with a host-installed Ollama instance. Remove the host-side port binding."
    )


def test_env_example_documents_enable_ollama_container():
    """ENABLE_OLLAMA_CONTAINER is documented in .env.example."""
    env_example = PROJECT_ROOT / ".env.example"
    assert env_example.exists(), ".env.example does not exist."
    content = env_example.read_text()
    assert "ENABLE_OLLAMA_CONTAINER" in content, (
        "ENABLE_OLLAMA_CONTAINER is not documented in .env.example."
    )
    assert "false" in content.lower(), (
        ".env.example does not show 'false' as the default for ENABLE_OLLAMA_CONTAINER."
    )


def test_readme_has_local_llm_development_section():
    """README.md contains a 'Local LLM development' section."""
    readme = PROJECT_ROOT / "README.md"
    assert readme.exists(), "README.md does not exist."
    content = readme.read_text()
    assert "Local LLM development" in content, (
        "README.md does not have a 'Local LLM development' section."
    )


def test_readme_explains_both_paths():
    """README.md explains both the host-Ollama path and the Compose-profile path."""
    readme = PROJECT_ROOT / "README.md"
    content = readme.read_text()
    assert "--profile ollama" in content, (
        "README.md does not mention '--profile ollama' for the Compose-managed path."
    )
    assert "host" in content.lower() and "ollama" in content.lower(), (
        "README.md does not mention the host-installed Ollama path."
    )
