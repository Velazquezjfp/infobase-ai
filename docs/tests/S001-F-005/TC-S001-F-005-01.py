"""TC-S001-F-005-01 — search disabled path.

POST /api/idirs/search with ENABLE_DOCUMENT_SEARCH=false returns 503
with {"error": "feature_disabled", "detail": "Die Dokumentsuche ..."}.
"""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_search_disabled_returns_503(fresh_idirs_modules, make_http_client=None):
    fresh_idirs_modules({"ENABLE_DOCUMENT_SEARCH": "false"})

    from fastapi import FastAPI
    from backend.api.idirs import router as idirs_router

    app = FastAPI()
    app.include_router(idirs_router)

    import httpx
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/api/idirs/search",
            json={"query": "passport"},
        )

    assert response.status_code == 503
    body = response.json()
    assert body["error"] == "feature_disabled"
    assert "Dokumentsuche" in body["detail"]
