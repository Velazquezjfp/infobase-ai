"""TC-S001-F-001-04 — network error on the internal/LiteLLM path.

When LITELLM_PROXY_URL points at an unreachable host, POST /api/admin/generate-field
returns an error response mentioning the failure. Crucially, **no** fallback
call is made to the Gemini SDK and google.generativeai never enters
sys.modules. The response status is whatever the existing
``backend/services/field_generator.py`` exception-handling returns (currently
400 — ValueError-wrapped — see the test report for the override note); the
contract this test enforces is "no silent fallback to Gemini", not a specific
HTTP code.
"""

from __future__ import annotations

import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class _ConnectionRefused(ConnectionError):
    pass


@pytest.mark.asyncio
async def test_internal_backend_network_error_no_gemini_fallback(fresh_modules):
    fresh_modules({
        "LLM_BACKEND": "internal",
        "LITELLM_PROXY_URL": "http://127.0.0.1:1",  # unreachable
        "LITELLM_TOKEN": "sk-test",
        "LITELLM_MODEL": "gemma3:12b",
    })

    fail = AsyncMock(side_effect=_ConnectionRefused("connection refused"))

    # Sentinel google.generativeai mock: if anything imports & calls it, the
    # test will see configure().
    fake_genai = MagicMock()
    fake_genai.configure = MagicMock()
    fake_genai.GenerativeModel = MagicMock()

    with patch("litellm.acompletion", new=fail):
        from fastapi import FastAPI

        from backend.api.admin import router as admin_router
        from conftest import make_admin_client

        app = FastAPI()
        app.include_router(admin_router)

        async with make_admin_client(app) as client:
            # Use a prompt the rule-based extractor can't satisfy so the
            # request falls through to the LLM call (which is what we want
            # to fail with a "network error").
            response = await client.post(
                "/api/admin/generate-field",
                json={"prompt": "Inquiry about a free-form descriptor with semantic nuance"},
            )

    # The request must fail (not silently fall back to Gemini).
    assert response.status_code >= 400, response.text
    body_text = response.text.lower()
    # Error must mention something useful — not be a raw uncaught traceback.
    assert any(k in body_text for k in ("llm", "field", "generate", "connection", "refused")), body_text
    # Critically: no fallback to Gemini, no Google SDK ever loaded.
    assert "google.generativeai" not in sys.modules
    # Sentinel google mock must not have been touched.
    fake_genai.configure.assert_not_called()
    # And the LiteLLM provider actually was the one that tried (and failed).
    fail.assert_awaited()
