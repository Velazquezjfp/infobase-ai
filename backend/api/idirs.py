"""
IDIRS Proxy API for hybrid search and RAG queries.

Provides endpoints to proxy requests to the IDIRS OpenSearch API,
with optional Gemini AI analysis for RAG confidence scoring.

Endpoints:
    POST /api/idirs/search: Hybrid document search (BM25 + kNN)
    POST /api/idirs/rag: RAG query with AI confidence analysis
"""

import logging
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.config import ENABLE_DOCUMENT_SEARCH, IDIRS_BASE_URL, IDIRS_TIMEOUT, RAG_CONFIDENCE_THRESHOLD
from backend.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/idirs")


# ============================================================================
# Request / Response models
# ============================================================================

class ErrorResponse(BaseModel):
    error: str
    detail: str


class SearchRequest(BaseModel):
    query: str = Field(..., description="Semantic search query")
    entity_filters: Optional[Dict[str, str]] = Field(None, description="Entity filters (e.g. referenznummer)")
    doc_type_filter: Optional[str] = Field(None, description="Filter by document type")
    top_k: int = Field(5, ge=1, le=50, description="Number of results to return")


class RagRequest(BaseModel):
    doc_ids: List[str] = Field(..., min_length=1, description="Document IDs to query")
    question: str = Field(..., description="Question to answer from documents")
    top_k: int = Field(5, ge=1, le=20, description="Number of chunks per document")
    language: str = Field("de", description="Response language (de/en)")


# ============================================================================
# POST /api/idirs/search
# ============================================================================

@router.post("/search")
async def idirs_search(req: SearchRequest) -> Dict[str, Any]:
    """
    Proxy hybrid search to IDIRS OpenSearch API.

    Sends the query and optional filters to IDIRS /search endpoint,
    returns formatted results with scores.
    """
    if not ENABLE_DOCUMENT_SEARCH:
        return JSONResponse(
            status_code=503,
            content={
                "error": "feature_disabled",
                "detail": "Die Dokumentsuche ist in dieser Demo-Umgebung noch nicht verfügbar.",
            },
        )

    payload: Dict[str, Any] = {
        "query": req.query,
        "top_k": req.top_k,
    }
    if req.entity_filters:
        payload["entity_filters"] = req.entity_filters
    if req.doc_type_filter:
        payload["doc_type_filter"] = req.doc_type_filter

    try:
        async with httpx.AsyncClient(timeout=IDIRS_TIMEOUT) as client:
            response = await client.post(f"{IDIRS_BASE_URL}/search", json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="IDIRS search timed out")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"IDIRS error: {e.response.text}")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Cannot connect to IDIRS service")


# ============================================================================
# POST /api/idirs/rag
# ============================================================================

@router.post("/rag")
async def idirs_rag(req: RagRequest) -> Dict[str, Any]:
    """
    RAG query with AI confidence analysis.

    For each doc_id, calls IDIRS /rag endpoint to retrieve chunks,
    then uses GeminiService to analyze the combined results and
    produce a confidence-rated answer.
    """
    if not ENABLE_DOCUMENT_SEARCH:
        return JSONResponse(
            status_code=503,
            content={
                "error": "feature_disabled",
                "detail": "Die Dokumentsuche ist in dieser Demo-Umgebung noch nicht verfügbar.",
            },
        )

    all_chunks: List[Dict[str, Any]] = []
    all_answers: List[str] = []

    try:
        async with httpx.AsyncClient(timeout=IDIRS_TIMEOUT) as client:
            for doc_id in req.doc_ids:
                rag_payload = {
                    "doc_id": doc_id,
                    "question": req.question,
                    "top_k": req.top_k,
                }
                response = await client.post(f"{IDIRS_BASE_URL}/rag", json=rag_payload)
                response.raise_for_status()
                data = response.json()

                if "chunks" in data:
                    all_chunks.extend(data["chunks"])
                if "answer" in data:
                    all_answers.append(data["answer"])

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="IDIRS RAG timed out")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"IDIRS error: {e.response.text}")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Cannot connect to IDIRS service")

    # Calculate confidence from non-zero chunk scores
    non_zero_scores = [c["score"] for c in all_chunks if c.get("score", 0) > 0]
    confidence = sum(non_zero_scores) / len(non_zero_scores) if non_zero_scores else 0.0
    is_high_confidence = confidence >= RAG_CONFIDENCE_THRESHOLD

    # Build Gemini analysis prompt
    chunks_text = "\n\n".join(
        f"[Chunk score={c.get('score', 0):.2f}] {c.get('text', '')}"
        for c in all_chunks
    )
    rag_answer = "\n\n".join(all_answers) if all_answers else "No answer generated."

    lang_label = "German" if req.language == "de" else "English"
    prompt = f"""You are a document analysis assistant for the BAMF (Federal Office for Migration and Refugees).

Analyze the following RAG results and provide a structured response in {lang_label}.

Question: {req.question}

RAG Answer:
{rag_answer}

Retrieved Chunks:
{chunks_text}

Confidence Score: {confidence:.1%}

Instructions:
- Summarize the answer clearly based on the RAG output and chunks.
- If confidence is high (>= {RAG_CONFIDENCE_THRESHOLD:.0%}), confirm the answer is well-supported by document evidence.
- If confidence is low (< {RAG_CONFIDENCE_THRESHOLD:.0%}), warn that the answer is uncertain and recommend manual document review.
- Respond in {lang_label}.
- Keep the response concise and professional.
"""

    try:
        gemini = GeminiService()
        model = gemini._get_model()
        gemini_response = model.generate_content(prompt)
        analysis = gemini_response.text
    except Exception as e:
        logger.warning(f"Gemini analysis failed, returning raw RAG answer: {e}")
        analysis = rag_answer

    # Build disclaimer
    if req.language == "de":
        disclaimer = (
            "Die Antwort wird durch Dokumentennachweise gut gestützt."
            if is_high_confidence
            else "Die Antwort ist unsicher. Eine manuelle Überprüfung der Dokumente wird empfohlen."
        )
    else:
        disclaimer = (
            "The answer is well-supported by document evidence."
            if is_high_confidence
            else "The answer is uncertain. Manual document review is recommended."
        )

    return {
        "analysis": analysis,
        "confidence": round(confidence, 4),
        "is_high_confidence": is_high_confidence,
        "disclaimer": disclaimer,
        "doc_ids": req.doc_ids,
        "chunk_count": len(all_chunks),
    }
