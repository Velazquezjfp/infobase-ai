"""TC-S001-F-003-04 — no extraction, graceful: when regulation has no
extractedText, the prompt contains only the URL as a citation; no HTTP calls
are made and no errors are raised.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

FIXTURE_CASE_CTX_NO_TEXT = {
    "schemaVersion": "2.0",
    "caseId": "ACTE-TEST-002",
    "caseType": "integration_course",
    "name": "Test Case No Text",
    "description": "Test description.",
    "regulations": [
        {
            "id": "test-reg-002",
            "title": "Another Regulation",
            "summary": "No extracted text here.",
            "url": "https://example.de/x",
        }
    ],
    "requiredDocuments": [],
    "validationRules": [],
    "commonIssues": [],
}


@pytest.fixture
def fresh_service(monkeypatch):
    for mod in list(sys.modules):
        if mod.startswith("backend."):
            sys.modules.pop(mod, None)

    monkeypatch.setenv("LLM_BACKEND", "internal")
    monkeypatch.setenv("LITELLM_PROXY_URL", "http://fake:4000")
    monkeypatch.setenv("LITELLM_TOKEN", "sk-test")
    monkeypatch.setenv("LITELLM_MODEL", "test-model")

    from backend.services import llm_provider as lp_mod
    lp_mod.reset_provider_for_tests()

    fake_provider = MagicMock()
    fake_provider.generate = AsyncMock(return_value="ok")

    with patch("backend.services.llm_provider.get_provider", return_value=fake_provider):
        from backend.services.gemini_service import GeminiService
        GeminiService._instance = None
        GeminiService._provider = None
        GeminiService._context_manager = None
        GeminiService._conversation_manager = None

        svc = GeminiService.__new__(GeminiService)
        svc._provider = fake_provider
        svc._context_manager = MagicMock()
        svc._conversation_manager = None

        yield svc


def test_no_extracted_text_no_extra_section(fresh_service):
    svc = fresh_service

    svc._context_manager.load_case_context.return_value = FIXTURE_CASE_CTX_NO_TEXT
    svc._context_manager.load_folder_context.return_value = None
    svc._context_manager.merge_contexts.return_value = "=== CASE CONTEXT ===\n"

    merged_ctx, _ = svc._load_context("ACTE-TEST-002")

    assert merged_ctx is not None
    assert "REGULATION CONTENT (pre-extracted)" not in merged_ctx, (
        "No pre-extracted section should appear when no regulation has extractedText"
    )
    assert "Paragraph 23 says" not in merged_ctx


def test_no_http_call_made(fresh_service, monkeypatch):
    """_load_context must not make any outbound HTTP request."""
    import urllib.request as urllib_req
    import urllib.error

    def _fail(*a, **kw):
        raise AssertionError("_load_context must not make HTTP calls")

    monkeypatch.setattr(urllib_req, "urlopen", _fail)

    svc = fresh_service
    svc._context_manager.load_case_context.return_value = FIXTURE_CASE_CTX_NO_TEXT
    svc._context_manager.load_folder_context.return_value = None
    svc._context_manager.merge_contexts.return_value = "=== CASE CONTEXT ===\n"

    # Should not raise
    merged_ctx, _ = svc._load_context("ACTE-TEST-002")
    assert merged_ctx is not None
