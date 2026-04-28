"""
SHACL Generator Service for Natural Language Form Modification.

This service handles:
1. Natural language command parsing via Gemini AI
2. Form field modification operations (add, remove, modify, reorder)
3. SHACL PropertyShape generation for individual fields
4. SHACL NodeShape generation for entire forms

Requirement: S5-001 - Natural Language Form Field Modification with SHACL Validation
"""

import logging
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict

from backend.models.shacl_property_shape import SHACLPropertyShape
from backend.schemas.schema_org_mappings import (
    get_schema_org_type,
    get_validation_pattern_for_type,
    infer_field_type_from_label,
    normalize_field_label,
)
from backend.schemas.validation_patterns import ValidationPattern
from backend.services.llm_provider import LLMProvider, get_provider

logger = logging.getLogger(__name__)


@dataclass
class FormField:
    """Form field specification matching frontend FormField interface."""
    id: str
    label: str
    type: str  # text, date, select, textarea
    value: str = ""
    options: Optional[List[str]] = None
    required: bool = False
    validationPattern: Optional[str] = None
    semanticType: Optional[str] = None
    shaclMetadata: Optional[Dict[str, Any]] = None


@dataclass
class FormModificationResult:
    """Result of a form modification operation."""
    fields: List[FormField]
    modifications: List[str]
    shacl_shape: Dict[str, Any]


