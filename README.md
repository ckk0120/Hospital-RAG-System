# 医院智能问答系统

一个面向医院场景的 RAG 检索问答项目，支持知识库构建、相似度检索、FastAPI 服务和 Android 集成。

## 项目定位

这个项目的目标不是“做一个能回答问题的脚本”，而是把医院知识检索服务做成一个可展示、可扩展、可交付的后端系统。核心点包括：

- 统一配置管理
- 模块化 RAG 检索链路
- 支持 Chroma 持久化向量库
- 提供 REST API 和命令行测试入口
- 保留医疗安全边界和可追溯来源

## 架构

```text
data/data.json -> rag.py -> Chroma 向量库 -> server.py / query.py
                           \-> verify_integration.py
```

### 代码分层

- `app/core/`：配置
- `app/services/`：索引、检索、评分、问答逻辑
- `app/api/`：HTTP 路由
- `app/schemas/`：请求与响应结构
- `tests/`：基础单元测试

## 目录

- `app/`：核心应用代码
- `rag.py`：构建向量库
- `server.py`：启动 API 服务
- `query.py`：命令行测试
- `verify_integration.py`：对接验证
- `data/data.json`：FAQ 知识库

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
pip install -r server_requirements.txt
```

### 2. 构建向量库

```bash
python rag.py
```

### 3. 启动服务

```bash
python server.py
```

### 4. 命令行测试

```bash
python query.py
```

## API

- `GET /`
- `GET /health`
- `GET /api/v1/health`
- `POST /api/v1/query`
- `GET /api/v1/stats`

## 测试

项目自带轻量级单元测试，优先验证纯逻辑部分：

```bash
python3 -m unittest discover -s tests
```

说明：当前环境如果没有安装 `fastapi`、`pydantic`、`langchain` 等依赖，部分运行时接口无法直接启动，但核心逻辑测试仍可独立验证。

## 面试可讲的升级点

- 配置集中化，避免硬编码
- 检索、服务、API 解耦
- 引入置信度与阈值控制
- 增加来源字段和可追溯性
- 保留测试入口与部署入口

## 后续优化方向

- Docker 部署
- API 鉴权
- 检索评估脚本
- 引入 rerank
- 增加多数据源知识库
