"""Shared fixtures for S001-F-005 tests."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def pytest_configure(config):
    config.addinivalue_line("python_files", "TC-*.py")


_IDIRS_MODULES = [
    "backend.config",
    "backend.api.idirs",
    "backend.api.search",
    "backend.services.gemini_service",
    "backend.services.llm_provider",
]


@pytest.fixture
def fresh_idirs_modules(monkeypatch):
    """Drop cached modules so env changes take effect on reimport."""

    def _factory(env: dict):
        for key in ("ENABLE_DOCUMENT_SEARCH", "LLM_BACKEND", "GEMINI_API_KEY"):
            monkeypatch.delenv(key, raising=False)

        merged = {
            "LLM_BACKEND": "external",
            "GEMINI_API_KEY": "test-key-for-unit-tests",
            **env,
        }
        for key, value in merged.items():
            monkeypatch.setenv(key, value)

        for mod in _IDIRS_MODULES:
            sys.modules.pop(mod, None)

        try:
            llm_provider = importlib.import_module("backend.services.llm_provider")
            llm_provider.reset_provider_for_tests()
        except Exception:
            pass

        try:
            from backend.services.gemini_service import GeminiService
            GeminiService._instance = None
            GeminiService._provider = None
        except Exception:
            pass

        for mod in _IDIRS_MODULES:
            sys.modules.pop(mod, None)

        config = importlib.import_module("backend.config")
        return config

    return _factory


def make_http_client(app):
    import httpx
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    )
