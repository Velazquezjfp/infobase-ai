"""TC-S001-F-004-02 — no outbound traffic.

With ENABLE_ANONYMIZATION=false, the anonymize_document tool is never called,
meaning no outbound TCP connection to the anonymization API host is initiated.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_anonymize_disabled_does_not_call_service(fresh_chat_modules, mock_websocket):
    fresh_chat_modules({"ENABLE_ANONYMIZATION": "false"})

    with patch("backend.tools.anonymization_tool.anonymize_document", new=AsyncMock()) as mock_tool:
        from backend.api.chat import handle_anonymization

        message = {
            "type": "anonymize",
            "filePath": "x.png",
            "documentId": "1",
            "folderId": "personal-data",
            "language": "de",
        }
        await handle_anonymization(mock_websocket, "ACTE-2024-001", message)

        mock_tool.assert_not_called()
