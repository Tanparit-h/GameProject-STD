using TerraMageTD;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.UI;

public static class TerraMageFirstSceneSetup
{
    private const string ScenePath = "Assets/Scenes/TerraMage_FirstScene.unity";

    public static void SetupFirstScene()
    {
        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

        CreateGround();
        CreateScaleBlocks();
        CreateCoreMarker();
        var player = CreatePlayer();
        CreateCameraRig(player);
        CreateAimTargetRange();
        CreateCrosshairUi();
        CreateWeaponWheelUi(player);
        CreateLight();

        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene, ScenePath);
        Debug.Log("TerraMageFirstSceneSetup complete.");
    }

    private static void CreateGround()
    {
        var ground = GameObject.CreatePrimitive(PrimitiveType.Cube);
        ground.name = "TerraMage_Ground";
        ground.transform.position = new Vector3(0f, -0.05f, 2f);
        ground.transform.localScale = new Vector3(28f, 0.1f, 28f);
        Tint(ground, new Color(0.22f, 0.24f, 0.28f));
    }

    private static void CreateScaleBlocks()
    {
        for (int i = 0; i < 5; i++)
        {
            var block = GameObject.CreatePrimitive(PrimitiveType.Cube);
            block.name = $"TerraMage_ScaleBlock_{i + 1}";
            block.transform.position = new Vector3(-6f + i * 3f, 0.35f, 0f);
            block.transform.localScale = new Vector3(1.2f, 0.7f + i * 0.12f, 1.2f);
            Tint(block, new Color(0.3f + i * 0.05f, 0.45f, 0.55f));
        }
    }

    private static void CreateCoreMarker()
    {
        var core = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        core.name = "TerraMage_CoreMarker";
        core.transform.position = new Vector3(0f, 0.45f, 9f);
        core.transform.localScale = Vector3.one * 0.75f;
        Tint(core, new Color(0.95f, 0.45f, 0.2f));
    }

    private static GameObject CreatePlayer()
    {
        var player = new GameObject("TerraMage_Player");
        player.transform.position = new Vector3(0f, 0.16f, -6f);

        var controller = player.AddComponent<CharacterController>();
        controller.height = 0.3f;
        controller.radius = 0.075f;
        controller.center = new Vector3(0f, 0.15f, 0f);
        controller.stepOffset = 0.06f;

        player.AddComponent<TerraMageTinyMageController>();
        var actionBuildController = player.AddComponent<TerraMageActionBuildController>();
        var meleeGestureController = player.AddComponent<TerraMageMeleeGestureController>();
        var weaponLoadout = player.AddComponent<TerraMageWeaponLoadout>();
        weaponLoadout.ConfigureDemoLoadout();

        actionBuildController.SetWeaponLoadout(weaponLoadout);
        actionBuildController.SetMeleeGestureController(meleeGestureController);
        meleeGestureController.SetWeaponLoadout(weaponLoadout);

        var body = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        body.name = "TerraMage_MockBody";
        body.transform.SetParent(player.transform);
        body.transform.localPosition = new Vector3(0f, 0.15f, 0f);
        body.transform.localScale = new Vector3(0.16f, 0.15f, 0.16f);
        Tint(body, new Color(0.18f, 0.55f, 0.9f));

        var hood = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        hood.name = "TerraMage_MockHood";
        hood.transform.SetParent(player.transform);
        hood.transform.localPosition = new Vector3(0f, 0.31f, 0f);
        hood.transform.localScale = Vector3.one * 0.13f;
        Tint(hood, new Color(0.92f, 0.95f, 1f));

        var staffPivot = new GameObject("TerraMage_StaffSwingRoot");
        staffPivot.transform.SetParent(player.transform);
        staffPivot.transform.localPosition = new Vector3(0.13f, 0.08f, 0.03f);
        staffPivot.transform.localRotation = Quaternion.identity;

        var staff = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        staff.name = "TerraMage_MockStaff";
        staff.transform.SetParent(staffPivot.transform);
        staff.transform.localPosition = new Vector3(0f, 0.1f, 0f);
        staff.transform.localRotation = Quaternion.Euler(12f, 0f, 0f);
        staff.transform.localScale = new Vector3(0.015f, 0.22f, 0.015f);
        Tint(staff, new Color(0.45f, 0.28f, 0.18f));
        meleeGestureController.SetWeaponSwingRoot(staffPivot.transform);
        meleeGestureController.SetWeaponVisual(staff.transform);

        return player;
    }

    private static void CreateCameraRig(GameObject player)
    {
        var cameraObject = new GameObject("TerraMage_Camera");
        cameraObject.transform.position = player.transform.position + new Vector3(0f, 1.25f, -3.8f);

        var camera = cameraObject.AddComponent<Camera>();
        camera.nearClipPlane = 0.01f;
        camera.fieldOfView = 55f;
        camera.tag = "MainCamera";

        cameraObject.AddComponent<AudioListener>();

        var followCamera = cameraObject.AddComponent<TerraMageFollowCamera>();
        followCamera.SetTarget(player.transform);

        var aimSystem = cameraObject.AddComponent<TerraMageAimSystem>();
        aimSystem.SetAimCamera(camera);
        aimSystem.SetDistanceOrigin(player.transform);

        var aimMarker = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        aimMarker.name = "TerraMage_AimMarker";
        aimMarker.transform.position = cameraObject.transform.position + cameraObject.transform.forward * 8f;
        aimMarker.transform.localScale = Vector3.one * 0.12f;
        Object.DestroyImmediate(aimMarker.GetComponent<Collider>());
        aimMarker.layer = 2;
        Tint(aimMarker, new Color(0.2f, 0.95f, 1f));
        aimSystem.SetAimMarker(aimMarker.transform);

        var playerController = player.GetComponent<TerraMageTinyMageController>();
        playerController.SetCameraPivot(cameraObject.transform);

        var actionBuildController = player.GetComponent<TerraMageActionBuildController>();
        actionBuildController.SetAimCamera(camera);
        actionBuildController.SetAimSystem(aimSystem);

        var meleeGestureController = player.GetComponent<TerraMageMeleeGestureController>();
        meleeGestureController.SetAimCamera(camera);
    }

    private static void CreateWeaponWheelUi(GameObject player)
    {
        var loadout = player.GetComponent<TerraMageWeaponLoadout>();
        var meleeGestureController = player.GetComponent<TerraMageMeleeGestureController>();
        var actionBuildController = player.GetComponent<TerraMageActionBuildController>();

        var canvasObject = new GameObject("TerraMage_WeaponWheelCanvas");
        var canvas = canvasObject.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        canvas.sortingOrder = 20;

        var scaler = canvasObject.AddComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1920f, 1080f);
        canvasObject.AddComponent<GraphicRaycaster>();

        var titleObject = new GameObject("TerraMage_WeaponWheelTitle", typeof(RectTransform));
        var titleRect = titleObject.GetComponent<RectTransform>();
        titleRect.SetParent(canvasObject.transform, false);
        titleRect.anchorMin = new Vector2(0.5f, 0.5f);
        titleRect.anchorMax = new Vector2(0.5f, 0.5f);
        titleRect.pivot = new Vector2(0.5f, 0.5f);
        titleRect.anchoredPosition = new Vector2(0f, 196f);
        titleRect.sizeDelta = new Vector2(420f, 44f);

        var titleText = titleObject.AddComponent<Text>();
        titleText.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        titleText.fontSize = 22;
        titleText.alignment = TextAnchor.MiddleCenter;
        titleText.color = new Color(0.95f, 0.96f, 1f, 1f);
        titleText.text = "Hold Tab - release to equip";

        var rootObject = new GameObject("TerraMage_WeaponWheelRoot", typeof(RectTransform));
        var rootRect = rootObject.GetComponent<RectTransform>();
        rootRect.SetParent(canvasObject.transform, false);
        rootRect.anchorMin = new Vector2(0.5f, 0.5f);
        rootRect.anchorMax = new Vector2(0.5f, 0.5f);
        rootRect.pivot = new Vector2(0.5f, 0.5f);
        rootRect.sizeDelta = new Vector2(360f, 360f);

        var wheelUI = player.AddComponent<TerraMageWeaponWheelUI>();
        wheelUI.Configure(loadout, canvas, rootRect);
        wheelUI.RebuildImmediately();
        wheelUI.HideImmediately();

        meleeGestureController.SetWeaponWheelUI(wheelUI);
        actionBuildController.SetWeaponWheelUI(wheelUI);

        var followCamera = Object.FindAnyObjectByType<TerraMageFollowCamera>();
        if (followCamera != null)
        {
            followCamera.SetWeaponWheelUI(wheelUI);
        }
    }

    private static void CreateCrosshairUi()
    {
        var canvasObject = new GameObject("TerraMage_CrosshairCanvas");
        var canvas = canvasObject.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        canvas.sortingOrder = 10;

        var scaler = canvasObject.AddComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1920f, 1080f);
        canvasObject.AddComponent<GraphicRaycaster>();

        CreateCrosshairLine("TerraMage_CrosshairHorizontal", canvasObject.transform, new Vector2(22f, 3f));
        CreateCrosshairLine("TerraMage_CrosshairVertical", canvasObject.transform, new Vector2(3f, 22f));
    }

    private static void CreateCrosshairLine(string objectName, Transform parent, Vector2 size)
    {
        var lineObject = new GameObject(objectName, typeof(RectTransform));
        var rect = lineObject.GetComponent<RectTransform>();
        rect.SetParent(parent, false);
        rect.anchorMin = new Vector2(0.5f, 0.5f);
        rect.anchorMax = new Vector2(0.5f, 0.5f);
        rect.pivot = new Vector2(0.5f, 0.5f);
        rect.anchoredPosition = Vector2.zero;
        rect.sizeDelta = size;

        var image = lineObject.AddComponent<RawImage>();
        image.color = new Color(0.95f, 0.98f, 1f, 0.86f);
    }

    private static void CreateAimTargetRange()
    {
        var rangeRoot = new GameObject("TerraMage_AimTargetRange");

        CreateAimTarget(
            "TerraMage_StaticTarget_01",
            PrimitiveType.Cube,
            new Vector3(-4f, 0.7f, 6f),
            new Vector3(0.8f, 1.4f, 0.8f),
            new Color(0.9f, 0.3f, 0.3f),
            rangeRoot.transform);

        CreateAimTarget(
            "TerraMage_StaticTarget_02",
            PrimitiveType.Sphere,
            new Vector3(0f, 0.8f, 8f),
            new Vector3(1.1f, 1.1f, 1.1f),
            new Color(0.3f, 0.8f, 0.4f),
            rangeRoot.transform);

        CreateAimTarget(
            "TerraMage_StaticTarget_03",
            PrimitiveType.Cylinder,
            new Vector3(4f, 0.75f, 10f),
            new Vector3(0.55f, 0.9f, 0.55f),
            new Color(0.35f, 0.55f, 1f),
            rangeRoot.transform);

        var movingTarget = CreateAimTarget(
            "TerraMage_MovingTarget",
            PrimitiveType.Capsule,
            new Vector3(-2.5f, 0.9f, 12f),
            new Vector3(0.8f, 1.2f, 0.8f),
            new Color(1f, 0.7f, 0.2f),
            rangeRoot.transform);
        movingTarget.AddComponent<TerraMageAimTargetMotion>();

        var disappearingTarget = CreateAimTarget(
            "TerraMage_DisappearingTarget",
            PrimitiveType.Cube,
            new Vector3(2.5f, 0.8f, 12f),
            new Vector3(1f, 1f, 1f),
            new Color(0.75f, 0.3f, 0.9f),
            rangeRoot.transform);
        var disappearingVisibility = disappearingTarget.AddComponent<TerraMageAimTargetVisibility>();
        disappearingVisibility.Configure(TerraMageAimTargetVisibilityMode.DisappearAfterDelay, 5f, 1f, 1f);

        var blinkingTarget = CreateAimTarget(
            "TerraMage_BlinkingTarget",
            PrimitiveType.Sphere,
            new Vector3(0f, 0.85f, 14f),
            new Vector3(1f, 1f, 1f),
            new Color(0.95f, 0.95f, 0.35f),
            rangeRoot.transform);
        var blinkingVisibility = blinkingTarget.AddComponent<TerraMageAimTargetVisibility>();
        blinkingVisibility.Configure(TerraMageAimTargetVisibilityMode.Blink, 1f, 1.1f, 0.55f);
    }

    private static GameObject CreateAimTarget(
        string objectName,
        PrimitiveType primitiveType,
        Vector3 position,
        Vector3 scale,
        Color tint,
        Transform parent)
    {
        var targetObject = GameObject.CreatePrimitive(primitiveType);
        targetObject.name = objectName;
        targetObject.transform.SetParent(parent);
        targetObject.transform.position = position;
        targetObject.transform.localScale = scale;
        Tint(targetObject, tint);

        var target = targetObject.AddComponent<TerraMageAimTarget>();
        target.Configure(objectName, tint);
        targetObject.AddComponent<TerraMageDamageable>();
        return targetObject;
    }

    private static void CreateLight()
    {
        var lightObject = new GameObject("TerraMage_Sun");
        lightObject.transform.rotation = Quaternion.Euler(50f, -30f, 0f);
        var light = lightObject.AddComponent<Light>();
        light.type = LightType.Directional;
        light.intensity = 1.25f;
    }

    private static void Tint(GameObject targetObject, Color tint)
    {
        foreach (var renderer in targetObject.GetComponentsInChildren<Renderer>())
        {
            foreach (var material in renderer.materials)
            {
                if (material != null && material.HasProperty("_Color"))
                {
                    material.color = tint;
                }
            }
        }
    }
}
