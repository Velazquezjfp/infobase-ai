"""
S001-NFR-006 TC-02 — PDF extract via API, legacy `public/documents/...` path.

Calls the live stack's `POST /api/documents/extract-pdf-text` with the path
shape the SPA's DocumentViewer actually sends today, asserts 200 + non-empty
text. Closes the bug from NFR-005's container migration.

Requires the stack to be running (`bash temp/up.sh`).
"""

from __future__ import annotations

import urllib.request
import urllib.error
import json

import pytest

pytestmark = pytest.mark.integration

LEGACY_PATH = "public/documents/ACTE-2024-001/applications/Anmeldeformular.pdf"
BACKEND_URL = "http://localhost:8000/api/documents/extract-pdf-text"


def test_extract_pdf_text_with_legacy_path():
    body = json.dumps({"documentPath": LEGACY_PATH}).encode("utf-8")
    req = urllib.request.Request(
        BACKEND_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            assert resp.status == 200, f"Expected 200 OK, got {resp.status}"
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="ignore")
        pytest.fail(f"Legacy-path PDF extract returned {exc.code}: {body_text}")

    text = payload.get("text", "")
    page_count = payload.get("pageCount", 0)
    assert text and len(text.strip()) > 0, f"Extracted text was empty: {payload!r}"
    assert page_count >= 1, f"Expected at least 1 page, got {page_count}"
