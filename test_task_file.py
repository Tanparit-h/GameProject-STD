import json
import unittest
from pathlib import Path


class TaskFileTests(unittest.TestCase):
    def test_interaction_vertical_slice_task_has_required_fields(self):
        task_path = Path("workspace/tasks/interaction_vertical_slice.json")
        data = json.loads(task_path.read_text(encoding="utf-8"))

        self.assertEqual(data["id"], "feature-interaction-v1")
        self.assertIn(data["phase"], ["PROTOTYPE_PLAN", "IMPLEMENTATION"])
        self.assertTrue(data["request"])
        self.assertIsInstance(data["approval"]["implementation"], bool)

    def test_all_task_files_have_required_fields(self):
        for task_path in Path("workspace/tasks").glob("*.json"):
            if task_path.name == "task_registry.json":
                continue
            data = json.loads(task_path.read_text(encoding="utf-8"))
            with self.subTest(task=task_path.name):
                self.assertTrue(data["id"])
                self.assertIn(data["phase"], ["PROTOTYPE_PLAN", "IMPLEMENTATION"])
                self.assertTrue(data["title"])
                self.assertTrue(data["request"])
                self.assertIsInstance(data["approval"]["implementation"], bool)


if __name__ == "__main__":
    unittest.main()
