import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from tools.office import main, print_status


class OfficeCliTests(unittest.TestCase):
    def test_print_status_runs(self):
        with redirect_stdout(StringIO()):
            self.assertEqual(print_status(), 0)

    def test_task_dry_run_command(self):
        with patch("sys.argv", ["office", "task", "feature-interaction-v1"]):
            with redirect_stdout(StringIO()):
                self.assertEqual(main(), 0)


if __name__ == "__main__":
    unittest.main()
