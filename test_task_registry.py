import unittest

from tools.task_registry import validate_registry


class TaskRegistryTests(unittest.TestCase):
    def test_registry_is_valid(self):
        ok, problems = validate_registry()

        self.assertTrue(ok, problems)


if __name__ == "__main__":
    unittest.main()
