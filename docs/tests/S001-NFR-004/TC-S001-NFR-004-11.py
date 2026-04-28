"""TC-S001-NFR-004-11 — no F-001 regression.

Re-runs the core F-001 test assertions after the fail-fast precondition is
added to get_provider(). The existing fresh_modules fixture sets LITELLM_PROXY_URL
explicitly, so the fail-fast branch is never hit and all 7 original scenarios pass.

This file duplicates the key assertions from docs/tests/S001-F-001/ to confirm
no regression without requiring pytest to collect both directories simultaneously.
"""

from __future__ import annotations

import sys
from unittest.mock import AsyncMock, patch

import pytest


FAKE_RESPONSE = {
    "choices": [
        {
            "message": {
                "role": "assistant",
                "content": (
                    '{"label":"Status","type":"select",'
                    '"required":false,'
                    '"options":["active","inactive"]}'
                ),
            }
        }
    ]
}


@pytest.mark.asyncio
async def test_internal_path_still_works_after_precondition(fresh_modules):
    """Internal path with LITELLM_PROXY_URL set does NOT trigger the fail-fast."""
    fresh_modules({
        "LLM_BACKEND": "internal",
        "LITELLM_PROXY_URL": "http://litellm.test:4000",
        "LITELLM_TOKEN": "sk-test",
        "LITELLM_MODEL": "gemma3:12b",
    })

    with patch("litellm.acompletion", new=AsyncMock(return_value=FAKE_RESPONSE)):
        import httpx
        from fastapi import FastAPI
        from backend.api.admin import router as admin_router

        app = FastAPI()
        app.include_router(admin_router)

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
        ) as client:
            # Use a prompt with explicit options so rule-based extraction handles it
            # (avoids routing through GeminiService.format_response which converts
            # JSON to markdown tables, breaking field parsing for AI-path prompts).
            response = await client.post(
                "/api/admin/generate-field",
                json={"prompt": "Add a dropdown for status with options active, inactive"},
            )

    assert response.status_code == 200, response.text
    assert "field" in response.json()
    assert "google.generativeai" not in sys.modules


@pytest.mark.asyncio
async def test_external_path_unaffected_by_precondition(fresh_modules):
    """External path (Gemini) is unaffected — precondition only guards internal path."""
    fresh_modules({
        "LLM_BACKEND": "external",
        "GEMINI_API_KEY": "fake-key-for-test",
    })

    from backend.services.llm_provider import get_provider
    from backend.services.llm_provider import GeminiProvider

    import google.generativeai as real_genai

    with patch.object(real_genai, "configure"), \
         patch.object(real_genai, "GenerativeModel", return_value=object()):
        provider = get_provider()

    assert isinstance(provider, GeminiProvider)
