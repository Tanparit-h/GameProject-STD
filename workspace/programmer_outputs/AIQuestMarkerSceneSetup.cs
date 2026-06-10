using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class AIQuestMarkerSceneSetup
{
    private const string ScenePath = "Assets/Scenes/QuestMarkerScene.unity";

    public static void SetupScene()
    {
        if (TryValidateExistingScene())
        {
            Debug.Log("AIQuestMarkerSceneSetup skipped rebuild because scene already matches spec.");
            return;
        }

        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        CreateGround();
        CreatePlayer();
        CreateLight();

        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene, ScenePath);
        Debug.Log("AIQuestMarkerSceneSetup complete.");
    }

    private static bool TryValidateExistingScene()
    {
        if (AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath) == null)
        {
            return false;
        }

        try
        {
            AIQuestMarkerSceneValidator.ValidateScene();
            return true;
        }
        catch (System.Exception ex)
        {
            Debug.Log($"AIQuestMarkerSceneSetup rebuilding scene: {ex.Message}");
            return false;
        }
    }

    private static void CreateGround()
    {
        var ground = GameObject.CreatePrimitive(PrimitiveType.Cube);
        ground.name = "AIQuest_Ground";
        ground.transform.position = new Vector3(0f, -0.05f, 0f);
        ground.transform.localScale = new Vector3(16f, 0.1f, 16f);
        Tint(ground, new Color(0.23f, 0.27f, 0.31f));
    }

    private static void CreatePlayer()
    {
        var player = new GameObject("AIQuest_Player");
        player.transform.position = new Vector3(0f, 1f, -4f);

        var tracker = player.AddComponent<QuestMarkerTracker>();

        var marker = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        marker.name = "AIQuest_MarkerVisual";
        marker.transform.SetParent(player.transform, false);
        marker.transform.localPosition = new Vector3(0f, 1.5f, 0f);
        marker.transform.localScale = new Vector3(0.14f, 0.3f, 0.14f);
        Tint(marker, new Color(0.18f, 0.82f, 0.46f));

        var playerMarker = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        playerMarker.name = "AIQuest_PlayerMarker";
        playerMarker.transform.SetParent(player.transform, false);
        playerMarker.transform.localPosition = Vector3.zero;
        playerMarker.transform.localScale = new Vector3(0.6f, 1f, 0.6f);
        Tint(playerMarker, new Color(0.2f, 0.64f, 0.93f));

        var objective = CreateObjective();
        tracker.Configure(objective, marker.transform);
    }

    private static QuestMarkerObjective CreateObjective()
    {
        var existing = GameObject.Find("AIQuest_Objective");
        if (existing != null)
        {
            return existing.GetComponent<QuestMarkerObjective>();
        }

        var objective = GameObject.CreatePrimitive(PrimitiveType.Cube);
        objective.name = "AIQuest_Objective";
        objective.transform.position = new Vector3(0f, 1f, 4f);
        objective.transform.localScale = new Vector3(1.2f, 2.4f, 1.2f);
        Tint(objective, new Color(0.94f, 0.48f, 0.22f));

        var objectiveComponent = objective.AddComponent<QuestMarkerObjective>();
        objectiveComponent.ConfigureObjective("Ancient Beacon", 1.25f);
        return objectiveComponent;
    }

    private static void CreateLight()
    {
        var lightObject = new GameObject("AIQuest_Light");
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
