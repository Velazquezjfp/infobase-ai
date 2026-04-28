"""TC-S001-F-004-01 — disabled path.

With ENABLE_ANONYMIZATION=false (default), sending {"type": "anonymize", ...} over
the WebSocket handler returns anonymization_complete with success=false and
error="feature_disabled".
"""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_anonymize_disabled_short_circuits(fresh_chat_modules, mock_websocket):
    fresh_chat_modules({"ENABLE_ANONYMIZATION": "false"})

    from backend.api.chat import handle_anonymization

    message = {
        "type": "anonymize",
        "filePath": "x.png",
        "documentId": "1",
        "folderId": "personal-data",
        "language": "de",
    }
    await handle_anonymization(mock_websocket, "ACTE-2024-001", message)

    assert len(mock_websocket.sent_messages) == 1
    reply = mock_websocket.sent_messages[0]
    assert reply["type"] == "anonymization_complete"
    assert reply["success"] is False
    assert reply["error"] == "feature_disabled"
    assert "Anonymisierungsfunktion" in reply["message"]
