from pathlib import Path
import unittest

from tools.unity_tool import (
    PROJECT_ROOT,
    apply_copy_plan,
    CREATOR_EXPORT_DIR,
    PROGRAMMER_OUTPUT_DIR,
    get_programmer_script_target,
    parse_unity_log,
    parse_unity_result_text,
    validate_unity_project_path,
)


class UnityToolTests(unittest.TestCase):
    def test_parse_unity_log_passes_clean_return_code(self):
        result = parse_unity_log("Tundra build success\nExit code: 0", return_code=0)

        self.assertIs(result["passed"], True)
        self.assertEqual(result["error_markers"], [])
        self.assertIn("Tundra build success", result["success_markers"])

    def test_parse_unity_log_fails_on_error_marker(self):
        result = parse_unity_log("Assets/Test.cs(1,1): error CS1002", return_code=0)

        self.assertIs(result["passed"], False)
        self.assertIn("error CS", result["error_markers"])

    def test_parse_unity_result_text_reads_exit_code(self):
        result = parse_unity_result_text(
            "UNITY_BATCHMODE_RESULT\n"
            "Exit code: 0\n"
            "Passed: True\n"
            "Success markers: Tundra build success, return code 0"
        )

        self.assertIs(result["passed"], True)
        self.assertEqual(result["return_code"], 0)

    def test_parse_unity_log_ignores_named_pipe_shutdown_warning(self):
        result = parse_unity_log(
            "Exception occured while accepting client connection: "
            "System.IO.IOException: The pipe is being closed.\n"
            "AIPrototypeSceneValidator passed.",
            return_code=0,
        )

        self.assertIs(result["passed"], True)

    def test_validate_unity_project_rejects_path_outside_game_project(self):
        ok, message, _ = validate_unity_project_path(PROJECT_ROOT)

        self.assertIs(ok, False)
        self.assertTrue(message.startswith("UNITY_PROJECT_OUTSIDE_ALLOWED_ROOT"))

    def test_apply_copy_plan_dry_run_does_not_copy(self):
        project = PROJECT_ROOT / "game_project" / "STDProject"
        if not project.exists():
            self.skipTest("STDProject is not present in this checkout")

        result = apply_copy_plan(dry_run=True, project_path=project)

        self.assertIn("UNITY_COPY_PLAN", result)
        self.assertIn("Dry run: True", result)

    def test_apply_copy_plan_marks_existing_targets_unchanged(self):
        project = PROJECT_ROOT / "game_project" / "STDProject"
        if not project.exists():
            self.skipTest("STDProject is not present in this checkout")

        source = PROGRAMMER_OUTPUT_DIR / "InteractSystem_Draft.cs"
        target = project / "Assets" / "Scripts" / "AIPrototype" / "InteractSystem.cs"
        if not source.exists() or not target.exists():
            self.skipTest("InteractSystem draft or Unity target is not present")

        result = apply_copy_plan(dry_run=True, project_path=project)

        self.assertIn("UNCHANGED:", result)

    def test_get_programmer_script_target_routes_terra_mage_runtime_scripts(self):
        project = PROJECT_ROOT / "game_project" / "STDProject"
        source = PROGRAMMER_OUTPUT_DIR / "TerraMageAimSystem.cs"

        target = get_programmer_script_target(project, source)

        self.assertEqual(
            target,
            project / "Assets" / "Scripts" / "AIPrototype" / "TerraMageTD" / "TerraMageAimSystem.cs",
        )

    def test_get_programmer_script_target_routes_terra_mage_editor_scripts(self):
        project = PROJECT_ROOT / "game_project" / "STDProject"
        source = PROGRAMMER_OUTPUT_DIR / "TerraMageFirstSceneValidator.cs"

        target = get_programmer_script_target(project, source)

        self.assertEqual(
            target,
            project / "Assets" / "Scripts" / "AIPrototype" / "Editor" / "TerraMageFirstSceneValidator.cs",
        )


if __name__ == "__main__":
    unittest.main()
