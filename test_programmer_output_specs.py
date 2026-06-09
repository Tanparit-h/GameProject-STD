import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from app.main_graph import parse_required_flag
from tools.programmer_output_specs import (
    is_terra_mage_third_person_aim_request,
    select_programmer_output_spec,
    validate_programmer_output_files,
)


class ProgrammerOutputSpecsTests(unittest.TestCase):
    def test_parse_required_flag_handles_markdown_emphasis(self):
        text = "0. Routing decision\n- Creator required: **no**\n- Programmer required: **yes**"

        creator_required = parse_required_flag(text, "Creator", default=True)
        programmer_required = parse_required_flag(text, "Programmer", default=False)

        self.assertIs(creator_required, False)
        self.assertIs(programmer_required, True)

    def test_detects_terra_mage_third_person_aim_task(self):
        request = (
            "Implement on the real Unity project. Starting from the current Terra Mage scene, "
            "change the camera to a third-person gameplay camera and add an aiming helper."
        )

        self.assertTrue(is_terra_mage_third_person_aim_request(request, "terra-mage-third-person-aim-v005"))

    def test_select_programmer_output_spec_for_terra_mage_aim_task(self):
        request = (
            "Implement on the real Unity project. Starting from the current Terra Mage scene, "
            "change the camera to a third-person gameplay camera and add an aiming helper."
        )

        spec = select_programmer_output_spec(request, "IMPLEMENTATION", "terra-mage-third-person-aim-v005")

        self.assertEqual(spec.key, "terra_mage_third_person_aim")
        self.assertIn("TerraMageAimSystem.cs", spec.file_contents)
        self.assertEqual(spec.scene_setup_method, "TerraMageFirstSceneSetup.SetupFirstScene")
        self.assertEqual(spec.scene_validation_method, "TerraMageFirstSceneValidator.ValidateFirstScene")

    def test_validate_programmer_output_files_uses_task_specific_spec(self):
        spec = select_programmer_output_spec(
            "terra mage third-person aim helper",
            "IMPLEMENTATION",
            "terra-mage-third-person-aim-v005",
        )
        with TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            file_paths = [str((output_dir / filename).resolve()) for filename in spec.file_contents]

            for filename, content in spec.file_contents.items():
                (output_dir / filename).write_text(content, encoding="utf-8")

            passed, problems = validate_programmer_output_files(output_dir.resolve(), file_paths, spec)

        self.assertTrue(passed, problems)


if __name__ == "__main__":
    unittest.main()
