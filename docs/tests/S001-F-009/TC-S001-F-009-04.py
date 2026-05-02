"""TC-S001-F-009-04 — health endpoints surface ``llm_backend`` alongside legacy ``gemini_initialized``.

The closed-environment deployment may run on LiteLLM, so the legacy
``gemini_initialized`` boolean alone is misleading. Each LLM-backed health
endpoint now also returns ``llm_backend`` populated from
``get_provider().__class__.__name__`` (or ``"unconfigured"`` when the
provider isn't built yet).
"""

from __future__ import annotations

import pytest


VALID_BACKEND_LABELS = {"LiteLLMProvider", "GeminiProvider", "unconfigured"}


@pytest.fixture
def configured_env(monkeypatch):
    monkeypatch.setenv("LLM_BACKEND", "external")
    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-key")


@pytest.mark.asyncio
async def test_chat_health_exposes_llm_backend_and_legacy_field(configured_env):
    from fastapi import FastAPI

    from backend.api.chat import router as chat_router
    from conftest import make_async_client

    app = FastAPI()
    app.include_router(chat_router)

    async with make_async_client(app) as client:
        response = await client.get("/api/chat/health")

    assert response.status_code in (200, 503), response.text
    body = response.json()
    assert "gemini_initialized" in body, body
    assert isinstance(body["gemini_initialized"], bool), body
    assert "llm_backend" in body, body
    assert body["llm_backend"] in VALID_BACKEND_LABELS, body["llm_backend"]


@pytest.mark.asyncio
async def test_search_health_exposes_llm_backend_and_legacy_field(configured_env):
    from fastapi import FastAPI

    from backend.api.search import router as search_router
    from conftest import make_async_client

    app = FastAPI()
    app.include_router(search_router, prefix="/api/search")

    async with make_async_client(app) as client:
        response = await client.get("/api/search/health")

    assert response.status_code == 200, response.text
    body = response.json()
    assert "gemini_initialized" in body, body
    assert isinstance(body["gemini_initialized"], bool), body
    assert "llm_backend" in body, body
    assert body["llm_backend"] in VALID_BACKEND_LABELS, body["llm_backend"]


@pytest.mark.asyncio
async def test_validation_health_exposes_llm_backend_and_legacy_field(configured_env):
    from fastapi import FastAPI

    from backend.api.validation import router as validation_router
    from conftest import make_async_client

    app = FastAPI()
    app.include_router(validation_router, prefix="/api/validation")

    async with make_async_client(app) as client:
        response = await client.get("/api/validation/health")

    assert response.status_code == 200, response.text
    body = response.json()
    assert "llm_backend" in body, body
    assert body["llm_backend"] in VALID_BACKEND_LABELS, body["llm_backend"]
    # gemini_initialized is preserved on the healthy/degraded paths but absent
    # on the catastrophic-error path; this fixture configures the happy path.
    assert "gemini_initialized" in body, body
    assert isinstance(body["gemini_initialized"], bool), body
