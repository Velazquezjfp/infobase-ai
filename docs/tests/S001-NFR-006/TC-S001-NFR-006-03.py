"""
S001-NFR-006 TC-03 — PDF extract via API, already-absolute container path.

Same endpoint, but with the already-resolved container path. This is what
direct-curl debugging (or future canonicalized manifests) would send.
The helper must pass it through unchanged.
"""

from __future__ import annotations

import urllib.request
import urllib.error
import json

import pytest

pytestmark = pytest.mark.integration

ABSOLUTE_PATH = "/var/app/documents/ACTE-2024-001/applications/Anmeldeformular.pdf"
BACKEND_URL = "http://localhost:8000/api/documents/extract-pdf-text"


def test_extract_pdf_text_with_absolute_path():
    body = json.dumps({"documentPath": ABSOLUTE_PATH}).encode("utf-8")
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
        pytest.fail(f"Absolute-path PDF extract returned {exc.code}: {body_text}")

    text = payload.get("text", "")
    assert text and len(text.strip()) > 0, f"Extracted text was empty: {payload!r}"
