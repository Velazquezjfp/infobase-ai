"""TC-S001-F-006-05 — GET /api/files/health reflects ENABLE_UPLOAD."""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_health_features_upload_false_when_flag_off(fresh_files_modules):
    fresh_files_modules({"ENABLE_UPLOAD": "false"})

    from fastapi import FastAPI
    from backend.api.files import router as files_router

    app = FastAPI()
    app.include_router(files_router)

    import httpx
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/api/files/health")

    body = response.json()
    assert body["features"]["upload"] is False


@pytest.mark.asyncio
async def test_health_features_upload_true_when_flag_on(fresh_files_modules):
    fresh_files_modules({"ENABLE_UPLOAD": "true"})

    from fastapi import FastAPI
    from backend.api.files import router as files_router

    app = FastAPI()
    app.include_router(files_router)

    import httpx
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/api/files/health")

    body = response.json()
    assert body["features"]["upload"] is True
