"""
Backend Models Module

This module provides data models for the BAMF ACTE Companion application.
Models define the structure and validation logic for core entities.

Available Models:
- SHACLPropertyShape: SHACL property shape for form field validation
"""

from backend.models.shacl_property_shape import (
    SHACLPropertyShape,
    create_email_shape,
    create_name_shape,
    create_date_shape,
    create_phone_shape,
    create_address_shape,
)

__all__ = [
    "SHACLPropertyShape",
    "create_email_shape",
    "create_name_shape",
    "create_date_shape",
    "create_phone_shape",
    "create_address_shape",
]
