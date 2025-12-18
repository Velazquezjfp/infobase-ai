"""
Form Parser Tool for Document Data Extraction.

This module provides tools for extracting structured data from document text
and mapping it to form field schemas. Used by the AI agent to automatically
populate form fields based on document content.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


def parse_document_to_form(
    document_text: str,
    form_schema: List[Dict[str, Any]]
) -> Dict[str, str]:
    """
    Extract form field values from document text based on form schema.

    This function serves as a wrapper that prepares the document and schema
    for the AI agent to process. The actual extraction is performed by the
    Gemini AI service using the prepared prompt.

    Args:
        document_text: The text content of the document to parse.
        form_schema: List of form field definitions with structure:
            [{"id": "name", "label": "Full Name", "type": "text", "required": True}, ...]

    Returns:
        Dict[str, str]: Mapping of field IDs to extracted values.
            Example: {"name": "John Doe", "birthDate": "1990-05-15"}

    Raises:
        ValueError: If document_text is empty or form_schema is invalid.
    """
    if not document_text or not document_text.strip():
        raise ValueError("Document text cannot be empty")

    if not form_schema or not isinstance(form_schema, list):
        raise ValueError("Form schema must be a non-empty list")

    logger.info(f"Parsing document (length: {len(document_text)}) for {len(form_schema)} fields")

    # This function prepares the extraction request
    # The actual AI-powered extraction happens in the Gemini service
    # when this information is passed as part of the chat message

    # For now, return the schema structure that will be used by the AI
    # The WebSocket handler will call Gemini with this information
    return {
        "document_text": document_text,
        "form_schema": form_schema,
        "instruction": "extract_form_fields"
    }


def build_extraction_prompt(
    document_text: str,
    form_schema: List[Dict[str, Any]]
) -> str:
    """
    Build a prompt for AI-powered form field extraction.

    Creates a structured prompt that instructs the AI to extract specific
    field values from the document text according to the form schema.

    Args:
        document_text: The document content to extract data from.
        form_schema: The form field definitions.

    Returns:
        str: A formatted prompt for the AI model.
    """
    prompt_parts = [
        "# Task: Extract Form Field Values",
        "",
        "Extract the following form field values from the provided document text.",
        "Return the results in JSON format with field IDs as keys.",
        "",
        "## Form Fields to Extract:",
        ""
    ]

    # Add field definitions
    for field in form_schema:
        field_id = field.get("id", "")
        field_label = field.get("label", "")
        field_type = field.get("type", "text")
        field_required = field.get("required", False)

        prompt_parts.append(f"- {field_id} ({field_label})")
        prompt_parts.append(f"  Type: {field_type}")
        prompt_parts.append(f"  Required: {'Yes' if field_required else 'No'}")
        prompt_parts.append("")

    prompt_parts.extend([
        "## Document Content:",
        "",
        document_text,
        "",
        "## Instructions:",
        "1. Extract values for each field from the document",
        "2. For date fields, convert to ISO format (YYYY-MM-DD)",
        "3. For select fields, match to the closest valid option",
        "4. Return only fields where data was found",
        "5. Format response as JSON: {\"field_id\": \"extracted_value\", ...}",
        "",
        "Return only the JSON object, no additional text."
    ])

    return "\n".join(prompt_parts)


def validate_form_schema(form_schema: List[Dict[str, Any]]) -> bool:
    """
    Validate that the form schema has the required structure.

    Checks that each field in the schema has the minimum required properties.

    Args:
        form_schema: The form schema to validate.

    Returns:
        bool: True if schema is valid, False otherwise.
    """
    if not isinstance(form_schema, list):
        return False

    required_keys = {"id", "label", "type"}

    for field in form_schema:
        if not isinstance(field, dict):
            return False
        if not required_keys.issubset(field.keys()):
            return False

    return True


def parse_extraction_result(
    ai_response: str,
    form_schema: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Parse the AI's extraction result and format it for frontend consumption.

    Converts the AI's JSON response into a standardized format with
    extracted values and confidence scores.

    Args:
        ai_response: The JSON string from the AI containing extracted values.
        form_schema: The original form schema for validation.

    Returns:
        Dict[str, Any]: Formatted result with structure:
            {
                "updates": {"field_id": "value", ...},
                "confidence": {"field_id": 0.9, ...}
            }
    """
    import json

    try:
        # Parse AI response as JSON
        extracted_data = json.loads(ai_response)

        # Validate extracted fields against schema
        valid_field_ids = {field["id"] for field in form_schema}

        updates = {}
        confidence = {}

        for field_id, value in extracted_data.items():
            if field_id in valid_field_ids:
                updates[field_id] = str(value) if value is not None else ""
                # Default confidence - could be enhanced with AI confidence scores
                confidence[field_id] = 0.85

        logger.info(f"Successfully parsed {len(updates)} field values")

        return {
            "updates": updates,
            "confidence": confidence
        }

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response as JSON: {str(e)}")
        return {
            "updates": {},
            "confidence": {}
        }
    except Exception as e:
        logger.error(f"Error parsing extraction result: {str(e)}")
        return {
            "updates": {},
            "confidence": {}
        }
