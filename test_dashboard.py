import unittest

from tools.dashboard import render_dashboard


class DashboardTests(unittest.TestCase):
    def test_render_dashboard_contains_core_sections(self):
        html = render_dashboard()

        self.assertIn("AI Game Studio Dashboard", html)
        self.assertIn("Repository", html)
        self.assertIn("Release State", html)
        self.assertIn("Latest Run", html)
        self.assertIn("Live Monitor", html)
        self.assertIn("Task Queue", html)
        self.assertIn("Approvals", html)


if __name__ == "__main__":
    unittest.main()
