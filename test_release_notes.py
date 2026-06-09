import unittest

from tools.release_notes import build_release_notes


class ReleaseNotesTests(unittest.TestCase):
    def test_build_release_notes_contains_sections(self):
        notes = build_release_notes()

        self.assertIn("Release State", notes)
        self.assertIn("Task Status", notes)
        self.assertIn("Recent Root Commits", notes)
        self.assertIn("Validation Command", notes)


if __name__ == "__main__":
    unittest.main()
