"""
SHACL Property Shape Model for Form Field Validation

This module provides the SHACLPropertyShape model class for defining
form field constraints with semantic validation using SHACL (Shapes Constraint Language).

The model extends the basic SHACL schema with validation messages and integrates
with the validation pattern library for common field types.

References:
- SHACL Spec: https://www.w3.org/TR/shacl/
- Schema.org: https://schema.org/
- XSD Datatypes: https://www.w3.org/TR/xmlschema-2/
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from backend.schemas.validation_patterns import (
    ValidationPattern,
    get_pattern_for_schema_org_property,
    EMAIL_PATTERN,
    PHONE_PATTERN,
    NAME_PATTERN,
    DATE_PATTERN,
    ADDRESS_PATTERN
)


@dataclass
class SHACLPropertyShape:
    """
    SHACL PropertyShape model for form field validation.

    Represents a SHACL PropertyShape with full constraint support including
    semantic types (schema.org), datatypes (XSD), patterns, cardinality,
    and user-friendly validation messages.

    Attributes:
        sh_path: Schema.org property path (e.g., "schema:email", "schema:givenName")
        sh_datatype: XSD datatype (e.g., "xsd:string", "xsd:date", "xsd:integer")
        sh_name: Human-readable field name displayed to users
        sh_description: Optional detailed description of the field
        sh_message: User-friendly validation error message
        sh_pattern: Optional regex pattern for validation
        sh_min_count: Minimum cardinality (1 = required field)
        sh_max_count: Maximum cardinality (1 = single value)
        sh_in: List of allowed values (for select/enum fields)
        sh_min_length: Minimum string length
        sh_max_length: Maximum string length
    """
    sh_path: str
    sh_datatype: str
    sh_name: str
    sh_message: str
    sh_description: Optional[str] = None
    sh_pattern: Optional[str] = None
    sh_min_count: Optional[int] = None
    sh_max_count: Optional[int] = None
    sh_in: Optional[List[str]] = None
    sh_min_length: Optional[int] = None
    sh_max_length: Optional[int] = None

    @classmethod
    def create_for_field_type(
        cls,
        field_name: str,
        field_type: str,
        schema_org_property: str,
        required: bool = False,
        description: Optional[str] = None,
        allowed_values: Optional[List[str]] = None,
        custom_pattern: Optional[ValidationPattern] = None
    ) -> "SHACLPropertyShape":
        """
        Factory method to create a SHACLPropertyShape for a specific field type.

        Args:
            field_name: Human-readable field name
            field_type: Field type (text, date, select, textarea, etc.)
            schema_org_property: Schema.org property path (e.g., "schema:email")
            required: Whether the field is required
            description: Optional field description
            allowed_values: List of allowed values for select fields
            custom_pattern: Custom validation pattern (overrides default)

        Returns:
            SHACLPropertyShape instance configured for the field type
        """
        # Determine XSD datatype
        datatype_mapping = {
            "text": "xsd:string",
            "date": "xsd:date",
            "select": "xsd:string",
            "textarea": "xsd:string",
            "number": "xsd:integer",
            "email": "xsd:string",
            "phone": "xsd:string",
            "boolean": "xsd:boolean",
        }
        sh_datatype = datatype_mapping.get(field_type.lower(), "xsd:string")

        # Get validation pattern
        pattern_obj = custom_pattern or get_pattern_for_schema_org_property(schema_org_property)

        sh_pattern = None
        sh_message = f"{field_name} is invalid"

        if pattern_obj:
            sh_pattern = pattern_obj["pattern"]
            sh_message = pattern_obj["message"]

        # Override message for required fields
        if required and not pattern_obj:
            sh_message = f"{field_name} is required"

        return cls(
            sh_path=schema_org_property,
            sh_datatype=sh_datatype,
            sh_name=field_name,
            sh_description=description,
            sh_message=sh_message,
            sh_pattern=sh_pattern,
            sh_min_count=1 if required else None,
            sh_max_count=1 if not allowed_values else None,
            sh_in=allowed_values,
            sh_min_length=None,
            sh_max_length=None,
        )

    def to_jsonld(self, include_context: bool = True) -> Dict[str, Any]:
        """
        Convert the PropertyShape to JSON-LD format.

        Args:
            include_context: Whether to include @context in output

        Returns:
            JSON-LD dictionary representation of the PropertyShape
        """
        result: Dict[str, Any] = {
            "@type": "sh:PropertyShape",
            "sh:path": self.sh_path,
            "sh:datatype": self.sh_datatype,
            "sh:name": self.sh_name,
            "sh:message": self.sh_message,
        }

        if include_context:
            result["@context"] = {
                "sh": "http://www.w3.org/ns/shacl#",
                "schema": "http://schema.org/",
                "xsd": "http://www.w3.org/2001/XMLSchema#"
            }

        if self.sh_description is not None:
            result["sh:description"] = self.sh_description

        if self.sh_pattern is not None:
            result["sh:pattern"] = self.sh_pattern

        if self.sh_min_count is not None:
            result["sh:minCount"] = self.sh_min_count

        if self.sh_max_count is not None:
            result["sh:maxCount"] = self.sh_max_count

        if self.sh_in is not None:
            result["sh:in"] = {"@list": self.sh_in}

        if self.sh_min_length is not None:
            result["sh:minLength"] = self.sh_min_length

        if self.sh_max_length is not None:
            result["sh:maxLength"] = self.sh_max_length

        return result

    @classmethod
    def from_jsonld(cls, data: Dict[str, Any]) -> "SHACLPropertyShape":
        """
        Create a SHACLPropertyShape from a JSON-LD dictionary.

        Args:
            data: JSON-LD dictionary representation

        Returns:
            SHACLPropertyShape instance
        """
        sh_in = None
        if "sh:in" in data:
            sh_in_value = data["sh:in"]
            if isinstance(sh_in_value, dict) and "@list" in sh_in_value:
                sh_in = sh_in_value["@list"]
            elif isinstance(sh_in_value, list):
                sh_in = sh_in_value

        return cls(
            sh_path=data.get("sh:path", ""),
            sh_datatype=data.get("sh:datatype", "xsd:string"),
            sh_name=data.get("sh:name", ""),
            sh_message=data.get("sh:message", "Validation failed"),
            sh_description=data.get("sh:description"),
            sh_pattern=data.get("sh:pattern"),
            sh_min_count=data.get("sh:minCount"),
            sh_max_count=data.get("sh:maxCount"),
            sh_in=sh_in,
            sh_min_length=data.get("sh:minLength"),
            sh_max_length=data.get("sh:maxLength"),
        )

    def validate_value(self, value: Any) -> tuple[bool, Optional[str]]:
        """
        Validate a value against this PropertyShape's constraints.

        Args:
            value: The value to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required constraint
        if self.sh_min_count and self.sh_min_count >= 1:
            if value is None or (isinstance(value, str) and not value.strip()):
                return False, self.sh_message

        # If value is empty and field is optional, it's valid
        if value is None or (isinstance(value, str) and not value.strip()):
            return True, None

        # Check pattern constraint
        if self.sh_pattern and isinstance(value, str):
            import re
            if not re.match(self.sh_pattern, value):
                return False, self.sh_message

        # Check allowed values constraint
        if self.sh_in and value not in self.sh_in:
            return False, self.sh_message

        # Check length constraints
        if isinstance(value, str):
            if self.sh_min_length and len(value) < self.sh_min_length:
                return False, self.sh_message
            if self.sh_max_length and len(value) > self.sh_max_length:
                return False, self.sh_message

        return True, None

    def is_required(self) -> bool:
        """Check if this field is required."""
        return self.sh_min_count is not None and self.sh_min_count >= 1

    def __repr__(self) -> str:
        """String representation of the PropertyShape."""
        return (
            f"SHACLPropertyShape(path={self.sh_path}, "
            f"datatype={self.sh_datatype}, "
            f"name={self.sh_name}, "
            f"required={self.is_required()})"
        )


