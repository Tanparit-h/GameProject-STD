using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class AIDialoguePromptSceneSetup
{
    private const string ScenePath = "Assets/Scenes/DialoguePromptScene.unity";

    public static void SetupScene()
    {
        if (TryValidateExistingScene())
        {
            Debug.Log("AIDialoguePromptSceneSetup skipped rebuild because scene already matches spec.");
            return;
        }

        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        CreateGround();
        CreatePlayer();
        CreateDialogueNpc();
        CreateLight();

        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene, ScenePath);
        Debug.Log("AIDialoguePromptSceneSetup complete.");
    }

    private static bool TryValidateExistingScene()
    {
        if (AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath) == null)
        {
            return false;
        }

        try
        {
            AIDialoguePromptSceneValidator.ValidateScene();
            return true;
        }
        catch (System.Exception ex)
        {
            Debug.Log($"AIDialoguePromptSceneSetup rebuilding scene: {ex.Message}");
            return false;
        }
    }

    private static void CreateGround()
    {
        var ground = GameObject.CreatePrimitive(PrimitiveType.Cube);
        ground.name = "AIDialogue_Ground";
        ground.transform.position = new Vector3(0f, -0.05f, 0f);
        ground.transform.localScale = new Vector3(12f, 0.1f, 12f);
        Tint(ground, new Color(0.24f, 0.28f, 0.32f));
    }

    private static void CreatePlayer()
    {
        var player = new GameObject("AIDialogue_Player");
        player.transform.position = new Vector3(0f, 1f, -2f);

        var trigger = player.AddComponent<SphereCollider>();
        trigger.isTrigger = true;
        trigger.radius = 2.5f;

        var body = player.AddComponent<Rigidbody>();
        body.isKinematic = true;
        body.useGravity = false;

        player.AddComponent<InteractSystem>();

        var marker = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        marker.name = "AIDialogue_PlayerMarker";
        marker.transform.SetParent(player.transform, false);
        marker.transform.localPosition = Vector3.zero;
        marker.transform.localScale = new Vector3(0.6f, 1f, 0.6f);
        Tint(marker, new Color(0.2f, 0.64f, 0.93f));
    }

    private static void CreateDialogueNpc()
    {
        var npcRoot = new GameObject("AIDialogue_Npc");
        npcRoot.transform.position = new Vector3(0f, 1f, 0f);

        var body = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        body.name = "AIDialogue_NpcVisual";
        body.transform.SetParent(npcRoot.transform, false);
        body.transform.localPosition = Vector3.zero;
        body.transform.localScale = new Vector3(0.9f, 1.2f, 0.9f);
        Tint(body, new Color(0.88f, 0.58f, 0.26f));

        var promptPanel = GameObject.CreatePrimitive(PrimitiveType.Cube);
        promptPanel.name = "AIDialogue_PromptPanel";
        promptPanel.transform.SetParent(npcRoot.transform, false);
        promptPanel.transform.localPosition = new Vector3(0f, 1.8f, 0f);
        promptPanel.transform.localScale = new Vector3(1.8f, 0.35f, 0.12f);
        Tint(promptPanel, new Color(0.11f, 0.15f, 0.19f));
        promptPanel.SetActive(false);

        var state = npcRoot.AddComponent<DialoguePromptState>();
        state.Configure(promptPanel, "Welcome, traveler.", "The ruins are just ahead.");

        var interactable = npcRoot.AddComponent<DialoguePromptInteractable>();
        interactable.ConfigureDialogue(state, "Guide NPC");
    }

    private static void CreateLight()
    {
        var lightObject = new GameObject("AIDialogue_Light");
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
