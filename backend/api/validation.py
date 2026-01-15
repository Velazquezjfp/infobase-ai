"""
Case Validation API - REST endpoints for case validation before submission.

This module provides API endpoints for validating cases using AI-powered analysis.
It evaluates form data, documents, and case context to provide structured feedback.

Features:
    - POST /api/validation/case/{case_id}: Validate a case for submission
    - Accepts form data, language preference, and cached document contents
    - Returns structured validation result with score, warnings, recommendations

Endpoints:
    - POST /api/validation/case/{case_id}: Validate case before submission
    - GET /api/validation/health: Health check for validation service
"""

import logging
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.services.validation_service import get_validation_service

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


class ValidationRequest(BaseModel):
    """
    Request model for case validation endpoint.

    Attributes:
        formData: Dictionary of form field IDs to their values
        language: Language code for response ('de' or 'en')
        documentContents: Optional dictionary of document IDs to cached text content
    """
    formData: Dict[str, str] = Field(
        default_factory=dict,
        description="Form field ID to value mapping"
    )
    language: str = Field(
        default="de",
        description="Response language code (de or en)"
    )
    documentContents: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional cached document text contents"
    )


class ValidationWarningResponse(BaseModel):
    """Single warning in validation response."""
    severity: str = Field(..., description="Severity level: critical, high, medium, low")
    category: str = Field(..., description="Warning category")
    title: str = Field(..., description="Short warning title")
    details: list[str] = Field(default_factory=list, description="Detailed issues")


class ValidationResponse(BaseModel):
    """
    Response model for case validation endpoint.

    Attributes:
        success: Whether validation completed successfully
        score: Validation score (1-100)
        summary: Brief overall assessment
        warnings: List of validation warnings grouped by severity
        recommendations: List of next step recommendations
        error: Error message if validation failed
    """
    success: bool
    score: int = Field(default=0, ge=0, le=100)
    summary: str = Field(default="")
    warnings: list[ValidationWarningResponse] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    error: Optional[str] = None


@router.post("/case/{case_id}", response_model=ValidationResponse)
async def validate_case(case_id: str, request: ValidationRequest) -> ValidationResponse:
    """
    Validate a case for submission completeness.

    Analyzes the case using AI to evaluate form data, documents, and context.
    Returns a structured assessment with score, warnings, and recommendations.

    Args:
        case_id: The case ID to validate (e.g., "ACTE-2024-001")
        request: Validation request containing form data and preferences

    Returns:
        ValidationResponse: Structured validation result

    Raises:
        HTTPException 500: If validation processing fails

    Example:
        POST /api/validation/case/ACTE-2024-001
        {
          "formData": {"fullName": "John Doe", "dateOfBirth": "1990-01-15"},
          "language": "en",
          "documentContents": {"doc_001": "extracted text..."}
        }
    """
    try:
        logger.info(
            f"Validation request for case {case_id} - "
            f"language: {request.language}, "
            f"form_fields: {len(request.formData)}, "
            f"document_contents: {len(request.documentContents) if request.documentContents else 0}"
        )

        # Get validation service
        service = get_validation_service()

        # Perform validation
        result = await service.validate_case(
            case_id=case_id,
            form_data=request.formData,
            language=request.language,
            document_contents=request.documentContents
        )

        # Convert to response format
        warnings = [
            ValidationWarningResponse(
                severity=w.severity,
                category=w.category,
                title=w.title,
                details=w.details
            )
            for w in result.warnings
        ]

        logger.info(
            f"Validation completed for case {case_id} - "
            f"score: {result.score}, "
            f"warnings: {len(result.warnings)}"
        )

        return ValidationResponse(
            success=result.success,
            score=result.score,
            summary=result.summary,
            warnings=warnings,
            recommendations=result.recommendations,
            error=result.error
        )

    except Exception as e:
        logger.error(f"Unexpected error in case validation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


@router.get("/health")
async def validation_health():
    """
    Health check endpoint for validation service.

    Returns:
        dict: Service health status and capabilities

    Example:
        GET /api/validation/health
    """
    try:
        service = get_validation_service()
        gemini_initialized = service._gemini_service is not None and service._gemini_service.is_initialized()

        return {
            "status": "healthy" if gemini_initialized else "degraded",
            "service": "case_validation",
            "gemini_initialized": gemini_initialized,
            "ai_powered": True
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "case_validation",
            "error": str(e)
        }
