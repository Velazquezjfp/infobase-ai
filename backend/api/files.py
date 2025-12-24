"""
File Management API for BAMF AI Case Management System.

This module provides REST endpoints for file upload, deletion, and management operations,
including drag-and-drop upload with size validation and case-scoped file storage.

Endpoints:
    POST /api/files/upload: Upload a file to a specific case folder
    DELETE /api/files/{case_id}/{folder_id}/{filename}: Delete a file from a case folder
    GET /api/files/exists/{case_id}/{folder_id}/{filename}: Check if a file exists (duplicate detection)
    GET /api/files/health: File service health check
"""

import logging
import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/files")


class UploadResponse(BaseModel):
    """
    Response model for file upload endpoint.

    Attributes:
        success: Whether the upload was successful
        file_path: Relative path to the uploaded file
        file_name: Name of the uploaded file
        size: Size of the uploaded file in bytes
        message: Success message
    """
    success: bool
    file_path: str = Field(..., description="Relative path: documents/{caseId}/{folderId}/{filename}")
    file_name: str
    size: int = Field(..., description="File size in bytes")
    message: str = "File uploaded successfully"


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
    file_name: Optional[str] = None


class DeleteResponse(BaseModel):
    """
    Response model for file deletion endpoint.

    Attributes:
        success: Whether the deletion was successful
        message: Success or error message
        file_name: Name of the deleted file
    """
    success: bool
    message: str
    file_name: str


@router.post(
    "/upload",
    response_model=UploadResponse,
    responses={
        200: {"description": "File uploaded successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request (bad path, invalid file)"},
        413: {"model": ErrorResponse, "description": "File exceeds 15 MB size limit"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Upload a file to a case folder",
    description="""
    Upload a file to a specific case folder with size validation and security checks.

    **Features:**
    - Maximum file size: 15 MB
    - Case-scoped storage: files stored in public/documents/{caseId}/{folderId}/
    - Filename sanitization to prevent path traversal attacks
    - Automatic folder creation if needed

    **Default folder:** If folder_id is not provided, files are stored in the "uploads" folder.

    **Duplicate handling:** Use the `rename_to` parameter to specify an alternative filename
    when uploading a file that would overwrite an existing file.

    **Security:**
    - Path traversal prevention (no ../ allowed)
    - Filename sanitization (special characters removed)
    - Case directory validation
    """,
)
async def upload_file(
    file: UploadFile = File(..., description="The file to upload"),
    case_id: str = Form(..., description="Case ID (e.g., ACTE-2024-001)"),
    folder_id: str = Form(default="uploads", description="Target folder ID (default: uploads)"),
    rename_to: Optional[str] = Form(default=None, description="Alternative filename (for duplicate handling)"),
) -> UploadResponse:
    """
    Upload a file to a specific case folder.

    Args:
        file: The uploaded file from multipart/form-data
        case_id: The case ID where the file should be stored
        folder_id: The folder ID within the case (defaults to "uploads")
        rename_to: Optional alternative filename (used when handling duplicates)

    Returns:
        UploadResponse: Upload result with file path and metadata

    Raises:
        HTTPException: If validation fails or upload error occurs
    """
    logger.info(f"Received upload request: {file.filename} for case {case_id}, folder {folder_id}, rename_to={rename_to}")

    try:
        # Import file service functions
        from backend.services.file_service import (
            validate_file_size,
            sanitize_filename,
            validate_case_path,
            create_folder_if_needed,
            save_uploaded_file
        )

        # Read file contents
        file_contents = await file.read()
        file_size = len(file_contents)

        # Validate file size (15 MB limit)
        validate_file_size(file_size)

        # Determine filename: use rename_to if provided, otherwise use original
        original_filename = file.filename or "uploaded_file"
        filename_to_use = rename_to if rename_to else original_filename

        # Sanitize filename to prevent security issues
        safe_filename = sanitize_filename(filename_to_use)

        # Validate case path to prevent path traversal
        validate_case_path(case_id, folder_id)

        # Construct target path
        target_dir = Path("public") / "documents" / case_id / folder_id
        target_path = target_dir / safe_filename

        # Create folder if it doesn't exist
        create_folder_if_needed(target_dir)

        # Save the file
        save_uploaded_file(target_path, file_contents)

        # Construct relative path for frontend
        relative_path = f"documents/{case_id}/{folder_id}/{safe_filename}"

        logger.info(f"Successfully uploaded {safe_filename} ({file_size} bytes) to {relative_path}")

        return UploadResponse(
            success=True,
            file_path=relative_path,
            file_name=safe_filename,
            size=file_size,
            message=f"File '{safe_filename}' uploaded successfully",
        )

    except ValueError as e:
        # Validation errors (size limit, invalid paths)
        logger.warning(f"Upload validation failed for {file.filename}: {str(e)}")

        # Check if it's a size limit error
        if "15 MB" in str(e) or "size limit" in str(e).lower():
            raise HTTPException(
                status_code=413,
                detail={
                    "error": "File too large",
                    "detail": str(e),
                    "file_name": file.filename,
                }
            )

        # Other validation errors
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Validation failed",
                "detail": str(e),
                "file_name": file.filename,
            }
        )

    except OSError as e:
        # File system errors
        logger.error(f"File system error during upload: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "File system error",
                "detail": "Failed to save file. Please try again or contact support.",
                "file_name": file.filename,
            }
        )

    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error during upload: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "detail": str(e),
                "file_name": file.filename,
            }
        )


