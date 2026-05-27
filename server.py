from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings


settings = get_settings()
logging.basicConfig(level=settings.log_level)

app = FastAPI(
    title=settings.api_title,
    description="基于 LangChain + Chroma 的医院智能问答检索服务",
    version=settings.api_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def read_root():
    return {
        "message": "医院问答 RAG API 运行中",
        "version": settings.api_version,
        "docs": "/docs",
        "health": "/api/v1/health",
    }


@app.get("/health")
def legacy_health():
    from app.api.routes import health

    return health()


@app.post("/query")
def legacy_query(request: dict):
    from app.schemas.query import QueryRequest
    from app.api.routes import query

    return query(QueryRequest(**request))


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("医院问答 RAG API 服务启动")
    print("访问地址: http://localhost:8000")
    print("API 文档: http://localhost:8000/docs")
    print("新版问答接口: http://localhost:8000/api/v1/query")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000)

