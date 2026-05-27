from __future__ import annotations

from pathlib import Path

from app.services.indexer import build_vector_store
from app.core.config import get_settings


def main() -> None:
    settings = get_settings()
    count = build_vector_store(Path("data/data.json"))
    print(f"✅ 成功导入 {count} 条文档到 Chroma 向量库")
    print(f"📁 向量数据库已保存到: {settings.chroma_db_dir}")
    print("\n" + "=" * 60)
    print("📋 A 与 B 对接信息")
    print("=" * 60)
    print(f"CHROMA_DB_DIR={settings.chroma_db_dir.resolve()}")
    print(f"EMBEDDING_MODEL={settings.embedding_model}")
    print(f"CHROMA_COLLECTION_NAME={settings.chroma_collection_name}")
    print("=" * 60)


if __name__ == "__main__":
    print("开始读取 JSON 文件...")
    main()

