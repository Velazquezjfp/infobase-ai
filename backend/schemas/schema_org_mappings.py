"""
Schema.org Vocabulary Mappings for Form Fields.

This module provides mappings from form field types and labels to schema.org
properties, enabling automatic semantic type inference for SHACL shape generation.

References:
- Schema.org vocabulary: https://schema.org/
- SHACL specification: https://www.w3.org/TR/shacl/

Requirement: S5-001 - Natural Language Form Field Modification with SHACL Validation
"""

from typing import Optional, Dict, Tuple
import re

from backend.schemas.validation_patterns import (
    ValidationPattern,
    EMAIL_PATTERN,
    PHONE_PATTERN,
    NAME_PATTERN,
    DATE_PATTERN,
    ADDRESS_PATTERN,
    POSTAL_CODE_PATTERN,
    POSTAL_CODE_DE_PATTERN,
)


# Schema.org property mappings by semantic type
SCHEMA_ORG_PROPERTIES: Dict[str, str] = {
    # Person-related properties
    "name": "schema:name",
    "given_name": "schema:givenName",
    "family_name": "schema:familyName",
    "full_name": "schema:name",
    "first_name": "schema:givenName",
    "last_name": "schema:familyName",
    "middle_name": "schema:additionalName",

    # Contact properties
    "email": "schema:email",
    "phone": "schema:telephone",
    "telephone": "schema:telephone",
    "mobile": "schema:telephone",
    "fax": "schema:faxNumber",

    # Address properties
    "address": "schema:address",
    "street": "schema:streetAddress",
    "street_address": "schema:streetAddress",
    "city": "schema:addressLocality",
    "postal_code": "schema:postalCode",
    "zip_code": "schema:postalCode",
    "country": "schema:addressCountry",
    "region": "schema:addressRegion",
    "state": "schema:addressRegion",

    # Date properties
    "date": "schema:Date",
    "birth_date": "schema:birthDate",
    "birthdate": "schema:birthDate",
    "date_of_birth": "schema:birthDate",
    "start_date": "schema:startDate",
    "end_date": "schema:endDate",

    # Identification properties
    "passport": "schema:identifier",
    "passport_number": "schema:identifier",
    "id_number": "schema:identifier",
    "identifier": "schema:identifier",
    "ssn": "schema:identifier",
    "tax_id": "schema:taxID",

    # Nationality and language
    "nationality": "schema:nationality",
    "language": "schema:knowsLanguage",
    "native_language": "schema:knowsLanguage",

    # Education
    "education": "schema:educationalLevel",
    "education_level": "schema:educationalLevel",
    "degree": "schema:educationalCredentialAwarded",

    # Employment
    "occupation": "schema:hasOccupation",
    "job_title": "schema:jobTitle",
    "employer": "schema:worksFor",

    # General
    "description": "schema:description",
    "notes": "schema:description",
    "comments": "schema:comment",
    "url": "schema:url",
    "website": "schema:url",
}

# Validation pattern associations by semantic type
SEMANTIC_TYPE_PATTERNS: Dict[str, ValidationPattern] = {
    "email": EMAIL_PATTERN,
    "phone": PHONE_PATTERN,
    "telephone": PHONE_PATTERN,
    "mobile": PHONE_PATTERN,
    "name": NAME_PATTERN,
    "given_name": NAME_PATTERN,
    "family_name": NAME_PATTERN,
    "full_name": NAME_PATTERN,
    "first_name": NAME_PATTERN,
    "last_name": NAME_PATTERN,
    "date": DATE_PATTERN,
    "birth_date": DATE_PATTERN,
    "birthdate": DATE_PATTERN,
    "date_of_birth": DATE_PATTERN,
    "start_date": DATE_PATTERN,
    "end_date": DATE_PATTERN,
    "address": ADDRESS_PATTERN,
    "street": ADDRESS_PATTERN,
    "street_address": ADDRESS_PATTERN,
    "postal_code": POSTAL_CODE_PATTERN,
    "zip_code": POSTAL_CODE_PATTERN,
}

# German-specific pattern overrides
GERMAN_POSTAL_CODE_FIELDS = {"postal_code", "zip_code", "postleitzahl", "plz"}


