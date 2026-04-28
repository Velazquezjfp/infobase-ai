"""TC-S001-F-001-02 — happy path, external/Gemini.

With LLM_BACKEND=external and a (mock) GEMINI_API_KEY, POST /api/admin/generate-field
returns 200 with a non-empty `field` object. The google.generativeai client is
patched so no real Google call is made.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_generate_field_external_backend(fresh_modules):
    fresh_modules({
        "LLM_BACKEND": "external",
        "GEMINI_API_KEY": "fake-gemini-key",
    })

    fake_completion = MagicMock()
    # Wrap in ```json``` like real Gemini responses so gemini_service.format_response
    # doesn't treat the bare JSON as tabular data and convert it to a markdown table.
    fake_completion.text = (
        "```json\n"
        '{"label":"Marital Status","type":"select","required":false,'
        '"options":["single","married","divorced"]}'
        "\n```"
    )
    fake_model = MagicMock()
    fake_model.generate_content = MagicMock(return_value=fake_completion)
    fake_genai = MagicMock()
    fake_genai.configure = MagicMock()
    fake_genai.GenerativeModel = MagicMock(return_value=fake_model)

    fake_types = MagicMock()
    fake_types.GenerationConfig = MagicMock(return_value=MagicMock())

    with patch.dict(
        "sys.modules",
        {
            "google.generativeai": fake_genai,
            "google.generativeai.types": fake_types,
        },
    ):
        from fastapi import FastAPI

        from backend.api.admin import router as admin_router
        from conftest import make_admin_client

        app = FastAPI()
        app.include_router(admin_router)

        async with make_admin_client(app) as client:
            # Use a prompt the rule-based extractor cannot fully resolve
            # (no action verb, no clear label pattern) so the request falls
            # through to the AI path — which is the path under test.
            response = await client.post(
                "/api/admin/generate-field",
                json={"prompt": "Inquiry about marital status semantic interpretation"},
            )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload.get("field"), payload
    fake_genai.configure.assert_called_with(api_key="fake-gemini-key")
