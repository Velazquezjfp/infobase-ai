"""
Admin API for BAMF AI Case Management System.

This module provides REST endpoints for administrative operations,
including AI-powered form field generation from natural language prompts.

Endpoints:
    POST /api/admin/generate-field: Generate a form field from NLP prompt
    GET /api/admin/health: Admin service health check
"""

import logging
from typing import Optional, List

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.services.field_generator import get_field_generator

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
            }
        },
        status_code=200
    )