@router.delete(
    "/{case_id}/{folder_id}/{filename}",
    response_model=DeleteResponse,
    responses={
        200: {"description": "File deleted successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request (bad path)"},
        403: {"model": ErrorResponse, "description": "Access denied (path traversal attempt)"},
        404: {"model": ErrorResponse, "description": "File not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Delete a file from a case folder",
    description="""
    Delete a file from a specific case folder with security validation.

    **Security:**
    - Path traversal prevention (validates resolved path stays within case directory)
    - Case ID and folder ID format validation
    - Filename sanitization

    **Note:** This endpoint is intended for files in the "uploads" folder.
    Deleting files from system folders may affect case functionality.
    """,
)
async def delete_file_endpoint(
    case_id: str,
    folder_id: str,
    filename: str,
) -> DeleteResponse:
    """
    Delete a file from a case folder.

    Args:
        case_id: The case ID (e.g., ACTE-2024-001)
        folder_id: The folder ID (e.g., uploads)
        filename: The name of the file to delete

    Returns:
        DeleteResponse: Deletion result with success status

    Raises:
        HTTPException: If validation fails or deletion error occurs
    """
    logger.info(f"Received delete request: {filename} from case {case_id}, folder {folder_id}")

    try:
        # Import file service function
        from backend.services.file_service import delete_file

        # Delete the file (includes security validation)
        delete_file(case_id, folder_id, filename)

        logger.info(f"Successfully deleted {filename} from {case_id}/{folder_id}")

        return DeleteResponse(
            success=True,
            message=f"File '{filename}' deleted successfully",
            file_name=filename,
        )

    except ValueError as e:
        # Path validation errors (including path traversal attempts)
        error_msg = str(e)
        logger.warning(f"Delete validation failed for {filename}: {error_msg}")

        # Check if it's a security/access denied error
        if "access denied" in error_msg.lower() or "invalid" in error_msg.lower():
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Access denied",
                    "detail": error_msg,
                    "file_name": filename,
                }
            )

        # Other validation errors
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Validation failed",
                "detail": error_msg,
                "file_name": filename,
            }
        )

    except FileNotFoundError as e:
        logger.warning(f"File not found for deletion: {filename}")
        raise HTTPException(
            status_code=404,
            detail={
                "error": "File not found",
                "detail": str(e),
                "file_name": filename,
            }
        )

    except PermissionError as e:
        logger.error(f"Permission denied when deleting {filename}: {str(e)}")
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Permission denied",
                "detail": str(e),
                "file_name": filename,
            }
        )

    except OSError as e:
        logger.error(f"File system error during deletion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "File system error",
                "detail": "Failed to delete file. Please try again or contact support.",
                "file_name": filename,
            }
        )

    except Exception as e:
        logger.error(f"Unexpected error during deletion: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "detail": str(e),
                "file_name": filename,
            }
        )


class FileExistsResponse(BaseModel):
    """
    Response model for file existence check endpoint.

    Attributes:
        exists: Whether the file exists
        file_name: The sanitized filename checked
        suggested_name: If file exists, a suggested unique filename
    """
    exists: bool
    file_name: str
    suggested_name: Optional[str] = None


@router.get(
    "/exists/{case_id}/{folder_id}/{filename}",
    response_model=FileExistsResponse,
    responses={
        200: {"description": "File existence check completed"},
        400: {"model": ErrorResponse, "description": "Invalid request (bad path)"},
    },
    summary="Check if a file exists in a case folder",
    description="""
    Check if a file already exists in a specific case folder.
    If the file exists, returns a suggested unique filename with a numeric suffix.

    **Use case:** Call this endpoint before uploading to detect duplicates
    and give the user options to rename or cancel.
    """,
)
async def check_file_exists_endpoint(
    case_id: str,
    folder_id: str,
    filename: str,
) -> FileExistsResponse:
    """
    Check if a file exists in a case folder.

    Args:
        case_id: The case ID (e.g., ACTE-2024-001)
        folder_id: The folder ID (e.g., uploads)
        filename: The name of the file to check

    Returns:
        FileExistsResponse: Existence status and suggested unique name if exists
    """
    logger.info(f"Checking file existence: {filename} in {case_id}/{folder_id}")

    try:
        from backend.services.file_service import (
            check_file_exists,
            generate_unique_filename,
            sanitize_filename,
        )

        # Sanitize filename first
        safe_filename = sanitize_filename(filename)

        # Check if file exists
        exists = check_file_exists(case_id, folder_id, safe_filename)

        # Generate suggested name if file exists
        suggested_name = None
        if exists:
            suggested_name = generate_unique_filename(case_id, folder_id, safe_filename)

        return FileExistsResponse(
            exists=exists,
            file_name=safe_filename,
            suggested_name=suggested_name,
        )

    except ValueError as e:
        logger.warning(f"File exists check validation failed: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Validation failed",
                "detail": str(e),
                "file_name": filename,
            }
        )

    except Exception as e:
        logger.error(f"Unexpected error during file exists check: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "detail": str(e),
                "file_name": filename,
            }
        )


@router.get(
    "/health",
    summary="File service health check",
    description="Check the health status of the file upload service.",
)
async def files_health_check() -> JSONResponse:
    """
    Health check endpoint for file service.

    Returns:
        JSONResponse: Service health status and configuration.
    """
    # Check if public/documents directory exists
    docs_dir = Path("public") / "documents"
    storage_available = docs_dir.exists() and docs_dir.is_dir()

    return JSONResponse(
        content={
            "service": "files",
            "status": "ready" if storage_available else "degraded",
            "features": {
                "upload": True,
                "max_file_size_mb": 15,
                "storage_path": "public/documents/",
            },
            "storage": {
                "available": storage_available,
                "path": str(docs_dir.absolute()),
            }
        },
        status_code=200 if storage_available else 503
    )
