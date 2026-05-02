"""Shared fixtures for S001-F-009 tests.

Per the slash-command convention, test files are named
``TC-{requirement-id}-{NN}.py`` rather than the default ``test_*.py`` pattern.
This file overrides ``python_files`` for the directory so pytest will collect
them when invoked as ``pytest docs/tests/S001-F-009/``.
"""

from __future__ import annotations

import sys
from pathlib import Path


def pytest_configure(config):
    config.addinivalue_line("python_files", "TC-*.py")


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def make_async_client(app):
    """Return an httpx.AsyncClient wired to the given ASGI app."""
    import httpx

    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    )
