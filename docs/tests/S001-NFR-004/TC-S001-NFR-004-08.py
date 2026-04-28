"""TC-S001-NFR-004-08 — backend integration via real proxy.

With LLM_BACKEND=internal and a live LiteLLM proxy at localhost:4000,
POST /api/admin/generate-field returns 200 with a valid field object.

This test closes the integration gap from wave 1: it does NOT mock litellm.acompletion —
the call hits the real proxy which routes to Ollama.

Requires: running LiteLLM proxy (docker compose -f litellm/docker-compose.yml up -d)
          and Ollama with gemma3:12b pulled locally.
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.integration

MASTER_KEY = os.environ.get("LITELLM_MASTER_KEY", "sk-bamf-local-dev-key")


@pytest.mark.asyncio
async def test_generate_field_via_real_proxy(fresh_modules):
    """POST /api/admin/generate-field returns 200 through the live proxy."""
    fresh_modules({
        "LLM_BACKEND": "internal",
        "LITELLM_PROXY_URL": "http://localhost:4000",
        "LITELLM_TOKEN": MASTER_KEY,
        "LITELLM_MODEL": "gemma3:12b",
    })

    import httpx
    from fastapi import FastAPI
    from backend.api.admin import router as admin_router

    app = FastAPI()
    app.include_router(admin_router)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
        timeout=120.0,
    ) as client:
        response = await client.post(
            "/api/admin/generate-field",
            json={"prompt": "Add a text field for applicant full name"},
        )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert "field" in payload, f"Missing 'field' key: {payload}"
    field = payload["field"]
    assert field.get("label"), "field.label must be non-empty"
    assert field.get("type") in {"text", "date", "select", "textarea"}, (
        f"Unexpected field type: {field.get('type')}"
    )
