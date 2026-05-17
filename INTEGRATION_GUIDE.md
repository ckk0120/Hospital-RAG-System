# A 与 B 模块对接说明文档

> **文档版本**: v1.0  
> **更新时间**: 2026-05-15  
> **A 模块负责人**: (你的名字)  
> **B 模块负责人**: (B 模块开发者名字)

---

## 📋 目录

- [对接概述](#对接概述)
- [A 模块输出信息](#a-模块输出信息)
- [B 模块配置要求](#b-模块配置要求)
- [Metadata 字段约定](#metadata-字段约定)
- [验证步骤](#验证步骤)
- [常见问题](#常见问题)

---

## 对接概述

本系统采用 **A-B-C/D 架构**:

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│  A 模块      │  ───→   │  B 模块      │  ───→   │  C/D 模块    │
│ 知识库构建   │         │ RAG 检索     │         │ LLM/前端    │
└─────────────┘         └─────────────┘         └─────────────┘
     ↓                         ↓
  ChromaDB              只读检索接口
  (写入端)              (读取端)
```

**职责划分:**

| 模块 | 职责 | 不负责 |
|------|------|--------|
| **A 模块** | 收集资料、文档清洗、生成 embedding、写入 ChromaDB | 不提供实时检索服务 |
| **B 模块** | 只读检索 ChromaDB、返回相关上下文 | 不写库、不更新知识库 |
| **C/D 模块** | LLM 推理、前端展示 | 不直接接触向量数据库 |

---

## A 模块输出信息

### ✅ 已生成的 ChromaDB 配置

以下配置是 **B 模块必须使用的环境变量**:

```bash
# ==================== B 模块环境变量配置 ====================
CHROMA_DB_DIR=./data/chroma_db
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
CHROMA_COLLECTION_NAME=langchain
# ============================================================
```

### 📊 数据库统计信息

运行 `python rag.py` 后,会显示以下信息:

```
✅ 成功导入 XX 条文档到 Chroma 向量库
📁 向量数据库已保存到: ./data/chroma_db

============================================================
📋 A 与 B 对接信息
============================================================
CHROMA_DB_DIR=/absolute/path/to/data/chroma_db
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
CHROMA_COLLECTION_NAME=langchain

Metadata 字段约定:
  - source: 数据来源文件 (B 模块优先读取)
  - title: 问题标题
  - department: 科室/栏目

⚠️  请将以上配置提供给 B 模块开发者!
============================================================
```

---

## B 模块配置要求

### 1️⃣ 环境变量 (必填)

B 模块需要在 `.env` 文件或系统环境中设置以下变量:

```ini
# ChromaDB 持久化目录 (A 模块生成的数据库路径)
CHROMA_DB_DIR=./data/chroma_db

# Embedding 模型名称 (必须与 A 模块建库时一致)
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5

# Chroma Collection 名称 (可选,默认 langchain)
CHROMA_COLLECTION_NAME=langchain
```

### 2️⃣ Python 依赖

B 模块需要安装以下依赖:

```txt
langchain-chroma>=0.1.0
langchain-huggingface>=0.0.1
sentence-transformers>=2.2.0
```

### 3️⃣ 检索接口规范

B 模块应实现以下接口:

```python
def retrieve_context(question: str, top_k: int = 3) -> list[dict]:
    """
    从 ChromaDB 检索相关上下文
    
    Args:
        question: 用户问题
        top_k: 返回结果数量 (默认 3)
    
    Returns:
        相关文档列表,每个文档包含:
        - content: 文档内容
        - source: 来源文件
        - score: 相似度分数 (0-1)
    """
```

**返回格式示例:**

```json
[
  {
    "content": "初诊患者一般需要先进行个人信息登记或建档,然后选择科室与医生完成挂号。",
    "source": "hospital_qa.json",
    "score": 0.87
  },
  {
    "content": "复诊需要重新挂号,但部分科室可能有复诊优惠。",
    "source": "hospital_qa.json",
    "score": 0.75
  }
]
```

### 4️⃣ 异常处理约定

B 模块在以下情况应返回空列表 `[]`:

| 异常情况 | 处理方式 |
|---------|---------|
| ChromaDB 路径不存在 | 返回 `[]`,记录警告日志 |
| LangChain/ChromaDB 依赖缺失 | 返回 `[]`,记录错误日志 |
| 检索失败 (网络/IO 错误) | 返回 `[]`,记录异常堆栈 |
| 问题为空或无效 | 返回 `[]`,不发起检索 |

**当返回 `[]` 时:**
- B 模块 **不应调用 LLM**
- 直接返回 fallback 响应给 C/D 模块
- 示例: `"抱歉,暂时无法回答您的问题。"`

---

## Metadata 字段约定

A 模块写入 ChromaDB 时,每个 chunk 的 metadata 包含以下字段:

### 标准字段

| 字段名 | 类型 | 必填 | 说明 | B 模块使用方式 |
|--------|------|------|------|---------------|
| `source` | string | ✅ | 数据来源文件 | **优先读取**,用于标注答案来源 |
| `title` | string | ❌ | 问题标题 (前50字符) | 可用于展示摘要 |
| `department` | string | ❌ | 科室/栏目 | 可用于分类过滤 |
| `question_type` | string | ❌ | 问题类型 (如 "faq") | 预留扩展 |

### 示例 Metadata

```python
metadata = {
    "source": "hospital_qa.json",
    "title": "初诊患者如何在南京市六合区中医院挂号?",
    "department": "综合科",
    "question_type": "faq"
}
```

### B 模块读取优先级

```python
# 伪代码示例
source = metadata.get("source") or metadata.get("file_name") or ""
```

**优先级顺序:**
1. `metadata.source` (首选)
2. `metadata.file_name` (备选)
3. 空字符串 `""` (兜底)

---

## 验证步骤

### Step 1: A 模块生成数据库

```bash
cd hospital_rag/Hospital-RAG-System
python rag.py
```

**预期输出:**
```
开始读取 JSON 文件...
共读取 29 条文档
已处理 1/29 条
...
✅ 成功导入 29 条文档到 Chroma 向量库
📁 向量数据库已保存到: ./data/chroma_db
```

### Step 2: 检查数据库文件

确认以下目录存在且非空:

```bash
ls -lh ./data/chroma_db/
```

应看到类似输出:
```
chroma.sqlite3
xxx-xxx-xxx-xxx/  (UUID 文件夹)
```

### Step 3: B 模块测试检索

B 模块开发者运行测试脚本:

```python
from app.rag import retrieve_context

results = retrieve_context("如何挂号?", top_k=3)
print(f"找到 {len(results)} 条结果")
for r in results:
    print(f"  - Source: {r['source']}")
    print(f"  - Score: {r['score']}")
    print(f"  - Content: {r['content'][:100]}...")
```

**预期输出:**
```
找到 3 条结果
  - Source: hospital_qa.json
  - Score: 0.87
  - Content: 问题：初诊患者如何在南京市六合区中医院挂号?
答案：初诊患者一般需要先进行个人信息登记...
```

### Step 4: 端到端测试

完整流程测试:

```
用户提问 → B 模块检索 → 返回 context → C/D 模块生成答案 → 展示给用户
```

---

## 常见问题

### Q1: B 模块提示 "ChromaDB directory does not exist"

**原因:** `CHROMA_DB_DIR` 路径配置错误

**解决:**
```bash
# 检查路径是否存在
ls ./data/chroma_db

# 如果不存在,重新运行 A 模块
python rag.py

# 或者修改 B 模块的环境变量为绝对路径
CHROMA_DB_DIR=/absolute/path/to/hospital_rag/Hospital-RAG-System/data/chroma_db
```

### Q2: 检索结果为空或分数很低

**可能原因:**
1. Embedding 模型不一致
2. Collection 名称不匹配
3. 数据库中无相关数据

**排查步骤:**
```python
# 1. 检查模型是否一致
print(settings.embedding_model)  # 应为 "BAAI/bge-small-zh-v1.5"

# 2. 检查 collection 名称
print(settings.chroma_collection_name)  # 应为 "langchain"

# 3. 检查数据库文档数量
vector_store._collection.count()  # 应 > 0
```

### Q3: B 模块缺少依赖

**错误信息:**
```
ModuleNotFoundError: No module named 'langchain_chroma'
```

**解决:**
```bash
pip install langchain-chroma langchain-huggingface sentence-transformers
```

### Q4: 中文检索效果不佳

**建议:**
- 当前使用 `BAAI/bge-small-zh-v1.5` 模型,对中文支持良好
- 如果效果仍不理想,可升级到 `BAAI/bge-large-zh-v1.5` (需重新建库)

---

## 📞 联系方式

如有对接问题,请联系:

- **A 模块负责人**: (你的名字)
  - Email: (你的邮箱)
  - 微信: (你的微信)

- **B 模块负责人**: (B 模块开发者)
  - Email: (B 的邮箱)

---

## 📝 更新日志

| 版本 | 日期 | 更新内容 | 负责人 |
|------|------|---------|--------|
| v1.0 | 2026-05-15 | 初始版本,确定对接规范 | (你的名字) |

---

**⚠️ 重要提醒:**

1. A 模块每次更新知识库后,**必须通知 B 模块重新加载**
2. Embedding 模型变更时,**必须重新构建 ChromaDB**
3. Metadata 字段变更时,**需同步更新 B 模块的读取逻辑**
