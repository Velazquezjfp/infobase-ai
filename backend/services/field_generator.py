"""
Field Generator Service for NLP-based Form Field Creation.

This module provides AI-powered form field generation from natural language
prompts. It uses the Gemini API to interpret user requests and generates
SHACL-compliant form field specifications.

Example usage:
    service = FieldGeneratorService()
    field = await service.generate_field("Add a dropdown for marital status with options single, married, divorced")
    # Returns FormFieldSpec with SHACL metadata
"""

import json
import logging
import re
import uuid
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any

from backend.schemas import (
    SHACLPropertyShape,
    build_field_context,
    get_schema_org_property,
    get_xsd_datatype,
)
from backend.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


@dataclass
class FormFieldSpec:
    """
    Specification for a generated form field.

    Attributes:
        id: Unique identifier for the field
        label: Human-readable label
        type: Field type (text, date, select, textarea)
        value: Default value (usually empty)
        options: List of options for select fields
        required: Whether the field is required
        shacl_metadata: SHACL/JSON-LD semantic metadata
    """
    id: str
    label: str
    type: str
    value: str = ""
    options: Optional[List[str]] = None
    required: bool = False
    shacl_metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "id": self.id,
            "label": self.label,
            "type": self.type,
            "value": self.value,
            "required": self.required,
        }
        if self.options:
            result["options"] = self.options
        if self.shacl_metadata:
            result["shaclMetadata"] = self.shacl_metadata
        return result


# Prompt template for field generation
FIELD_GENERATION_PROMPT = """You are an expert form field generator for a case management system.
Analyze the user's natural language request and generate a form field specification.

User Request: {prompt}

Generate a JSON response with the following structure:
{{
    "label": "Human-readable field label",
    "type": "text|date|select|textarea",
    "required": true|false,
    "options": ["option1", "option2"] // Only for select type
}}

Rules:
1. For "dropdown", "select", "choice", "list of options" → type: "select"
2. For "date", "birthday", "expiry date", "when" → type: "date"
3. For "long text", "description", "comments", "notes", "paragraph" → type: "textarea"
4. For everything else → type: "text"
5. If user says "required", "mandatory", "must have" → required: true
6. Extract options from phrases like "with options X, Y, Z" or "choices: A, B, C"
7. Generate a clear, professional label from the request
8. Support both English and German prompts

Return ONLY the JSON object, no explanations.
"""


