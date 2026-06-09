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
            "task_details",
            "latest_report_summary",
        ]:
            self.assertIn(key, status)

    def test_collect_status_accepts_implementation_report(self):
        report = (
            "## Task Metadata\n\n"
            "Task id: feature-interaction-v1\n\n"
            "Task file: workspace\\\\tasks\\\\interaction_vertical_slice.json\n\n"
            "Task family: interaction_vertical_slice\n\n"
            "---\n\n"
            "## Phase\n\nIMPLEMENTATION\n"
            "---\n\n"
            "## 4.1 Creator Gate Status\n\nSKIPPED\n\n---\n\n"
            "## 7.1 Programmer Gate Status\n\nCLEAN_PASS\n\n---\n\n"
            "## 9.5 Unity Evidence Report\n\n"
            "## 9.6 Unity Gate Status\n\nCLEAN_PASS\n\n---\n\n"
            "DETERMINISTIC_UNITY_GATE\n"
            "Validation passed: True\n"
            "Scene setup passed: True\n"
            "Scene validation passed: True\n"
            "CLEAN_PASS\n"
            "\n---\n\n"
            "## Final Status\n\nROLE_GRAPH_OK\n"
        )
        original_exists = Path.exists
        original_read_text = Path.read_text

        def fake_exists(path):
            if str(path) == "mock_report.md":
                return True
            return original_exists(path)

        def fake_read_text(path, *args, **kwargs):
            if str(path) == "mock_report.md":
                return report
            return original_read_text(path, *args, **kwargs)

        with patch.object(report_index, "LATEST_REPORT", Path("mock_report.md")):
            with patch("pathlib.Path.exists", fake_exists), patch("pathlib.Path.read_text", fake_read_text):
                status = collect_status()

        self.assertTrue(status["latest_report_clean"])
        self.assertEqual(status["latest_report_summary"]["task_family"], "interaction_vertical_slice")
        self.assertEqual(status["latest_report_summary"]["final_status"], "ROLE_GRAPH_OK")


if __name__ == "__main__":
    unittest.main()
