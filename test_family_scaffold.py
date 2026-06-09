import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import tools.family_scaffold as family_scaffold


class FamilyScaffoldTests(unittest.TestCase):
    def test_normalize_family_key(self):
        self.assertEqual(family_scaffold.normalize_family_key("Door Toggle Interaction"), "door_toggle_interaction")

    def test_scaffold_programmer_family_creates_expected_files(self):
        with TemporaryDirectory() as temp_dir:
            with patch.object(family_scaffold, "TEMPLATE_ROOT", Path(temp_dir)):
                written = family_scaffold.scaffold_programmer_family("new_test_family")

        written_names = sorted(path.name for path in written)
        self.assertEqual(
            written_names,
            [
                "FamilyImplementationReport.md",
                "FamilySceneSetup.cs",
                "FamilySceneValidator.cs",
                "README.md",
            ],
        )


if __name__ == "__main__":
    unittest.main()