class FieldGeneratorService:
    """
    Service for generating form fields from natural language prompts.

    Uses the Gemini API to interpret user requests and generates
    SHACL-compliant form field specifications.
    """

    def __init__(self):
        """Initialize the field generator with Gemini service."""
        self._gemini_service = GeminiService()

    async def generate_field(self, prompt: str) -> FormFieldSpec:
        """
        Generate a form field from a natural language prompt.

        Args:
            prompt: Natural language description of the desired field
                   Examples:
                   - "Add a text field for passport number"
                   - "Add dropdown for education level with options high school, bachelor, master"
                   - "I need a required date field for visa expiry"

        Returns:
            FormFieldSpec: Generated field specification with SHACL metadata

        Raises:
            ValueError: If the prompt is empty or field generation fails
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        logger.info(f"Generating field from prompt: {prompt[:100]}...")

        try:
            # First, try rule-based extraction for common patterns
            field_spec = self._try_rule_based_extraction(prompt)

            if field_spec is None:
                # Fall back to AI-based generation
                field_spec = await self._generate_with_ai(prompt)

            # Generate unique ID
            field_spec.id = self._generate_field_id(field_spec.label)

            # Add SHACL metadata
            field_spec.shacl_metadata = build_field_context(
                field_type=field_spec.type,
                field_label=field_spec.label,
                required=field_spec.required,
                options=field_spec.options,
            )

            logger.info(
                f"Generated field: label='{field_spec.label}', "
                f"type='{field_spec.type}', required={field_spec.required}"
            )

            return field_spec

        except Exception as e:
            logger.error(f"Error generating field: {str(e)}")
            raise ValueError(f"Failed to generate field: {str(e)}")

    def _try_rule_based_extraction(self, prompt: str) -> Optional[FormFieldSpec]:
        """
        Try to extract field specification using rule-based patterns.

        This provides faster responses for common, unambiguous requests.

        Args:
            prompt: User's natural language prompt

        Returns:
            FormFieldSpec if extraction succeeds, None otherwise
        """
        prompt_lower = prompt.lower()

        # Detect field type
        field_type = "text"  # default

        if any(word in prompt_lower for word in ["dropdown", "select", "choice", "auswahl", "liste"]):
            field_type = "select"
        elif any(word in prompt_lower for word in ["date", "datum", "birthday", "geburtstag", "expiry", "ablauf"]):
            field_type = "date"
        elif any(word in prompt_lower for word in ["textarea", "long text", "description", "beschreibung", "notes", "notizen", "paragraph"]):
            field_type = "textarea"

        # Detect required
        required = any(word in prompt_lower for word in ["required", "mandatory", "pflicht", "muss", "erforderlich"])

        # Extract label - look for "for X" or "für X" patterns
        label = None
        label_patterns = [
            r"(?:field|feld)\s+(?:for|für)\s+['\"]?([^'\"]+?)['\"]?(?:\s+with|\s+mit|$)",
            r"(?:add|hinzufügen|erstellen?)\s+(?:a\s+)?(?:\w+\s+)?(?:field|feld)?\s*(?:for|für)\s+['\"]?([^'\"]+?)['\"]?(?:\s+with|\s+mit|$)",
            r"(?:dropdown|select|choice|auswahl)\s+(?:for|für)\s+['\"]?([^'\"]+?)['\"]?(?:\s+with|\s+mit|$)",
            r"(?:date|datum)\s+(?:field|feld)?\s*(?:for|für)\s+['\"]?([^'\"]+?)['\"]?(?:\s+with|\s+mit|$)",
        ]

        for pattern in label_patterns:
            match = re.search(pattern, prompt_lower, re.IGNORECASE)
            if match:
                label = match.group(1).strip()
                # Title case the label
                label = label.title()
                break

        # If no label found with patterns, try to extract key noun phrase
        if not label:
            # Simple extraction: take the main subject after "add" or similar
            simple_match = re.search(
                r"(?:add|create|need|want|hinzufügen|erstellen|brauche)\s+(?:a\s+)?(?:required\s+)?(?:\w+\s+)?(?:field\s+)?(?:for\s+)?(.+?)(?:\s+with\s+options|\s+mit\s+optionen|$)",
                prompt_lower
            )
            if simple_match:
                label = simple_match.group(1).strip()
                # Clean up common words
                label = re.sub(r'\b(field|feld|text|date|datum|dropdown|select)\b', '', label, flags=re.IGNORECASE)
                label = label.strip()
                if label:
                    label = label.title()

        # If still no label, we can't do rule-based extraction
        if not label or len(label) < 2:
            return None

        # Extract options for select fields
        options = None
        if field_type == "select":
            options_patterns = [
                r"(?:with\s+options?|options?:|choices?:|mit\s+optionen?|optionen?:)\s*['\"]?([^'\"]+)['\"]?",
                r"(?:with\s+options?|options?:|choices?:|mit\s+optionen?|optionen?:)\s*(.+)$",
            ]
            for pattern in options_patterns:
                match = re.search(pattern, prompt, re.IGNORECASE)
                if match:
                    options_str = match.group(1)
                    # Split by comma, "and", "or", "und", "oder"
                    options = re.split(r'\s*[,]\s*|\s+and\s+|\s+or\s+|\s+und\s+|\s+oder\s+', options_str)
                    options = [opt.strip().title() for opt in options if opt.strip()]
                    if len(options) < 2:
                        options = None  # Need at least 2 options
                    break

            # If no options found for select, return None to use AI
            if not options:
                return None

        return FormFieldSpec(
            id="",  # Will be generated
            label=label,
            type=field_type,
            required=required,
            options=options,
        )

    async def _generate_with_ai(self, prompt: str) -> FormFieldSpec:
        """
        Generate field specification using Gemini AI.

        Args:
            prompt: User's natural language prompt

        Returns:
            FormFieldSpec: AI-generated field specification

        Raises:
            ValueError: If AI response cannot be parsed
        """
        full_prompt = FIELD_GENERATION_PROMPT.format(prompt=prompt)

        response = await self._gemini_service.generate_response(
            prompt=full_prompt,
            stream=False
        )

        # Parse the JSON response
        try:
            # Clean up the response (remove markdown code blocks if present)
            response_text = response.strip()
            if response_text.startswith("```"):
                response_text = re.sub(r'^```\w*\n?', '', response_text)
                response_text = re.sub(r'\n?```$', '', response_text)

            field_data = json.loads(response_text)

            return FormFieldSpec(
                id="",  # Will be generated
                label=field_data.get("label", "New Field"),
                type=field_data.get("type", "text"),
                required=field_data.get("required", False),
                options=field_data.get("options"),
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {response}")
            raise ValueError(f"Failed to parse AI response: {str(e)}")

    def _generate_field_id(self, label: str) -> str:
        """
        Generate a unique field ID from the label.

        Args:
            label: Field label

        Returns:
            Unique field ID (snake_case with suffix)
        """
        # Convert to snake_case
        safe_id = re.sub(r'[^a-zA-Z0-9\s]', '', label.lower())
        safe_id = re.sub(r'\s+', '_', safe_id.strip())

        # Add short UUID suffix for uniqueness
        suffix = uuid.uuid4().hex[:6]

        return f"{safe_id}_{suffix}"

    def validate_field_spec(self, field_spec: FormFieldSpec) -> List[str]:
        """
        Validate a field specification.

        Args:
            field_spec: Field specification to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not field_spec.label or len(field_spec.label.strip()) < 2:
            errors.append("Label must be at least 2 characters")

        if field_spec.type not in ["text", "date", "select", "textarea"]:
            errors.append(f"Invalid field type: {field_spec.type}")

        if field_spec.type == "select":
            if not field_spec.options or len(field_spec.options) < 2:
                errors.append("Select fields must have at least 2 options")

        return errors


# Singleton instance
_field_generator_instance: Optional[FieldGeneratorService] = None


def get_field_generator() -> FieldGeneratorService:
    """
    Get the singleton FieldGeneratorService instance.

    Returns:
        FieldGeneratorService: The singleton instance
    """
    global _field_generator_instance
    if _field_generator_instance is None:
        _field_generator_instance = FieldGeneratorService()
    return _field_generator_instance
