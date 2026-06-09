import unittest

from pathlib import Path
from unittest.mock import patch

from tools.release_gate import dashboard_index_clean, latest_report_clean
import tools.release_gate as release_gate


class ReleaseGateTests(unittest.TestCase):
    def test_latest_report_clean_returns_boolean_and_message(self):
        ok, message = latest_report_clean()

        self.assertIsInstance(ok, bool)
        self.assertIsInstance(message, str)

    def test_dashboard_index_clean_returns_boolean_and_message(self):
        ok, message = dashboard_index_clean()

        self.assertIsInstance(ok, bool)
        self.assertIsInstance(message, str)

    def test_latest_report_clean_accepts_implementation_report(self):
        report = (
            "## Phase\n\nIMPLEMENTATION\n"
            "## 9.6 Unity Gate Status\n\nCLEAN_PASS\n"
            "DETERMINISTIC_UNITY_GATE\n"
            "Validation passed: True\n"
            "Scene setup passed: True\n"
            "Scene validation passed: True\n"
            "## Final Status\n\nROLE_GRAPH_OK\n"
        )
        with patch.object(release_gate, "LATEST_REPORT", Path("mock_report.md")):
            with patch("pathlib.Path.exists", return_value=True), patch("pathlib.Path.read_text", return_value=report):
                ok, _ = latest_report_clean()

        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
