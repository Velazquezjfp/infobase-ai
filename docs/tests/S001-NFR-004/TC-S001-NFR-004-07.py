"""TC-S001-NFR-004-07 — model swap via env (structural check).

Verifies that:
1. config.yaml uses os.environ/LITELLM_OLLAMA_HOST for api_base (env-driven host)
2. litellm/.env.example documents LITELLM_OLLAMA_MODEL with gemma3:12b default
3. litellm/README.md documents the manual steps required to swap models

The live swap (changing the model and restarting Docker) is an operator
workflow that cannot be automated in a unit test. This test validates the
structural preconditions that make the swap possible.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
LITELLM_DIR = REPO_ROOT / "litellm"


def test_config_uses_env_for_api_base():
    """config.yaml uses os.environ/ substitution for api_base."""
    config_path = LITELLM_DIR / "config.yaml"
    assert config_path.exists(), f"config.yaml missing at {config_path}"

    with config_path.open() as f:
        config = yaml.safe_load(f)

    model_list = config.get("model_list", [])
    assert model_list, "model_list must not be empty"

    entry = model_list[0]
    api_base = entry["litellm_params"]["api_base"]
    assert "LITELLM_OLLAMA_HOST" in api_base, (
        f"api_base should reference LITELLM_OLLAMA_HOST via os.environ/; got: {api_base!r}"
    )


def test_env_example_documents_ollama_model():
    """litellm/.env.example contains LITELLM_OLLAMA_MODEL with gemma3:12b default."""
    env_example = LITELLM_DIR / ".env.example"
    assert env_example.exists(), f".env.example missing at {env_example}"
    content = env_example.read_text()
    assert "LITELLM_OLLAMA_MODEL=gemma3:12b" in content, (
        "Expected LITELLM_OLLAMA_MODEL=gemma3:12b default in litellm/.env.example"
    )


def test_readme_documents_model_swap():
    """litellm/README.md documents the model-swap procedure."""
    readme = LITELLM_DIR / "README.md"
    assert readme.exists(), f"README.md missing at {readme}"
    content = readme.read_text()
    assert "config.yaml" in content, "README must mention config.yaml in swap instructions"
    assert "LITELLM_OLLAMA_MODEL" in content, "README must mention LITELLM_OLLAMA_MODEL"
