import json
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

print("开始读取 JSON 文件...")
with open("/data/data.json", "r", encoding="utf-8") as f:
    qa_data = json.load(f)

print(f"共读取 {len(qa_data)} 条文档")

docs = []
for i, item in enumerate(qa_data):
    # 兼容不同格式的 JSON 数据
    question = item.get('question') or item.get('问题') or item.get('标题', '')
    answer = item.get('answer') or item.get('标准答案') or item.get('正文', '')
    keywords = item.get('key-words') or item.get('关键词') or item.get('栏目', '')
    
    content = f"问题：{question}\n答案：{answer}\n关键词：{keywords}"
    docs.append(Document(page_content=content, metadata={"source": "hospital_qa"}))
    if i % 10 == 0:
        print(f"已处理 {i+1}/{len(qa_data)} 条")

print("开始加载 HuggingFace Embeddings 模型...（使用轻量级模型 all-MiniLM-L6-v2）")
embeddings = HuggingFaceEmbeddings(
    model_name='sentence-transformers/all-MiniLM-L6-v2',
    model_kwargs={'device': 'cpu'}
)

print("开始创建 Chroma 向量数据库...")
vectordb = Chroma.from_documents(
    docs,
    embeddings,
    collection_name='hospital_qa',
    persist_directory='./chroma_db'
)

# 新版本 langchain-chroma 使用 persist_directory 后自动保存
# vectordb.persist()  # 旧版本方法,已废弃
print(f"成功导入 {len(docs)} 条文档到 Chroma 向量库")
print(f"向量数据库已保存到: ./chroma_db")