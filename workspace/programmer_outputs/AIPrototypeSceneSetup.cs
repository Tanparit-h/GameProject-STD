using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class AIPrototypeSceneSetup
{
    private const string ScenePath = "Assets/Scenes/SampleScene.unity";
    private const string AssetPath = "Assets/AIAssets/interactive_objects.glb";

    public static void SetupSampleScene()
    {
        var scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);

        RemoveExisting("AIPrototype_Player");
        RemoveExisting("AIPrototype_Interactable");
        RemoveExisting("AIPrototype_VisualReference");

        var player = new GameObject("AIPrototype_Player");
        player.transform.position = new Vector3(0f, 1f, -2f);

        var trigger = player.AddComponent<SphereCollider>();
        trigger.isTrigger = true;
        trigger.radius = 2.5f;

        var body = player.AddComponent<Rigidbody>();
        body.isKinematic = true;
        body.useGravity = false;

        player.AddComponent<InteractSystem>();

        var interactable = GameObject.CreatePrimitive(PrimitiveType.Cube);
        interactable.name = "AIPrototype_Interactable";
        interactable.transform.position = new Vector3(0f, 1f, 0f);
        interactable.AddComponent<InteractableObject>();

        var visualReference = AssetDatabase.LoadAssetAtPath<GameObject>(AssetPath);
        if (visualReference != null)
        {
            var instance = (GameObject)PrefabUtility.InstantiatePrefab(visualReference);
            instance.name = "AIPrototype_VisualReference";
            instance.transform.position = new Vector3(3f, 0f, 0f);
        }
        else
        {
            var fallback = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            fallback.name = "AIPrototype_VisualReference";
            fallback.transform.position = new Vector3(3f, 1f, 0f);
            fallback.transform.localScale = Vector3.one * 0.75f;
            Debug.Log($"AIPrototype visual reference fallback created because {AssetPath} was not loaded as a GameObject.");
        }

        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene);

        Debug.Log("AIPrototypeSceneSetup complete.");
    }

    private static void RemoveExisting(string objectName)
    {
        var existing = GameObject.Find(objectName);
        if (existing != null)
        {
            Object.DestroyImmediate(existing);
        }
    }
}
