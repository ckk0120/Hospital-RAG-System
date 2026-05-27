import unittest

from app.services.scoring import extract_qa, normalize_distance


class ScoringTests(unittest.TestCase):
    def test_normalize_distance(self):
        self.assertAlmostEqual(normalize_distance(0.2), 0.8)
        self.assertAlmostEqual(normalize_distance(1.0), 0.0)

    def test_extract_qa(self):
        question, answer = extract_qa("问题：如何挂号？\n答案：去窗口或线上挂号。")
        self.assertEqual(question, "如何挂号？")
        self.assertEqual(answer, "去窗口或线上挂号。")


if __name__ == "__main__":
    unittest.main()

