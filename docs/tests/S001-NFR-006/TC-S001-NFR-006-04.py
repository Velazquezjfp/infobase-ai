"""
S001-NFR-006 TC-04 — email parse via API, legacy `public/documents/...` path.

Same fix pattern as TC-02 but for /api/documents/parse-email.
Skips gracefully if the Email.eml seed isn't present (different demo state).
"""

from __future__ import annotations

import urllib.request
import urllib.error
import json
import subprocess

import pytest

pytestmark = pytest.mark.integration

LEGACY_PATH = "public/documents/ACTE-2024-001/emails/Email.eml"
BACKEND_URL = "http://localhost:8000/api/documents/parse-email"


def _eml_exists_in_container() -> bool:
    """Inspect the running backend to confirm the demo .eml seed is present."""
    try:
        result = subprocess.run(
            ["docker", "compose", "exec", "-T", "backend", "sh", "-c",
             "test -f /var/app/documents/ACTE-2024-001/emails/Email.eml && echo yes || echo no"],
            capture_output=True, text=True, timeout=10,
        )
        return "yes" in result.stdout
    except Exception:
        return False


def test_parse_email_with_legacy_path():
    if not _eml_exists_in_container():
        pytest.skip("Email.eml seed not present in container — skipping email parse test")

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
        pytest.fail(f"Legacy-path email parse returned {exc.code}: {body_text}")

    # Either body_text or subject must be present — confirms the file was actually parsed.
    has_content = bool(payload.get("body_text", "").strip()) or bool(payload.get("subject", "").strip())
    assert has_content, f"Email parsed but content empty: {payload!r}"
