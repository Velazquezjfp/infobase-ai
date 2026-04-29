"""TC-S001-F-005-03 — no outbound TCP connection when disabled.

When ENABLE_DOCUMENT_SEARCH=false, the handler short-circuits before
opening any httpx connection to IDIRS_BASE_URL.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_search_disabled_no_outbound_connection(fresh_idirs_modules):
    fresh_idirs_modules({"ENABLE_DOCUMENT_SEARCH": "false"})

    from fastapi import FastAPI
    import backend.api.idirs as idirs_module
    from backend.api.idirs import router as idirs_router

    app = FastAPI()
    app.include_router(idirs_router)

    import httpx

    with patch.object(idirs_module, "httpx") as mock_httpx:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
        ) as client:
            response = await client.post(
                "/api/idirs/search",
                json={"query": "passport"},
            )

    # The early return fires before any httpx call in the idirs module
    mock_httpx.AsyncClient.assert_not_called()
    assert response.status_code == 503
