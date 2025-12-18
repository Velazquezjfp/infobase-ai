"""
WebSocket Chat API for BAMF AI Case Management System.

This module provides WebSocket endpoints for real-time AI chat functionality.
Each WebSocket connection is scoped to a specific case (ACTE) to ensure
proper context isolation.
"""

import json
import logging
from typing import Dict, Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from backend.services.gemini_service import GeminiService
from backend.tools.form_parser import (
    build_extraction_prompt,
    validate_form_schema,
    parse_extraction_result
)

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """
    Manage WebSocket connections for chat sessions.

    Handles connection lifecycle and message routing for case-scoped
    WebSocket connections.
    """

    def __init__(self):
        """Initialize the connection manager."""
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, case_id: str, websocket: WebSocket) -> None:
        """
        Accept and register a new WebSocket connection.

        Args:
            case_id: The case ID for this connection.
            websocket: The WebSocket connection instance.
        """
        await websocket.accept()
        self.active_connections[case_id] = websocket
        logger.info(f"WebSocket connected for case: {case_id}")

    def disconnect(self, case_id: str) -> None:
        """
        Unregister a WebSocket connection.

        Args:
            case_id: The case ID to disconnect.
        """
        if case_id in self.active_connections:
            del self.active_connections[case_id]
            logger.info(f"WebSocket disconnected for case: {case_id}")

    async def send_message(self, case_id: str, message: Dict[str, Any]) -> None:
        """
        Send a message to a specific case's WebSocket connection.

        Args:
            case_id: The case ID to send the message to.
            message: The message dictionary to send.
        """
        if case_id in self.active_connections:
            await self.active_connections[case_id].send_json(message)


# Global connection manager instance
manager = ConnectionManager()

# Initialize Gemini service (singleton)
gemini_service = GeminiService()


@router.websocket("/ws/chat/{case_id}")
async def websocket_chat_endpoint(websocket: WebSocket, case_id: str):
    """
    WebSocket endpoint for case-scoped AI chat.

    Handles real-time bidirectional communication between the frontend
    and the AI service. Each connection is isolated to a specific case.

    Args:
        websocket: The WebSocket connection.
        case_id: The case ID (e.g., "ACTE-2024-001") for this session.

    WebSocket Message Format:
        Incoming (from client):
        {
            "type": "chat",
            "content": "User message",
            "caseId": "ACTE-2024-001",
            "folderId": "personal-data" (optional),
            "documentContent": "..." (optional),
            "formSchema": [...] (optional)
        }

        Outgoing (to client):
        {
            "type": "chat_response" | "form_update" | "error",
            "content": "AI response",
            "timestamp": "2024-01-01T12:00:00Z",
            "updates": {...} (for form_update),
            "confidence": {...} (for form_update)
        }
    """
    await manager.connect(case_id, websocket)

    # Check if Gemini service is initialized
    if not gemini_service.is_initialized():
        await websocket.send_json({
            "type": "error",
            "message": "API key not configured",
            "timestamp": None
        })
        await websocket.close()
        return

    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "system",
            "content": f"Connected to AI assistant for case {case_id}",
            "timestamp": None
        })

        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                message = json.loads(data)

                # Validate message format
                if not isinstance(message, dict):
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid message format: expected JSON object",
                        "timestamp": None
                    })
                    continue

                message_type = message.get("type")
                content = message.get("content", "").strip()

                # Validate required fields
                if not message_type:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Message must include 'type' field",
                        "timestamp": None
                    })
                    continue

                if message_type == "chat":
                    # Handle chat message
                    await handle_chat_message(
                        websocket,
                        case_id,
                        content,
                        message
                    )

                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}",
                        "timestamp": None
                    })

            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received from case {case_id}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": None
                })

            except Exception as e:
                logger.error(f"Error processing message for case {case_id}: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Failed to process message: {str(e)}",
                    "timestamp": None
                })

    except WebSocketDisconnect:
        manager.disconnect(case_id)
        logger.info(f"Client disconnected from case {case_id}")

    except Exception as e:
        logger.error(f"WebSocket error for case {case_id}: {str(e)}")
        manager.disconnect(case_id)


async def handle_chat_message(
    websocket: WebSocket,
    case_id: str,
    content: str,
    message: Dict[str, Any]
) -> None:
    """
    Handle a chat message and generate AI response.

    Args:
        websocket: The WebSocket connection.
        case_id: The case ID.
        content: The user's message content.
        message: The complete message dictionary.
    """
    # Validate content
    if not content:
        await websocket.send_json({
            "type": "error",
            "message": "Message content cannot be empty",
            "timestamp": None
        })
        return

    # Extract optional fields
    document_content = message.get("documentContent")
    form_schema = message.get("formSchema")
    folder_id = message.get("folderId")

    logger.info(
        f"Processing chat message for case {case_id}"
        f"{f', folder: {folder_id}' if folder_id else ''}"
    )

    # Check if this is a form filling request
    is_form_fill_request = (
        form_schema and
        (
            "fill" in content.lower() or
            "extract" in content.lower() or
            "populate" in content.lower()
        )
    )

    try:
        if is_form_fill_request and validate_form_schema(form_schema):
            # Handle form field extraction
            await handle_form_extraction(
                websocket,
                case_id,
                document_content or content,
                form_schema
            )
        else:
            # Handle regular chat message
            # Context is now automatically loaded by gemini_service using case_id

            # Generate AI response
            response = await gemini_service.generate_response(
                prompt=content,
                case_id=case_id,
                folder_id=folder_id,
                document_content=document_content
            )

            # Send response
            await websocket.send_json({
                "type": "chat_response",
                "content": response,
                "timestamp": None  # Frontend will add timestamp
            })

    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": str(e),
            "timestamp": None
        })


async def handle_form_extraction(
    websocket: WebSocket,
    case_id: str,
    document_text: str,
    form_schema: list
) -> None:
    """
    Handle form field extraction from document content.

    Uses AI to extract structured data from document text based on
    the provided form schema.

    Args:
        websocket: The WebSocket connection.
        case_id: The case ID.
        document_text: The document content to extract from.
        form_schema: The form field definitions.
    """
    logger.info(f"Extracting form fields for case {case_id}")

    try:
        # Build extraction prompt
        extraction_prompt = build_extraction_prompt(document_text, form_schema)

        # Get AI response with extracted data
        ai_response = await gemini_service.generate_response(
            prompt=extraction_prompt,
            document_content=None,  # Already included in prompt
            context=None
        )

        # Parse the extraction result
        result = parse_extraction_result(ai_response, form_schema)

        # Send form update message
        await websocket.send_json({
            "type": "form_update",
            "updates": result["updates"],
            "confidence": result["confidence"],
            "timestamp": None
        })

        # Also send a chat response confirming the action
        field_count = len(result["updates"])
        await websocket.send_json({
            "type": "chat_response",
            "content": f"I've extracted {field_count} field{'s' if field_count != 1 else ''} from the document and updated the form.",
            "timestamp": None
        })

    except Exception as e:
        logger.error(f"Error extracting form fields: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": f"Failed to extract form fields: {str(e)}",
            "timestamp": None
        })


@router.get("/api/chat/health")
async def chat_health_check():
    """
    Health check endpoint for chat service.

    Returns:
        JSONResponse: Service health status.
    """
    is_ready = gemini_service.is_initialized()

    return JSONResponse(
        content={
            "service": "chat",
            "status": "ready" if is_ready else "not_ready",
            "gemini_initialized": is_ready
        },
        status_code=200 if is_ready else 503
    )
