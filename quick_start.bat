@echo off
REM A 模块快速启动脚本 (Windows 版本)

echo ==========================================
echo 🚀 A 模块快速启动
echo ==========================================
echo.

REM Step 1: 检查 Python 环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python,请先安装 Python 3.10+
    pause
    exit /b 1
)

echo ✅ Python 环境正常
echo.

REM Step 2: 检查依赖
echo 📦 检查依赖...
python -c "import langchain_chroma" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  缺少依赖,正在安装...
    pip install -r requirements.txt
)
echo ✅ 依赖检查完成
echo.

REM Step 3: 构建数据库
echo 🔨 构建 ChromaDB...
python rag.py
if errorlevel 1 (
    echo ❌ 数据库构建失败
    pause
    exit /b 1
)
echo.

REM Step 4: 验证对接
echo 🔍 验证对接规范...
python verify_integration.py
if errorlevel 1 (
    echo.
    echo ==========================================
    echo ⚠️  验证失败,请检查错误信息
    echo ==========================================
    pause
    exit /b 1
)

echo.
echo ==========================================
echo 🎉 A 模块准备就绪!
echo ==========================================
echo.
echo 下一步:
echo   1. 将 INTEGRATION_GUIDE.md 发送给 B 模块开发者
echo   2. 将 .\data\chroma_db 目录提供给 B 模块
echo   3. 告知 B 模块使用相同的环境变量配置
echo.

pause
