#!/usr/bin/env python3
"""
S001-NFR-005 Phase 7 — end-to-end WebSocket chat verification.

Connects via two paths:
  1. Proxied:  ws://localhost:{FRONTEND_PORT}/ws/chat/...  (production-realistic;
               nginx proxies the Upgrade to backend:8000)
  2. Direct:   ws://localhost:{BACKEND_PORT}/ws/chat/...   (sanity check;
               services.backend.ports stays open for sprint-1 dev)

For each: receive welcome frame, send a chat prompt, wait for a `chat_response`
or `error` frame (timeout 90s), assert non-empty content. Exit 0 on success.

Re-execs under backend/venv/bin/python3 if `websockets` isn't importable.
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# ---------- prelude: ensure websockets is importable ----------
ROOT = Path(__file__).resolve().parent.parent
VENV_PY = ROOT / "backend" / "venv" / "bin" / "python3"
try:
    import websockets  # noqa: F401
except ImportError:
    if VENV_PY.exists() and sys.executable != str(VENV_PY):
        os.execv(str(VENV_PY), [str(VENV_PY), *sys.argv])
    print("ERROR: websockets module not importable; run from backend/venv or pip install websockets", file=sys.stderr)
    sys.exit(2)

import websockets  # noqa: E402

# ---------- env ----------
def load_env():
    env_path = ROOT / ".env"
    out = dict(os.environ)
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            out.setdefault(k, v)
    return out

ENV = load_env()
FRONTEND_PORT = ENV.get("FRONTEND_PORT", "3000")
BACKEND_PORT = ENV.get("BACKEND_PORT", "8000")
CASE_ID = "ACTE-2024-001"
PROMPT = "reply with the single word: pong"
WS_TIMEOUT_SECONDS = 90  # cold model load can take a while

# ---------- backend log tail ----------
LOG_PATH = Path("/tmp/nfr005-backend.log")

def start_log_tail():
    LOG_PATH.unlink(missing_ok=True)
    return subprocess.Popen(
        ["docker", "compose", "logs", "--since", "0s", "-f", "backend"],
        stdout=open(LOG_PATH, "w"),
        stderr=subprocess.DEVNULL,
        cwd=ROOT,
    )

def stop_log_tail(proc):
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        proc.kill()

# ---------- the WS test ----------
async def run_ws_test(label: str, port: str) -> str:
    """Connect, send prompt, await a chat_response frame, return its content."""
    url = f"ws://localhost:{port}/ws/chat/{CASE_ID}?language=en"
    print(f"  • [{label}] connecting to {url}")
    async with websockets.connect(url, open_timeout=10, ping_interval=None) as ws:
        # 1. Welcome frame
        try:
            welcome_raw = await asyncio.wait_for(ws.recv(), timeout=10)
        except asyncio.TimeoutError:
            raise RuntimeError(f"[{label}] no welcome frame within 10s")
        welcome = json.loads(welcome_raw)
        if welcome.get("type") not in ("system", "error"):
            raise RuntimeError(f"[{label}] unexpected welcome type: {welcome}")
        if welcome.get("type") == "error":
            raise RuntimeError(f"[{label}] welcome was an error frame: {welcome}")
        print(f"    welcome ok ({welcome.get('content','')[:60]!r})")

        # 2. Send chat
        await ws.send(json.dumps({
            "type": "chat",
            "content": PROMPT,
            "caseId": CASE_ID,
        }))
        print(f"    sent chat prompt")

        # 3. Receive frames until terminal frame.
        # Streaming-mode protocol (backend/api/chat.py:336–354):
        #   - many `chat_chunk` frames with `is_complete: False` (each piece of the answer)
        #   - one final `chat_chunk` with `is_complete: True` and empty content
        # Non-streaming-mode protocol:
        #   - one `chat_response` frame with the full answer
        # Either way, we accumulate chunk content and return on terminal frame.
        deadline = time.time() + WS_TIMEOUT_SECONDS
        accumulated = []
        while time.time() < deadline:
            try:
                msg_raw = await asyncio.wait_for(ws.recv(), timeout=deadline - time.time())
            except asyncio.TimeoutError:
                raise RuntimeError(f"[{label}] no terminal frame within {WS_TIMEOUT_SECONDS}s; got {len(accumulated)} chunk(s)")
            msg = json.loads(msg_raw)
            mtype = msg.get("type")
            if mtype == "chat_response":
                content = msg.get("content", "")
                if not content:
                    raise RuntimeError(f"[{label}] chat_response had empty content: {msg}")
                print(f"    response (non-stream): {content[:200]!r}")
                return content
            elif mtype == "chat_chunk":
                if msg.get("is_complete"):
                    full = "".join(accumulated)
                    if not full.strip():
                        raise RuntimeError(f"[{label}] streaming completed but accumulated content is empty")
                    print(f"    response (stream, {len(accumulated)} chunks): {full[:200]!r}")
                    return full
                else:
                    accumulated.append(msg.get("content", ""))
                    if len(accumulated) % 10 == 0:
                        print(f"    [streaming: {len(accumulated)} chunks so far]")
            elif mtype == "error":
                raise RuntimeError(f"[{label}] error frame: {msg.get('message')}")
            else:
                print(f"    [skip {mtype}]")
                continue
        raise RuntimeError(f"[{label}] timed out waiting for terminal frame")

# ---------- main ----------
async def main():
    print("==> verify-e2e.py")
    log_proc = start_log_tail()
    time.sleep(1)
    try:
        proxied = await run_ws_test("PROXIED :3000", FRONTEND_PORT)
        direct  = await run_ws_test("DIRECT  :8000", BACKEND_PORT)
    finally:
        time.sleep(0.5)  # let last log lines flush
        stop_log_tail(log_proc)

    # 4. Grep the captured backend log for proxy-traverse evidence
    log_text = LOG_PATH.read_text() if LOG_PATH.exists() else ""
    has_litellm_call = (
        "host.docker.internal:4000" in log_text
        or "litellm" in log_text.lower()
        or "/v1/chat/completions" in log_text
    )
    if not has_litellm_call:
        print(f"  ! warning: backend log shows no litellm reference; chain may not have actually traversed proxy")
        print(f"    log file: {LOG_PATH} ({len(log_text)} bytes)")
    else:
        print(f"  ✓ backend log shows litellm/proxy traversal")

    # Final
    if proxied and direct:
        print("\nOK: e2e chat path traversed (proxied + direct)")
        return 0
    return 1

if __name__ == "__main__":
    try:
        rc = asyncio.run(main())
    except Exception as e:
        print(f"\nFAIL: {e}", file=sys.stderr)
        sys.exit(1)
    sys.exit(rc)
