"""
A 模块验证脚本 - 测试 ChromaDB 是否符合对接规范

运行方式:
    python verify_integration.py

预期输出:
    ✅ 所有检查通过,可以交付给 B 模块
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))


def check_database_exists():
    """检查 ChromaDB 目录是否存在"""
    from app.config import get_settings
    settings = get_settings()
    db_dir = Path(settings.chroma_db_dir)
    
    print(f"📁 检查数据库路径: {db_dir}")
    if not db_dir.exists():
        print(f"❌ 数据库目录不存在: {db_dir}")
        print(f"💡 请先运行: python rag.py")
        return False
    
    print(f"✅ 数据库目录存在")
    return True


def check_collection_accessible():
    """检查 Collection 是否可访问"""
    from app.config import get_settings
    from langchain_chroma import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings
    
    settings = get_settings()
    
    print(f"\n🔍 检查 Collection: {settings.chroma_collection_name}")
    
    try:
        embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
        vector_store = Chroma(
            collection_name=settings.chroma_collection_name,
            persist_directory=str(settings.chroma_db_dir),
            embedding_function=embeddings,
        )
        
        count = vector_store._collection.count()
        print(f"✅ Collection 可访问,文档数量: {count}")
        
        if count == 0:
            print(f"⚠️  警告: 数据库为空,请先运行: python rag.py")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 无法访问 Collection: {e}")
        return False


def test_retrieval():
    """测试检索功能"""
    from app.rag import retrieve_context
    
    print(f"\n🧪 测试检索功能...")
    
    test_questions = [
        "如何挂号?",
        "医保怎么使用?",
        "急诊流程是什么?"
    ]
    
    all_passed = True
    
    for question in test_questions:
        print(f"\n  问题: {question}")
        results = retrieve_context(question, top_k=2)
        
        if not results:
            print(f"  ❌ 未找到相关结果")
            all_passed = False
            continue
        
        print(f"  ✅ 找到 {len(results)} 条结果")
        
        # 检查返回格式
        for i, result in enumerate(results):
            required_keys = ["content", "source", "score"]
            missing_keys = [k for k in required_keys if k not in result]
            
            if missing_keys:
                print(f"  ❌ 结果 {i+1} 缺少字段: {missing_keys}")
                all_passed = False
            else:
                print(f"  ✅ 结果 {i+1}: source={result['source']}, score={result['score']:.4f}")
    
    return all_passed


def check_metadata_format():
    """检查 Metadata 格式是否符合规范"""
    from app.config import get_settings
    from langchain_chroma import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings
    
    settings = get_settings()
    
    print(f"\n📋 检查 Metadata 格式...")
    
    try:
        embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
        vector_store = Chroma(
            collection_name=settings.chroma_collection_name,
            persist_directory=str(settings.chroma_db_dir),
            embedding_function=embeddings,
        )
        
        # 获取一条记录检查 metadata
        results = vector_store.similarity_search("测试", k=1)
        
        if not results:
            print(f"⚠️  警告: 无法获取样本记录")
            return True
        
        metadata = results[0].metadata
        print(f"  样本 Metadata: {metadata}")
        
        # 检查必需字段
        if "source" in metadata:
            print(f"  ✅ 包含 source 字段: {metadata['source']}")
        else:
            print(f"  ⚠️  缺少 source 字段 (B 模块会尝试读取 file_name)")
        
        # 建议字段
        optional_fields = ["title", "department"]
        for field in optional_fields:
            if field in metadata:
                print(f"  ✅ 包含 {field} 字段: {metadata[field]}")
            else:
                print(f"  ℹ️  缺少 {field} 字段 (可选)")
        
        return True
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False


def print_integration_info():
    """打印对接信息"""
    from app.config import get_settings
    
    settings = get_settings()
    
    print("\n" + "="*60)
    print("📋 A 与 B 对接信息")
    print("="*60)
    print(f"CHROMA_DB_DIR={os.path.abspath(settings.chroma_db_dir)}")
    print(f"EMBEDDING_MODEL={settings.embedding_model}")
    print(f"CHROMA_COLLECTION_NAME={settings.chroma_collection_name}")
    print("\nMetadata 字段约定:")
    print("  - source: 数据来源文件 (B 模块优先读取)")
    print("  - title: 问题标题")
    print("  - department: 科室/栏目")
    print("\n⚠️  请将以上配置提供给 B 模块开发者!")
    print("="*60)


def main():
    """主函数"""
    print("="*60)
    print("🔍 A 模块对接验证")
    print("="*60)
    
    checks = [
        ("数据库存在性", check_database_exists),
        ("Collection 可访问性", check_collection_accessible),
        ("Metadata 格式", check_metadata_format),
        ("检索功能", test_retrieval),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{'='*60}")
        print(f"检查项: {name}")
        print('='*60)
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ 检查异常: {e}")
            results.append((name, False))
    
    # 汇总结果
    print("\n" + "="*60)
    print("📊 验证结果汇总")
    print("="*60)
    
    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status} - {name}")
        if not result:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 所有检查通过!可以交付给 B 模块")
        print_integration_info()
        return 0
    else:
        print("\n⚠️  部分检查失败,请修复后重试")
        return 1


if __name__ == "__main__":
    exit(main())
