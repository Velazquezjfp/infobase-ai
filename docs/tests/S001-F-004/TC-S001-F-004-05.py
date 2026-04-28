"""TC-S001-F-004-05 — health endpoint exposes anonymization flag.

GET /api/chat/health must include an "anonymization" field whose value is
"disabled" when ENABLE_ANONYMIZATION=false and "enabled" when true.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI


@pytest.mark.asyncio
async def test_health_shows_anonymization_disabled(fresh_chat_modules):
    fresh_chat_modules({"ENABLE_ANONYMIZATION": "false"})

    from backend.api.chat import router
    app = FastAPI()
    app.include_router(router)

    from conftest import make_chat_client
    async with make_chat_client(app) as client:
        response = await client.get("/api/chat/health")

    data = response.json()
    assert "anonymization" in data
    assert data["anonymization"] == "disabled"


@pytest.mark.asyncio
async def test_health_shows_anonymization_enabled(fresh_chat_modules):
    fresh_chat_modules({"ENABLE_ANONYMIZATION": "true"})

    from backend.api.chat import router
    app = FastAPI()
    app.include_router(router)

    from conftest import make_chat_client
    async with make_chat_client(app) as client:
        response = await client.get("/api/chat/health")

    data = response.json()
    assert "anonymization" in data
    assert data["anonymization"] == "enabled"
