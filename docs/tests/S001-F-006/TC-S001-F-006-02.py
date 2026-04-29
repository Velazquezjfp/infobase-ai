"""TC-S001-F-006-02 — disabled upload writes nothing to disk.

Snapshots the case directory before and after the rejected upload and
asserts the contents are identical.
"""

from __future__ import annotations

import io
import os
from pathlib import Path

import pytest


def _snapshot(directory: Path):
    if not directory.exists():
        return set()
    return {p.relative_to(directory) for p in directory.rglob("*") if p.is_file()}


@pytest.mark.asyncio
async def test_upload_disabled_does_not_write_file(tmp_path, monkeypatch, fresh_files_modules):
    # Point the upload directory at the test's tmp_path so the snapshot is
    # deterministic and does not collide with real artefacts.
    case_id = "ACTE-TEST-006"
    folder_id = "uploads"

    monkeypatch.chdir(tmp_path)
    case_dir = tmp_path / "public" / "documents" / case_id / folder_id
    case_dir.mkdir(parents=True)
    sentinel = case_dir / "preexisting.txt"
    sentinel.write_text("kept")

    before = _snapshot(case_dir)

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
        files = {"file": ("new.txt", io.BytesIO(b"should not be written"), "text/plain")}
        data = {"case_id": case_id, "folder_id": folder_id}
        response = await client.post("/api/files/upload", files=files, data=data)

    assert response.status_code == 403

    after = _snapshot(case_dir)
    assert before == after, f"Directory mutated despite 403: added={after - before}, removed={before - after}"
    assert sentinel.exists() and sentinel.read_text() == "kept"
