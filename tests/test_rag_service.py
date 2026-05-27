import unittest

from app.services.rag_service import HospitalRAGService


class RagServiceTests(unittest.TestCase):
    def test_empty_question(self):
        service = HospitalRAGService(retriever=lambda q, k: [])
        result = service.ask("   ")
        self.assertFalse(result.success)
        self.assertEqual(result.error, "empty_question")

    def test_low_confidence(self):
        fake_contexts = [
            {
                "content": "问题：测试\n答案：示例",
                "answer": "示例",
                "confidence": 0.1,
                "score": 0.9,
                "source": "demo.json",
                "title": "测试",
                "department": "综合科",
                "metadata": {},
            }
        ]
        service = HospitalRAGService(retriever=lambda q, k: fake_contexts)
        result = service.ask("测试问题")
        self.assertFalse(result.success)
        self.assertEqual(result.error, "low_confidence")

    def test_success(self):
        fake_contexts = [
            {
                "content": "问题：如何挂号？\n答案：去窗口。",
                "answer": "去窗口。",
                "confidence": 0.9,
                "score": 0.1,
                "source": "demo.json",
                "title": "挂号",
                "department": "门诊",
                "metadata": {},
            }
        ]
        service = HospitalRAGService(retriever=lambda q, k: fake_contexts)
        result = service.ask("如何挂号？")
        self.assertTrue(result.success)
        self.assertEqual(result.answer, "去窗口。")
        self.assertEqual(len(result.sources), 1)


if __name__ == "__main__":
    unittest.main()

