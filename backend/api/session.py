"""
Session API for BAMF ACTE Companion (S001-F-007).

Exposes the ephemeral one-shot-session reset endpoint. Sprint-1 frontends call
this on logout, browser close (via navigator.sendBeacon), and idle timeout to
restore the case to its seed state from ``root_docs/`` and the matching context
template.
"""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.session_manager import reset_case_to_seed

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/session")


class ResetRequest(BaseModel):
    """Body for POST /api/session/reset."""
    case_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Case identifier to reset (e.g. 'ACTE-2024-001')",
    )


class ResetResponse(BaseModel):
    """Response body for POST /api/session/reset."""
    success: bool
    case_id: str
    copied: int
    registered: int


@router.post("/reset", response_model=ResetResponse)
async def reset_session(body: ResetRequest) -> ResetResponse:
    """Reset the given case to its seed state.

    Wipes ${DOCUMENTS_PATH}/{case_id}/, restores the context dir from the
    matching template, copies seed files from ``root_docs/`` and rebuilds the
    document manifest. Idempotent.
    """
    try:
        stats = reset_case_to_seed(body.case_id)
    except FileNotFoundError as exc:
        # No template matches — surface as 404 so callers can distinguish from
        # transient I/O failures.
        logger.warning("Reset failed for %s: %s", body.case_id, exc)
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:  # noqa: BLE001
        logger.error("Reset failed for %s: %s", body.case_id, exc, exc_info=True)
        raise HTTPException(status_code=500, detail="session_reset_failed")

    return ResetResponse(
        success=True,
        case_id=body.case_id,
        copied=stats["copied"],
        registered=stats["registered"],
    )
