import unittest

from tools.release_gate import dashboard_index_clean, latest_report_clean


class ReleaseGateTests(unittest.TestCase):
    def test_latest_report_clean_returns_boolean_and_message(self):
        ok, message = latest_report_clean()

        self.assertIsInstance(ok, bool)
        self.assertIsInstance(message, str)

    def test_dashboard_index_clean_returns_boolean_and_message(self):
        ok, message = dashboard_index_clean()

        self.assertIsInstance(ok, bool)
        self.assertIsInstance(message, str)


if __name__ == "__main__":
    unittest.main()
