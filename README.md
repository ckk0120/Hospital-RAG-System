# 🏥 医院智能问答系统 (Hospital RAG System)

基于 **LangChain + Chroma + HuggingFace** 的医疗知识库问答系统，支持 Android 移动端集成。

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 目录

- [项目简介](#-项目简介)
- [核心功能](#-核心功能)
- [技术栈](#-技术栈)
- [项目结构](#-项目结构)
- [快速开始](#-快速开始)
- [API 文档](#-api-文档)
- [Android 集成](#-android-集成)
- [常见问题](#-常见问题)
- [性能优化](#-性能优化)
- [开发路线图](#-开发路线图)
- [贡献指南](#-贡献指南)
- [许可证](#-许可证)

---

## 📖 项目简介

本项目是一个基于 **RAG (Retrieval-Augmented Generation)** 技术的医院智能问答系统，旨在为患者提供准确、便捷的医疗咨询服务。系统通过向量数据库存储医院相关知识，利用语义相似度检索最相关的答案，并可通过 RESTful API 为 Android/iOS 应用提供服务。

### 应用场景

- 🏥 医院门诊智能导诊
- 📱 移动端健康咨询助手
- 💻 医院官网在线客服
- 🤖 智能客服系统集成

---

## ✨ 核心功能

- ✅ **智能问答**: 基于语义理解的自然语言问答
- ✅ **向量检索**: Chroma 向量数据库高效相似度搜索
- ✅ **多格式兼容**: 支持多种 JSON 数据格式
- ✅ **RESTful API**: FastAPI 构建的高性能后端服务
- ✅ **移动端支持**: 完整的 Android 集成方案
- ✅ **自动文档**: Swagger UI 交互式 API 文档
- ✅ **轻量级模型**: all-MiniLM-L6-v2 快速推理

---

## 🛠️ 技术栈

### 后端核心

- **LangChain**: LLM 应用开发框架
- **Chroma**: 向量数据库
- **HuggingFace Transformers**: Embeddings 模型
- **FastAPI**: 高性能 Web 框架
- **Uvicorn**: ASGI 服务器

### 前端/移动端

- **Android**: Kotlin + Retrofit
- **备选方案**: Volley, OkHttp

### 数据处理

- **JSON**: 知识库数据存储格式
- **Sentence Transformers**: 文本向量化

---

## 📁 项目结构

```
hospital_rag/
├── 📄 rag.py                    # 向量数据库构建脚本
├── 📄 server.py                 # FastAPI 后端服务
├── 📄 query.py                  # 命令行测试工具
├── 📄 rebuild_db.py             # 数据库重建脚本
├── 📄 crawl_all.py              # 数据爬取脚本
│
├──data
|   ├── 📊 data.json                 # 医院问答知识库数据
|   ├── 📊 hospital_data.json
|   └── 📊 hospital_articles.json    # 医院文章数据
│
├── 🗄️ chroma_db/                # Chroma 向量数据库 (自动生成)
│   └── ...
│
├── 📦 requirements.txt          # RAG 核心依赖
├── 📦 server_requirements.txt   # 服务端额外依赖
│
├── 📘 ANDROID_INTEGRATION.md    # Android 集成详细指南
└── 📘 README.md                 # 项目说明文档
```

---

## 🚀 快速开始

### 前置要求

- Python 3.10+
- Anaconda (推荐)
- Git

### 1️⃣ 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd hospital_rag

# 创建虚拟环境 (使用 Anaconda)
conda create -n rag_env python=3.10
conda activate rag_env
```

### 2️⃣ 安装依赖

```bash
# 安装 RAG 核心依赖
pip install -r requirements.txt

# 如果部署后端服务，还需安装
pip install -r server_requirements.txt
```

### 3️⃣ 构建向量数据库

```bash
# 运行数据库构建脚本
python rag.py
```

**预期输出:**

```
开始读取 JSON 文件...
共读取 29 条文档
已处理 1/29 条
...
开始加载 HuggingFace Embeddings 模型...
开始创建 Chroma 向量数据库...
成功导入 29 条文档到 Chroma 向量库
向量数据库已保存到: ./chroma_db
```

### 4️⃣ 测试问答功能

```bash
# 命令行交互测试
python query.py
```

**示例对话:**

```
请输入您的问题 (输入 'quit' 退出): 初诊患者如何挂号？

正在搜索相关答案...

找到 3 条相关结果:

--- 结果 1 ---
问题：初诊患者如何在南京市六合区中医院挂号？
答案：初诊患者一般需要先进行个人信息登记或建档...
```

### 5️⃣ 启动后端服务

```bash
# 启动 FastAPI 服务器
python server.py
```

**访问服务:**

- 🌐 API 根路径: <http://localhost:8000>
- 📖 API 文档: <http://localhost:8000/docs>
- ❤️ 健康检查: <http://localhost:8000/health>

---

## 📡 API 文档

### 接口概览

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | API 状态信息 |
| `/health` | GET | 健康检查 |
| `/query` | POST | 智能问答 (核心接口) |
| `/stats` | GET | 数据库统计 |

### 核心接口: POST /query

**请求示例:**

```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "医保如何使用?",
       "top_k": 3
     }'
```

**响应示例:**

```json
{
  "success": true,
  "answer": "通常支持医保结算，可使用医保卡、支付宝电子医保码...",
  "sources": [
    {
      "content": "问题：南京市六合区中医院是否支持医保结算？...",
      "question": "南京市六合区中医院是否支持医保结算？",
      "answer": "通常支持医保结算...",
      "score": 0.1234
    }
  ]
}
```

### 参数说明

#### Request Body

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `question` | string | ✅ | - | 用户问题 |
| `top_k` | integer | ❌ | 3 | 返回结果数量 |

#### Response

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | boolean | 请求是否成功 |
| `answer` | string | 最佳答案 |
| `sources` | array | 相关文档来源 |
| `error` | string | 错误信息 (可选) |

---

## 📱 Android 集成

详细的 Android 集成指南请查看: [ANDROID_INTEGRATION.md](ANDROID_INTEGRATION.md)

### 快速集成步骤

#### 1. 添加依赖 (build.gradle)

```gradle
dependencies {
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'
    implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
}
```

#### 2. 定义数据模型

```kotlin
data class QueryRequest(val question: String, val top_k: Int = 3)
data class QueryResponse(val success: Boolean, val answer: String, val sources: List<Source>)
```

#### 3. 调用 API

```kotlin
val request = QueryRequest(question = "如何挂号?")
RetrofitClient.apiService.askQuestion(request).enqueue(callback)
```

### 架构示意图

```
┌──────────────┐         HTTP/JSON         ┌─────────────────┐
│  Android App │  ←────────────────────→   │  FastAPI Server  │
│  (Kotlin)    │                            │  (Python)        │
└──────────────┘                            └────────┬────────┘
                                                     │
                                              ┌──────▼────────┐
                                              │  Chroma DB     │
                                              │  (Vector Store)│
                                              └───────────────┘
```

---

## ❓ 常见问题

### Q1: 遇到 `ModuleNotFoundError: No module named 'langchain.vectorstores'`

**解决方案:** 新版本 LangChain 已更改导入路径

```python
# 旧版本 (已废弃)
from langchain.vectorstores import Chroma

# 新版本
from langchain_chroma import Chroma
```

安装依赖:

```bash
pip install langchain-chroma
```

### Q2: 遇到 `AttributeError: 'Chroma' object has no attribute 'persist'`

**解决方案:** 新版本自动持久化，无需手动调用

```python
# 旧版本 (已废弃)
vectordb.persist()

# 新版本 - 设置 persist_directory 后自动保存
vectordb = Chroma.from_documents(
    docs, 
    embeddings,
    persist_directory='./chroma_db'
)
```

### Q3: 查询结果为空字符串

**原因:** JSON 数据字段名不匹配

**解决方案:** 代码已更新为兼容多种格式:

```python
question = item.get('question') or item.get('问题') or item.get('标题', '')
```

重新构建数据库:

```bash
python rebuild_db.py
```

### Q4: Android 无法连接服务器

**检查清单:**

- ✅ 手机和电脑在同一 WiFi 网络
- ✅ 使用局域网 IP (如 `192.168.1.100`) 而非 `localhost`
- ✅ 防火墙开放 8000 端口
- ✅ AndroidManifest.xml 添加网络权限

```xml
<uses-permission android:name="android.permission.INTERNET" />
```

### Q5: 响应速度慢

**优化建议:**

1. 使用 GPU 加速 (修改 `model_kwargs={'device': 'cuda'}`)
2. 减少 `top_k` 值
3. 启用缓存机制 (Redis)

---

## ⚡ 性能优化

### 当前配置

- **模型**: all-MiniLM-L6-v2 (轻量级)
- **设备**: CPU
- **平均响应时间**: ~2-5秒

### 优化方案

#### 1. GPU 加速

```python
embeddings = HuggingFaceEmbeddings(
    model_name='sentence-transformers/all-MiniLM-L6-v2',
    model_kwargs={'device': 'cuda'}  # 使用 GPU
)
```

#### 2. 批量处理

```python
# 批量嵌入提升效率
batch_size = 32
for i in range(0, len(docs), batch_size):
    batch = docs[i:i+batch_size]
    # 处理批次...
```

#### 3. 缓存热门问题

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_query(question: str):
    return vectordb.similarity_search(question)
```

#### 4. 异步处理

```python
@app.post("/query")
async def query_answer(request: QueryRequest):
    results = await vectordb.asimilarity_search(request.question)
    return results
```

---

## 🗺️ 开发路线图

### Phase 1: 基础功能 (已完成 ✅)

- [x] 向量数据库构建
- [x] 命令行问答工具
- [x] FastAPI 后端服务
- [x] Android 集成方案

### Phase 2: 功能增强 (计划中 📅)

- [ ] 多轮对话支持 (上下文理解)
- [ ] 用户认证系统 (JWT)
- [ ] 问答历史记录
- [ ] 反馈评分机制

### Phase 3: 高级特性 (未来 🚀)

- [ ] 语音输入/输出
- [ ] 图片识别问诊
- [ ] 医生排班查询
- [ ] 预约挂号集成
- [ ] 离线模式

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议!

### 提交 PR 步骤

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- 遵循 PEP 8 Python 代码风格
- 添加必要的注释和文档
- 确保测试通过

---

## 📊 项目统计

![GitHub stars](https://img.shields.io/github/stars/your-repo?style=social)
![GitHub forks](https://img.shields.io/github/forks/your-repo?style=social)
![GitHub issues](https://img.shields.io/github/issues/your-repo)

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 👥 团队

**开发团队**: 大创机器人项目组  
**学校**: (请填写你的学校)  
**指导老师**: (请填写老师姓名)  

---

## 📧 联系方式

- 📮 Email: (请填写联系邮箱)
- 💬 微信群: (可添加群二维码)
- 🐛 问题反馈: [GitHub Issues](https://github.com/your-repo/issues)

---

## 🙏 致谢

感谢以下开源项目:

- [LangChain](https://github.com/langchain-ai/langchain)
- [Chroma](https://github.com/chroma-core/chroma)
- [HuggingFace](https://huggingface.co/)
- [FastAPI](https://fastapi.tiangolo.com/)

---

## 📚 参考资料

1. LangChain 官方文档: <https://python.langchain.com/>
2. Chroma 文档: <https://docs.trychroma.com/>
3. FastAPI 教程: <https://fastapi.tiangolo.com/tutorial/>
4. Android Retrofit: <https://square.github.io/retrofit/>

---

**⭐ 如果这个项目对你有帮助,请给个 Star!**

Made with ❤️ by 大创机器人团队
