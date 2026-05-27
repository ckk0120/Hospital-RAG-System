from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import get_settings
from app.services.scoring import extract_qa, normalize_distance


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    settings = get_settings()
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        model_kwargs={"device": settings.device},
    )


@lru_cache(maxsize=1)
def get_vector_store() -> Chroma:
    settings = get_settings()
    db_dir = Path(settings.chroma_db_dir)
    if not db_dir.exists():
        raise FileNotFoundError(f"向量库目录不存在: {db_dir}")

    return Chroma(
        collection_name=settings.chroma_collection_name,
        persist_directory=str(db_dir),
        embedding_function=get_embeddings(),
    )


def retrieve_context(question: str, top_k: int = 3) -> list[dict]:
    question = (question or "").strip()
    if not question:
        return []

    settings = get_settings()
    if top_k < 1:
        top_k = settings.top_k_default
    top_k = min(top_k, 10)

    try:
        store = get_vector_store()
        results = store.similarity_search_with_score(question, k=top_k)
    except Exception:
        return []

    contexts: list[dict] = []
    for doc, score in results:
        content = doc.page_content or ""
        metadata = doc.metadata or {}
        q_text, a_text = extract_qa(content)

        raw_score = float(score)
        confidence = round(normalize_distance(raw_score), 4)
        contexts.append(
            {
                "content": content,
                "question": q_text,
                "answer": a_text,
                "source": metadata.get("source", ""),
                "title": metadata.get("title"),
                "department": metadata.get("department"),
                "score": round(raw_score, 4),
                "confidence": confidence,
                "metadata": metadata,
            }
        )

    return contexts
