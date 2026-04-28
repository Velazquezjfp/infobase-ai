"""TC-S001-F-004-04 — enabled path unchanged.

With ENABLE_ANONYMIZATION=true the handler proceeds past the flag check and
invokes anonymize_document (existing workflow). The legacy
TestAnonymizationIntegration.test_full_anonymization_workflow is still gated by
SKIP_INTEGRATION_TESTS and is not duplicated here; this test only verifies that
the flag does not interfere with the call path.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_anonymize_enabled_calls_service(fresh_chat_modules, mock_websocket):
    fresh_chat_modules({"ENABLE_ANONYMIZATION": "true"})

    fake_result = MagicMock()
    fake_result.success = True
    fake_result.original_path = "/docs/x.png"
    fake_result.anonymized_path = "/docs/x_anonymized.png"
    fake_result.detections_count = 0
    fake_result.detection_labels = []
    fake_result.detections = {}
    fake_result.error = None
    fake_result.render_metadata = None

    with patch(
        "backend.tools.anonymization_tool.anonymize_document",
        new=AsyncMock(return_value=fake_result),
    ) as mock_tool:
        from backend.api.chat import handle_anonymization

        message = {
            "type": "anonymize",
            "filePath": "/docs/x.png",
            "documentId": "doc-1",
            "folderId": "personal-data",
            "language": "de",
        }
        await handle_anonymization(mock_websocket, "ACTE-2024-001", message)

        mock_tool.assert_called_once()
