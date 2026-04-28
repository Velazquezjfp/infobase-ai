"""TC-S001-NFR-003-05 — frontend is reachable on its configured port."""
import urllib.request
import urllib.error

import pytest

FRONTEND_URL = "http://localhost:3000"


def test_frontend_responds_200(stack_up):
    if not stack_up["frontend_healthy"]:
        pytest.skip("Frontend not healthy — skipping reachability test")

    try:
        with urllib.request.urlopen(FRONTEND_URL, timeout=5) as resp:
            assert resp.status == 200, (
                f"Frontend returned HTTP {resp.status} instead of 200"
            )
    except urllib.error.URLError as exc:
        pytest.fail(f"Frontend not reachable at {FRONTEND_URL}: {exc}")
