"""Shared response/request models reused across API routers.

Hosts the canonical `ErrorResponse` model so that admin and files routers expose
a single OpenAPI schema component instead of duplicating the definition.
"""

from typing import Optional

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Canonical API error body.

    `error` is the machine-readable discriminator (e.g. "feature_disabled",
    "Validation failed"); `detail` is the human-readable message.
    """

    error: str
    detail: Optional[str] = None


class FileErrorResponse(ErrorResponse):
    """Error body for file endpoints — adds the offending filename."""

    file_name: Optional[str] = None
