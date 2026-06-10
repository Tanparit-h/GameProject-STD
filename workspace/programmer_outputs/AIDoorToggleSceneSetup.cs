using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class AIDoorToggleSceneSetup
{
    private const string ScenePath = "Assets/Scenes/DoorToggleScene.unity";

    public static void SetupScene()
    {
        if (TryValidateExistingScene())
        {
            Debug.Log("AIDoorToggleSceneSetup skipped rebuild because scene already matches spec.");
            return;
        }

        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        CreateGround();
        CreatePlayer();
        CreateDoor();
        CreateLight();

        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene, ScenePath);
        Debug.Log("AIDoorToggleSceneSetup complete.");
    }

    private static bool TryValidateExistingScene()
    {
        if (AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath) == null)
        {
            return false;
        }

        try
        {
            AIDoorToggleSceneValidator.ValidateScene();
            return true;
        }
        catch (System.Exception ex)
        {
            Debug.Log($"AIDoorToggleSceneSetup rebuilding scene: {ex.Message}");
            return false;
        }
    }

    private static void CreateGround()
    {
        var ground = GameObject.CreatePrimitive(PrimitiveType.Cube);
        ground.name = "AIDoor_Ground";
        ground.transform.position = new Vector3(0f, -0.05f, 0f);
        ground.transform.localScale = new Vector3(12f, 0.1f, 12f);
        Tint(ground, new Color(0.28f, 0.32f, 0.35f));
    }

    private static void CreatePlayer()
    {
        var player = new GameObject("AIDoor_Player");
        player.transform.position = new Vector3(0f, 1f, -2.2f);

        var trigger = player.AddComponent<SphereCollider>();
        trigger.isTrigger = true;
        trigger.radius = 2.5f;

        var body = player.AddComponent<Rigidbody>();
        body.isKinematic = true;
        body.useGravity = false;

        player.AddComponent<InteractSystem>();

        var marker = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        marker.name = "AIDoor_PlayerMarker";
        marker.transform.SetParent(player.transform, false);
        marker.transform.localPosition = new Vector3(0f, 0f, 0f);
        marker.transform.localScale = new Vector3(0.6f, 1f, 0.6f);
        Tint(marker, new Color(0.2f, 0.65f, 0.95f));
    }

    private static void CreateDoor()
    {
        var root = new GameObject("AIDoor_ToggleDoor");
        root.transform.position = new Vector3(0f, 1f, 0f);

        var frameLeft = GameObject.CreatePrimitive(PrimitiveType.Cube);
        frameLeft.name = "AIDoor_FrameLeft";
        frameLeft.transform.SetParent(root.transform, false);
        frameLeft.transform.localPosition = new Vector3(-0.55f, 0f, 0f);
        frameLeft.transform.localScale = new Vector3(0.1f, 2.2f, 0.22f);

        var frameRight = GameObject.CreatePrimitive(PrimitiveType.Cube);
        frameRight.name = "AIDoor_FrameRight";
        frameRight.transform.SetParent(root.transform, false);
        frameRight.transform.localPosition = new Vector3(0.55f, 0f, 0f);
        frameRight.transform.localScale = new Vector3(0.1f, 2.2f, 0.22f);

        var frameTop = GameObject.CreatePrimitive(PrimitiveType.Cube);
        frameTop.name = "AIDoor_FrameTop";
        frameTop.transform.SetParent(root.transform, false);
        frameTop.transform.localPosition = new Vector3(0f, 1.05f, 0f);
        frameTop.transform.localScale = new Vector3(1.2f, 0.1f, 0.22f);

        Tint(frameLeft, new Color(0.35f, 0.25f, 0.18f));
        Tint(frameRight, new Color(0.35f, 0.25f, 0.18f));
        Tint(frameTop, new Color(0.35f, 0.25f, 0.18f));

        var hinge = new GameObject("AIDoor_DoorLeafHinge");
        hinge.transform.SetParent(root.transform, false);
        hinge.transform.localPosition = new Vector3(-0.45f, 0f, 0f);

        var doorLeaf = GameObject.CreatePrimitive(PrimitiveType.Cube);
        doorLeaf.name = "AIDoor_DoorLeaf";
        doorLeaf.transform.SetParent(hinge.transform, false);
        doorLeaf.transform.localPosition = new Vector3(0.45f, 0f, 0f);
        doorLeaf.transform.localScale = new Vector3(0.9f, 2f, 0.12f);
        Tint(doorLeaf, new Color(0.72f, 0.54f, 0.33f));

        var toggle = doorLeaf.AddComponent<DoorToggleInteractable>();
        toggle.ConfigureDoor(hinge.transform, "Prototype Door", 92f, false);
    }

    private static void CreateLight()
    {
        var lightObject = new GameObject("AIDoor_Light");
        lightObject.transform.rotation = Quaternion.Euler(50f, -30f, 0f);
        var light = lightObject.AddComponent<Light>();
        light.type = LightType.Directional;
        light.intensity = 1.15f;
    }

    private static void Tint(GameObject targetObject, Color tint)
    {
        foreach (var renderer in targetObject.GetComponentsInChildren<Renderer>())
        {
            var sourceMaterials = renderer.sharedMaterials;
            var tintedMaterials = new Material[sourceMaterials.Length];

            for (int i = 0; i < sourceMaterials.Length; i++)
            {
                var sourceMaterial = sourceMaterials[i];
                if (sourceMaterial == null)
                {
                    continue;
                }

                var tintedMaterial = new Material(sourceMaterial);
                if (tintedMaterial.HasProperty("_Color"))
                {
                    tintedMaterial.color = tint;
                }

                tintedMaterials[i] = tintedMaterial;
            }

            renderer.sharedMaterials = tintedMaterials;
        }
    }
}
