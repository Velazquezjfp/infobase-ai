"""TC-S001-NFR-004-06 — auth enforced by proxy.

A /v1/chat/completions call without an Authorization header must return 401.
Requires a live proxy (integration test).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

import pytest

pytestmark = pytest.mark.integration


def test_auth_required():
    """Unauthenticated request returns 401."""
    body = json.dumps({
        "model": "gemma3:12b",
        "messages": [{"role": "user", "content": "hello"}],
    }).encode()
    req = urllib.request.Request(
        "http://localhost:4000/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=10)
        pytest.fail("Expected 401, but request succeeded")
    except urllib.error.HTTPError as exc:
        assert exc.code == 401, f"Expected 401, got {exc.code}"
