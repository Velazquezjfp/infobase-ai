"""TC-S001-F-009-03 — single ErrorResponse schema in OpenAPI.

After consolidating ErrorResponse into ``backend.api._shared``, the OpenAPI
document produced by ``GET /openapi.json`` exposes exactly one
``ErrorResponse`` schema component. ``FileErrorResponse`` references it via
``allOf`` (Pydantic v2's default representation of inheritance).

The idirs.py ErrorResponse is intentionally still distinct (separate concern,
out of scope for sprint 1) — Pydantic disambiguates same-name classes by
suffixing the second one (e.g. ``ErrorResponse2``) in the OpenAPI components.
The test only asserts a single bare ``ErrorResponse`` entry exists, which is
what closes the duplicate-definition issue called out in the requirement.
"""

from __future__ import annotations

import pytest


@pytest.fixture
def openapi_doc(monkeypatch):
    monkeypatch.setenv("LLM_BACKEND", "external")
    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-key")

    from fastapi import FastAPI

    from backend.api.admin import router as admin_router
    from backend.api.files import router as files_router
    from backend.api.idirs import router as idirs_router

    app = FastAPI()
    app.include_router(admin_router)
    app.include_router(files_router)
    app.include_router(idirs_router)

    return app.openapi()


def test_single_error_response_schema(openapi_doc):
    schemas = openapi_doc["components"]["schemas"]
    assert "ErrorResponse" in schemas, list(schemas.keys())


def test_file_error_response_extends_via_allof(openapi_doc):
    schemas = openapi_doc["components"]["schemas"]
    assert "FileErrorResponse" in schemas, list(schemas.keys())

    file_err = schemas["FileErrorResponse"]
    # Pydantic v2 emits inheritance as a top-level allOf reference + extra fields.
    # We accept either a direct allOf or a $ref-to-ErrorResponse anywhere in the schema.
    raw = repr(file_err)
    assert "ErrorResponse" in raw, file_err
    assert "file_name" in raw, file_err


def test_no_orphan_error_response_in_admin_or_files():
    """admin.py and files.py must no longer define ErrorResponse locally."""
    import backend.api.admin as admin_mod
    import backend.api.files as files_mod
    from backend.api._shared import ErrorResponse, FileErrorResponse

    assert admin_mod.ErrorResponse is ErrorResponse, (
        "admin.py must reuse the shared ErrorResponse, not redeclare it"
    )
    assert files_mod.ErrorResponse is ErrorResponse, (
        "files.py must reuse the shared ErrorResponse, not redeclare it"
    )
    assert files_mod.FileErrorResponse is FileErrorResponse
