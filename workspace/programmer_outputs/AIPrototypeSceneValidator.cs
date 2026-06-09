using System;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class AIPrototypeSceneValidator
{
    private const string ScenePath = "Assets/Scenes/SampleScene.unity";
    private const string AssetPath = "Assets/AIAssets/interactive_objects.glb";

    public static void ValidateSampleScene()
    {
        EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);

        var player = RequireObject("AIPrototype_Player");
        RequireComponent<InteractSystem>(player, "AIPrototype_Player");

        var trigger = RequireComponent<SphereCollider>(player, "AIPrototype_Player");
        if (!trigger.isTrigger)
        {
            throw new InvalidOperationException("AIPrototype_Player SphereCollider must be a trigger.");
        }

        var body = RequireComponent<Rigidbody>(player, "AIPrototype_Player");
        if (!body.isKinematic)
        {
            throw new InvalidOperationException("AIPrototype_Player Rigidbody must be kinematic.");
        }

        var interactable = RequireObject("AIPrototype_Interactable");
        RequireComponent<InteractableObject>(interactable, "AIPrototype_Interactable");
        RequireComponent<Collider>(interactable, "AIPrototype_Interactable");

        RequireObject("AIPrototype_VisualReference");

        if (AssetDatabase.LoadAssetAtPath<UnityEngine.Object>(AssetPath) == null)
        {
            throw new InvalidOperationException($"Required visual asset is missing: {AssetPath}");
        }

        Debug.Log("AIPrototypeSceneValidator passed.");
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
