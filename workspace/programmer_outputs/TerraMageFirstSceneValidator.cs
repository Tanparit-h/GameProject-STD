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
        RequireComponent<TerraMageMeleeGestureController>(player, "TerraMage_Player");

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

        RequireObject("TerraMage_AimMarker");
        RequireObject("TerraMage_Ground");
        RequireObject("TerraMage_CoreMarker");
        RequireObject("TerraMage_ScaleBlock_1");
        RequireObject("TerraMage_AimTargetRange");

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
