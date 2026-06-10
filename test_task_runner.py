import unittest

from tools.task_runner import build_task_command, find_task_file, run_task


class TaskRunnerTests(unittest.TestCase):
    def test_find_task_file(self):
        task_file = find_task_file("feature-interaction-v1")

        self.assertEqual(task_file.name, "interaction_vertical_slice.json")

    def test_build_task_command_sets_task_env(self):
        command, env = build_task_command("feature-interaction-v1")

        self.assertIn("app.main_graph", command)
        self.assertEqual(env["AI_STUDIO_TASK_FILE"], "workspace\\tasks\\interaction_vertical_slice.json")
        self.assertEqual(env["AI_STUDIO_TASK_FAMILY"], "interaction_vertical_slice")

    def test_run_task_dry_run(self):
        output = run_task("feature-interaction-v1", dry_run=True)

        self.assertIn("TASK_RUNNER_DRY_RUN", output)
        self.assertIn("feature-interaction-v1", output)

    def test_run_task_dry_run_for_supported_door_family(self):
        output = run_task("feature-door-toggle-v1", dry_run=True)

        self.assertIn("TASK_RUNNER_DRY_RUN", output)
        self.assertIn("feature-door-toggle-v1", output)

    def test_run_task_dry_run_for_supported_inventory_family(self):
        output = run_task("feature-inventory-pickup-v1", dry_run=True)

        self.assertIn("TASK_RUNNER_DRY_RUN", output)
        self.assertIn("feature-inventory-pickup-v1", output)

    def test_run_task_dry_run_for_supported_dialogue_family(self):
        output = run_task("feature-dialogue-prompt-v1", dry_run=True)

        self.assertIn("TASK_RUNNER_DRY_RUN", output)
        self.assertIn("feature-dialogue-prompt-v1", output)

    def test_run_task_blocks_scaffold_only_family(self):
        output = run_task("terra-mage-first-wall-v003", dry_run=True)

        self.assertIn("TASK_RUNNER_BLOCKED", output)
        self.assertIn("terra_mage_first_wall", output)


if __name__ == "__main__":
    unittest.main()
