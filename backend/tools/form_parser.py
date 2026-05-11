"""
Form Parser Tool for Document Data Extraction.

This module provides tools for extracting structured data from document text
and mapping it to form field schemas. Used by the AI agent to automatically
populate form fields based on document content.
"""

import logging
from typing import Dict, List, Any, Optional

from backend.utils.llm_output import (
    JSON_ONLY_HEADER,
    extract_json_from_llm_response,
)

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
    # Log the form schema for debugging
    logger.info(f"Building extraction prompt for {len(form_schema)} fields")
    for idx, field in enumerate(form_schema[:3]):  # Log first 3 fields
        logger.info(f"  Field[{idx}]: id={field.get('id')}, label={field.get('label')}, shaclMetadata keys={list(field.get('shaclMetadata', {}).keys())}")

    prompt_parts = [
        "# Task: Extract Form Field Values",
        "",
        JSON_ONLY_HEADER,
        # S001-NFR-008: example output uses ABSTRACT placeholders, never
        # concrete names/dates. Small models (llama3.2:1b) will otherwise
        # copy "Ahmad Ali" / "1990-05-15" verbatim into the output when the
        # source document doesn't contain the fields — turning extraction
        # into plagiarism of the prompt.
        "Example output schema: {\"<field_id>\": \"<extracted_value>\", ...}",
        "",
        "CRITICAL: Extract ONLY values that are LITERALLY present in the document",
        "text below. Do NOT invent, guess, or copy values from this prompt's",
        "examples. If a field is not in the document, OMIT it from the JSON.",
        "If NO fields are found, return exactly: {}",
        "",
        "Extract the following form field values from the provided document text.",
        "",
        "## Form Fields to Extract:",
        ""
    ]

    # S001-NFR-008: enrich each field with SHACL metadata that's already
    # present in the form schema but was previously dropped. The `sh:description`
    # in particular is the richest semantic signal — explains the *intent* of
    # the field so the model can semantically match (e.g. map email content
    # to `reasonForApplication`). Aligned with the blueprint in
    # `ontology_shacl_material/prompt_example.md`.
    for field in form_schema:
        field_id = field.get("id", "")
        field_label = field.get("label", "")
        field_type = field.get("type", "text")
        field_required = field.get("required", False)
        field_options = field.get("options", [])

        shacl_metadata = field.get("shaclMetadata", {})
        sh_path = shacl_metadata.get("sh:path", "")
        sh_description = shacl_metadata.get("sh:description", "")
        sh_datatype = shacl_metadata.get("sh:datatype", "")
        sh_min_count = shacl_metadata.get("sh:minCount")
        sh_max_count = shacl_metadata.get("sh:maxCount")

        logger.debug(
            f"Field {field_id}: path={sh_path}, datatype={sh_datatype}, "
            f"has_description={bool(sh_description)}"
        )

        prompt_parts.append(f"- {field_id}")
        prompt_parts.append(f"  Label: {field_label}")

        # The SEMANTIC INTENT of the field. Most useful signal for the LLM.
        if sh_description:
            prompt_parts.append(f"  Definition: {sh_description}")

        # Type with optional XSD specifier (helps the LLM with formats).
        if sh_datatype:
            prompt_parts.append(f"  Type: {field_type} ({sh_datatype})")
        else:
            prompt_parts.append(f"  Type: {field_type}")

        prompt_parts.append(f"  Required: {'Yes' if field_required else 'No'}")

        # Cardinality (rarely useful for extraction but cheap to include).
        if sh_min_count is not None or sh_max_count is not None:
            mn = sh_min_count if sh_min_count is not None else 0
            mx = sh_max_count if sh_max_count is not None else "∞"
            prompt_parts.append(f"  Cardinality: {mn}..{mx}")

        # Ontology link (full path, not the truncated tail).
        if sh_path:
            prompt_parts.append(f"  Ontology: {sh_path}")

        # Options for select fields.
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
        "- For EACH field, use ALL available hints to find matching data:",
        "  1. The field Label (e.g., 'Geburtsort', 'Full Name')",
        "  2. The Semantic property (e.g., 'geburtsort', 'name', 'birthDate')",
        "  3. The field ID (e.g., 'fullName', 'passport_number')",
        "- The Semantic property indicates the MEANING of the field - use it to understand what data to look for",
        "- Return only fields where data was clearly found",
        "- If data is ambiguous or unclear, omit the field rather than guessing",
        "",
        "### 2. Multilingual and Semantic Matching:",
        "- Documents may be in German, English, Arabic, or other languages",
        "- Use the Semantic property to UNDERSTAND what the field represents, then search for equivalent terms",
        "- Examples of semantic interpretation:",
        "  * Semantic 'geburtsort' or 'birthPlace' → look for: place of birth, Geburtsort, lieu de naissance, مكان الولادة",
        "  * Semantic 'name' or 'fullName' → look for: Name, Full Name, Vollständiger Name, الاسم",
        "  * Semantic 'geburtsdatum' or 'birthDate' → look for: date of birth, Geburtsdatum, تاريخ الميلاد",
        "- The semantic property may be in ANY language (German, English, etc.) - interpret its meaning",
        "- Search the document for data that matches the CONCEPT, not just the exact word",
        "- Extract the actual data value, not the label",
        "",
        "### 3. Date Format Conversion:",
        "- Input dates may be in formats: DD.MM.YYYY / DD/MM/YYYY / DD-MM-YYYY",
        "- ALWAYS convert to ISO format YYYY-MM-DD",
        "- Validate dates are realistic (year 1900-2030 for birthdates)",
        "- Conversion pattern: DD.MM.YYYY → YYYY-MM-DD (rearrange components)",
        # S001-NFR-008: removed concrete date examples ('15.05.1990' → '1990-05-15')
        # because 1B models copied them verbatim into the response when source
        # documents had no birthDate field.
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
        "- Format: {\"<field_id>\": \"<extracted_value>\", ...}",
        "- Use field IDs as keys (not labels)",
        "- All values must be strings",
        "- Do not include explanations, confidence scores, or additional text",
        "- If no fields are found in the document, return exactly: {}",
        "",
        "## Important:",
        "Return ONLY the JSON object with extracted values. No markdown, no code blocks, no additional text.",
        "Use ONLY values from the document text above — never copy names, dates,",
        "or country names from this prompt's instructions/examples."
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


