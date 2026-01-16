"""
Documents API for BAMF AI Case Management System.

This module provides REST endpoints for retrieving document trees and managing
document metadata through the document registry system.

Endpoints:
    GET /api/documents/tree/{case_id}: Get the complete document tree for a case
    GET /api/documents/all: Get all documents across all cases
    GET /api/documents/health: Document service health check
    POST /api/documents/extract-pdf-text: Extract text from a PDF document
"""

import logging
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.services.pdf_service import get_pdf_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents")


# ============================================================================
# Response Models
# ============================================================================

class DocumentResponse(BaseModel):
    """
    Response model for a single document.

    Maps the internal document registry format to the frontend-expected format.
    """
    id: str = Field(..., description="Document ID")
    name: str = Field(..., description="Document filename")
    type: str = Field(..., description="File type/extension")
    size: str = Field(default="0 KB", description="File size")
    uploadedAt: str = Field(..., description="Upload timestamp")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")
    caseId: str = Field(..., description="Case ID")
    folderId: str | None = Field(None, description="Folder ID")
    renders: List[Dict] = Field(default_factory=list, description="S5-006: Document renders (original, anonymized, translated, etc.)")


class LocalizedName(BaseModel):
    """Localized folder name."""
    de: str = Field(..., description="German name")
    en: str = Field(..., description="English name")


class FolderResponse(BaseModel):
    """Response model for a folder containing documents."""
    id: str = Field(..., description="Folder ID")
    name: str = Field(..., description="Folder display name (localized)")
    nameKey: str = Field(default="", description="Translation key for folder name")
    localizedName: Optional[LocalizedName] = Field(None, description="All localized names")
    documents: List[DocumentResponse] = Field(default_factory=list, description="Documents in folder")
    subfolders: List["FolderResponse"] = Field(default_factory=list, description="Nested subfolders")
    isExpanded: bool = Field(default=True, description="Whether folder is expanded in UI")
    mandatory: bool = Field(default=False, description="Whether folder is required")
    order: int = Field(default=999, description="Display order")


class DocumentTreeResponse(BaseModel):
    """
    Response model for the complete document tree of a case.

    Contains all folders and their documents, plus any root-level documents.
    """
    folders: List[FolderResponse] = Field(default_factory=list, description="All folders in the case")
    rootDocuments: List[DocumentResponse] = Field(default_factory=list, description="Documents at root level")


# ============================================================================
# API Endpoints
# ============================================================================

@router.get(
    "/tree/{case_id}",
    response_model=DocumentTreeResponse,
    responses={
        200: {"description": "Document tree retrieved successfully"},
        404: {"description": "Case not found"},
        500: {"description": "Internal server error"},
    },
    summary="Get document tree for a case",
    description="""
    Retrieve the complete document tree for a specific case, including all folders
    and documents organized in a hierarchical structure.

    **Use case:** Called by the frontend on app startup to load the document structure
    from the persisted manifest.

    **Returns:**
    - All folders with their documents
    - Root-level documents (not in any folder)
    - Document metadata including upload time, file type, etc.
    """,
)
async def get_document_tree(case_id: str, language: str = 'de') -> DocumentTreeResponse:
    """
    Get the complete document tree for a case.

    Args:
        case_id: The case ID (e.g., "ACTE-2024-001")
        language: Language code for folder names ('de' or 'en'). Defaults to 'de'.

    Returns:
        DocumentTreeResponse: The document tree with folders and documents.

    Raises:
        HTTPException: If retrieval fails.
    """
    logger.info(f"Retrieving document tree for case {case_id} (language={language})")

    try:
        from backend.services.document_registry import build_document_tree

        # Build the document tree from the registry with language support
        tree = build_document_tree(case_id, language)

        # Transform registry format to frontend format
        folders = []
        for folder in tree.get('folders', []):
            # Transform documents in this folder
            documents = [
                _transform_document(doc) for doc in folder.get('documents', [])
            ]

            # Build localized name object if available
            localized_name = None
            if folder.get('localizedName'):
                localized_name = LocalizedName(
                    de=folder['localizedName'].get('de', folder['name']),
                    en=folder['localizedName'].get('en', folder['name'])
                )

            folders.append(FolderResponse(
                id=folder['id'],
                name=folder['name'],
                nameKey=folder.get('nameKey', folder['id']),
                localizedName=localized_name,
                documents=documents,
                subfolders=folder.get('subfolders', []),
                isExpanded=folder.get('isExpanded', True),
                mandatory=folder.get('mandatory', False),
                order=folder.get('order', 999)
            ))

        # Transform root documents
        root_documents = [
            _transform_document(doc) for doc in tree.get('rootDocuments', [])
        ]

        logger.info(
            f"Successfully retrieved document tree for {case_id}: "
            f"{len(folders)} folders, {len(root_documents)} root documents"
        )

        return DocumentTreeResponse(
            folders=folders,
            rootDocuments=root_documents
        )

    except Exception as e:
        logger.error(f"Failed to retrieve document tree for {case_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to retrieve document tree",
                "detail": str(e),
                "case_id": case_id,
            }
        )


