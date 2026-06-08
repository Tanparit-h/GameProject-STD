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


if __name__ == "__main__":
    unittest.main()
