using System;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class AIDoorToggleSceneValidator
{
    private const string ScenePath = "Assets/Scenes/DoorToggleScene.unity";

    public static void ValidateScene()
    {
        EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);

        var player = RequireObject("AIDoor_Player");
        RequireComponent<InteractSystem>(player, "AIDoor_Player");

        var trigger = RequireComponent<SphereCollider>(player, "AIDoor_Player");
        if (!trigger.isTrigger)
        {
            throw new InvalidOperationException("AIDoor_Player SphereCollider must be a trigger.");
        }

        var body = RequireComponent<Rigidbody>(player, "AIDoor_Player");
        if (!body.isKinematic)
        {
            throw new InvalidOperationException("AIDoor_Player Rigidbody must be kinematic.");
        }

        RequireObject("AIDoor_Ground");
        RequireObject("AIDoor_ToggleDoor");
        RequireObject("AIDoor_FrameLeft");
        RequireObject("AIDoor_FrameRight");
        RequireObject("AIDoor_FrameTop");
        RequireObject("AIDoor_PlayerMarker");

        var hingeObject = RequireObject("AIDoor_DoorLeafHinge");
        var doorLeaf = RequireObject("AIDoor_DoorLeaf");
        var toggle = RequireComponent<DoorToggleInteractable>(doorLeaf, "AIDoor_DoorLeaf");
        RequireComponent<Collider>(doorLeaf, "AIDoor_DoorLeaf");

        if (toggle.DoorHinge != hingeObject.transform)
        {
            throw new InvalidOperationException("Door toggle interactable must reference the hinge transform.");
        }

        if (toggle.OpenAngle < 45f)
        {
            throw new InvalidOperationException("Door must open with a meaningful swing angle.");
        }

        if (toggle.DisplayName != "Prototype Door")
        {
            throw new InvalidOperationException("Door prompt should describe the prototype door.");
        }

        AssertLocalYaw(toggle.DoorHinge, toggle.ClosedLocalEuler.y, "Door must start closed.");
        if (toggle.IsOpen)
        {
            throw new InvalidOperationException("Door must start in the closed state.");
        }

        toggle.Interact();
        if (!toggle.IsOpen)
        {
            throw new InvalidOperationException("First interaction must open the door.");
        }

        AssertLocalYaw(toggle.DoorHinge, toggle.OpenLocalEuler.y, "Open interaction must rotate the door leaf.");

        toggle.Interact();
        if (toggle.IsOpen)
        {
            throw new InvalidOperationException("Second interaction must close the door.");
        }

        AssertLocalYaw(toggle.DoorHinge, toggle.ClosedLocalEuler.y, "Second interaction must restore the closed rotation.");

        Debug.Log("AIDoorToggleSceneValidator passed.");
    }

    private static void AssertLocalYaw(Transform target, float expectedY, string message)
    {
        float actualY = target.localEulerAngles.y;
        if (Mathf.Abs(Mathf.DeltaAngle(actualY, expectedY)) > 0.01f)
        {
            throw new InvalidOperationException(message);
        }
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
