"""TC-S001-F-009-05 — existing backend tests continue to import-load.

The refactor removed the local ``ErrorResponse`` class definitions from
``admin.py`` and ``files.py``. Any test that used to reference those classes
must now resolve them through ``backend.api._shared``. This test asserts
the existing ``backend.tests`` package still loads cleanly under the new
imports.
"""

from __future__ import annotations

import importlib

import pytest


@pytest.fixture(autouse=True)
def configured_env(monkeypatch):
    monkeypatch.setenv("LLM_BACKEND", "external")
    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-key")


def test_admin_router_still_imports_and_responses_reference_shared_error_response():
    importlib.invalidate_caches()
    admin = importlib.import_module("backend.api.admin")
    from backend.api._shared import ErrorResponse

    # The router has its responses= references baked in at decoration time.
    # Inspect the OpenAPI extra responses to confirm they reference the shared class.
    for route in admin.router.routes:
        if not hasattr(route, "responses") or route.responses is None:
            continue
        for status_code, spec in route.responses.items():
            model = spec.get("model")
            if model is not None and model.__name__ == "ErrorResponse":
                assert model is ErrorResponse, (
                    f"admin route {route.path} status {status_code} references "
                    f"a stale ErrorResponse: {model!r}"
                )


def test_files_router_responses_use_shared_file_error_response():
    importlib.invalidate_caches()
    files = importlib.import_module("backend.api.files")
    from backend.api._shared import ErrorResponse, FileErrorResponse

    for route in files.router.routes:
        if not hasattr(route, "responses") or route.responses is None:
            continue
        for status_code, spec in route.responses.items():
            model = spec.get("model")
            if model is None:
                continue
            assert model in (ErrorResponse, FileErrorResponse), (
                f"files route {route.path} status {status_code} references an "
                f"unexpected model: {model!r}"
            )


def test_existing_backend_tests_module_still_imports():
    """Smoke check — pre-existing test modules under backend.tests still import."""
    importlib.invalidate_caches()
    importlib.import_module("backend.tests")
    importlib.import_module("backend.tests.test_anonymization")
    importlib.import_module("backend.tests.test_conversation_manager")
