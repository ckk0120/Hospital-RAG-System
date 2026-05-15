from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

print("正在加载向量数据库...")

# 加载 Embeddings 模型
embeddings = HuggingFaceEmbeddings(
    model_name='sentence-transformers/all-MiniLM-L6-v2',
    model_kwargs={'device': 'cpu'}
)

# 加载已保存的向量数据库
vectordb = Chroma(
    persist_directory='./chroma_db',
    embedding_function=embeddings,
    collection_name='hospital_qa'
)

print(f"数据库加载成功!共有 {vectordb._collection.count()} 条文档\n")

# 测试查询功能
print("=" * 60)
print("欢迎使用医院问答系统测试!")
print("=" * 60)

while True:
    query = input("\n请输入您的问题 (输入 'quit' 退出): ").strip()
    
    if query.lower() in ['quit', 'exit', 'q']:
        print("感谢使用,再见!")
        break
    
    if not query:
        continue
    
    # 相似度搜索
    print("\n正在搜索相关答案...")
    results = vectordb.similarity_search(query, k=3)
    
    print(f"\n找到 {len(results)} 条相关结果:\n")
    for i, doc in enumerate(results, 1):
        print(f"--- 结果 {i} ---")
        print(doc.page_content[:500])  # 只显示前500个字符
        print(f"相似度分数: {doc.metadata.get('score', 'N/A')}")
        print()
