# 🚀 A 模块快速开始指南

## 一键启动 (推荐)

### Windows 用户

```bash
quick_start.bat
```

### Linux/Mac 用户

```bash
chmod +x quick_start.sh
./quick_start.sh
```

---

## 手动步骤

### Step 1: 安装依赖

```bash
pip install -r requirements.txt
```

### Step 2: 构建数据库

```bash
python rag.py
```

**预期输出:**
```
✅ 成功导入 XX 条文档到 Chroma 向量库
📁 向量数据库已保存到: ./data/chroma_db

============================================================
📋 A 与 B 对接信息
============================================================
CHROMA_DB_DIR=/absolute/path/to/data/chroma_db
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
CHROMA_COLLECTION_NAME=langchain
============================================================
```

### Step 3: 验证对接

```bash
python verify_integration.py
```

**预期输出:**
```
🎉 所有检查通过!可以交付给 B 模块
```

---

## 📦 交付物清单

完成后,将以下内容提供给 B 模块:

1. ✅ `./data/chroma_db/` 目录 (打包为 chroma_db.tar.gz)
2. ✅ [`HANDOFF_TO_B.md`](HANDOFF_TO_B.md) 文件
3. ✅ [`INTEGRATION_GUIDE.md`](INTEGRATION_GUIDE.md) 文件 (可选,详细版)

---

## 🔑 B 模块配置 (复制给对方)

```ini
CHROMA_DB_DIR=./data/chroma_db
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
CHROMA_COLLECTION_NAME=langchain
```

---

## ❓ 常见问题

### Q: 提示 "ModuleNotFoundError"

```bash
pip install langchain-chroma langchain-huggingface sentence-transformers
```

### Q: 验证失败

检查:
1. `rag.py` 是否成功运行
2. `./data/chroma_db/` 目录是否存在
3. 环境变量是否正确设置

### Q: 如何重新构建数据库

```bash
# 删除旧数据库
rm -rf ./data/chroma_db

# 重新构建
python rag.py
```

---

## 📞 需要帮助?

查看详细文档:
- 📘 [完整对接指南](INTEGRATION_GUIDE.md)
- 📋 [完成清单](CHECKLIST.md)
- 📝 [对接信息摘要](HANDOFF_TO_B.md)
