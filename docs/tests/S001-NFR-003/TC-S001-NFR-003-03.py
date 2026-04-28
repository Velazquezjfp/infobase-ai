"""TC-S001-NFR-003-03 — cases-data volume persists a folder across container restarts."""
import json
import time
import urllib.request
import urllib.error

from conftest import _compose, COMPOSE_AVAILABLE
import pytest

BACKEND_URL = "http://localhost:8000"
CASE_ID = "ACTE-TEST-PERSIST-001"


def _request(method, path, data=None):
    url = f"{BACKEND_URL}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(
        url, data=body, method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, {}


def test_folder_persists_across_restart(stack_up):
    if not stack_up["backend_healthy"]:
        pytest.skip("Backend not healthy — skipping persistence test")

    # Create a new folder
    folder_id = "persist-test-folder"
    status, _ = _request(
        "POST",
        f"/api/folders/{CASE_ID}",
        {"folder_id": folder_id, "name": "Persistence Test Folder"},
    )
    assert status in (200, 201), f"Failed to create folder: HTTP {status}"

    # Restart backend container
    _compose("restart", "backend")
    deadline = time.time() + 60
    ready = False
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{BACKEND_URL}/health", timeout=2):
                ready = True
                break
        except (urllib.error.URLError, OSError):
            time.sleep(2)
    assert ready, "Backend did not come back healthy after restart"

    # The folder should still be accessible
    status, body = _request("GET", f"/api/folders/{CASE_ID}")
    assert status == 200, f"GET /api/folders/{CASE_ID} returned HTTP {status} after restart"
    folder_ids = [f.get("id", f.get("folder_id", "")) for f in (body if isinstance(body, list) else [])]
    assert folder_id in folder_ids, (
        f"Folder '{folder_id}' not found after container restart. "
        f"Found: {folder_ids}"
    )
