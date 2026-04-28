"""TC-S001-F-001-05 — streaming over WS /ws/chat/{case_id} on the internal path.

With LLM_BACKEND=internal, the WebSocket endpoint must produce at least 2
chat_chunk messages and a final chat_chunk with is_complete=true.

Implementation note: starlette's bundled TestClient is broken against the
project's pinned httpx version (httpx 0.28 dropped the ``app=`` constructor
kwarg, but starlette 0.27 still passes it). To avoid coupling this test to
that incompatibility, we drive the WebSocket handler coroutine directly with
a fake WebSocket that records what the server sends back.
"""

from __future__ import annotations

import asyncio
from unittest.mock import patch

import pytest


class _FakeStream:
    """Mimics litellm.acompletion(stream=True) — async iterable of chunks."""

    def __init__(self, chunks):
        self._chunks = list(chunks)

    def __aiter__(self):
        self._index = 0
        return self

    async def __anext__(self):
        if self._index >= len(self._chunks):
            raise StopAsyncIteration
        item = self._chunks[self._index]
        self._index += 1
        return item


def _chunk(text: str) -> dict:
    return {"choices": [{"delta": {"content": text}}]}


async def _fake_acompletion(*_args, **kwargs):
    if kwargs.get("stream"):
        return _FakeStream([_chunk("Hallo "), _chunk("aus "), _chunk("LiteLLM.")])
    return {"choices": [{"message": {"content": "non-streaming reply"}}]}


from starlette.websockets import WebSocketDisconnect


class FakeWebSocket:
    """Just enough of starlette.websockets.WebSocket for the chat handler."""

    def __init__(self, inbound):
        # ``inbound`` is a list of dicts; each will be returned, in order,
        # from receive_text(). After they are exhausted we raise
        # WebSocketDisconnect so the handler exits cleanly.
        import json
        self._inbound = [json.dumps(m) for m in inbound]
        self.sent: list[dict] = []
        self._closed = False

    async def accept(self):
        return None

    async def send_json(self, data):
        self.sent.append(data)

    async def receive_text(self) -> str:
        if not self._inbound:
            raise WebSocketDisconnect(code=1000)
        return self._inbound.pop(0)

    async def close(self):
        self._closed = True


@pytest.mark.asyncio
async def test_websocket_streams_chat_chunks_under_internal_backend(fresh_modules):
    fresh_modules({
        "LLM_BACKEND": "internal",
        "LITELLM_PROXY_URL": "http://litellm.test:4000",
        "LITELLM_TOKEN": "sk-test",
        "LITELLM_MODEL": "gemma3:12b",
    })

    with patch("litellm.acompletion", new=_fake_acompletion):
        from backend.api.chat import websocket_chat_endpoint

        ws = FakeWebSocket(inbound=[
            {
                "type": "chat",
                "content": "Hallo",
                "caseId": "ACTE-2026-001",
                "stream": True,
            },
        ])

        await asyncio.wait_for(
            websocket_chat_endpoint(ws, case_id="ACTE-2026-001", language="de"),
            timeout=5.0,
        )

    chunks = [m for m in ws.sent if m.get("type") == "chat_chunk"]
    assert chunks, f"no chat_chunk messages emitted; got: {ws.sent}"
    terminators = [c for c in chunks if c.get("is_complete") is True]
    assert terminators, f"no terminator chunk; got: {chunks}"
    non_terminal = [c for c in chunks if not c.get("is_complete")]
    assert len(non_terminal) >= 2, (
        f"expected at least 2 streaming chunks before terminator, got {non_terminal}"
    )
