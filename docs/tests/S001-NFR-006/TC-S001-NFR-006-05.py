"""
S001-NFR-006 TC-05 — translation tool round-trip via WebSocket with legacy path.

Sends a `/translate` WS request with the SPA's legacy `public/documents/...`
path shape (which is what the actual frontend sends). Asserts:
  - `translation_complete` arrives with `success: true`
  - `translatedPath` is non-empty (translated render was written)

Closes the bug reported during operator email-translation testing: the
translation_service was opening `Path(email_path)` literally, which failed
inside the container because cwd is /app and the file lives under
DOCUMENTS_BASE_PATH (/var/app/documents).

Skips gracefully if Email.eml seed isn't present.
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import time

import pytest

pytestmark = pytest.mark.integration

LEGACY_PATH = "public/documents/ACTE-2024-001/emails/Email.eml"
WS_URL = "ws://localhost:3000/ws/chat/ACTE-2024-001?language=de"


def _eml_seed_present() -> bool:
    try:
        result = subprocess.run(
            ["docker", "compose", "exec", "-T", "backend", "sh", "-c",
             "test -f /var/app/documents/ACTE-2024-001/emails/Email.eml && echo yes || echo no"],
            capture_output=True, text=True, timeout=10,
        )
        return "yes" in result.stdout
    except Exception:
        return False


async def _run_translate():
    import websockets

    async with websockets.connect(WS_URL, open_timeout=10, ping_interval=None) as ws:
        # Welcome frame
        welcome_raw = await asyncio.wait_for(ws.recv(), timeout=10)
        welcome = json.loads(welcome_raw)
        if welcome.get("type") == "error":
            raise RuntimeError(f"welcome was an error: {welcome}")

        # Send translation request — same shape the SPA's `Übersetzen` button sends.
        await ws.send(json.dumps({
            "type": "translate",
            "filePath": LEGACY_PATH,
            "targetLanguage": "de",
            "sourceLanguage": "auto",
            "documentId": None,
        }))

        # Wait for translation_complete (allow up to 180s for cold-loaded LLM).
        deadline = time.time() + 180
        while time.time() < deadline:
            raw = await asyncio.wait_for(ws.recv(), timeout=deadline - time.time())
            msg = json.loads(raw)
            t = msg.get("type")
            if t == "translation_complete":
                return msg
            if t == "error":
                raise RuntimeError(f"error frame: {msg.get('message')}")
            # ignore any other frames (chunks, system)
        raise RuntimeError("timed out waiting for translation_complete")


def test_translation_via_legacy_path():
    if not _eml_seed_present():
        pytest.skip("Email.eml seed not present in container — skipping translation test")

    result = asyncio.run(_run_translate())

    assert result.get("success") is True, f"translation_complete returned success=False: {result}"
    translated_path = result.get("translatedPath") or ""
    assert translated_path, f"translatedPath empty in {result}"
    # Sanity: translated file should be under DOCUMENTS_BASE_PATH (or named *_translated_*).
    assert "_translated_" in translated_path or translated_path.endswith(".eml"), (
        f"translatedPath shape unexpected: {translated_path!r}"
    )
