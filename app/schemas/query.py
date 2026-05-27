from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="用户问题")
    top_k: int = Field(default=3, ge=1, le=10, description="返回结果数量")


class SourceItem(BaseModel):
    content: str
    question: Optional[str] = None
    answer: Optional[str] = None
    source: str = ""
    title: Optional[str] = None
    department: Optional[str] = None
    score: float = 0.0
    confidence: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class QueryResponse(BaseModel):
    success: bool
    answer: str
    sources: list[SourceItem] = Field(default_factory=list)
    error: Optional[str] = None
    latency_ms: Optional[float] = None
