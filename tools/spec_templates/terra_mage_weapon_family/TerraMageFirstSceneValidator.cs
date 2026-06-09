using System;
using TerraMageTD;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class TerraMageFirstSceneValidator
{
    private const string ScenePath = "Assets/Scenes/TerraMage_FirstScene.unity";

    public static void ValidateFirstScene()
    {
        EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);

        var player = RequireObject("TerraMage_Player");
        var characterController = RequireComponent<CharacterController>(player, "TerraMage_Player");
        var tinyMageController = RequireComponent<TerraMageTinyMageController>(player, "TerraMage_Player");
        var actionBuildController = RequireComponent<TerraMageActionBuildController>(player, "TerraMage_Player");
        var meleeGestureController = RequireComponent<TerraMageMeleeGestureController>(player, "TerraMage_Player");
        var weaponLoadout = RequireComponent<TerraMageWeaponLoadout>(player, "TerraMage_Player");
        var weaponWheelUI = RequireComponent<TerraMageWeaponWheelUI>(player, "TerraMage_Player");

        if (characterController.height > 0.35f)
        {
            throw new InvalidOperationException("TerraMage_Player must read as a tiny 30 cm character.");
        }

        if (tinyMageController.CameraPivot == null)
        {
            throw new InvalidOperationException("TerraMageTinyMageController must be linked to the third-person camera.");
        }

        if (actionBuildController.AimCamera == null)
        {
            throw new InvalidOperationException("TerraMageActionBuildController must have an aim camera reference.");
        }

        RequireObject("TerraMage_MockBody");
        RequireObject("TerraMage_MockHood");
        RequireObject("TerraMage_MockStaff");

        var cameraObject = RequireObject("TerraMage_Camera");
        var cameraComponent = RequireComponent<Camera>(cameraObject, "TerraMage_Camera");
        var followCamera = RequireComponent<TerraMageFollowCamera>(cameraObject, "TerraMage_Camera");
        var aimSystem = RequireComponent<TerraMageAimSystem>(cameraObject, "TerraMage_Camera");

        if (followCamera.Target != player.transform)
        {
            throw new InvalidOperationException("TerraMageFollowCamera must target TerraMage_Player.");
        }

        if (aimSystem.AimCamera != cameraComponent)
        {
            throw new InvalidOperationException("TerraMageAimSystem must reference TerraMage_Camera.");
        }

        if (aimSystem.DistanceOrigin != player.transform)
        {
            throw new InvalidOperationException("TerraMageAimSystem must use TerraMage_Player as distance origin.");
        }

        if (aimSystem.AimMarker == null)
        {
            throw new InvalidOperationException("TerraMageAimSystem must reference TerraMage_AimMarker.");
        }

        if (actionBuildController.AimSystem != aimSystem)
        {
            throw new InvalidOperationException("TerraMageActionBuildController must use TerraMageAimSystem for ranged target debug.");
        }

        if (meleeGestureController.AimCamera != cameraComponent)
        {
            throw new InvalidOperationException("TerraMageMeleeGestureController must use TerraMage_Camera for melee hit checks.");
        }

        if (meleeGestureController.WeaponVisual == null)
        {
            throw new InvalidOperationException("TerraMageMeleeGestureController must reference TerraMage_MockStaff for swing animation.");
        }

        RequireObject("TerraMage_AimMarker");
        RequireObject("TerraMage_Ground");
        RequireObject("TerraMage_CoreMarker");
        RequireObject("TerraMage_ScaleBlock_1");
        RequireObject("TerraMage_AimTargetRange");
        RequireObject("TerraMage_WeaponWheelCanvas");
        RequireObject("TerraMage_WeaponWheelRoot");
        RequireObject("TerraMage_WeaponWheelTitle");

        RequireAimTarget("TerraMage_StaticTarget_01");
        RequireAimTarget("TerraMage_StaticTarget_02");
        RequireAimTarget("TerraMage_StaticTarget_03");

        var movingTarget = RequireAimTarget("TerraMage_MovingTarget");
        RequireComponent<TerraMageAimTargetMotion>(movingTarget, "TerraMage_MovingTarget");

        var disappearingTarget = RequireAimTarget("TerraMage_DisappearingTarget");
        var disappearingVisibility =
            RequireComponent<TerraMageAimTargetVisibility>(disappearingTarget, "TerraMage_DisappearingTarget");
        if (disappearingVisibility.Mode != TerraMageAimTargetVisibilityMode.DisappearAfterDelay)
        {
            throw new InvalidOperationException("TerraMage_DisappearingTarget must use DisappearAfterDelay mode.");
        }

        var blinkingTarget = RequireAimTarget("TerraMage_BlinkingTarget");
        var blinkingVisibility =
            RequireComponent<TerraMageAimTargetVisibility>(blinkingTarget, "TerraMage_BlinkingTarget");
        if (blinkingVisibility.Mode != TerraMageAimTargetVisibilityMode.Blink)
        {
            throw new InvalidOperationException("TerraMage_BlinkingTarget must use Blink mode.");
        }

        if (weaponLoadout.ActiveSlotCount != 2)
        {
            throw new InvalidOperationException("Demo loadout must include exactly one melee weapon and one ranged weapon.");
        }

        var meleeWeapon = weaponLoadout.GetWeapon(0);
        if (meleeWeapon == null || meleeWeapon.DisplayName != "Stone Gauntlet")
        {
            throw new InvalidOperationException("Slot 0 must be the Stone Gauntlet melee weapon.");
        }

        var rangedWeapon = weaponLoadout.GetWeapon(1);
        if (rangedWeapon == null || rangedWeapon.DisplayName != "Shard Sling")
        {
            throw new InvalidOperationException("Slot 1 must be the Shard Sling ranged weapon.");
        }

        if (weaponWheelUI.OpenWheelKey != KeyCode.Tab)
        {
            throw new InvalidOperationException("Weapon wheel must open with Tab.");
        }

        if (Mathf.Abs(TerraMageWeaponWheelUI.CalculateSegmentSweep(2) - 180f) > 0.01f)
        {
            throw new InvalidOperationException("Two active wheel entries must divide the wheel into 2 equal halves.");
        }

        if (Mathf.Abs(TerraMageWeaponWheelUI.CalculateSegmentSweep(3) - 120f) > 0.01f)
        {
            throw new InvalidOperationException("Three active wheel entries must divide the wheel into 3 equal segments.");
        }

        weaponWheelUI.RebuildImmediately();
        if (weaponWheelUI.VisualSegmentCount != weaponLoadout.ActiveSlotCount)
        {
            throw new InvalidOperationException("Weapon wheel must render only the active assigned entries.");
        }

        float expectedSweep = 360f / weaponLoadout.ActiveSlotCount;
        if (Mathf.Abs(weaponWheelUI.CurrentSegmentSweepDegrees - expectedSweep) > 0.01f)
        {
            throw new InvalidOperationException("Weapon wheel segments must fill the full circle evenly.");
        }

        weaponLoadout.SelectSlot(0);
        if (actionBuildController.CurrentAttackMode != TerraMageWeaponAttackMode.Melee)
        {
            throw new InvalidOperationException("Assigned melee weapons must keep melee attack mode.");
        }

        if (meleeGestureController.CurrentMeleeReach <= 0f)
        {
            throw new InvalidOperationException("Melee weapon selection must expose melee reach.");
        }

        weaponLoadout.SelectSlot(1);
        if (weaponLoadout.CurrentWeapon.DisplayName != "Shard Sling")
        {
            throw new InvalidOperationException("Demo loadout must include a ranged Shard Sling profile.");
        }

        if (actionBuildController.CurrentAttackMode != TerraMageWeaponAttackMode.Ranged)
        {
            throw new InvalidOperationException("Ranged weapon selection must change attack mode.");
        }

        if (actionBuildController.CurrentPullRange <= 0f || actionBuildController.CurrentThrowForce <= 0f)
        {
            throw new InvalidOperationException("Ranged weapon selection must expose ranged combat values.");
        }

        if (weaponWheelUI.HoverSlotIndex != weaponLoadout.SelectedSlotIndex)
        {
            throw new InvalidOperationException("Weapon wheel hover must stay synced with the selected weapon after selection.");
        }

        Debug.Log("TerraMageFirstSceneValidator passed.");
    }

    private static GameObject RequireAimTarget(string objectName)
    {
        var found = RequireObject(objectName);
        RequireComponent<TerraMageAimTarget>(found, objectName);
        RequireComponent<Collider>(found, objectName);
        return found;
    }

    private static GameObject RequireObject(string objectName)
    {
        var found = GameObject.Find(objectName);
        if (found == null)
        {
            throw new InvalidOperationException($"Required scene object is missing: {objectName}");
        }

        return found;
    }

    private static T RequireComponent<T>(GameObject target, string objectName) where T : Component
    {
        var component = target.GetComponent<T>();
        if (component == null)
        {
            throw new InvalidOperationException($"{objectName} is missing required component {typeof(T).Name}.");
        }

        return component;
    }
}
