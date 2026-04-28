"""TC-S001-F-003-03 — LLM grounding: when a regulation carries extractedText,
_build_prompt includes the extracted text in the final prompt.

Injects a fake LLMProvider and case context with extractedText set, then
verifies that the prompt passed to the provider contains the extracted text.
"""

from __future__ import annotations

import sys
import importlib
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

FIXTURE_REGULATIONS = [
    {
        "id": "test-reg-001",
        "title": "Test Regulation",
        "summary": "A test regulation.",
        "url": "https://example.de/x",
        "extractedText": "Paragraph 23 says the applicant must provide proof.",
    }
]

FIXTURE_CASE_CTX = {
    "schemaVersion": "2.0",
    "caseId": "ACTE-TEST-001",
    "caseType": "integration_course",
    "name": "Test Case",
    "description": "Test description.",
    "regulations": FIXTURE_REGULATIONS,
    "requiredDocuments": [],
    "validationRules": [],
    "commonIssues": [],
}


@pytest.fixture
def fresh_service(monkeypatch):
    """Return a freshly-constructed GeminiService with a mocked LLM provider."""
    # Drop cached modules so singleton resets
    for mod in list(sys.modules):
        if mod.startswith("backend."):
            sys.modules.pop(mod, None)

    monkeypatch.setenv("LLM_BACKEND", "internal")
    monkeypatch.setenv("LITELLM_PROXY_URL", "http://fake:4000")
    monkeypatch.setenv("LITELLM_TOKEN", "sk-test")
    monkeypatch.setenv("LITELLM_MODEL", "test-model")

    # Re-import after env setup
    from backend.services import llm_provider as lp_mod
    lp_mod.reset_provider_for_tests()

    fake_provider = MagicMock()
    fake_provider.generate = AsyncMock(return_value="ok")
    fake_provider.generate_stream = AsyncMock(return_value=iter([]))

    with patch("backend.services.llm_provider.get_provider", return_value=fake_provider):
        from backend.services.gemini_service import GeminiService
        # Reset singleton
        GeminiService._instance = None
        GeminiService._provider = None
        GeminiService._context_manager = None
        GeminiService._conversation_manager = None

        svc = GeminiService.__new__(GeminiService)
        svc._provider = fake_provider
        svc._context_manager = MagicMock()
        svc._conversation_manager = None

        yield svc, fake_provider


def test_extracted_text_in_prompt(fresh_service):
    svc, _ = fresh_service

    svc._context_manager.load_case_context.return_value = FIXTURE_CASE_CTX
    svc._context_manager.load_folder_context.return_value = None
    svc._context_manager.merge_contexts.return_value = "=== CASE CONTEXT ===\nCase: ACTE-TEST-001\n"

    merged_ctx, _ = svc._load_context("ACTE-TEST-001")

    assert merged_ctx is not None, "_load_context must return a context string"
    assert "Paragraph 23 says" in merged_ctx, (
        "merged_context must contain extractedText from regulation"
    )
    assert "https://example.de/x" in merged_ctx, (
        "merged_context must include the URL as a citation marker"
    )

    # Build the final prompt and confirm the extracted text flows through
    full_prompt = svc._build_prompt(
        "What does regulation test-reg-001 say?",
        context=merged_ctx,
    )
    assert "Paragraph 23 says" in full_prompt, (
        "_build_prompt output must contain the extracted regulation text"
    )
