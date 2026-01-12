"""
Validation Pattern Library for SHACL Property Shapes

This module provides common validation patterns for form field types,
including regex patterns and user-friendly error messages.

Each pattern is a dictionary with:
- pattern: Regular expression for validation
- message: User-friendly error message displayed on validation failure

References:
- SHACL sh:pattern: https://www.w3.org/TR/shacl/#PatternConstraintComponent
- W3C HTML5 Email regex: https://html.spec.whatwg.org/multipage/input.html#e-mail-state-(type=email)
"""

from typing import TypedDict


class ValidationPattern(TypedDict):
    """
    Validation pattern with regex and error message.

    Attributes:
        pattern: Regular expression for validation
        message: User-friendly error message
    """
    pattern: str
    message: str


# Email validation pattern
# Based on simplified HTML5 email validation
# Matches: user@domain.com, name.surname@subdomain.domain.co.uk
EMAIL_PATTERN: ValidationPattern = {
    "pattern": r"^[^\s@]+@[^\s@]+\.[^\s@]+$",
    "message": "Email must be a valid email address containing @ and a domain"
}

# Phone number validation pattern
# Accepts various formats: +49 123 456789, (123) 456-7890, 123-456-7890
# International format with optional country code
PHONE_PATTERN: ValidationPattern = {
    "pattern": r"^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,9}$",
    "message": "Phone number must be valid (e.g., +49 123 456789 or 123-456-7890)"
}

# Name validation pattern
# Accepts letters, spaces, hyphens, and apostrophes
# Supports international characters (Unicode letters)
# Minimum 2 characters
NAME_PATTERN: ValidationPattern = {
    "pattern": r"^[\p{L}\s\-']{2,}$",
    "message": "Name must contain at least 2 characters and only letters, spaces, hyphens, or apostrophes"
}

# Date validation pattern
# ISO 8601 date format: YYYY-MM-DD
# Validates format only, not date validity (e.g., 2024-02-30 would match)
DATE_PATTERN: ValidationPattern = {
    "pattern": r"^\d{4}-\d{2}-\d{2}$",
    "message": "Date must be in YYYY-MM-DD format"
}

# Address validation pattern
# Accepts alphanumeric characters, spaces, commas, periods, hyphens
# Minimum 5 characters for basic address validation
ADDRESS_PATTERN: ValidationPattern = {
    "pattern": r"^[\p{L}\p{N}\s,.\-]{5,}$",
    "message": "Address must contain at least 5 characters"
}

# Postal code validation pattern (German format)
# German postal codes: 5 digits (e.g., 10115 for Berlin)
POSTAL_CODE_DE_PATTERN: ValidationPattern = {
    "pattern": r"^\d{5}$",
    "message": "Postal code must be 5 digits"
}

# Postal code validation pattern (International)
# More flexible pattern for international postal codes
POSTAL_CODE_PATTERN: ValidationPattern = {
    "pattern": r"^[\p{L}\p{N}\s\-]{3,10}$",
    "message": "Postal code must be between 3 and 10 characters"
}


# Pattern registry for easy lookup by field type
VALIDATION_PATTERNS: dict[str, ValidationPattern] = {
    "email": EMAIL_PATTERN,
    "phone": PHONE_PATTERN,
    "telephone": PHONE_PATTERN,
    "name": NAME_PATTERN,
    "givenName": NAME_PATTERN,
    "familyName": NAME_PATTERN,
    "date": DATE_PATTERN,
    "birthDate": DATE_PATTERN,
    "address": ADDRESS_PATTERN,
    "postalCode": POSTAL_CODE_PATTERN,
    "postalCodeDE": POSTAL_CODE_DE_PATTERN,
}


def get_validation_pattern(field_type: str) -> ValidationPattern | None:
    """
    Get validation pattern by field type.

    Args:
        field_type: Field type or semantic type (e.g., "email", "phone", "name")

    Returns:
        ValidationPattern if found, None otherwise
    """
    return VALIDATION_PATTERNS.get(field_type.lower())


def get_pattern_for_schema_org_property(schema_property: str) -> ValidationPattern | None:
    """
    Get validation pattern for a schema.org property.

    Args:
        schema_property: Schema.org property path (e.g., "schema:email", "schema:telephone")

    Returns:
        ValidationPattern if found, None otherwise
    """
    # Extract property name from schema.org path
    if ":" in schema_property:
        property_name = schema_property.split(":")[-1]
    else:
        property_name = schema_property

    return get_validation_pattern(property_name)
