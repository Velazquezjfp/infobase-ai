"""
WebSocket Chat API for BAMF AI Case Management System.

This module provides WebSocket endpoints for real-time AI chat functionality.
Each WebSocket connection is scoped to a specific case (ACTE) to ensure
proper context isolation.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from backend.services.gemini_service import GeminiService
from backend.services.conversation_manager import get_conversation_manager
from backend.config import ENABLE_CHAT_HISTORY
from backend.tools.form_parser import (
    build_extraction_prompt,
    validate_form_schema,
    parse_extraction_result
)
from backend.tools.anonymization_tool import anonymize_document, is_supported_format

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
async def websocket_chat_endpoint(
    websocket: WebSocket,
    case_id: str,
    language: str = 'de'  # S5-014: Language parameter from query string
):
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
        # S5-014: Send translated welcome message based on language preference
        # Also replace ACTE prefix with language-appropriate term (Akte/Case)
        case_prefix = 'Akte' if language == 'de' else 'Case'
        translated_case_id = case_id.replace('ACTE', case_prefix)

        welcome_messages = {
            'de': f"Verbunden mit KI-Assistent für {translated_case_id}",
            'en': f"Connected to AI assistant for {translated_case_id}"
        }
        welcome_message = welcome_messages.get(language, welcome_messages['de'])

        await websocket.send_json({
            "type": "system",
            "content": welcome_message,
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

                elif message_type == "anonymize":
                    # Handle anonymization request
                    await handle_anonymization(
                        websocket,
                        case_id,
                        message
                    )

                elif message_type == "translate":
                    # S5-004: Handle translation request
                    await handle_translation(
                        websocket,
                        case_id,
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

    Supports both streaming and non-streaming responses based on the
    'stream' parameter in the message.

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
    enable_streaming = message.get("stream", True)  # Default to streaming for performance
    language = message.get("language", "de")  # S5-014: Language for AI responses (default: German)

    logger.info(
        f"Processing chat message for case {case_id}"
        f"{f', folder: {folder_id}' if folder_id else ''}"
        f", streaming: {enable_streaming}"
        f", language: {language}"
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
            # Handle form field extraction (no streaming for form extraction)
            # S5-002: Extract current form values for suggestion mode
            current_values = message.get("currentFormValues")
            await handle_form_extraction(
                websocket,
                case_id,
                document_content or content,
                form_schema,
                current_values,
                language  # Pass language for localized responses
            )
        else:
            # Handle regular chat message with optional streaming
            # Context is now automatically loaded by gemini_service using case_id

            # Generate AI response
            response = await gemini_service.generate_response(
                prompt=content,
                case_id=case_id,
                folder_id=folder_id,
                document_content=document_content,
                stream=enable_streaming,
                language=language  # S5-014: Pass language for AI responses
            )

            # Check if response is a streaming generator
            if hasattr(response, '__aiter__'):
                # Streaming mode - send chunks as they arrive
                async for chunk in response:
                    await websocket.send_json({
                        "type": "chat_chunk",
                        "content": chunk,
                        "is_complete": False,
                        "timestamp": None
                    })

                # Send completion marker
                await websocket.send_json({
                    "type": "chat_chunk",
                    "content": "",
                    "is_complete": True,
                    "timestamp": None
                })
            else:
                # Non-streaming mode - send complete response
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
    form_schema: list,
    current_values: Dict[str, str] = None,
    language: str = "de"
) -> None:
    """
    Handle form field extraction from document content.

    Uses AI to extract structured data from document text based on
    the provided form schema. S5-002: When current_values is provided,
    categorizes results into direct updates (empty fields) and suggestions
    (non-empty fields requiring user approval).

    Args:
        websocket: The WebSocket connection.
        case_id: The case ID.
        document_text: The document content to extract from.
        form_schema: The form field definitions.
        current_values: Optional dict of current form field values (S5-002).
        language: Language for response messages ('de' or 'en').
    """
    logger.info(f"Extracting form fields for case {case_id}")
    logger.info(f"  Document text length: {len(document_text) if document_text else 0}")
    logger.info(f"  Form schema fields: {len(form_schema) if form_schema else 0}")
    if form_schema and len(form_schema) > 0:
        logger.info(f"  First field example: {form_schema[0]}")

    try:
        # Build extraction prompt
        extraction_prompt = build_extraction_prompt(document_text, form_schema)

        # Get AI response with extracted data
        # Pass case_id to load case-specific context for validation rules
        ai_response = await gemini_service.generate_response(
            prompt=extraction_prompt,
            case_id=case_id,
            document_content=None,  # Already included in prompt
            stream=False  # Form extraction should not stream
        )

        # Parse the extraction result (S5-002: with current_values for comparison)
        result = parse_extraction_result(ai_response, form_schema, current_values)

        # S5-002: Check if we have categorized results (suggestions mode)
        if "suggestions" in result:
            # Send direct updates for empty fields
            direct_count = len(result["direct_updates"])
            if direct_count > 0:
                await websocket.send_json({
                    "type": "form_update",
                    "updates": result["direct_updates"],
                    "confidence": result.get("all_confidence", {}),
                    "timestamp": None
                })

            # Send suggestions for non-empty fields
            suggestion_count = len(result["suggestions"])
            if suggestion_count > 0:
                await websocket.send_json({
                    "type": "form_suggestion",
                    "suggestions": result["suggestions"],
                    "timestamp": None
                })

            # Send chat response with summary (localized)
            ignored_count = len(result.get("ignored", []))
            summary_parts = []

            if language == "de":
                # German messages
                if direct_count > 0:
                    summary_parts.append(f"{direct_count} Feld{'er' if direct_count != 1 else ''} ausgefüllt")
                if suggestion_count > 0:
                    summary_parts.append(f"{suggestion_count} Vorschläge verfügbar" if suggestion_count != 1 else "1 Vorschlag verfügbar")
                if ignored_count > 0:
                    summary_parts.append(f"{ignored_count} Feld{'er' if ignored_count != 1 else ''} unverändert")
                summary = "Formulardaten extrahiert: " + ", ".join(summary_parts) + "."
            else:
                # English messages
                if direct_count > 0:
                    summary_parts.append(f"{direct_count} field{'s' if direct_count != 1 else ''} filled")
                if suggestion_count > 0:
                    summary_parts.append(f"{suggestion_count} suggestion{'s' if suggestion_count != 1 else ''} available")
                if ignored_count > 0:
                    summary_parts.append(f"{ignored_count} field{'s' if ignored_count != 1 else ''} unchanged")
                summary = "I've extracted form data: " + ", ".join(summary_parts) + "."
            await websocket.send_json({
                "type": "chat_response",
                "content": summary,
                "timestamp": None
            })
        else:
            # Legacy mode: send all as updates (no current_values provided)
            await websocket.send_json({
                "type": "form_update",
                "updates": result["updates"],
                "confidence": result["confidence"],
                "timestamp": None
            })

            # Also send a chat response confirming the action (localized)
            field_count = len(result["updates"])
            if language == "de":
                content = f"Ich habe {field_count} Feld{'er' if field_count != 1 else ''} aus dem Dokument extrahiert und das Formular aktualisiert."
            else:
                content = f"I've extracted {field_count} field{'s' if field_count != 1 else ''} from the document and updated the form."
            await websocket.send_json({
                "type": "chat_response",
                "content": content,
                "timestamp": None
            })

    except Exception as e:
        logger.error(f"Error extracting form fields: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": f"Failed to extract form fields: {str(e)}",
            "timestamp": None
        })


async def handle_anonymization(
    websocket: WebSocket,
    case_id: str,
    message: Dict[str, Any]
) -> None:
    """
    Handle document anonymization request.

    Processes the anonymization request by calling the external anonymization
    service and returns the result with the path to the anonymized file.

    Args:
        websocket: The WebSocket connection.
        case_id: The case ID.
        message: The anonymization request message containing filePath.
    """
    file_path = message.get("filePath")
    folder_id = message.get("folderId")
    document_id = message.get("documentId")  # S5-006: Get documentId for render registration
    language = message.get("language", "de")  # S5-014: Get language for response messages

    logger.info(f"Processing anonymization request for case {case_id}, file: {file_path}, documentId: {document_id}, language: {language}")

    # Validate file path
    if not file_path:
        await websocket.send_json({
            "type": "anonymization_complete",
            "originalPath": "",
            "anonymizedPath": None,
            "detectionsCount": 0,
            "success": False,
            "error": "No file path provided",
            "timestamp": None
        })
        return

    # Check if file format is supported
    if not is_supported_format(file_path):
        await websocket.send_json({
            "type": "anonymization_complete",
            "originalPath": file_path,
            "anonymizedPath": None,
            "detectionsCount": 0,
            "success": False,
            "error": "Unsupported file format. Only image files (PNG, JPG, etc.) can be anonymized.",
            "timestamp": None
        })
        return

    try:
        # S5-006: Call anonymization tool with render registration
        result = await anonymize_document(
            file_path,
            document_id=document_id,
            register_render=bool(document_id)  # Only register if documentId provided
        )

        # S5-006: Send anonymization result with render metadata
        # Include detection labels and coordinates for frontend display
        await websocket.send_json({
            "type": "anonymization_complete",
            "originalPath": result.original_path,
            "anonymizedPath": result.anonymized_path,
            "detectionsCount": result.detections_count,
            "detectionLabels": result.detection_labels or [],  # List of field names
            "detections": result.detections or {},  # Full detection data with coordinates
            "success": result.success,
            "error": result.error,
            "timestamp": None,
            "renderMetadata": result.render_metadata,  # S5-006: Include render metadata
            "documentId": document_id  # S5-006: Echo back documentId
        })

        # Also send a chat message about the result with labels list
        # S5-014: Use language-specific messages
        if result.success:
            labels = result.detection_labels or []
            count = result.detections_count

            if language == 'de':
                # German messages
                labels_header = "**Anonymisierte Felder:**"
                if count == 1:
                    main_msg = f"Dokument erfolgreich anonymisiert. {count} personenbezogenes Feld gefunden und maskiert."
                else:
                    main_msg = f"Dokument erfolgreich anonymisiert. {count} personenbezogene Felder gefunden und maskiert."
                saved_msg = "Die anonymisierte Version wurde gespeichert."
            else:
                # English messages (default)
                labels_header = "**Anonymized fields:**"
                main_msg = f"Document anonymized successfully. Found and masked {count} PII field{'s' if count != 1 else ''}."
                saved_msg = "The anonymized version has been saved."

            labels_text = ""
            if labels:
                labels_text = f"\n\n{labels_header}\n" + "\n".join(f"• {label}" for label in labels)

            await websocket.send_json({
                "type": "chat_response",
                "content": f"{main_msg}{labels_text}\n\n{saved_msg}",
                "timestamp": None
            })
        else:
            if language == 'de':
                error_msg = f"Anonymisierung fehlgeschlagen: {result.error}"
            else:
                error_msg = f"Anonymization failed: {result.error}"

            await websocket.send_json({
                "type": "chat_response",
                "content": error_msg,
                "timestamp": None
            })

    except Exception as e:
        logger.error(f"Error during anonymization: {str(e)}")
        await websocket.send_json({
            "type": "anonymization_complete",
            "originalPath": file_path,
            "anonymizedPath": None,
            "detectionsCount": 0,
            "success": False,
            "error": f"Anonymization failed: {str(e)}",
            "timestamp": None
        })


async def handle_translation(
    websocket: WebSocket,
    case_id: str,
    message: Dict[str, Any]
) -> None:
    """
    Handle document translation request (S5-004, S5-008).

    Processes the translation request by calling the translation service
    and returns the result with render metadata for the translated file.

    Args:
        websocket: The WebSocket connection.
        case_id: The case ID.
        message: The translation request message containing filePath, targetLanguage, documentId.
    """
    file_path = message.get("filePath")
    target_lang = message.get("targetLanguage", "de")  # Default to German
    source_lang = message.get("sourceLanguage", "auto")  # Auto-detect by default
    document_id = message.get("documentId")  # S5-006: Get documentId for render registration

    logger.info(f"Processing translation request for case {case_id}, file: {file_path}, target: {target_lang}")

    # Validate file path
    if not file_path:
        await websocket.send_json({
            "type": "translation_complete",
            "originalPath": "",
            "translatedPath": None,
            "success": False,
            "error": "No file path provided",
            "timestamp": None
        })
        return

    try:
        from backend.services.translation_service import get_translation_service
        from backend.services.file_service import add_document_render

        translation_service = get_translation_service()

        # Determine file type and route to appropriate translation method
        file_extension = Path(file_path).suffix.lower()

        if file_extension == '.eml':
            # S5-008: Translate email
            result = await translation_service.translate_email(
                file_path,
                target_lang=target_lang,
                source_lang=source_lang
            )
        else:
            # For now, only emails are supported
            await websocket.send_json({
                "type": "translation_complete",
                "originalPath": file_path,
                "translatedPath": None,
                "success": False,
                "error": "Translation currently only supports .eml files. PDF and image translation coming soon.",
                "timestamp": None
            })
            return

        # S5-006: Register as render if document_id provided
        render_metadata = None
        if result.success and result.translated_path and document_id:
            try:
                render_metadata = add_document_render(
                    document_id=document_id,
                    render_type=f'translated',
                    file_path=result.translated_path,
                    metadata={"language": target_lang}
                )
                logger.info(f"Registered translated render: {render_metadata['id']}")
            except Exception as e:
                logger.warning(f"Failed to register translation render: {e}")
                # Continue even if render registration fails

        # S5-006: Send translation result with render metadata
        await websocket.send_json({
            "type": "translation_complete",
            "originalPath": result.original_path,
            "translatedPath": result.translated_path,
            "sourceLanguage": result.source_language,
            "targetLanguage": result.target_language,
            "success": result.success,
            "error": result.error,
            "timestamp": None,
            "renderMetadata": render_metadata,  # S5-006: Include render metadata
            "documentId": document_id  # S5-006: Echo back documentId
        })

        # Also send a chat message about the result
        if result.success:
            await websocket.send_json({
                "type": "chat_response",
                "content": f"Document translated successfully to {target_lang.upper()}. The translated version has been saved as a new render.",
                "timestamp": None
            })
        else:
            await websocket.send_json({
                "type": "chat_response",
                "content": f"Translation failed: {result.error}",
                "timestamp": None
            })

    except Exception as e:
        logger.error(f"Error during translation: {str(e)}")
        await websocket.send_json({
            "type": "translation_complete",
            "originalPath": file_path,
            "translatedPath": None,
            "success": False,
            "error": f"Translation failed: {str(e)}",
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


@router.post("/api/chat/clear/{case_id}")
async def clear_conversation_history(case_id: str):
    """
    Clear conversation history for a specific case (S5-010).

    This endpoint clears all stored conversation history for the specified case.
    Only works when ENABLE_CHAT_HISTORY is enabled.

    Args:
        case_id: The case ID (e.g., "ACTE-2024-001") to clear history for.

    Returns:
        JSONResponse: Success/failure status with details.

    Example:
        POST /api/chat/clear/ACTE-2024-001
        Response: {"success": true, "case_id": "ACTE-2024-001", "messages_cleared": 5}
    """
    try:
        if not ENABLE_CHAT_HISTORY:
            return JSONResponse(
                content={
                    "success": False,
                    "case_id": case_id,
                    "messages_cleared": 0,
                    "message": "Chat history feature is disabled"
                },
                status_code=400
            )

        # Get conversation manager
        conversation_manager = get_conversation_manager()

        # Clear conversation history
        messages_cleared = conversation_manager.clear_conversation(case_id)

        logger.info(f"Cleared conversation history for case {case_id} ({messages_cleared} messages)")

        return JSONResponse(
            content={
                "success": True,
                "case_id": case_id,
                "messages_cleared": messages_cleared,
                "message": f"Successfully cleared {messages_cleared} message(s) from conversation history"
            },
            status_code=200
        )

    except Exception as e:
        logger.error(f"Error clearing conversation history for case {case_id}: {str(e)}")
        return JSONResponse(
            content={
                "success": False,
                "case_id": case_id,
                "messages_cleared": 0,
                "error": str(e)
            },
            status_code=500
        )