def compare_values(
    current_values: Dict[str, str],
    extracted_values: Dict[str, str],
    confidence_scores: Dict[str, float]
) -> Dict[str, Any]:
    """
    Compare current form values with extracted values to categorize updates.

    Categorizes extracted values into three groups:
    - direct_updates: Fields that are empty (fill directly without suggestion)
    - suggestions: Fields with different values that need user approval
    - ignored: Fields with identical values (no action needed)

    Args:
        current_values: Current form field values {"field_id": "value", ...}
        extracted_values: AI-extracted values {"field_id": "value", ...}
        confidence_scores: Confidence scores for each extracted value

    Returns:
        Dict[str, Any]: Categorized results with structure:
            {
                "direct_updates": {"field_id": "value", ...},
                "suggestions": {
                    "field_id": {
                        "value": "suggested_value",
                        "confidence": 0.85,
                        "current": "current_value"
                    }, ...
                },
                "ignored": ["field_id1", "field_id2"]
            }
    """
    direct_updates = {}
    suggestions = {}
    ignored = []

    for field_id, extracted_value in extracted_values.items():
        current_value = current_values.get(field_id, "").strip()
        extracted_value_clean = extracted_value.strip()
        confidence = confidence_scores.get(field_id, 0.85)

        # Case 1: Empty field - fill directly without suggestion
        if not current_value:
            direct_updates[field_id] = extracted_value_clean
            logger.debug(f"Field '{field_id}' is empty, will fill directly")

        # Case 2: Identical values - ignore
        elif current_value.lower() == extracted_value_clean.lower():
            ignored.append(field_id)
            logger.debug(f"Field '{field_id}' has identical value, ignoring")

        # Case 3: Different values - create suggestion
        else:
            suggestions[field_id] = {
                "value": extracted_value_clean,
                "confidence": confidence,
                "current": current_value
            }
            logger.debug(f"Field '{field_id}' differs, creating suggestion")

    logger.info(
        f"Value comparison: {len(direct_updates)} direct updates, "
        f"{len(suggestions)} suggestions, {len(ignored)} ignored"
    )

    return {
        "direct_updates": direct_updates,
        "suggestions": suggestions,
        "ignored": ignored
    }


