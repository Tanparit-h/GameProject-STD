import unittest

from tools.report_index import collect_status


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
        ]:
            self.assertIn(key, status)


if __name__ == "__main__":
    unittest.main()
