from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.query import QueryRequest, QueryResponse, SourceItem
from app.services.rag_service import HospitalRAGService
from app.services.vector_store import get_vector_store


router = APIRouter(prefix="/api/v1")
rag_service = HospitalRAGService()


@router.get("/health")
def health():
    try:
        store = get_vector_store()
        count = store._collection.count()
        loaded = True
    except Exception:
        count = 0
        loaded = False

    return {
        "status": "ok" if loaded else "degraded",
        "database_loaded": loaded,
        "document_count": count,
    }


@router.get("/stats")
def stats():
    try:
        store = get_vector_store()
        return {
            "total_documents": store._collection.count(),
            "collection_name": store._collection.name,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    result = rag_service.ask(request.question, request.top_k)
    sources = [SourceItem(**item) for item in result.sources]
    return QueryResponse(
        success=result.success,
        answer=result.answer,
        sources=sources,
        error=result.error,
        latency_ms=result.latency_ms,
    )

