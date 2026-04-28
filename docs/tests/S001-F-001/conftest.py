"""Shared fixtures for S001-F-001 tests.

Per the slash-command convention, test files are named
``TC-{requirement-id}-{NN}.py`` rather than the default ``test_*.py`` pattern.
This file overrides ``python_files`` for the directory so pytest will collect
them when invoked as ``pytest docs/tests/S001-F-001/``.

Each test exercises a fresh provider singleton so env-var changes between
tests actually take effect.
"""

from __future__ import annotations


def pytest_configure(config):
    config.addinivalue_line("python_files", "TC-*.py")


def make_admin_client(app):
    """Return an httpx.AsyncClient wired to the given ASGI app.

    The starlette TestClient bundled with the project's pinned fastapi 0.104
    is incompatible with the pinned httpx 0.28 (which dropped the ``app=``
    constructor kwarg). Tests construct an httpx.AsyncClient over an
    ASGITransport directly, which is the modern equivalent.
    """
    import httpx

    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    )

import importlib
import sys
from pathlib import Path

import pytest

# Make `backend.*` importable regardless of where pytest is invoked from.
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture
def fresh_modules(monkeypatch):
    """Drop cached backend modules so import-time env-var reads re-execute.

    Returns a callable that takes the env vars to set, then re-imports the
    relevant modules and returns (config, llm_provider).
    """

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

        # Drop any cached imports so module-level env reads re-execute and
        # singletons (GeminiService._instance, get_field_generator's global,
        # the LLM provider cache) get rebuilt against the fresh env vars.
        for mod in [
            "backend.config",
            "backend.services.llm_provider",
            "backend.services.gemini_service",
            "backend.services.validation_service",
            "backend.services.shacl_generator",
            "backend.services.field_generator",
            # API modules cache the service-level globals at import time —
            # drop them too so they re-bind to the fresh classes.
            "backend.api.admin",
            "backend.api.chat",
            "backend.api.search",
            "backend.api.validation",
        ]:
            sys.modules.pop(mod, None)

        # Force a clean google.generativeai entry too — internal-path tests
        # assert it never gets imported.
        for mod in list(sys.modules):
            if mod == "google.generativeai" or mod.startswith("google.generativeai."):
                sys.modules.pop(mod, None)

        config = importlib.import_module("backend.config")
        llm_provider = importlib.import_module("backend.services.llm_provider")
        # Reset the singleton too in case a prior test built one.
        llm_provider.reset_provider_for_tests()
        return config, llm_provider

    return _factory
