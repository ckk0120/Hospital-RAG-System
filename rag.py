import json
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os

# ==================== 配置区域 (与 B 模块对接) ====================
# 这些配置必须与 B 模块的环境变量保持一致
CHROMA_DB_DIR = "./data/chroma_db"  # ChromaDB 持久化目录
EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"  # Embedding 模型名称
COLLECTION_NAME = "langchain"  # Collection 名称
# ================================================================

print("开始读取 JSON 文件...")
data_path = os.path.join(os.path.dirname(__file__), "data", "data.json")
with open(data_path, "r", encoding="utf-8") as f:
    qa_data = json.load(f)

print(f"共读取 {len(qa_data)} 条文档")

docs = []
for i, item in enumerate(qa_data):
    # 兼容不同格式的 JSON 数据
    question = item.get('question') or item.get('问题') or item.get('标题', '')
    answer = item.get('answer') or item.get('标准答案') or item.get('正文', '')
    keywords = item.get('key-words') or item.get('关键词') or item.get('栏目', '')
    
    content = f"问题：{question}\n答案：{answer}"
    
    # 【重要】按照对接规范写入 metadata
    # B 模块会读取 metadata.source 作为上下文来源
    metadata = {
        "source": "hospital_qa.json",  # 数据来源文件
        "title": question[:50],  # 问题标题 (截取前50字符)
        "department": keywords if keywords else "综合科",  # 科室/栏目
        "question_type": "faq",  # 问题类型
    }
    
    docs.append(Document(page_content=content, metadata=metadata))
    if i % 10 == 0:
        print(f"已处理 {i+1}/{len(qa_data)} 条")

print(f"\n开始加载 Embedding 模型: {EMBEDDING_MODEL}")
embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={'device': 'cpu'}
)

print(f"开始创建 Chroma 向量数据库...")
print(f"  - 数据库路径: {CHROMA_DB_DIR}")
print(f"  - Collection: {COLLECTION_NAME}")
print(f"  - Embedding 模型: {EMBEDDING_MODEL}")

vectordb = Chroma.from_documents(
    docs,
    embeddings,
    collection_name=COLLECTION_NAME,
    persist_directory=CHROMA_DB_DIR
)

# 新版本 langchain-chroma 使用 persist_directory 后自动保存
print(f"\n✅ 成功导入 {len(docs)} 条文档到 Chroma 向量库")
print(f"📁 向量数据库已保存到: {CHROMA_DB_DIR}")

# ==================== 输出对接信息 ====================
print("\n" + "="*60)
print("📋 A 与 B 对接信息")
print("="*60)
print(f"CHROMA_DB_DIR={os.path.abspath(CHROMA_DB_DIR)}")
print(f"EMBEDDING_MODEL={EMBEDDING_MODEL}")
print(f"CHROMA_COLLECTION_NAME={COLLECTION_NAME}")
print("\nMetadata 字段约定:")
print("  - source: 数据来源文件 (B 模块优先读取)")
print("  - title: 问题标题")
print("  - department: 科室/栏目")
print("\n⚠️  请将以上配置提供给 B 模块开发者!")
print("="*60)