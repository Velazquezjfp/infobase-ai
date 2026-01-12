"""
Admin API for BAMF AI Case Management System.

This module provides REST endpoints for administrative operations,
including AI-powered form field generation from natural language prompts.

Endpoints:
    POST /api/admin/generate-field: Generate a form field from NLP prompt
    POST /api/admin/modify-form: Modify form using natural language (S5-001)
    GET /api/admin/health: Admin service health check
"""

import logging
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.services.field_generator import get_field_generator
from backend.services.shacl_generator import get_shacl_generator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin")


class GenerateFieldRequest(BaseModel):
    """
    Request model for field generation endpoint.

    Attributes:
        prompt: Natural language description of the desired field.
                Examples:
                - "Add a text field for passport number"
                - "Add dropdown for education level with options high school, bachelor, master"
                - "I need a required date field for visa expiry"
    """
    prompt: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Natural language prompt describing the field to generate",
        examples=[
            "Add a dropdown for marital status with options single, married, divorced",
            "Add a required text field for passport number",
            "Create a date field for visa expiry date",
        ]
    )


class SHACLMetadataResponse(BaseModel):
    """SHACL metadata in JSON-LD format."""
    context: dict = Field(..., alias="@context")
    type: str = Field(..., alias="@type")
    sh_path: str = Field(..., alias="sh:path")
    sh_datatype: str = Field(..., alias="sh:datatype")
    sh_name: str = Field(..., alias="sh:name")
    sh_description: Optional[str] = Field(None, alias="sh:description")
    sh_min_count: Optional[int] = Field(None, alias="sh:minCount")
    sh_max_count: Optional[int] = Field(None, alias="sh:maxCount")
    sh_in: Optional[dict] = Field(None, alias="sh:in")

    class Config:
        populate_by_name = True


class GeneratedFieldResponse(BaseModel):
    """
    Response model for a generated form field.

    Attributes:
        id: Unique field identifier
        label: Human-readable label
        type: Field type (text, date, select, textarea)
        value: Default value (usually empty)
        options: List of options (for select fields)
        required: Whether the field is required
        shaclMetadata: SHACL semantic metadata in JSON-LD format
    """
    id: str
    label: str
    type: str
    value: str = ""
    options: Optional[List[str]] = None
    required: bool = False
    shaclMetadata: Optional[dict] = None


class GenerateFieldResponse(BaseModel):
    """Wrapper response for field generation endpoint."""
    field: GeneratedFieldResponse
    message: str = "Field generated successfully"


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None


# S5-001: Form Modification Models

class FormModificationRequest(BaseModel):
    """
    Request model for form modification endpoint (S5-001).

    Attributes:
        command: Natural language command describing the modification
        currentFields: Current list of form fields
        caseId: Case ID for the form
    """
    command: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Natural language command for form modification",
        examples=[
            "Add an email field for contact email",
            "Add a phone number field",
            "Remove the phone number field",
            "Add dropdown for marital status with options single, married, divorced"
        ]
    )
    currentFields: List[Dict[str, Any]] = Field(
        default=[],
        description="Current form fields as dictionaries"
    )
    caseId: str = Field(
        default="UnknownCase",
        description="Case ID for the form"
    )


class FormModificationResponse(BaseModel):
    """
    Response model for form modification endpoint (S5-001).

    Attributes:
        fields: Updated list of form fields with SHACL metadata
        shaclShape: Complete SHACL NodeShape in JSON-LD format
        modifications: List of modifications applied (human-readable)
        message: Success message
    """
    fields: List[Dict[str, Any]]
    shaclShape: Dict[str, Any]
    modifications: List[str]
    message: str = "Form modified successfully"


