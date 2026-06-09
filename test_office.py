import unittest
from unittest.mock import patch

from tools.office import main, print_status


class OfficeCliTests(unittest.TestCase):
    def test_print_status_runs(self):
        self.assertEqual(print_status(), 0)

    def test_task_dry_run_command(self):
        with patch("sys.argv", ["office", "task", "feature-interaction-v1"]):
            self.assertEqual(main(), 0)


if __name__ == "__main__":
    unittest.main()
