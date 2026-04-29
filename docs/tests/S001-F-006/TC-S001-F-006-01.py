"""TC-S001-F-006-01 — POST /api/files/upload returns 403 when ENABLE_UPLOAD=false.

Body matches ErrorResponse{error: "feature_disabled", detail, file_name}.
"""

from __future__ import annotations

import io

import pytest


@pytest.mark.asyncio
async def test_upload_disabled_returns_403_feature_disabled(fresh_files_modules):
    fresh_files_modules({"ENABLE_UPLOAD": "false"})

    from fastapi import FastAPI
    from backend.api.files import router as files_router

    app = FastAPI()
    app.include_router(files_router)

    import httpx
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        files = {"file": ("hello.txt", io.BytesIO(b"hello world"), "text/plain")}
        data = {"case_id": "ACTE-2024-001", "folder_id": "uploads"}
        response = await client.post("/api/files/upload", files=files, data=data)

    assert response.status_code == 403
    body = response.json()
    # FastAPI wraps HTTPException(detail=...) under top-level "detail".
    detail = body.get("detail", body)
    assert detail["error"] == "feature_disabled"
    assert "Demo" in detail["detail"] or "deaktiviert" in detail["detail"]
    assert detail["file_name"] == "hello.txt"
