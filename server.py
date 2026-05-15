from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from typing import List, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="医院问答 RAG API",
    description="基于 LangChain + Chroma 的医院智能问答系统",
    version="1.0.0"
)

# ==================== 数据模型 ====================
class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3  # 默认返回3条结果
    
class QueryResponse(BaseModel):
    success: bool
    answer: str
    sources: List[dict]
    error: Optional[str] = None

# ==================== 初始化向量数据库 ====================
logger.info("正在加载 Embeddings 模型...")
embeddings = HuggingFaceEmbeddings(
    model_name='sentence-transformers/all-MiniLM-L6-v2',
    model_kwargs={'device': 'cpu'}
)

logger.info("正在加载向量数据库...")
try:
    vectordb = Chroma(
        persist_directory='./chroma_db',
        embedding_function=embeddings,
        collection_name='hospital_qa'
    )
    logger.info(f"数据库加载成功!共有 {vectordb._collection.count()} 条文档")
except Exception as e:
    logger.error(f"数据库加载失败: {e}")
    vectordb = None

# ==================== API 路由 ====================

@app.get("/")
def read_root():
    """API 根路径"""
    return {
        "message": "医院问答 RAG API 运行中",
        "version": "1.0.0",
        "status": "healthy" if vectordb else "degraded"
    }

@app.get("/health")
def health_check():
    """健康检查接口"""
    doc_count = vectordb._collection.count() if vectordb else 0
    return {
        "status": "ok",
        "database_loaded": vectordb is not None,
        "document_count": doc_count
    }

@app.post("/query", response_model=QueryResponse)
def query_answer(request: QueryRequest):
    """
    问答接口 - Android 应用主要调用此接口
    
    请求示例:
    {
        "question": "如何挂号?",
        "top_k": 3
    }
    
    响应示例:
    {
        "success": true,
        "answer": "综合答案内容...",
        "sources": [
            {"content": "...", "score": 0.85},
            {"content": "...", "score": 0.78}
        ]
    }
    """
    try:
        if not vectordb:
            raise HTTPException(status_code=500, detail="向量数据库未加载")
        
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="问题不能为空")
        
        logger.info(f"收到查询: {request.question}")
        
        # 相似度搜索
        results = vectordb.similarity_search_with_score(
            request.question, 
            k=request.top_k
        )
        
        if not results:
            return QueryResponse(
                success=False,
                answer="抱歉,没有找到相关答案。",
                sources=[]
            )
        
        # 整合答案
        sources = []
        combined_answer = ""
        
        for i, (doc, score) in enumerate(results):
            content = doc.page_content
            
            # 提取问题和答案部分
            lines = content.split('\n')
            q_text = ""
            a_text = ""
            
            for line in lines:
                if line.startswith('问题：'):
                    q_text = line.replace('问题：', '').strip()
                elif line.startswith('答案：'):
                    a_text = line.replace('答案：', '').strip()
            
            sources.append({
                "content": content[:500],  # 限制长度
                "question": q_text,
                "answer": a_text,
                "score": round(float(score), 4)
            })
            
            # 整合最佳答案
            if i == 0 and a_text:
                combined_answer = a_text
        
        # 如果没有提取到答案,使用原始内容
        if not combined_answer:
            combined_answer = results[0][0].page_content[:300]
        
        logger.info(f"返回 {len(sources)} 条结果")
        
        return QueryResponse(
            success=True,
            answer=combined_answer,
            sources=sources
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询出错: {str(e)}")
        return QueryResponse(
            success=False,
            answer="系统错误,请稍后重试。",
            sources=[],
            error=str(e)
        )

@app.get("/stats")
def get_stats():
    """获取数据库统计信息"""
    if not vectordb:
        raise HTTPException(status_code=500, detail="数据库未加载")
    
    count = vectordb._collection.count()
    return {
        "total_documents": count,
        "collection_name": "hospital_qa"
    }

# ==================== 启动入口 ====================
if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("医院问答 RAG API 服务启动")
    print("访问地址: http://localhost:8000")
    print("API 文档: http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run(
        app, 
        host="0.0.0.0",  # 允许外部访问
        port=8000
    )
