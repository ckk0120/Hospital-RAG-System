from __future__ import annotations

from app.services.rag_service import HospitalRAGService


def main() -> None:
    service = HospitalRAGService()
    print("欢迎使用医院问答系统测试!")
    print("=" * 60)

    while True:
        query = input("\n请输入您的问题 (输入 'quit' 退出): ").strip()
        if query.lower() in {"quit", "exit", "q"}:
            print("感谢使用,再见!")
            break
        if not query:
            continue

        result = service.ask(query, top_k=3)
        print("\n正在搜索相关答案...")
        print(f"\n结果: {'成功' if result.success else '未命中'}")
        print(f"答案: {result.answer}")
        print(f"耗时: {result.latency_ms} ms")
        print(f"来源数量: {len(result.sources)}")


if __name__ == "__main__":
    main()

