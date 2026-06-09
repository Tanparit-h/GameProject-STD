import unittest
from pathlib import Path
from unittest.mock import patch

from tools.report_index import collect_status
import tools.report_index as report_index


class ReportIndexTests(unittest.TestCase):
    def test_collect_status_contains_expected_keys(self):
        status = collect_status()

        for key in [
            "generated_at",
            "root_head",
            "root_status",
            "unity_head",
            "unity_status",
            "reports",
            "tasks",
            "approval_count",
        ]:
            self.assertIn(key, status)

    def test_collect_status_accepts_prototype_plan_report(self):
        report = (
            "## Phase\n\nPROTOTYPE_PLAN\n"
            "SKIPPED_UNITY_IMPLEMENTATION\n"
            "CLEAN_PASS\n"
            "ROLE_GRAPH_OK\n"
        )
        with patch.object(report_index, "LATEST_REPORT", Path("mock_report.md")):
            with patch("pathlib.Path.exists", return_value=True), patch("pathlib.Path.read_text", return_value=report):
                status = collect_status()

        self.assertTrue(status["latest_report_clean"])


if __name__ == "__main__":
    unittest.main()