@router.get(
    "/all",
    responses={
        200: {"description": "All documents retrieved successfully"},
        500: {"description": "Internal server error"},
    },
    summary="Get all documents across all cases",
    description="""
    Retrieve all documents from the registry across all cases.

    **Use case:** Administrative view or debugging.
    """,
)
async def get_all_documents() -> JSONResponse:
    """
    Get all documents from the registry.

    Returns:
        JSONResponse: List of all document entries.
    """
    logger.info("Retrieving all documents")

    try:
        from backend.services.document_registry import get_all_documents

        documents = get_all_documents()

        logger.info(f"Successfully retrieved {len(documents)} documents")

        return JSONResponse(
            content={
                "success": True,
                "count": len(documents),
                "documents": documents,
            },
            status_code=200
        )

    except Exception as e:
        logger.error(f"Failed to retrieve all documents: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to retrieve documents",
                "detail": str(e),
            }
        )


@router.get(
    "/health",
    summary="Document service health check",
    description="Check the health status of the document registry service.",
)
async def documents_health_check() -> JSONResponse:
    """
    Health check endpoint for document service.

    Returns:
        JSONResponse: Service health status.
    """
    try:
        from backend.services.document_registry import load_manifest
        from pathlib import Path

        # Try to load manifest
        registry = load_manifest()
        manifest_ok = True
        document_count = len(registry.documents)

        # Check if documents directory exists
        from backend.config import DOCUMENTS_BASE_PATH
        docs_dir = Path(DOCUMENTS_BASE_PATH)
        storage_available = docs_dir.exists() and docs_dir.is_dir()

        return JSONResponse(
            content={
                "service": "documents",
                "status": "ready" if (manifest_ok and storage_available) else "degraded",
                "features": {
                    "document_tree": True,
                    "manifest_persistence": manifest_ok,
                    "filesystem_reconciliation": True,
                },
                "manifest": {
                    "loaded": manifest_ok,
                    "document_count": document_count,
                },
                "storage": {
                    "available": storage_available,
                    "path": str(docs_dir.absolute()),
                }
            },
            status_code=200 if (manifest_ok and storage_available) else 503
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return JSONResponse(
            content={
                "service": "documents",
                "status": "unhealthy",
                "error": str(e),
            },
            status_code=503
        )


# ============================================================================
# Helper Functions
# ============================================================================

def _transform_document(registry_doc: Dict) -> DocumentResponse:
    """
    Transform a document from registry format to frontend format.

    Args:
        registry_doc: Document entry from the registry.

    Returns:
        DocumentResponse: Transformed document for frontend.
    """
    from pathlib import Path

    file_name = registry_doc.get('fileName', 'unknown')
    file_path = registry_doc.get('filePath', '')

    # Extract file extension
    file_ext = Path(file_name).suffix.lstrip('.').lower() or 'unknown'

    # Calculate file size if file exists
    file_size = "0 KB"
    if file_path:
        try:
            path = Path(file_path)
            if path.exists():
                size_bytes = path.stat().st_size
                if size_bytes < 1024:
                    file_size = f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    file_size = f"{size_bytes / 1024:.1f} KB"
                else:
                    file_size = f"{size_bytes / (1024 * 1024):.1f} MB"
        except Exception as e:
            logger.warning(f"Failed to get file size for {file_path}: {e}")

    return DocumentResponse(
        id=registry_doc.get('documentId', ''),
        name=file_name,
        type=file_ext,
        size=file_size,
        uploadedAt=registry_doc.get('uploadedAt', ''),
        metadata={
            "fileHash": registry_doc.get('fileHash', ''),
            "filePath": file_path,
            "renderCount": str(len(registry_doc.get('renders', []))),
        },
        caseId=registry_doc.get('caseId', ''),
        folderId=registry_doc.get('folderId'),
        renders=registry_doc.get('renders', [])  # S5-006: Include renders array
    )


# ============================================================================
# S5-003: PDF Text Extraction Endpoint
# ============================================================================

class PDFTextExtractionRequest(BaseModel):
    """Request model for PDF text extraction."""
    documentPath: str = Field(..., description="Path to the PDF document")


class PDFTextExtractionResponse(BaseModel):
    """Response model for PDF text extraction."""
    text: str = Field(..., description="Extracted text from PDF")
    pageCount: int = Field(..., description="Number of pages in PDF")
    charCount: int = Field(..., description="Number of characters extracted")


@router.post("/extract-pdf-text", response_model=PDFTextExtractionResponse)
async def extract_pdf_text(request: PDFTextExtractionRequest):
    """
    Extract text content from a PDF document.

    This endpoint uses the PDF service to extract all text from a PDF file.
    Useful for displaying PDF content in the document viewer and enabling
    search functionality.

    Args:
        request: Request with document path

    Returns:
        PDFTextExtractionResponse: Extracted text and metadata

    Raises:
        HTTPException 404: If PDF file not found
        HTTPException 500: If text extraction fails
    """
    try:
        pdf_service = get_pdf_service()

        # Extract text from PDF
        text = pdf_service.extract_text(request.documentPath)

        # Get page count
        page_count = pdf_service.get_page_count(request.documentPath)

        logger.info(
            f"Extracted {len(text)} characters from {page_count} pages: {request.documentPath}"
        )

        return PDFTextExtractionResponse(
            text=text,
            pageCount=page_count,
            charCount=len(text)
        )

    except FileNotFoundError:
        logger.error(f"PDF file not found: {request.documentPath}")
        raise HTTPException(
            status_code=404,
            detail=f"PDF file not found: {request.documentPath}"
        )

    except Exception as e:
        logger.error(f"Failed to extract PDF text: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract PDF text: {str(e)}"
        )


# ============================================================================
# S5-008: Email Parsing Endpoint
# ============================================================================

class EmailParseRequest(BaseModel):
    """Request model for email parsing endpoint."""
    documentPath: str = Field(..., description="Path to .eml file")


class EmailParseResponse(BaseModel):
    """Response model for email parsing endpoint."""
    from_addr: str = Field(..., description="Sender email and name")
    to_addr: str = Field(..., description="Recipient email(s)")
    subject: str = Field(..., description="Email subject")
    date: str = Field(..., description="Email date")
    body_text: str = Field(..., description="Plain text body")
    body_html: Optional[str] = Field(None, description="HTML body if available")
    attachments: List[Dict[str, Any]] = Field(default_factory=list, description="Attachment metadata")


@router.post("/parse-email", response_model=EmailParseResponse)
async def parse_email(request: EmailParseRequest):
    """
    Parse an .eml file and extract email data.

    Supports multiple character encodings including Arabic (ISO-8859-6).
    Extracts headers, body content (plain text and HTML), and attachment metadata.

    Args:
        request: Request with document path to .eml file

    Returns:
        EmailParseResponse: Parsed email data

    Raises:
        HTTPException 404: If email file not found
        HTTPException 500: If email parsing fails

    Example:
        POST /api/documents/parse-email
        {
          "documentPath": "public/documents/ACTE-2024-001/emails/Email.eml"
        }
    """
    try:
        from backend.services.email_service import get_email_service

        email_service = get_email_service()

        # Parse the email file
        email_data = email_service.parse_eml_file(request.documentPath)

        # Convert attachments to dict format
        attachments_list = [
            {
                "filename": att.filename,
                "content_type": att.content_type,
                "size": att.size
            }
            for att in email_data.attachments
        ]

        logger.info(
            f"Parsed email: {email_data.subject} "
            f"(body: {len(email_data.body_text)} chars)"
        )

        return EmailParseResponse(
            from_addr=email_data.from_addr,
            to_addr=email_data.to_addr,
            subject=email_data.subject,
            date=email_data.date,
            body_text=email_data.body_text,
            body_html=email_data.body_html,
            attachments=attachments_list
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Email file not found: {request.documentPath}"
        )

    except Exception as e:
        logger.error(f"Failed to parse email: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse email: {str(e)}"
        )