# Common property shape templates for quick use
def create_email_shape(required: bool = True) -> SHACLPropertyShape:
    """Create a SHACL PropertyShape for email fields."""
    return SHACLPropertyShape(
        sh_path="schema:email",
        sh_datatype="xsd:string",
        sh_name="Email Address",
        sh_description="Contact email address",
        sh_message=EMAIL_PATTERN["message"],
        sh_pattern=EMAIL_PATTERN["pattern"],
        sh_min_count=1 if required else None,
        sh_max_count=1,
    )


def create_name_shape(
    path: str,
    name: str,
    required: bool = True
) -> SHACLPropertyShape:
    """Create a SHACL PropertyShape for name fields."""
    return SHACLPropertyShape(
        sh_path=path,
        sh_datatype="xsd:string",
        sh_name=name,
        sh_message=NAME_PATTERN["message"],
        sh_pattern=NAME_PATTERN["pattern"],
        sh_min_count=1 if required else None,
        sh_max_count=1,
    )


def create_date_shape(
    path: str,
    name: str,
    required: bool = True
) -> SHACLPropertyShape:
    """Create a SHACL PropertyShape for date fields."""
    return SHACLPropertyShape(
        sh_path=path,
        sh_datatype="xsd:date",
        sh_name=name,
        sh_message=DATE_PATTERN["message"],
        sh_pattern=DATE_PATTERN["pattern"],
        sh_min_count=1 if required else None,
        sh_max_count=1,
    )


def create_phone_shape(required: bool = False) -> SHACLPropertyShape:
    """Create a SHACL PropertyShape for phone number fields."""
    return SHACLPropertyShape(
        sh_path="schema:telephone",
        sh_datatype="xsd:string",
        sh_name="Phone Number",
        sh_description="Contact telephone number",
        sh_message=PHONE_PATTERN["message"],
        sh_pattern=PHONE_PATTERN["pattern"],
        sh_min_count=1 if required else None,
        sh_max_count=1,
    )


def create_address_shape(required: bool = True) -> SHACLPropertyShape:
    """Create a SHACL PropertyShape for address fields."""
    return SHACLPropertyShape(
        sh_path="schema:address",
        sh_datatype="xsd:string",
        sh_name="Address",
        sh_description="Physical address",
        sh_message=ADDRESS_PATTERN["message"],
        sh_pattern=ADDRESS_PATTERN["pattern"],
        sh_min_count=1 if required else None,
        sh_max_count=1,
    )
