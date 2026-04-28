"""TC-S001-NFR-004-05 — chat completion via proxy.

POST /v1/chat/completions with model=gemma3:12b returns 200 and a non-empty
choices[0].message.content. Requires a live proxy and Ollama (integration test).
"""

from __future__ import annotations

import json
import os
import urllib.request

import pytest

pytestmark = pytest.mark.integration

MASTER_KEY = os.environ.get("LITELLM_MASTER_KEY", "sk-bamf-local-dev-key")


def test_chat_completion():
    """Proxy returns a non-empty completion for a simple prompt."""
    body = json.dumps({
        "model": "gemma3:12b",
        "messages": [{"role": "user", "content": "say hello"}],
    }).encode()
    req = urllib.request.Request(
        "http://localhost:4000/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {MASTER_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        payload = json.loads(resp.read())

    content = payload["choices"][0]["message"]["content"]
    assert content and content.strip(), "completion content must be non-empty"
