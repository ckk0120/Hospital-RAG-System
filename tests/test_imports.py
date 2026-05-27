import unittest


class ImportTests(unittest.TestCase):
    def test_core_imports_available(self):
        import app.core.config  # noqa: F401
        import app.services.scoring  # noqa: F401


if __name__ == "__main__":
    unittest.main()