@router.post(
    "/generate-field",
    response_model=GenerateFieldResponse,
    responses={
        200: {"description": "Field generated successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request or generation failed"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Generate a form field from natural language",
    description="""
    Generate a SHACL-compliant form field specification from a natural language prompt.

    The service uses rule-based extraction for common patterns and falls back to AI
    (Gemini) for more complex or ambiguous requests.

    **Supported field types:**
    - `text`: Standard text input
    - `date`: Date picker
    - `select`: Dropdown with options
    - `textarea`: Multi-line text

    **Example prompts:**
    - "Add a text field for passport number"
    - "Add dropdown for marital status with options single, married, divorced"
    - "I need a required date field for visa expiry"
    - "Create a textarea for additional notes"

    **Supported languages:** English, German
    """,
)
async def generate_field(request: GenerateFieldRequest) -> GenerateFieldResponse:
    """
    Generate a form field from a natural language prompt.

    Args:
        request: The field generation request containing the NLP prompt.

    Returns:
        GenerateFieldResponse: The generated field specification with SHACL metadata.

    Raises:
        HTTPException: If field generation fails.
    """
    logger.info(f"Received field generation request: {request.prompt[:50]}...")

    try:
        # Get the singleton field generator service
        generator = get_field_generator()

        # Generate the field
        field_spec = await generator.generate_field(request.prompt)

        # Validate the generated field
        validation_errors = generator.validate_field_spec(field_spec)
        if validation_errors:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Generated field validation failed",
                    "validation_errors": validation_errors,
                }
            )

        # Convert to response model
        field_response = GeneratedFieldResponse(
            id=field_spec.id,
            label=field_spec.label,
            type=field_spec.type,
            value=field_spec.value,
            options=field_spec.options,
            required=field_spec.required,
            shaclMetadata=field_spec.shacl_metadata,
        )

        logger.info(f"Generated field: {field_spec.label} (type={field_spec.type})")

        return GenerateFieldResponse(
            field=field_response,
            message=f"Successfully generated '{field_spec.label}' field",
        )

    except ValueError as e:
        logger.error(f"Field generation failed: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={"error": "Field generation failed", "detail": str(e)}
        )

    except Exception as e:
        logger.error(f"Unexpected error in field generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "detail": str(e)}
        )


@router.post(
    "/modify-form",
    response_model=FormModificationResponse,
    responses={
        200: {"description": "Form modified successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request or modification failed"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Modify form using natural language (S5-001)",
    description="""
    Modify a form using natural language commands with automatic SHACL generation.

    The service uses Gemini AI to interpret natural language commands and applies
    modifications to the form structure. Each field automatically receives:
    - Schema.org semantic type (e.g., schema:email, schema:name)
    - Validation patterns based on semantic type
    - SHACL PropertyShape metadata for validation

    **Supported operations:**
    - Add field: "Add an email field for contact email"
    - Remove field: "Remove the phone number field"
    - Add select field: "Add dropdown for marital status with options single, married, divorced"
    - Add required field: "Add a required date field for birth date"

    **Supported field types:**
    - `text`: Standard text input (email, phone, name, etc.)
    - `date`: Date picker
    - `select`: Dropdown with options
    - `textarea`: Multi-line text

    **Automatic semantic type inference:**
    The system automatically infers schema.org types from field labels:
    - "email" → schema:email with email validation
    - "phone" → schema:telephone with phone validation
    - "name" → schema:name with name validation
    - "birth date" → schema:birthDate with date validation
    - "address" → schema:address with address validation

    **Response includes:**
    - Updated field list with SHACL metadata
    - Complete SHACL NodeShape for the entire form
    - List of modifications applied

    **Supported languages:** English, German
    """,
)
async def modify_form(request: FormModificationRequest) -> FormModificationResponse:
    """
    Modify a form using natural language commands (S5-001).

    Args:
        request: Form modification request with command and current fields

    Returns:
        FormModificationResponse: Updated fields, SHACL shape, and modifications

    Raises:
        HTTPException: If modification fails or command is unclear
    """
    logger.info(f"Received form modification request: {request.command[:50]}... for case {request.caseId}")

    try:
        # Get the SHACL generator service
        generator = get_shacl_generator()

        # Apply modification
        result = await generator.apply_modification(
            command=request.command,
            current_fields=request.currentFields,
            case_id=request.caseId
        )

        logger.info(f"Form modification successful: {', '.join(result.modifications)}")

        return FormModificationResponse(
            fields=result.fields,
            shaclShape=result.shacl_shape,
            modifications=result.modifications,
            message=f"Successfully modified form: {', '.join(result.modifications)}"
        )

    except ValueError as e:
        # User error (clarification needed, field not found, etc.)
        logger.warning(f"Form modification failed: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={"error": "Form modification failed", "detail": str(e)}
        )

    except Exception as e:
        # Internal error
        logger.error(f"Unexpected error in form modification: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "detail": str(e)}
        )


@router.get(
    "/health",
    summary="Admin service health check",
    description="Check the health status of the admin service.",
)
async def admin_health_check() -> JSONResponse:
    """
    Health check endpoint for admin service.

    Returns:
        JSONResponse: Service health status.
    """
    return JSONResponse(
        content={
            "service": "admin",
            "status": "ready",
            "features": {
                "field_generation": True,
                "form_modification": True,  # S5-001
            }
        },
        status_code=200
    )