class SHACLGeneratorService:
    """
    Service for natural language form modification and SHACL generation.

    Uses Gemini AI to interpret natural language commands and automatically
    generates SHACL shapes with schema.org vocabulary for semantic validation.
    """

    def __init__(self) -> None:
        """
        Initialize the SHACL generator.

        Resolves the active LLM provider (S001-F-001); no SDK-specific keys
        are needed at construction time anymore.
        """
        self._provider: LLMProvider = get_provider()
        self._field_id_counter = 0

    def _generate_field_id(self, label: str) -> str:
        """Generate a unique field ID from label."""
        normalized = normalize_field_label(label)
        self._field_id_counter += 1
        return f"{normalized}_{self._field_id_counter}"

    async def parse_nl_command(self, command: str, current_fields: List[FormField]) -> Dict[str, Any]:
        """
        Parse a natural language command to extract modification intent.

        Args:
            command: Natural language command (e.g., "Add an email field for contact email")
            current_fields: Current list of form fields

        Returns:
            Dictionary with:
                - action: "add", "remove", "modify", "reorder", or "clarify"
                - field_label: Label of the field to modify (for add/remove/modify)
                - field_type: Type of field (for add)
                - required: Whether field is required (for add)
                - options: List of options (for add with select type)
                - target_position: Position for reorder
                - clarification: Message if action is "clarify"
        """
        # Build prompt for Gemini
        current_field_list = "\n".join([f"- {f.label} ({f.type})" for f in current_fields])

        prompt = f"""
You are a form modification assistant. Parse the following natural language command and extract the modification intent.

Current form fields:
{current_field_list if current_field_list else "(empty form)"}

User command: "{command}"

Analyze the command and respond with a JSON object containing:
- "action": one of ["add", "remove", "modify", "reorder", "clarify"]
- "field_label": the field label/name (string)
- "field_type": one of ["text", "date", "select", "textarea"] (for add action)
- "required": boolean (for add action, default false)
- "options": list of strings (for add action with select type, optional)
- "clarification": string (only if action is "clarify" - ask for more details)

Rules:
1. For "add" commands:
   - Infer field type from context (email/phone/name → text, birth date → date, notes → textarea, status/level → select)
   - Extract field label from command
   - Detect if field is required from words like "required", "mandatory", "must"
   - For select fields, extract options if mentioned

2. For "remove" commands:
   - Match field label to existing fields (fuzzy match)
   - If no match, set action to "clarify"

3. For "modify" commands:
   - Identify the field to modify and the property to change

4. If the command is ambiguous or lacks information, set action to "clarify" with a helpful message.

Examples:
- "Add an email field for contact email" → {{"action": "add", "field_label": "Contact Email", "field_type": "text", "required": false}}
- "Add a required phone number field" → {{"action": "add", "field_label": "Phone Number", "field_type": "text", "required": true}}
- "Add dropdown for marital status with options single, married, divorced" → {{"action": "add", "field_label": "Marital Status", "field_type": "select", "required": false, "options": ["single", "married", "divorced"]}}
- "Remove the phone number field" → {{"action": "remove", "field_label": "Phone Number"}}
- "Add a field" → {{"action": "clarify", "clarification": "What type of field would you like to add? Please specify (e.g., email, name, date, etc.)"}}

Respond with ONLY the JSON object, no additional text.
"""

        try:
            response_text = await self._provider.generate(
                prompt, temperature=0.1
            )
            response_text = (response_text or "").strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = re.sub(r'^```(?:json)?\s*', '', response_text)
                response_text = re.sub(r'\s*```$', '', response_text)

            parsed = json.loads(response_text)

            logger.info(f"Parsed NL command: {command} → {parsed}")
            return parsed

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            return {
                "action": "clarify",
                "clarification": "I couldn't understand that command. Please try rephrasing."
            }
        except Exception as e:
            logger.error(f"Error parsing NL command: {e}")
            return {
                "action": "clarify",
                "clarification": f"An error occurred: {str(e)}"
            }

    def generate_property_shape(self, field: FormField) -> SHACLPropertyShape:
        """
        Generate a SHACL PropertyShape for a single form field.

        Args:
            field: The form field specification

        Returns:
            SHACLPropertyShape with semantic type and validation
        """
        # Get schema.org type and validation pattern
        schema_type = get_schema_org_type(field.type, field.label)
        validation_pattern = get_validation_pattern_for_type(schema_type)

        # Use custom pattern if provided, otherwise use inferred pattern
        pattern = field.validationPattern if field.validationPattern else (
            validation_pattern["pattern"] if validation_pattern else None
        )
        message = validation_pattern["message"] if validation_pattern else f"{field.label} is invalid"

        # Create SHACL PropertyShape
        shape = SHACLPropertyShape.create_for_field_type(
            field_name=field.label,
            field_type=field.type,
            schema_org_property=schema_type,
            required=field.required,
            allowed_values=field.options,
            custom_pattern=ValidationPattern(pattern=pattern, message=message) if pattern else None
        )

        return shape

    def generate_node_shape(self, fields: List[FormField], case_id: str = "UnknownCase") -> Dict[str, Any]:
        """
        Generate a SHACL NodeShape for an entire form.

        Args:
            fields: List of form fields
            case_id: Case ID for the form

        Returns:
            SHACL NodeShape in JSON-LD format
        """
        # Generate property shapes for all fields
        property_shapes = []
        for field in fields:
            shape = self.generate_property_shape(field)
            property_shapes.append(shape.to_jsonld())

        # Create NodeShape
        node_shape = {
            "@context": {
                "sh": "http://www.w3.org/ns/shacl#",
                "schema": "http://schema.org/",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
            },
            "@type": "sh:NodeShape",
            "sh:targetClass": "schema:Thing",
            "sh:name": f"{case_id} Application Form",
            "sh:description": f"SHACL shape for {case_id} form with semantic validation",
            "sh:property": property_shapes
        }

        return node_shape

    async def apply_modification(
        self,
        command: str,
        current_fields: List[Dict[str, Any]],
        case_id: str = "UnknownCase"
    ) -> FormModificationResult:
        """
        Apply a natural language modification to the form fields.

        Args:
            command: Natural language command
            current_fields: Current form fields as dictionaries
            case_id: Case ID for the form

        Returns:
            FormModificationResult with updated fields, modifications, and SHACL shape
        """
        # Convert dictionaries to FormField objects
        fields = [FormField(**f) for f in current_fields]

        # Parse the command
        parsed = await self.parse_nl_command(command, fields)

        modifications = []

        # Handle clarification requests
        if parsed["action"] == "clarify":
            raise ValueError(parsed.get("clarification", "Command unclear. Please provide more details."))

        # Handle add action
        if parsed["action"] == "add":
            field_label = parsed["field_label"]
            field_type = parsed.get("field_type", "text")
            required = parsed.get("required", False)
            options = parsed.get("options")

            # If field type not provided, infer from label
            if not field_type or field_type == "text":
                inferred_type = infer_field_type_from_label(field_label)
                if inferred_type != "text":
                    field_type = inferred_type

            # Get schema.org type and validation pattern
            schema_type = get_schema_org_type(field_type, field_label)
            validation_pattern = get_validation_pattern_for_type(schema_type)

            # Create new field
            new_field = FormField(
                id=self._generate_field_id(field_label),
                label=field_label,
                type=field_type,
                required=required,
                options=options,
                validationPattern=validation_pattern["pattern"] if validation_pattern else None,
                semanticType=schema_type
            )

            # Generate SHACL metadata
            shape = self.generate_property_shape(new_field)
            new_field.shaclMetadata = shape.to_jsonld()

            fields.append(new_field)
            modifications.append(f"Added field: {field_label} ({field_type})")

        # Handle remove action
        elif parsed["action"] == "remove":
            field_label = parsed["field_label"]
            normalized_target = normalize_field_label(field_label)

            # Find matching field (fuzzy match)
            removed = False
            for i, field in enumerate(fields):
                if normalize_field_label(field.label) == normalized_target:
                    fields.pop(i)
                    modifications.append(f"Removed field: {field.label}")
                    removed = True
                    break

            if not removed:
                raise ValueError(f"Field '{field_label}' not found in form. Available fields: {', '.join([f.label for f in fields])}")

        # Handle modify action (basic implementation)
        elif parsed["action"] == "modify":
            raise ValueError("Modify action is not yet implemented. Please use add/remove commands.")

        # Handle reorder action
        elif parsed["action"] == "reorder":
            raise ValueError("Reorder action is not yet implemented. Please use add/remove commands.")

        # Generate SHACL NodeShape for updated form
        shacl_shape = self.generate_node_shape(fields, case_id)

        # Convert fields back to dictionaries
        field_dicts = [asdict(f) for f in fields]

        return FormModificationResult(
            fields=field_dicts,
            modifications=modifications,
            shacl_shape=shacl_shape
        )


# Singleton instance
_shacl_generator_instance: Optional[SHACLGeneratorService] = None


def get_shacl_generator() -> SHACLGeneratorService:
    """
    Get or create the singleton SHACL generator service.

    The constructor resolves the active LLM provider via
    backend.services.llm_provider.get_provider(); no API keys are read here.
    """
    global _shacl_generator_instance
    if _shacl_generator_instance is None:
        _shacl_generator_instance = SHACLGeneratorService()
    return _shacl_generator_instance
