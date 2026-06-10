import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from app.main_graph import parse_required_flag
from tools.programmer_output_specs import (
    UnsupportedProgrammerFamilyError,
    get_supported_programmer_family_keys,
    is_terra_mage_weapon_family_request,
    is_terra_mage_third_person_aim_request,
    select_programmer_output_spec,
    validate_programmer_output_files,
)


class ProgrammerOutputSpecsTests(unittest.TestCase):
    def test_default_interaction_spec_uses_implementation_files(self):
        spec = select_programmer_output_spec(
            "Create and validate a real Unity interaction vertical slice.",
            "IMPLEMENTATION",
            "feature-interaction-v1",
        )

        self.assertIn("InteractSystem.cs", spec.file_contents)
        self.assertIn("InteractableObject.cs", spec.file_contents)
        self.assertIn("AIPrototypeSceneSetup.cs", spec.file_contents)
        self.assertIn("AIPrototypeSceneValidator.cs", spec.file_contents)
        self.assertEqual(spec.key, "interaction_vertical_slice")

    def test_supported_family_keys_exclude_scaffold_only_entries(self):
        supported = get_supported_programmer_family_keys()

        self.assertIn("interaction_vertical_slice", supported)
        self.assertIn("door_toggle_interaction", supported)
        self.assertIn("terra_mage_third_person_aim", supported)
        self.assertIn("terra_mage_weapon_family", supported)
        self.assertNotIn("dialogue_prompt", supported)

    def test_select_programmer_output_spec_rejects_scaffold_only_family(self):
        with self.assertRaises(UnsupportedProgrammerFamilyError):
            select_programmer_output_spec(
                "Implement an NPC dialogue prompt.",
                "IMPLEMENTATION",
                "feature-dialogue-prompt-v1",
                "dialogue_prompt",
            )

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

    def test_select_programmer_output_spec_for_door_toggle_family(self):
        request = (
            "Implement and validate a real Unity interaction where the player presses E near a door "
            "to toggle open and closed states."
        )

        spec = select_programmer_output_spec(request, "IMPLEMENTATION", "feature-door-toggle-v1")

        self.assertEqual(spec.key, "door_toggle_interaction")
        self.assertIn("DoorToggleInteractable.cs", spec.file_contents)
        self.assertEqual(spec.scene_setup_method, "AIDoorToggleSceneSetup.SetupScene")
        self.assertEqual(spec.scene_validation_method, "AIDoorToggleSceneValidator.ValidateScene")

    def test_validate_programmer_output_files_for_door_toggle_family(self):
        spec = select_programmer_output_spec(
            "door toggle interaction when player presses e",
            "IMPLEMENTATION",
            "feature-door-toggle-v1",
        )
        with TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            file_paths = [str((output_dir / filename).resolve()) for filename in spec.file_contents]

            for filename, content in spec.file_contents.items():
                (output_dir / filename).write_text(content, encoding="utf-8")

            passed, problems = validate_programmer_output_files(output_dir.resolve(), file_paths, spec)

        self.assertTrue(passed, problems)

    def test_detects_terra_mage_weapon_family_tasks(self):
        request = (
            "Implement a Terra Mage weapon wheel with bare hands locked in slot 0, open it with Tab, "
            "and change melee or ranged attacks based on the selected weapon."
        )

        self.assertTrue(is_terra_mage_weapon_family_request(request, "terra-mage-weapon-wheel-v006"))
        self.assertTrue(is_terra_mage_weapon_family_request(request, "terra-mage-weapon-combat-profiles-v007"))
        self.assertTrue(is_terra_mage_weapon_family_request(request, "terra-mage-weapon-wheel-scene-validation-v008"))

    def test_select_programmer_output_spec_for_terra_mage_weapon_family(self):
        request = (
            "Implement a Terra Mage weapon wheel with slot 0 locked to bare hands. "
            "Holding Tab should open the wheel and the selected weapon must change melee or ranged combat."
        )

        spec = select_programmer_output_spec(request, "IMPLEMENTATION", "terra-mage-weapon-wheel-v006")

        self.assertEqual(spec.key, "terra_mage_weapon_family")
        self.assertIn("TerraMageWeaponDefinition.cs", spec.file_contents)
        self.assertIn("TerraMageWeaponWheelUI.cs", spec.file_contents)
        self.assertEqual(spec.scene_setup_method, "TerraMageFirstSceneSetup.SetupFirstScene")
        self.assertEqual(spec.scene_validation_method, "TerraMageFirstSceneValidator.ValidateFirstScene")

    def test_terra_mage_weapon_family_uses_locked_bare_hands_slot_zero(self):
        spec = select_programmer_output_spec(
            "terra mage weapon wheel with slot 0 locked to bare hands",
            "IMPLEMENTATION",
            "terra-mage-weapon-wheel-scene-validation-v008",
        )

        loadout = spec.file_contents["TerraMageWeaponLoadout.cs"]
        validator = spec.file_contents["TerraMageFirstSceneValidator.cs"]
        report = spec.file_contents["TerraMage_WeaponWheelCombat_ImplementationReport.md"]

        self.assertIn("CreateBareHands()", loadout)
        self.assertIn('return slotIndex == 0;', loadout)
        self.assertIn('weapon.WeaponId != "bare_hands"', loadout)
        self.assertIn('assignedWeapons[0].WeaponId == "bare_hands"', loadout)
        self.assertIn('DisplayName != "Bare Hands"', validator)
        self.assertIn("IsSlotLocked(0)", validator)
        self.assertIn("Slot 0 is locked to `Bare Hands`.", report)

    def test_terra_mage_weapon_family_scene_setup_is_idempotent(self):
        spec = select_programmer_output_spec(
            "terra mage weapon wheel scene setup validation",
            "IMPLEMENTATION",
            "terra-mage-weapon-wheel-scene-validation-v008",
        )

        scene_setup = spec.file_contents["TerraMageFirstSceneSetup.cs"]

        self.assertIn("TryValidateExistingScene()", scene_setup)
        self.assertIn("skipped rebuild because scene already matches spec", scene_setup)
        self.assertIn("TerraMageFirstSceneValidator.ValidateFirstScene()", scene_setup)

    def test_validate_programmer_output_files_for_terra_mage_weapon_family(self):
        spec = select_programmer_output_spec(
            "terra mage weapon wheel with tab and bare hands slot",
            "IMPLEMENTATION",
            "terra-mage-weapon-wheel-v006",
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