def normalize_field_label(label: str) -> str:
    """
    Normalize a field label to a standard format for semantic type lookup.

    Args:
        label: The field label (e.g., "Contact Email", "Full Name", "Geburtsdatum")

    Returns:
        Normalized label (e.g., "contact_email", "full_name", "birth_date")
    """
    # Convert to lowercase
    normalized = label.lower()

    # Remove special characters and replace spaces/hyphens with underscores
    normalized = re.sub(r'[^\w\s-]', '', normalized)
    normalized = re.sub(r'[\s-]+', '_', normalized)

    # Remove common prefixes/suffixes
    normalized = re.sub(r'^(enter_|input_|select_|provide_)', '', normalized)
    normalized = re.sub(r'(_field|_input|_value)$', '', normalized)

    # German to English mappings for common terms
    german_mappings = {
        'name': 'name',
        'vorname': 'given_name',
        'nachname': 'family_name',
        'familienname': 'family_name',
        'geburtsdatum': 'birth_date',
        'telefon': 'phone',
        'telefonnummer': 'phone',
        'e_mail': 'email',
        'email': 'email',
        'adresse': 'address',
        'strasse': 'street',
        'stadt': 'city',
        'postleitzahl': 'postal_code',
        'plz': 'postal_code',
        'land': 'country',
        'staatsangehorigkeit': 'nationality',
        'nationalitat': 'nationality',
        'passnummer': 'passport_number',
        'reisepass': 'passport',
        'beruf': 'occupation',
    }

    # Check for German terms
    for german, english in german_mappings.items():
        if german in normalized:
            normalized = normalized.replace(german, english)

    return normalized


def get_schema_org_type(field_type: str, field_label: str) -> str:
    """
    Get the schema.org property type for a form field.

    Args:
        field_type: The form field type (text, date, select, textarea)
        field_label: The human-readable field label

    Returns:
        Schema.org property URI (e.g., "schema:email", "schema:name")
    """
    # Normalize the label for lookup
    normalized = normalize_field_label(field_label)

    # Try exact match first
    if normalized in SCHEMA_ORG_PROPERTIES:
        return SCHEMA_ORG_PROPERTIES[normalized]

    # Try partial matches (e.g., "applicant_email" -> "email")
    for key, value in SCHEMA_ORG_PROPERTIES.items():
        if key in normalized or normalized in key:
            return value

    # Fallback based on field type
    if field_type == "date":
        return "schema:Date"
    elif field_type == "select":
        return "schema:Text"
    elif field_type == "textarea":
        return "schema:description"
    else:
        return "schema:Text"


def get_validation_pattern_for_type(semantic_type: str, is_german: bool = False) -> Optional[ValidationPattern]:
    """
    Get the validation pattern for a semantic field type.

    Args:
        semantic_type: The semantic type (normalized field label or schema.org property)
        is_german: Whether to use German-specific patterns (e.g., German postal codes)

    Returns:
        ValidationPattern with regex and error message, or None if no pattern applies
    """
    # Extract property name from schema.org URI if provided
    if semantic_type.startswith("schema:"):
        semantic_type = semantic_type.replace("schema:", "").lower()
        # Convert camelCase to snake_case
        semantic_type = re.sub(r'([a-z])([A-Z])', r'\1_\2', semantic_type).lower()

    normalized = normalize_field_label(semantic_type)

    # German postal code override
    if is_german and normalized in GERMAN_POSTAL_CODE_FIELDS:
        return POSTAL_CODE_DE_PATTERN

    # Try exact match
    if normalized in SEMANTIC_TYPE_PATTERNS:
        return SEMANTIC_TYPE_PATTERNS[normalized]

    # Try partial matches
    for key, pattern in SEMANTIC_TYPE_PATTERNS.items():
        if key in normalized:
            return pattern

    return None


def infer_field_type_from_label(field_label: str) -> str:
    """
    Infer the appropriate form field type from the label.

    Args:
        field_label: The human-readable field label

    Returns:
        Form field type: "text", "date", "select", "textarea"
    """
    normalized = normalize_field_label(field_label)

    # Date fields
    date_keywords = ["date", "birth", "birthdate", "start_date", "end_date"]
    if any(keyword in normalized for keyword in date_keywords):
        return "date"

    # Textarea fields (longer text)
    textarea_keywords = ["description", "notes", "comments", "address", "reason", "explanation"]
    if any(keyword in normalized for keyword in textarea_keywords):
        return "textarea"

    # Select fields (enums)
    select_keywords = ["status", "level", "type", "category", "nationality", "country", "language"]
    if any(keyword in normalized for keyword in select_keywords):
        return "select"

    # Default to text
    return "text"


def get_schema_org_and_pattern(field_type: str, field_label: str, is_german: bool = False) -> Tuple[str, Optional[ValidationPattern]]:
    """
    Get both schema.org type and validation pattern for a field.

    Args:
        field_type: The form field type (text, date, select, textarea)
        field_label: The human-readable field label
        is_german: Whether to use German-specific patterns

    Returns:
        Tuple of (schema.org property URI, ValidationPattern or None)
    """
    schema_type = get_schema_org_type(field_type, field_label)
    validation_pattern = get_validation_pattern_for_type(schema_type, is_german)

    return schema_type, validation_pattern


# Export main functions
__all__ = [
    "get_schema_org_type",
    "get_validation_pattern_for_type",
    "infer_field_type_from_label",
    "get_schema_org_and_pattern",
    "normalize_field_label",
    "SCHEMA_ORG_PROPERTIES",
    "SEMANTIC_TYPE_PATTERNS",
]
