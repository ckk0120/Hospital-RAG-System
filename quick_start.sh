#!/bin/bash
# A 模块快速启动脚本 - 一键完成数据库构建和验证

set -e  # 遇到错误立即退出

echo "=========================================="
echo "🚀 A 模块快速启动"
echo "=========================================="
echo ""

# 检查 Python 环境
if ! command -v python &> /dev/null; then
    echo "❌ 未找到 Python,请先安装 Python 3.10+"
    exit 1
fi

echo "✅ Python 版本: $(python --version)"
echo ""

# Step 1: 检查依赖
echo "📦 检查依赖..."
if ! python -c "import langchain_chroma" 2>/dev/null; then
    echo "⚠️  缺少依赖,正在安装..."
    pip install -r requirements.txt
fi
echo "✅ 依赖检查完成"
echo ""

# Step 2: 构建数据库
echo "🔨 构建 ChromaDB..."
python rag.py
echo ""

# Step 3: 验证对接
echo "🔍 验证对接规范..."
python verify_integration.py
VERIFY_EXIT_CODE=$?
echo ""

# 总结
if [ $VERIFY_EXIT_CODE -eq 0 ]; then
    echo "=========================================="
    echo "🎉 A 模块准备就绪!"
    echo "=========================================="
    echo ""
    echo "下一步:"
    echo "  1. 将 INTEGRATION_GUIDE.md 发送给 B 模块开发者"
    echo "  2. 将 ./data/chroma_db 目录提供给 B 模块"
    echo "  3. 告知 B 模块使用相同的环境变量配置"
    echo ""
else
    echo "=========================================="
    echo "⚠️  验证失败,请检查错误信息"
    echo "=========================================="
    exit 1
fi
