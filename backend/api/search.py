"""
S5-003: Search API - Semantic Search Endpoints.

This module provides REST API endpoints for semantic search functionality.
Integrates with Gemini AI service for intelligent document search with
cross-language support.

Features:
    - Semantic search using natural language queries
    - Automatic language detection for queries and documents
    - PDF text extraction integration
    - Cross-language search support (e.g., German query → English document)
    - Text highlighting with position information

Endpoints:
    - POST /api/search/semantic: Perform semantic search on document content
"""

import logging
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.services.gemini_service import GeminiService
from backend.services.pdf_service import get_pdf_service
from backend.tools.language_detector import (
    detect_language,
    detect_query_and_document_languages,
    is_cross_language_search,
    get_language_name
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize services
gemini_service = GeminiService()
pdf_service = get_pdf_service()


class SemanticSearchRequest(BaseModel):
    """
    Request model for semantic search endpoint.

    Attributes:
        query: Natural language search query
        documentContent: Full text content of the document (for non-PDF)
        documentType: Type of document (pdf, txt, etc.)
        documentPath: Path to document file (for PDF extraction)
        queryLanguage: Optional language code for query (auto-detected if not provided)
        documentLanguage: Optional language code for document (auto-detected if not provided)
    """
    query: str = Field(..., description="Natural language search query", min_length=1)
    documentContent: Optional[str] = Field(None, description="Document text content")
    documentType: str = Field(..., description="Document type (pdf, txt, etc.)")
    documentPath: Optional[str] = Field(None, description="Path to PDF document file")
    queryLanguage: Optional[str] = Field(None, description="Query language (ISO 639-1)")
    documentLanguage: Optional[str] = Field(None, description="Document language (ISO 639-1)")


class SearchHighlight(BaseModel):
    """
    Model for a single search highlight result.

    Attributes:
        start: Starting character position
        end: Ending character position
        relevance: Relevance score (0.0-1.0)
        matchedText: The exact text that matched
        context: Explanation of why this matches
    """
    start: int
    end: int
    relevance: float
    matchedText: str
    context: str


class SemanticSearchResponse(BaseModel):
    """
    Response model for semantic search endpoint.

    Attributes:
        highlights: Array of highlighted text segments
        count: Total number of matches found
        matchSummary: Brief summary of search results
        queryLanguage: Detected or provided query language
        documentLanguage: Detected or provided document language
        isCrossLanguage: Whether this is a cross-language search
    """
    highlights: list[SearchHighlight]
    count: int
    matchSummary: str
    queryLanguage: str
    documentLanguage: str
    isCrossLanguage: bool


@router.post("/semantic", response_model=SemanticSearchResponse)
async def semantic_search(request: SemanticSearchRequest) -> SemanticSearchResponse:
    """
    Perform semantic search on document content using Gemini AI.

    This endpoint analyzes document content and finds text passages that
    semantically match the user's natural language query. Supports cross-language
    search where query and document can be in different languages.

    Args:
        request: Search request with query and document information

    Returns:
        SemanticSearchResponse: Search results with highlights and metadata

    Raises:
        HTTPException 400: If request validation fails
        HTTPException 404: If PDF file not found
        HTTPException 500: If search processing fails

    Example:
        POST /api/search/semantic
        {
          "query": "passport number",
          "documentContent": "Reisepassnummer: 123456789",
          "documentType": "txt",
          "queryLanguage": "en",
          "documentLanguage": "de"
        }
    """
    try:
        logger.info(
            f"Semantic search request - "
            f"query: '{request.query}', "
            f"doc_type: {request.documentType}"
        )

        # Step 1: Get document content
        document_text = ""

        if request.documentType.lower() == "pdf":
            # Extract text from PDF
            if not request.documentPath:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="documentPath is required for PDF documents"
                )

            try:
                document_text = pdf_service.extract_text(request.documentPath)
                logger.info(
                    f"Extracted {len(document_text)} chars from PDF: {request.documentPath}"
                )

            except FileNotFoundError:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"PDF file not found: {request.documentPath}"
                )

            except Exception as e:
                logger.error(f"PDF extraction failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to extract PDF text: {str(e)}"
                )

        else:
            # Use provided document content
            if not request.documentContent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="documentContent is required for non-PDF documents"
                )

            document_text = request.documentContent

        # Validate document text
        if not document_text or not document_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document is empty or contains no extractable text"
            )

        # Step 2: Detect languages if not provided
        query_lang = request.queryLanguage
        doc_lang = request.documentLanguage

        if not query_lang or not doc_lang:
            detected_q_lang, detected_d_lang = detect_query_and_document_languages(
                request.query,
                document_text
            )

            query_lang = query_lang or detected_q_lang
            doc_lang = doc_lang or detected_d_lang

        # Check if cross-language search
        is_cross = is_cross_language_search(query_lang, doc_lang)

        if is_cross:
            logger.info(
                f"Cross-language search: {get_language_name(query_lang)} → "
                f"{get_language_name(doc_lang)}"
            )

        # Step 3: Perform semantic search using Gemini
        highlights_raw = await gemini_service.semantic_search(
            query=request.query,
            document_text=document_text,
            query_lang=query_lang,
            doc_lang=doc_lang
        )

        # Step 4: Convert to response format
        highlights = [
            SearchHighlight(
                start=h['start_position'],
                end=h['end_position'],
                relevance=h.get('relevance_score', 0.5),
                matchedText=h['matched_text'],
                context=h.get('context', 'Semantic match')
            )
            for h in highlights_raw
        ]

        # Generate match summary
        count = len(highlights)

        if count == 0:
            match_summary = "No matches found"
        elif count == 1:
            match_summary = "Found 1 relevant passage"
        else:
            match_summary = f"Found {count} relevant passages"

        if is_cross:
            match_summary += f" (cross-language: {get_language_name(query_lang)} → {get_language_name(doc_lang)})"

        logger.info(
            f"Search complete - {count} matches, "
            f"query_lang: {query_lang}, "
            f"doc_lang: {doc_lang}"
        )

        return SemanticSearchResponse(
            highlights=highlights,
            count=count,
            matchSummary=match_summary,
            queryLanguage=query_lang,
            documentLanguage=doc_lang,
            isCrossLanguage=is_cross
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        logger.error(f"Unexpected error in semantic search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/health")
async def search_health():
    """
    Health check endpoint for search service.

    Returns:
        dict: Service health status and capabilities

    Example:
        GET /api/search/health
    """
    return {
        "status": "healthy",
        "service": "semantic_search",
        "gemini_initialized": gemini_service.is_initialized(),
        "pdf_support": True,
        "cross_language_support": True
    }
