"""TC-S001-F-006-06 — enabled passthrough.

With ENABLE_UPLOAD=true, a 1KB upload returns 200 and persists the file
under public/documents/{case_id}/{folder_id}/. Same as today's behaviour.
"""

from __future__ import annotations

import io

import pytest


@pytest.mark.asyncio
async def test_enabled_upload_persists_file(tmp_path, monkeypatch, fresh_files_modules):
    case_id = "ACTE-TEST-006"
    folder_id = "uploads"

    # Run the handler with cwd at tmp_path so writes land somewhere disposable.
    monkeypatch.chdir(tmp_path)
    (tmp_path / "public" / "documents").mkdir(parents=True)

    fresh_files_modules({"ENABLE_UPLOAD": "true"})

    from fastapi import FastAPI
    from backend.api.files import router as files_router

    app = FastAPI()
    app.include_router(files_router)

    payload = b"x" * 1024  # 1 KB, well under the 15 MB cap

    import httpx
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        files = {"file": ("hello.txt", io.BytesIO(payload), "text/plain")}
        data = {"case_id": case_id, "folder_id": folder_id}
        response = await client.post("/api/files/upload", files=files, data=data)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["size"] == 1024

    written = tmp_path / "public" / "documents" / case_id / folder_id / body["file_name"]
    assert written.exists(), f"Expected file at {written}"
    assert written.read_bytes() == payload
