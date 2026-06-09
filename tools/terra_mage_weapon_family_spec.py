from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = PROJECT_ROOT / "tools" / "spec_templates" / "terra_mage_weapon_family"

WEAPON_TASK_IDS = {
    "terra-mage-weapon-wheel-v006",
    "terra-mage-weapon-combat-profiles-v007",
    "terra-mage-weapon-wheel-scene-validation-v008",
}


def _normalize(text: str) -> str:
    return " ".join((text or "").lower().replace("_", " ").split())


def _read_template(filename: str) -> str:
    return (TEMPLATE_DIR / filename).read_text(encoding="utf-8").replace("\r\n", "\n")


def is_terra_mage_weapon_family_request(feature_request: str, task_id: str = "") -> bool:
    normalized_request = _normalize(feature_request)
    normalized_task_id = _normalize(task_id)

    if normalized_task_id in WEAPON_TASK_IDS:
        return True

    has_terra_mage = "terra mage" in normalized_request
    has_weapon = "weapon" in normalized_request or "อาวุธ" in feature_request
    has_wheel_or_combat = (
        "wheel" in normalized_request
        or "tab" in normalized_request
        or "melee" in normalized_request
        or "range" in normalized_request
        or "bare hands" in normalized_request
        or "มือเปล่า" in feature_request
        or "ต่อย" in feature_request
    )

    return has_terra_mage and has_weapon and has_wheel_or_combat


def build_terra_mage_weapon_family_spec(spec_factory, base_file_contents: dict[str, str]):
    file_contents = dict(base_file_contents)
    file_contents.update(
        {
            "TerraMageActionBuildController.cs": _read_template("TerraMageActionBuildController.cs"),
            "TerraMageAimSystem.cs": _read_template("TerraMageAimSystem.cs"),
            "TerraMageFollowCamera.cs": _read_template("TerraMageFollowCamera.cs"),
            "TerraMageInput.cs": _read_template("TerraMageInput.cs"),
            "TerraMageMeleeGestureController.cs": _read_template("TerraMageMeleeGestureController.cs"),
            "TerraMageTinyMageController.cs": _read_template("TerraMageTinyMageController.cs"),
            "TerraMageWeaponDefinition.cs": _read_template("TerraMageWeaponDefinition.cs"),
            "TerraMageWeaponLoadout.cs": _read_template("TerraMageWeaponLoadout.cs"),
            "TerraMageWeaponWheelUI.cs": _read_template("TerraMageWeaponWheelUI.cs"),
            "TerraMageFirstSceneSetup.cs": _read_template("TerraMageFirstSceneSetup.cs"),
            "TerraMageFirstSceneValidator.cs": _read_template("TerraMageFirstSceneValidator.cs"),
            "TerraMage_WeaponWheelCombat_ImplementationReport.md": _read_template(
                "TerraMage_WeaponWheelCombat_ImplementationReport.md"
            ),
        }
    )

    return spec_factory(
        key="terra_mage_weapon_family",
        file_contents=file_contents,
        required_snippets={
            "TerraMageTinyMageController.cs": [
                "SetCameraPivot",
                "ProjectOnPlane",
                "jumpBufferTimer",
                "coyoteTimer",
            ],
            "TerraMageFollowCamera.cs": [
                "SetWeaponWheelUI",
                "weaponWheelUI.IsOpen",
                "Quaternion.Euler",
            ],
            "TerraMageActionBuildController.cs": [
                "TerraMageWeaponAttackMode",
                "CurrentPullRange",
                "UsePrimaryAction",
                "weaponWheelUI",
            ],
            "TerraMageAimSystem.cs": [
                "ViewportPointToRay",
                "RaycastAll",
                "CurrentTarget",
            ],
            "TerraMageAimTarget.cs": [
                "SetHighlighted",
                "SetVisible",
                "GetAimPoint",
            ],
            "TerraMageAimTargetMotion.cs": [
                "Mathf.Sin",
                "amplitude",
            ],
            "TerraMageAimTargetVisibility.cs": [
                "DisappearAfterDelay",
                "Blink",
                "elapsedTime",
            ],
            "TerraMageMaterialSystem.cs": [
                "CreateLooseEarth",
                "CalculateImpactDamage",
            ],
            "TerraMageInput.cs": [
                "MouseDelta",
                "GetAxisRaw",
                "ToInputSystemKey",
            ],
            "TerraMageMeleeGestureController.cs": [
                "PerformQuickAttack",
                "CurrentMeleeReach",
                "TryFindMeleeHit",
                "weaponWheelUI",
            ],
            "TerraMageWeaponDefinition.cs": [
                "CreateBareHands",
                "CreateMelee",
                "CreateRanged",
            ],
            "TerraMageWeaponLoadout.cs": [
                "ConfigureDemoLoadout",
                "AssignWeapon",
                "ActiveSlotCount",
                "shard_sling",
            ],
            "TerraMageWeaponWheelUI.cs": [
                "CalculateSegmentSweep",
                "CreateSegmentSprite",
                "EquipHoveredSlot",
                "MouseDelta",
                "OpenWheelKey",
                "RebuildImmediately",
                "VisualSegmentCount",
            ],
            "TerraMageFirstSceneSetup.cs": [
                "CreateWeaponWheelUi",
                "ConfigureDemoLoadout",
                "TerraMage_WeaponWheelCanvas",
                "Hold Tab - release to equip",
            ],
            "TerraMageFirstSceneValidator.cs": [
                "TerraMageWeaponLoadout",
                "TerraMageWeaponWheelUI.CalculateSegmentSweep(2)",
                "KeyCode.Tab",
                "Shard Sling",
            ],
            "TerraMage_WeaponWheelCombat_ImplementationReport.md": [
                "weapon wheel",
                "Stone Gauntlet",
                "Tab",
                "scene validation",
            ],
        },
        scene_setup_method="TerraMageFirstSceneSetup.SetupFirstScene",
        scene_validation_method="TerraMageFirstSceneValidator.ValidateFirstScene",
    )
