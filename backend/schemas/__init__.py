"""
SHACL Schema Package for BAMF AI Case Management System

This package provides SHACL (Shapes Constraint Language) schema definitions
for form fields, represented in JSON-LD format. SHACL enables semantic
validation and provides machine-readable metadata for form structures.

Main Components:
- SHACLPropertyShape: Defines constraints for individual form fields
- SHACLNodeShape: Defines constraints for forms/entities
- JSON-LD contexts and helper functions for building SHACL metadata

Usage:
    from backend.schemas import (
        SHACLPropertyShape,
        SHACLNodeShape,
        build_field_context,
        SHACL_CONTEXT,
    )

    # Create a property shape for a required text field
    name_shape = SHACLPropertyShape(
        sh_path="schema:name",
        sh_datatype="xsd:string",
        sh_name="Full Name",
        sh_min_count=1,
    )

    # Convert to JSON-LD
    jsonld = name_shape.to_jsonld()

    # Or use the helper function
    context = build_field_context("text", "Full Name", required=True)
"""

from .shacl import (
    SHACLPropertyShape,
    SHACLNodeShape,
)

from .jsonld_context import (
    SHACL_CONTEXT,
    SCHEMA_ORG_CONTEXT,
    XSD_DATATYPE_MAPPING,
    SCHEMA_ORG_PROPERTY_MAPPING,
    get_xsd_datatype,
    get_schema_org_property,
    build_field_context,
    create_form_node_shape,
)

__all__ = [
    # Classes
    "SHACLPropertyShape",
    "SHACLNodeShape",
    # Constants
    "SHACL_CONTEXT",
    "SCHEMA_ORG_CONTEXT",
    "XSD_DATATYPE_MAPPING",
    "SCHEMA_ORG_PROPERTY_MAPPING",
    # Functions
    "get_xsd_datatype",
    "get_schema_org_property",
    "build_field_context",
    "create_form_node_shape",
]
