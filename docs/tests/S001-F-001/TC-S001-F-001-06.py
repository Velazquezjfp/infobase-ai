"""TC-S001-F-001-06 — no google.generativeai import on the internal path.

Imports `backend.services.llm_provider`, calls get_provider() under
LLM_BACKEND=internal, and asserts that `google.generativeai` is absent from
sys.modules. This protects against regressions where someone re-introduces a
top-level import of the Google SDK in the service layer.
"""

from __future__ import annotations

import sys


def test_internal_path_does_not_import_google_generativeai(fresh_modules):
    _config, llm_provider = fresh_modules({
        "LLM_BACKEND": "internal",
        "LITELLM_PROXY_URL": "http://litellm.test:4000",
        "LITELLM_TOKEN": "sk-test",
        "LITELLM_MODEL": "gemma3:12b",
    })

    # Importing the service layer must also stay clean.
    import importlib
    importlib.import_module("backend.services.gemini_service")
    importlib.import_module("backend.services.validation_service")
    importlib.import_module("backend.services.shacl_generator")

    provider = llm_provider.get_provider()
    assert type(provider).__name__ == "LiteLLMProvider"

    leaked = [m for m in sys.modules if m == "google.generativeai" or m.startswith("google.generativeai.")]
    assert not leaked, (
        "google.generativeai must not be imported on the internal path, "
        f"but found: {leaked}"
    )
