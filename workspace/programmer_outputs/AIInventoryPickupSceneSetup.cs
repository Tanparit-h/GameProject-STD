using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class AIInventoryPickupSceneSetup
{
    private const string ScenePath = "Assets/Scenes/InventoryPickupScene.unity";

    public static void SetupScene()
    {
        if (TryValidateExistingScene())
        {
            Debug.Log("AIInventoryPickupSceneSetup skipped rebuild because scene already matches spec.");
            return;
        }

        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        CreateGround();
        var inventory = CreatePlayer();
        CreatePickup(inventory);
        CreateLight();

        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene, ScenePath);
        Debug.Log("AIInventoryPickupSceneSetup complete.");
    }

    private static bool TryValidateExistingScene()
    {
        if (AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath) == null)
        {
            return false;
        }

        try
        {
            AIInventoryPickupSceneValidator.ValidateScene();
            return true;
        }
        catch (System.Exception ex)
        {
            Debug.Log($"AIInventoryPickupSceneSetup rebuilding scene: {ex.Message}");
            return false;
        }
    }

    private static void CreateGround()
    {
        var ground = GameObject.CreatePrimitive(PrimitiveType.Cube);
        ground.name = "AIInventory_Ground";
        ground.transform.position = new Vector3(0f, -0.05f, 0f);
        ground.transform.localScale = new Vector3(12f, 0.1f, 12f);
        Tint(ground, new Color(0.24f, 0.29f, 0.33f));
    }

    private static InventoryState CreatePlayer()
    {
        var player = new GameObject("AIInventory_Player");
        player.transform.position = new Vector3(0f, 1f, -2f);

        var trigger = player.AddComponent<SphereCollider>();
        trigger.isTrigger = true;
        trigger.radius = 2.5f;

        var body = player.AddComponent<Rigidbody>();
        body.isKinematic = true;
        body.useGravity = false;

        player.AddComponent<InteractSystem>();
        var inventory = player.AddComponent<InventoryState>();

        var marker = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        marker.name = "AIInventory_PlayerMarker";
        marker.transform.SetParent(player.transform, false);
        marker.transform.localPosition = Vector3.zero;
        marker.transform.localScale = new Vector3(0.6f, 1f, 0.6f);
        Tint(marker, new Color(0.18f, 0.64f, 0.93f));

        return inventory;
    }

    private static void CreatePickup(InventoryState inventory)
    {
        var pickup = new GameObject("AIInventory_Pickup");
        pickup.transform.position = new Vector3(0f, 1f, 0f);

        var colliderComponent = pickup.AddComponent<BoxCollider>();
        colliderComponent.size = new Vector3(0.8f, 0.8f, 0.8f);

        var visual = GameObject.CreatePrimitive(PrimitiveType.Cube);
        visual.name = "AIInventory_PickupVisual";
        visual.transform.SetParent(pickup.transform, false);
        visual.transform.localPosition = Vector3.zero;
        visual.transform.localScale = new Vector3(0.75f, 0.75f, 0.75f);
        Object.DestroyImmediate(visual.GetComponent<Collider>());
        Tint(visual, new Color(0.94f, 0.78f, 0.22f));

        var pickupInteractable = pickup.AddComponent<PickupInteractable>();
        pickupInteractable.ConfigurePickup(inventory, "sun_shard", "Sun Shard", colliderComponent, visual);
    }

    private static void CreateLight()
    {
        var lightObject = new GameObject("AIInventory_Light");
        lightObject.transform.rotation = Quaternion.Euler(50f, -30f, 0f);
        var light = lightObject.AddComponent<Light>();
        light.type = LightType.Directional;
        light.intensity = 1.1f;
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
