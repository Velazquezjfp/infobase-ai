"""TC-S001-NFR-001-02 — running container responds 200 {"status": "healthy"} on /health.

LLM_BACKEND=external is passed so the server boots without a LiteLLM proxy (smoke-test mode).
The /health endpoint has no LLM dependency.
"""
import json
import urllib.request


def test_health_endpoint_returns_200(running_container):
    with urllib.request.urlopen(f"{running_container}/health", timeout=5) as resp:
        assert resp.status == 200
        body = json.loads(resp.read())
    assert body == {"status": "healthy"}
