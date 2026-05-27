from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import get_settings


def _load_json_documents(data_path: Path) -> list[Document]:
    raw = json.loads(data_path.read_text(encoding="utf-8"))
    docs: list[Document] = []

    for item in raw:
        question = item.get("question") or item.get("问题") or item.get("标题") or ""
        answer = item.get("answer") or item.get("标准答案") or item.get("正文") or ""
        keywords = item.get("key-words") or item.get("关键词") or item.get("栏目") or ""
        source = item.get("source") or data_path.name
        title = question[:80] if question else item.get("标题", "")[:80]

        if not (question or answer):
            continue

        content = f"问题：{question}\n答案：{answer}".strip()
        docs.append(
            Document(
                page_content=content,
                metadata={
                    "source": source,
                    "title": title,
                    "department": keywords or "综合科",
                    "question_type": item.get("question_type", "faq"),
                },
            )
        )

    return docs


def _build_embeddings():
    settings = get_settings()
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        model_kwargs={"device": settings.device},
    )


def build_vector_store(
    data_path: Path | None = None,
    force_rebuild: bool = False,
) -> int:
    settings = get_settings()
    data_path = data_path or (Path(__file__).resolve().parents[2] / "data" / "data.json")

    if not data_path.exists():
        raise FileNotFoundError(f"数据文件不存在: {data_path}")

    docs = _load_json_documents(data_path)
    if not docs:
        raise ValueError("没有可用于建库的文档")

    settings.chroma_db_dir.mkdir(parents=True, exist_ok=True)
    embeddings = _build_embeddings()

    if force_rebuild and settings.chroma_db_dir.exists():
        for child in settings.chroma_db_dir.iterdir():
            if child.is_file():
                child.unlink()
            elif child.is_dir():
                import shutil

                shutil.rmtree(child)

    vectordb = Chroma.from_documents(
        docs,
        embeddings,
        collection_name=settings.chroma_collection_name,
        persist_directory=str(settings.chroma_db_dir),
    )
    return vectordb._collection.count()