def _value_grounded_in_document(value: str, document_text: str, field_type: str) -> bool:
    """
    S001-NFR-008: post-extraction grounding check.

    Returns True only if the extracted value can plausibly be located in the
    source document. This is the structural guardrail against model
    hallucination — no matter what the prompt says or what priors the model
    has (e.g. defaulting birthDate to "1990-01-01"), if the value isn't in
    the document we drop the field.

    Lenient by design: dates are normalized across common formats; multi-word
    text matches if a majority of words appear; case-insensitive throughout.
    """
    if not value or not document_text:
        return False

    value_lower = value.strip().lower()
    doc_lower = document_text.lower()

    # Select values are validated against the field's options, not the doc.
    if field_type == "select":
        return True

    # Date: try several representations the source document might use.
    if field_type == "date":
        import re
        m = re.match(r'(\d{4})-(\d{2})-(\d{2})', value_lower)
        if m:
            year, month, day = m.groups()
            day_stripped = day.lstrip('0') or '0'
            month_stripped = month.lstrip('0') or '0'
            candidates = [
                f"{day}.{month}.{year}",
                f"{day}/{month}/{year}",
                f"{day}-{month}-{year}",
                f"{day_stripped}.{month_stripped}.{year}",
                f"{day_stripped}/{month_stripped}/{year}",
                f"{year}-{month}-{day}",
                f"{year}/{month}/{day}",
                f"{day} {month} {year}",
            ]
            return any(c in doc_lower for c in candidates)
        # Date value isn't ISO — fall back to substring
        return value_lower in doc_lower

    # Text / textarea: substring or word-majority match.
    if value_lower in doc_lower:
        return True
    words = [w for w in value_lower.split() if len(w) >= 2]
    if not words:
        return value_lower in doc_lower
    present = sum(1 for w in words if w in doc_lower)
    # Allow if at least 60% of meaningful words show up in the document
    return present / len(words) >= 0.6


def parse_extraction_result(
    ai_response: str,
    form_schema: List[Dict[str, Any]],
    current_values: Optional[Dict[str, str]] = None,
    document_text: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Parse the AI's extraction result and format it for frontend consumption.

    Converts the AI's JSON response into a standardized format with
    extracted values and confidence scores. Validates data types and formats.
    When current_values is provided, categorizes results into direct updates
    vs suggestions based on whether fields are empty or already filled.

    Args:
        ai_response: The JSON string from the AI containing extracted values.
        form_schema: The original form schema for validation.
        current_values: Optional dict of current form values for comparison.

    Returns:
        Dict[str, Any]: Formatted result with structure:
            Without current_values:
            {
                "updates": {"field_id": "value", ...},
                "confidence": {"field_id": 0.9, ...}
            }

            With current_values (S5-002):
            {
                "direct_updates": {"field_id": "value", ...},
                "suggestions": {
                    "field_id": {
                        "value": "suggested_value",
                        "confidence": 0.85,
                        "current": "current_value"
                    }, ...
                },
                "ignored": ["field_id1", "field_id2"]
            }
    """
    from datetime import datetime

    try:
        # S001-NFR-007 + S001-NFR-008: shared utility handles code-fence
        # stripping, preamble recovery, and truncation repair (small models
        # generate verbose output that overflows max_output_tokens — repair
        # balances braces/quotes so partial responses still parse).
        extracted_data = extract_json_from_llm_response(
            ai_response, expect="object", repair_truncation=True
        )
        if extracted_data is None:
            return {"updates": {}, "confidence": {}}

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

            # S001-NFR-008: post-extraction grounding. Drop any field whose
            # value cannot be located in the source document — kills
            # hallucinations like the model defaulting birthDate to
            # "1990-01-01" on documents that contain no date at all.
            if document_text is not None:
                if not _value_grounded_in_document(value_str, document_text, field_type):
                    logger.info(
                        f"Dropping field '{field_id}': value {value_str!r} "
                        f"not grounded in document text"
                    )
                    continue

            # Store validated value and confidence
            updates[field_id] = value_str
            confidence[field_id] = field_confidence

        logger.info(f"Successfully parsed {len(updates)} field values (grounded)")

        # S5-002: If current_values provided, categorize into direct updates vs suggestions
        if current_values is not None:
            result = compare_values(current_values, updates, confidence)
            # Also include the full confidence map for reference
            result["all_confidence"] = confidence
            return result
        else:
            # Legacy behavior: return all as updates
            return {
                "updates": updates,
                "confidence": confidence
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
