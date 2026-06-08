import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tools.approval_log as approval_log


class ApprovalLogTests(unittest.TestCase):
    def test_append_and_read_approval(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            approval_path = Path(temp_dir) / "approval_log.jsonl"
            with patch.object(approval_log, "APPROVAL_LOG", approval_path), patch.object(
                approval_log, "APPROVAL_DIR", Path(temp_dir)
            ):
                approval_log.append_approval(
                    task_id="task-1",
                    phase="IMPLEMENTATION",
                    decision="approved",
                    owner="tester",
                    reason="test approval",
                )

                records = approval_log.read_approvals()

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["task_id"], "task-1")
        self.assertEqual(records[0]["decision"], "approved")

    def test_invalid_decision_fails(self):
        with self.assertRaises(ValueError):
            approval_log.append_approval(
                task_id="task-1",
                phase="IMPLEMENTATION",
                decision="maybe",
                owner="tester",
                reason="test approval",
            )


if __name__ == "__main__":
    unittest.main()
