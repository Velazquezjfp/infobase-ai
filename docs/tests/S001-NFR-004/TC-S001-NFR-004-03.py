"""TC-S001-NFR-004-03 — proxy liveness after startup.

After `docker compose up -d`, the /health/liveliness endpoint returns 200
within 30 seconds. Requires a running Docker daemon and Ollama.

This test is marked as integration and will be skipped unless explicitly
requested (e.g. pytest -m integration).
"""

from __future__ import annotations

import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]

pytestmark = pytest.mark.integration


def test_proxy_health_liveliness():
    """GET /health/liveliness returns 200 within 30 seconds."""
    url = "http://localhost:4000/health/liveliness"
    deadline = time.time() + 30
    last_error: Exception = RuntimeError("no attempt made")

    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=3) as resp:
                assert resp.status == 200, f"Expected 200, got {resp.status}"
                body = resp.read().decode()
                assert "healthy" in body.lower(), f"Unexpected health body: {body!r}"
                return
        except Exception as exc:
            last_error = exc
            time.sleep(2)

    pytest.fail(f"Proxy not healthy after 30 s — last error: {last_error}")
