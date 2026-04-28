"""Shared fixtures for S001-NFR-004 tests."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

LITELLM_DIR = REPO_ROOT / "litellm"


def pytest_configure(config):
    config.addinivalue_line("python_files", "TC-*.py")


@pytest.fixture
def fresh_modules(monkeypatch):
    """Drop cached backend modules so import-time env-var reads re-execute."""

    def _factory(env: dict) -> tuple:
        for key in (
            "LLM_BACKEND",
            "LITELLM_PROXY_URL",
            "LITELLM_TOKEN",
            "LITELLM_MODEL",
            "GEMINI_API_KEY",
        ):
            monkeypatch.delenv(key, raising=False)
        for key, value in env.items():
            monkeypatch.setenv(key, value)

        for mod in [
            "backend.config",
            "backend.services.llm_provider",
            "backend.services.gemini_service",
            "backend.services.validation_service",
            "backend.services.shacl_generator",
            "backend.services.field_generator",
            "backend.api.admin",
            "backend.api.chat",
            "backend.api.search",
            "backend.api.validation",
        ]:
            sys.modules.pop(mod, None)

        for mod in list(sys.modules):
            if mod == "google.generativeai" or mod.startswith("google.generativeai."):
                sys.modules.pop(mod, None)

        config_mod = importlib.import_module("backend.config")
        llm_provider = importlib.import_module("backend.services.llm_provider")
        llm_provider.reset_provider_for_tests()
        return config_mod, llm_provider

    return _factory
