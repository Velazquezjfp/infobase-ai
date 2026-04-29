"""TC-S001-F-005-05 — enabled passthrough.

With ENABLE_DOCUMENT_SEARCH=true and a mocked IDIRS responding 200,
POST /api/idirs/search returns the upstream payload verbatim.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import httpx


@pytest.mark.asyncio
async def test_search_enabled_passthrough(fresh_idirs_modules):
    fresh_idirs_modules({"ENABLE_DOCUMENT_SEARCH": "true"})

    from fastapi import FastAPI
    from backend.api.idirs import router as idirs_router

    app = FastAPI()
    app.include_router(idirs_router)

    upstream_payload = {"results": [{"doc_name": "passport.pdf", "score": 0.95}]}

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json = MagicMock(return_value=upstream_payload)

    mock_async_client_instance = AsyncMock()
    mock_async_client_instance.__aenter__ = AsyncMock(return_value=mock_async_client_instance)
    mock_async_client_instance.__aexit__ = AsyncMock(return_value=False)
    mock_async_client_instance.post = AsyncMock(return_value=mock_response)

    # Create and enter the ASGI client before the patch so its constructor
    # uses the real httpx.AsyncClient.
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        with patch("backend.api.idirs.httpx.AsyncClient", return_value=mock_async_client_instance):
            response = await test_client.post(
                "/api/idirs/search",
                json={"query": "passport"},
            )

    assert response.status_code == 200
    assert response.json() == upstream_payload
