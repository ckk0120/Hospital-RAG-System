from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Callable

from app.core.config import get_settings


@dataclass
class RAGResult:
    success: bool
    answer: str
    sources: list[dict]
    error: str | None = None
    latency_ms: float | None = None


class HospitalRAGService:
    def __init__(self, retriever: Callable[[str, int], list[dict]] | None = None) -> None:
        self.settings = get_settings()
        self._retriever = retriever

    def ask(self, question: str, top_k: int = 3) -> RAGResult:
        start = perf_counter()
        question = (question or "").strip()
        if not question:
            return RAGResult(False, "问题不能为空。", [], "empty_question", 0.0)

        retriever = self._retriever
        if retriever is None:
            from app.services.vector_store import retrieve_context

            retriever = retrieve_context

        contexts = retriever(question, top_k)
        latency_ms = round((perf_counter() - start) * 1000, 2)

        if not contexts:
            return RAGResult(
                False,
                "抱歉，暂时没有找到可靠答案。",
                [],
                "no_relevant_context",
                latency_ms,
            )

        best = contexts[0]
        if best["confidence"] < self.settings.retrieval_threshold:
            return RAGResult(
                False,
                "抱歉，暂时没有找到足够可靠的答案。",
                contexts,
                "low_confidence",
                latency_ms,
            )

        answer = best.get("answer") or best.get("content", "")[:300]
        return RAGResult(True, answer, contexts, None, latency_ms)
