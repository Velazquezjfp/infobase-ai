"""Shared fixtures for S001-F-004 tests."""

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


def make_chat_client(app):
    import httpx
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    )


_CHAT_MODULES = [
    "backend.config",
    "backend.api.chat",
    "backend.services.anonymization_service",
    "backend.tools.anonymization_tool",
    "backend.services.gemini_service",
    "backend.services.llm_provider",
    "backend.services.context_manager",
    "backend.services.conversation_manager",
]


@pytest.fixture
def fresh_chat_modules(monkeypatch):
    """Drop cached modules so env changes take effect on reimport.

    Always sets LLM_BACKEND=external + GEMINI_API_KEY=test so the module-level
    GeminiService() in chat.py can initialize without a real LiteLLM proxy.
    """

    def _factory(env: dict):
        # Clear relevant env vars first
        for key in (
            "ENABLE_ANONYMIZATION",
            "ENABLE_CHAT_HISTORY",
            "LLM_BACKEND",
            "LITELLM_PROXY_URL",
            "LITELLM_TOKEN",
            "LITELLM_MODEL",
            "GEMINI_API_KEY",
        ):
            monkeypatch.delenv(key, raising=False)

        # Apply caller-supplied vars, plus stable LLM defaults
        merged = {
            "LLM_BACKEND": "external",
            "GEMINI_API_KEY": "test-key-for-unit-tests",
            **env,
        }
        for key, value in merged.items():
            monkeypatch.setenv(key, value)

        # Drop cached modules so import-time reads re-execute
        for mod in _CHAT_MODULES:
            sys.modules.pop(mod, None)

        # Reset provider singleton
        try:
            llm_provider = importlib.import_module("backend.services.llm_provider")
            llm_provider.reset_provider_for_tests()
        except Exception:
            pass

        # Reset GeminiService singleton
        try:
            from backend.services.gemini_service import GeminiService
            GeminiService._instance = None
            GeminiService._provider = None
        except Exception:
            pass

        # Reset AnonymizationService singleton
        try:
            from backend.services.anonymization_service import AnonymizationService
            AnonymizationService._instance = None
        except Exception:
            pass

        for mod in _CHAT_MODULES:
            sys.modules.pop(mod, None)

        config = importlib.import_module("backend.config")
        return config

    return _factory


@pytest.fixture
def mock_websocket():
    """A minimal WebSocket mock that captures sent JSON."""
    ws = MagicMock()
    ws.sent_messages = []

    async def _send_json(payload):
        ws.sent_messages.append(payload)

    ws.send_json = AsyncMock(side_effect=_send_json)
    return ws
