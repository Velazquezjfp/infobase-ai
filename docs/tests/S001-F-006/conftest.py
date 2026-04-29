"""Shared fixtures for S001-F-006 tests."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def pytest_configure(config):
    config.addinivalue_line("python_files", "TC-*.py")


_MODULES = [
    "backend.config",
    "backend.api.files",
]


@pytest.fixture
def fresh_files_modules(monkeypatch):
    """Drop cached modules so ENABLE_UPLOAD changes take effect on reimport.

    Returns a factory that, given an env dict, applies it via monkeypatch and
    reimports backend.config + backend.api.files. The handler reads the flag
    via ``backend.config.ENABLE_UPLOAD`` at request time, so the latest module
    state is what the test exercises.
    """

    def _factory(env: dict):
        for key in ("ENABLE_UPLOAD",):
            monkeypatch.delenv(key, raising=False)

        for key, value in env.items():
            monkeypatch.setenv(key, value)

        for mod in _MODULES:
            sys.modules.pop(mod, None)

        config = importlib.import_module("backend.config")
        importlib.import_module("backend.api.files")
        return config

    return _factory


def make_http_client(app):
    import httpx
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    )
