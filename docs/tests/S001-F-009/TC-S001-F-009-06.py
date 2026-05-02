"""TC-S001-F-009-06 — frontend health-badge contract preserved.

The requirement preserves the legacy ``gemini_initialized`` boolean on every
LLM-backed health endpoint so that any current or future frontend health
badge can keep parsing it unchanged. This test pins the backend-side shape
on each of the three affected endpoints: regardless of whether a consumer
exists *today*, the response field must be a bare boolean — the new
``llm_backend`` string must not displace it.
"""

from __future__ import annotations

import pytest


@pytest.fixture
def configured_env(monkeypatch):
    monkeypatch.setenv("LLM_BACKEND", "external")
    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-key")


@pytest.mark.asyncio
async def test_chat_health_keeps_gemini_initialized_boolean(configured_env):
    from fastapi import FastAPI

    from backend.api.chat import router as chat_router
    from conftest import make_async_client

    app = FastAPI()
    app.include_router(chat_router)

    async with make_async_client(app) as client:
        body = (await client.get("/api/chat/health")).json()

    assert "gemini_initialized" in body, body
    assert isinstance(body["gemini_initialized"], bool), body
    assert "llm_backend" in body and body["llm_backend"] != body["gemini_initialized"], (
        "llm_backend must be additive — not a rename of gemini_initialized"
    )


@pytest.mark.asyncio
async def test_search_health_keeps_gemini_initialized_boolean(configured_env):
    from fastapi import FastAPI

    from backend.api.search import router as search_router
    from conftest import make_async_client

    app = FastAPI()
    app.include_router(search_router, prefix="/api/search")

    async with make_async_client(app) as client:
        body = (await client.get("/api/search/health")).json()

    assert isinstance(body.get("gemini_initialized"), bool), body


@pytest.mark.asyncio
async def test_validation_health_keeps_gemini_initialized_boolean(configured_env):
    from fastapi import FastAPI

    from backend.api.validation import router as validation_router
    from conftest import make_async_client

    app = FastAPI()
    app.include_router(validation_router, prefix="/api/validation")

    async with make_async_client(app) as client:
        body = (await client.get("/api/validation/health")).json()

    assert isinstance(body.get("gemini_initialized"), bool), body
