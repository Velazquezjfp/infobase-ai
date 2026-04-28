"""TC-S001-F-001-07 — no LiteLLM proxy call on the external path.

With LLM_BACKEND=external and LITELLM_PROXY_URL pointing at an unreachable host
(127.0.0.1:1), the application starts and POST /api/admin/generate-field
succeeds against the (mocked) Gemini SDK — proving that the LITELLM_PROXY_URL
was never contacted. We assert that the litellm SDK's acompletion is never
called.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_external_backend_never_calls_litellm(fresh_modules):
    fresh_modules({
        "LLM_BACKEND": "external",
        "LITELLM_PROXY_URL": "http://127.0.0.1:1",  # unreachable, must never be hit
        "GEMINI_API_KEY": "fake-gemini-key",
    })

    # Mock google.generativeai to succeed without network.
    fake_completion = MagicMock()
    # Real Gemini responses come fenced; matching that avoids the
    # gemini_service.format_response path that converts bare JSON to a
    # markdown table (which then breaks downstream JSON parsing).
    fake_completion.text = (
        "```json\n"
        '{"label":"Phone Number","type":"text","required":true}'
        "\n```"
    )
    fake_model = MagicMock()
    fake_model.generate_content = MagicMock(return_value=fake_completion)
    fake_genai = MagicMock()
    fake_genai.configure = MagicMock()
    fake_genai.GenerativeModel = MagicMock(return_value=fake_model)
    fake_types = MagicMock()
    fake_types.GenerationConfig = MagicMock(return_value=MagicMock())

    sentinel_litellm = AsyncMock(side_effect=AssertionError(
        "LiteLLM must not be invoked on the external path"
    ))

    with patch.dict(
        "sys.modules",
        {
            "google.generativeai": fake_genai,
            "google.generativeai.types": fake_types,
        },
    ), patch("litellm.acompletion", new=sentinel_litellm):
        from fastapi import FastAPI

        from backend.api.admin import router as admin_router
        from conftest import make_admin_client

        app = FastAPI()
        app.include_router(admin_router)

        async with make_admin_client(app) as client:
            response = await client.post(
                "/api/admin/generate-field",
                json={"prompt": "Add a required phone number field"},
            )

    assert response.status_code == 200, response.text
    assert response.json().get("field"), response.json()
    sentinel_litellm.assert_not_awaited()
    sentinel_litellm.assert_not_called()
