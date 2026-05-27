from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parents[2]


def _env(name: str, default: str) -> str:
    value = os.getenv(name, default)
    return value.strip() if isinstance(value, str) else default


@dataclass(frozen=True)
class Settings:
    chroma_db_dir: Path = BASE_DIR / _env("CHROMA_DB_DIR", "data/chroma_db")
    embedding_model: str = _env("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
    chroma_collection_name: str = _env("CHROMA_COLLECTION_NAME", "langchain")
    device: str = _env("DEVICE", "cpu")
    log_level: str = _env("LOG_LEVEL", "INFO")
    top_k_default: int = int(_env("TOP_K_DEFAULT", "3"))
    retrieval_threshold: float = float(_env("RETRIEVAL_THRESHOLD", "0.35"))
    api_title: str = "医院问答 RAG API"
    api_version: str = "2.0.0"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

