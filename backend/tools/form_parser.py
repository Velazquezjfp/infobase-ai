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
        field_options = field.get("options", [])

        prompt_parts.append(f"- {field_id} ({field_label})")
        prompt_parts.append(f"  Type: {field_type}")
        prompt_parts.append(f"  Required: {'Yes' if field_required else 'No'}")

        # Include options for select fields
        if field_type == "select" and field_options:
            options_str = ", ".join([f'"{opt}"' for opt in field_options])
            prompt_parts.append(f"  Options: [{options_str}]")

        prompt_parts.append("")

    prompt_parts.extend([
        "## Document Content:",
        "",
        document_text,
        "",
        "## Extraction Instructions:",
        "",
        "### 1. Field Extraction Rules:",
        "- Extract values for each field from the document content",
        "- Match field labels semantically (e.g., 'Full Name' matches 'Name:', 'Applicant:', 'Person:')",
        "- Return only fields where data was clearly found",
        "- If data is ambiguous or unclear, omit the field rather than guessing",
        "",
        "### 2. Multilingual Document Handling:",
        "- Documents may be in German or English",
        "- Common German-English field mappings:",
        "  * 'Vorname' or 'Rufname' → firstName",
        "  * 'Nachname' or 'Familienname' → lastName",
        "  * 'Name' or 'Vollständiger Name' → fullName",
        "  * 'Geburtsdatum' or 'Geboren' → birthDate",
        "  * 'Geburtsort' → placeOfBirth",
        "  * 'Staatsangehörigkeit' or 'Nationalität' → nationality",
        "  * 'Passnummer' or 'Reisepassnummer' → passportNumber",
        "  * 'Adresse' or 'Anschrift' → address",
        "- Extract the actual data value, not the label",
        "",
        "### 3. Date Format Conversion:",
        "- Input dates may be in German format: DD.MM.YYYY (e.g., 15.05.1990)",
        "- Input dates may also be: DD/MM/YYYY, DD-MM-YYYY, or other variants",
        "- ALWAYS convert to ISO format: YYYY-MM-DD (e.g., 1990-05-15)",
        "- Validate dates are realistic (year between 1900-2030 for birthdates)",
        "- Examples:",
        "  * '15.05.1990' → '1990-05-15'",
        "  * '01/12/1985' → '1985-12-01'",
        "  * 'Born: 20.03.2000' → '2000-03-20'",
        "",
        "### 4. Select Field Matching:",
        "- For fields with predefined options, match document text to the closest option",
        "- Use fuzzy matching: 'intensive course' should match option 'Intensive'",
        "- Case-insensitive matching: 'EVENING' matches 'Evening'",
        "- Partial word matching: 'weekend classes' matches 'Weekend'",
        "- If no clear match found, omit the field",
        "",
        "### 5. Text Field Extraction:",
        "- Extract complete values (e.g., full name, not just first name)",
        "- Preserve special characters: umlauts (ä, ö, ü), accents (é, ç), hyphens, apostrophes",
        "- Trim whitespace from extracted values",
        "- For textarea fields, preserve line breaks if meaningful",
        "",
        "### 6. Output Format:",
        "- Return ONLY a valid JSON object",
        "- Format: {\"field_id\": \"extracted_value\", \"another_field_id\": \"another_value\"}",
        "- Use field IDs as keys (not labels)",
        "- All values must be strings",
        "- Do not include explanations, confidence scores, or additional text",
        "- Example: {\"fullName\": \"Ahmad Ali\", \"birthDate\": \"1990-05-15\", \"countryOfOrigin\": \"Afghanistan\"}",
        "",
        "## Important:",
        "Return ONLY the JSON object with extracted values. No markdown, no code blocks, no additional text."
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
    extracted values and confidence scores. Validates data types and formats.

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
    import re
    from datetime import datetime

    try:
        # Clean response - remove markdown code blocks if present
        cleaned_response = ai_response.strip()
        if cleaned_response.startswith("```"):
            # Extract JSON from code block
            lines = cleaned_response.split("\n")
            cleaned_response = "\n".join(lines[1:-1]) if len(lines) > 2 else cleaned_response
            cleaned_response = cleaned_response.replace("```json", "").replace("```", "").strip()

        # Parse AI response as JSON
        extracted_data = json.loads(cleaned_response)

        # Build field schema lookup
        field_schema_map = {field["id"]: field for field in form_schema}

        updates = {}
        confidence = {}

        for field_id, value in extracted_data.items():
            if field_id not in field_schema_map:
                logger.warning(f"Extracted field {field_id} not in schema, skipping")
                continue

            field_def = field_schema_map[field_id]
            field_type = field_def.get("type", "text")
            field_options = field_def.get("options", [])

            # Convert value to string
            value_str = str(value).strip() if value is not None else ""

            if not value_str:
                continue

            # Validate and calculate confidence based on field type
            field_confidence = 0.85  # Default confidence

            if field_type == "date":
                # Validate date format (ISO: YYYY-MM-DD)
                if _is_valid_iso_date(value_str):
                    field_confidence = 0.95  # High confidence for valid dates
                else:
                    # Try to parse and convert non-ISO dates
                    converted_date = _convert_to_iso_date(value_str)
                    if converted_date:
                        value_str = converted_date
                        field_confidence = 0.80  # Medium confidence for converted dates
                    else:
                        logger.warning(f"Invalid date format for {field_id}: {value_str}")
                        field_confidence = 0.50  # Low confidence for questionable dates

            elif field_type == "select":
                # Validate against options list
                if field_options:
                    matched_option = _match_select_option(value_str, field_options)
                    if matched_option:
                        value_str = matched_option
                        # Higher confidence for exact matches
                        if value_str.lower() == extracted_data[field_id].lower():
                            field_confidence = 0.95
                        else:
                            field_confidence = 0.80  # Fuzzy match
                    else:
                        logger.warning(f"Value '{value_str}' doesn't match options for {field_id}")
                        field_confidence = 0.40  # Low confidence for non-matching values

            elif field_type == "text":
                # Check if value looks reasonable (not too short or too long)
                if len(value_str) < 2:
                    field_confidence = 0.60  # Low confidence for very short text
                elif len(value_str) > 200:
                    field_confidence = 0.70  # Medium confidence for very long text
                else:
                    field_confidence = 0.90  # High confidence for normal text

            elif field_type == "textarea":
                # Textarea can be longer
                field_confidence = 0.85

            # Store validated value and confidence
            updates[field_id] = value_str
            confidence[field_id] = field_confidence

        logger.info(f"Successfully parsed {len(updates)} field values")

        return {
            "updates": updates,
            "confidence": confidence
        }

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response as JSON: {str(e)}")
        logger.error(f"Response content: {ai_response[:200]}...")
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


def _is_valid_iso_date(date_str: str) -> bool:
    """
    Check if a date string is in valid ISO format (YYYY-MM-DD).

    Args:
        date_str: The date string to validate.

    Returns:
        bool: True if valid ISO date, False otherwise.
    """
    import re
    from datetime import datetime

    iso_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(iso_pattern, date_str):
        return False

    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def _convert_to_iso_date(date_str: str) -> Optional[str]:
    """
    Attempt to convert various date formats to ISO format (YYYY-MM-DD).

    Handles formats like: DD.MM.YYYY, DD/MM/YYYY, DD-MM-YYYY

    Args:
        date_str: The date string to convert.

    Returns:
        Optional[str]: ISO formatted date or None if conversion fails.
    """
    from datetime import datetime

    # Try common European date formats
    formats = [
        "%d.%m.%Y",  # DD.MM.YYYY
        "%d/%m/%Y",  # DD/MM/YYYY
        "%d-%m-%Y",  # DD-MM-YYYY
        "%Y-%m-%d",  # Already ISO
        "%d.%m.%y",  # DD.MM.YY
        "%d/%m/%y",  # DD/MM/YY
    ]

    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None


def _match_select_option(value: str, options: List[str]) -> Optional[str]:
    """
    Find the best matching option from a select field's options list.

    Uses fuzzy matching to handle case differences and partial matches.

    Args:
        value: The extracted value to match.
        options: List of valid option values.

    Returns:
        Optional[str]: The matched option or None if no match found.
    """
    if not value or not options:
        return None

    value_lower = value.lower().strip()

    # Try exact match first (case-insensitive)
    for option in options:
        if option.lower() == value_lower:
            return option

    # Try partial match (value contains option or option contains value)
    for option in options:
        option_lower = option.lower()
        if value_lower in option_lower or option_lower in value_lower:
            return option

    # Try word-based matching (any word in value matches any word in option)
    value_words = set(value_lower.split())
    for option in options:
        option_words = set(option.lower().split())
        if value_words & option_words:  # Intersection of word sets
            return option

    return None
