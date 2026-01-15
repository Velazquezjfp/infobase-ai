"""
Context API for BAMF AI Case Management System.

S5-011: Provides endpoints for retrieving document tree views and context information.

Endpoints:
    GET /api/context/tree/{case_id}: Get document tree view for a case
    GET /api/context/case/{case_id}: Get full case context with folder contexts
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/context")


class TreeViewResponse(BaseModel):
    """
    Response model for tree view endpoint.

    Attributes:
        treeView: Hierarchical text representation of document tree
        folders: List of folder display names
        documentCount: Total number of documents in the case
    """
    treeView: str = Field(..., description="Hierarchical tree representation")
    folders: List[str] = Field(..., description="List of folder names")
    documentCount: int = Field(..., description="Total document count")


@router.get(
    "/tree/{case_id}",
    response_model=TreeViewResponse,
    responses={
        200: {"description": "Tree view retrieved successfully"},
        404: {"description": "Case not found"},
        500: {"description": "Internal server error"},
    },
    summary="Get document tree view for a case",
    description="""
    Retrieve the document tree view for a specific case.

    **S5-011: Cascading Context with Document Tree View**

    Returns a hierarchical text representation of all folders and documents
    in the case, formatted with ASCII tree characters (├── └──).

    **Features:**
    - Cached for performance (regenerates on document changes)
    - Includes folder display names from context files
    - Shows empty folders
    - Lists all documents with their original filenames

    **Use cases:**
    - Frontend debugging and tree view display
    - Manual verification of document structure
    - Testing document tree generation
    """,
)
async def get_tree_view(case_id: str) -> TreeViewResponse:
    """
    Get the document tree view for a case.

    Args:
        case_id: The case ID (e.g., ACTE-2024-001)

    Returns:
        TreeViewResponse: Tree view data with folders and document count

    Raises:
        HTTPException: If case not found or generation fails
    """
    logger.info(f"Received tree view request for case: {case_id}")

    try:
        # Import context manager and document registry
        from backend.services.context_manager import generate_document_tree
        from backend.services.document_registry import get_documents_by_case, build_document_tree

        # Generate tree view (uses cache if available)
        tree_view = generate_document_tree(case_id)

        # Get document count
        documents = get_documents_by_case(case_id)
        document_count = len(documents)

        # Get folder list
        tree_data = build_document_tree(case_id)
        folders = tree_data.get('folders', [])
        folder_names = [folder.get('name', folder.get('id', 'Unknown')) for folder in folders]

        logger.info(
            f"Generated tree view for {case_id}: "
            f"{document_count} documents, {len(folder_names)} folders"
        )

        return TreeViewResponse(
            treeView=tree_view,
            folders=folder_names,
            documentCount=document_count
        )

    except FileNotFoundError:
        logger.warning(f"Case not found: {case_id}")
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Case not found",
                "case_id": case_id,
            }
        )

    except Exception as e:
        logger.error(f"Failed to generate tree view for {case_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to generate tree view",
                "detail": str(e),
                "case_id": case_id,
            }
        )


@router.get(
    "/case/{case_id}",
    responses={
        200: {"description": "Full case context retrieved successfully"},
        404: {"description": "Case not found"},
        500: {"description": "Internal server error"},
    },
    summary="Get full case context including folder contexts",
    description="""
    Retrieve the complete case context for transparency and AI context awareness.

    **Case Context Transparency Feature**

    Returns the full case-level context including:
    - Case information (id, type, name, description)
    - Applicant information
    - Applicable regulations
    - Required documents with validation rules
    - Validation rules
    - Common issues and suggestions
    - All folder contexts with expected documents and criteria

    **Purpose:**
    This endpoint enables users to see exactly what context information
    is available to the AI assistant, promoting transparency.
    """,
)
async def get_case_context(case_id: str) -> Dict[str, Any]:
    """
    Get the full case context including all folder contexts.

    Args:
        case_id: The case ID (e.g., ACTE-2024-001)

    Returns:
        Dict containing full case context with folder contexts

    Raises:
        HTTPException: If case not found or loading fails
    """
    logger.info(f"Received case context request for case: {case_id}")

    try:
        from backend.services.context_manager import ContextManager
        import json

        # Initialize context manager
        context_manager = ContextManager()

        # Load case context
        case_context = context_manager.load_case_context(case_id)

        # Load all folder contexts
        folders_path = Path(context_manager.cases_path) / case_id / "folders"
        folder_contexts = []

        if folders_path.exists():
            for folder_file in folders_path.glob("*.json"):
                try:
                    with open(folder_file, 'r', encoding='utf-8') as f:
                        folder_ctx = json.load(f)
                        folder_contexts.append(folder_ctx)
                        logger.debug(f"Loaded folder context: {folder_ctx.get('folderId')}")
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse folder context {folder_file}: {e}")
                except Exception as e:
                    logger.warning(f"Failed to load folder context {folder_file}: {e}")

        # Sort folders alphabetically by name
        folder_contexts.sort(key=lambda x: x.get('folderName', x.get('folderId', '')))

        # Add folders to case context
        case_context['folders'] = folder_contexts

        logger.info(
            f"Loaded case context for {case_id}: "
            f"{len(case_context.get('regulations', []))} regulations, "
            f"{len(case_context.get('requiredDocuments', []))} required documents, "
            f"{len(folder_contexts)} folder contexts"
        )

        return case_context

    except FileNotFoundError:
        logger.warning(f"Case context not found: {case_id}")
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Case context not found",
                "case_id": case_id,
            }
        )

    except Exception as e:
        logger.error(f"Failed to load case context for {case_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to load case context",
                "detail": str(e),
                "case_id": case_id,
            }
        )
