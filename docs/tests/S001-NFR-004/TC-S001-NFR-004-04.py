"""TC-S001-NFR-004-04 — model listed by proxy.

GET /v1/models with the correct master key returns gemma3:12b in data[].id.
Requires a live proxy (integration test).
"""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

MASTER_KEY = os.environ.get("LITELLM_MASTER_KEY", "sk-bamf-local-dev-key")


def test_model_listed():
    """gemma3:12b appears in the proxy's model list."""
    req = urllib.request.Request(
        "http://localhost:4000/v1/models",
        headers={"Authorization": f"Bearer {MASTER_KEY}"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        payload = json.loads(resp.read())

    model_ids = [m["id"] for m in payload.get("data", [])]
    assert "gemma3:12b" in model_ids, (
        f"gemma3:12b not found in proxy model list; ids: {model_ids}"
    )
