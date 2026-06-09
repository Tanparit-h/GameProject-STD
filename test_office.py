import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from tools.office import main, print_families, print_status, print_tasks


class OfficeCliTests(unittest.TestCase):
    def test_print_status_runs(self):
        with redirect_stdout(StringIO()):
            self.assertEqual(print_status(), 0)

    def test_print_tasks_runs(self):
        with redirect_stdout(StringIO()):
            self.assertEqual(print_tasks(), 0)

    def test_print_families_runs(self):
        with redirect_stdout(StringIO()):
            self.assertEqual(print_families(), 0)

    def test_task_dry_run_command(self):
        with patch("sys.argv", ["office", "task", "feature-interaction-v1"]):
            with redirect_stdout(StringIO()):
                self.assertEqual(main(), 0)

    def test_task_command_returns_nonzero_for_blocked_family(self):
        with patch("sys.argv", ["office", "task", "feature-door-toggle-v1"]):
            with redirect_stdout(StringIO()):
                self.assertEqual(main(), 1)

    def test_monitor_command_routes_to_monitor_service(self):
        with patch("tools.office.serve_monitor", return_value=0) as mocked_monitor:
            with patch("sys.argv", ["office", "monitor", "--host", "127.0.0.1", "--port", "9001"]):
                with redirect_stdout(StringIO()):
                    self.assertEqual(main(), 0)
        mocked_monitor.assert_called_once_with(host="127.0.0.1", port=9001)


if __name__ == "__main__":
    unittest.main()
