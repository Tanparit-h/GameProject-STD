import unittest

from tools.task_registry import list_tasks, validate_registry


class TaskRegistryTests(unittest.TestCase):
    def test_registry_is_valid(self):
        ok, problems = validate_registry()

        self.assertTrue(ok, problems)

    def test_list_tasks_includes_status(self):
        tasks = list_tasks()

        self.assertGreaterEqual(len(tasks), 1)
        self.assertIn("status", tasks[0])
        self.assertIn("family", tasks[0])
        self.assertIn("family_support", tasks[0])
        self.assertIn("title", tasks[0])


if __name__ == "__main__":
    unittest.main()
