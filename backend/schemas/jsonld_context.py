"""
JSON-LD Context Definitions for SHACL Form Fields

This module provides JSON-LD context constants and helper functions
for building semantic metadata for form fields.

The contexts define namespace prefixes and mappings used throughout
the SHACL schema definitions.
"""

from typing import Dict, Any, Optional


# Standard JSON-LD context for SHACL form fields
SHACL_CONTEXT: Dict[str, str] = {
    "sh": "http://www.w3.org/ns/shacl#",
    "schema": "http://schema.org/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
}

# Commonly used Schema.org context for person/application forms
SCHEMA_ORG_CONTEXT: Dict[str, str] = {
    "schema": "http://schema.org/",
    "name": "schema:name",
    "givenName": "schema:givenName",
    "familyName": "schema:familyName",
    "birthDate": "schema:birthDate",
    "nationality": "schema:nationality",
    "address": "schema:address",
    "email": "schema:email",
    "telephone": "schema:telephone",
}

# Mapping from form field types to XSD datatypes
XSD_DATATYPE_MAPPING: Dict[str, str] = {
    "text": "xsd:string",
    "date": "xsd:date",
    "select": "xsd:string",  # Select uses sh:in for allowed values
    "textarea": "xsd:string",
    "number": "xsd:integer",
    "email": "xsd:string",
    "phone": "xsd:string",
    "boolean": "xsd:boolean",
}

# Mapping from common field labels to Schema.org properties
SCHEMA_ORG_PROPERTY_MAPPING: Dict[str, str] = {
    # Person properties
    "name": "schema:name",
    "full name": "schema:name",
    "fullname": "schema:name",
    "given name": "schema:givenName",
    "first name": "schema:givenName",
    "family name": "schema:familyName",
    "last name": "schema:familyName",
    "surname": "schema:familyName",
    "birth date": "schema:birthDate",
    "birthdate": "schema:birthDate",
    "date of birth": "schema:birthDate",
    "nationality": "schema:nationality",
    "country of origin": "schema:nationality",
    "citizenship": "schema:nationality",

    # Contact properties
    "address": "schema:address",
    "current address": "schema:address",
    "home address": "schema:address",
    "email": "schema:email",
    "email address": "schema:email",
    "phone": "schema:telephone",
    "telephone": "schema:telephone",
    "phone number": "schema:telephone",

    # Education/Certificate properties
    "education": "schema:hasCredential",
    "certificate": "schema:hasCredential",
    "language certificate": "schema:knowsLanguage",
    "language": "schema:knowsLanguage",

    # Application properties
    "description": "schema:description",
    "reason": "schema:description",
    "reason for application": "schema:description",
    "notes": "schema:description",
    "comments": "schema:comment",

    # Course/Program properties
    "course": "schema:courseCode",
    "course preference": "schema:courseCode",
    "program": "schema:programName",
}


def get_xsd_datatype(field_type: str) -> str:
    """
    Get the XSD datatype for a form field type.

    Args:
        field_type: The form field type (text, date, select, textarea)

    Returns:
        The corresponding XSD datatype string
    """
    return XSD_DATATYPE_MAPPING.get(field_type.lower(), "xsd:string")


def get_schema_org_property(label: str) -> Optional[str]:
    """
    Get the Schema.org property for a field label.

    Args:
        label: The field label (case-insensitive)

    Returns:
        The Schema.org property path if found, None otherwise
    """
    normalized_label = label.lower().strip()
    return SCHEMA_ORG_PROPERTY_MAPPING.get(normalized_label)


def build_field_context(
    field_type: str,
    field_label: str,
    required: bool = False,
    options: Optional[list] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build a complete JSON-LD context for a form field.

    This function creates a SHACL PropertyShape context dictionary
    that can be used as the shaclMetadata for a FormField.

    Args:
        field_type: The form field type (text, date, select, textarea)
        field_label: The human-readable field label
        required: Whether the field is required
        options: List of allowed values for select fields
        description: Optional description of the field

    Returns:
        A JSON-LD dictionary representing the SHACL PropertyShape

    Example:
        >>> build_field_context("text", "Full Name", required=True)
        {
            "@context": {...},
            "@type": "sh:PropertyShape",
            "sh:path": "schema:name",
            "sh:datatype": "xsd:string",
            "sh:name": "Full Name",
            "sh:minCount": 1,
            "sh:maxCount": 1
        }
    """
    # Determine the Schema.org property path
    schema_property = get_schema_org_property(field_label)
    if schema_property is None:
        # Generate a generic property path from the label
        safe_label = field_label.lower().replace(" ", "_").replace("-", "_")
        schema_property = f"schema:{safe_label}"

    # Build the base context
    context: Dict[str, Any] = {
        "@context": SHACL_CONTEXT.copy(),
        "@type": "sh:PropertyShape",
        "sh:path": schema_property,
        "sh:datatype": get_xsd_datatype(field_type),
        "sh:name": field_label,
        "sh:maxCount": 1,  # Default to single value
    }

    # Add required constraint
    if required:
        context["sh:minCount"] = 1

    # Add description if provided
    if description:
        context["sh:description"] = description

    # Add allowed values for select fields
    if options and field_type.lower() == "select":
        context["sh:in"] = {"@list": options}

    return context


def create_form_node_shape(
    form_name: str,
    target_class: str = "schema:Thing",
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a SHACL NodeShape for a form.

    Args:
        form_name: The name of the form
        target_class: The Schema.org class this form describes
        description: Optional description of the form

    Returns:
        A JSON-LD dictionary representing the SHACL NodeShape
    """
    result: Dict[str, Any] = {
        "@context": SHACL_CONTEXT.copy(),
        "@type": "sh:NodeShape",
        "sh:targetClass": target_class,
        "sh:name": form_name,
        "sh:property": [],
    }

    if description:
        result["sh:description"] = description

    return result
