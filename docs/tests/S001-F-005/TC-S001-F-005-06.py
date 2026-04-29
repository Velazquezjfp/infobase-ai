"""TC-S001-F-005-06 — health endpoint reports document_search status.

GET /api/search/health returns {"document_search": "disabled"} when
ENABLE_DOCUMENT_SEARCH=false.
"""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_health_reports_document_search_disabled(fresh_idirs_modules):
    fresh_idirs_modules({"ENABLE_DOCUMENT_SEARCH": "false"})

    from fastapi import FastAPI
    from backend.api.search import router as search_router

    app = FastAPI()
    app.include_router(search_router, prefix="/api/search")

    import httpx
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/api/search/health")

    assert response.status_code == 200
    body = response.json()
    assert body["document_search"] == "disabled"


@pytest.mark.asyncio
async def test_health_reports_document_search_enabled(fresh_idirs_modules):
    fresh_idirs_modules({"ENABLE_DOCUMENT_SEARCH": "true"})

    from fastapi import FastAPI
    from backend.api.search import router as search_router

    app = FastAPI()
    app.include_router(search_router, prefix="/api/search")

    import httpx
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/api/search/health")

    assert response.status_code == 200
    body = response.json()
    assert body["document_search"] == "enabled"
