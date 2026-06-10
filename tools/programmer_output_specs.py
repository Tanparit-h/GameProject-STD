from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Callable

from tools.terra_mage_weapon_family_spec import (
    build_terra_mage_weapon_family_spec,
    is_terra_mage_weapon_family_request,
)


@dataclass(frozen=True)
class ProgrammerOutputSpec:
    key: str
    file_contents: dict[str, str]
    required_snippets: dict[str, list[str]]
    scene_setup_method: str
    scene_validation_method: str


@dataclass(frozen=True)
class ProgrammerFamilyDefinition:
    key: str
    title: str
    support_level: str
    description: str
    detector: Callable[[str, str], bool]
    spec_builder: Callable[[], ProgrammerOutputSpec] | None


class UnsupportedProgrammerFamilyError(ValueError):
    pass


class AmbiguousProgrammerFamilyError(ValueError):
    pass


def _clean(text: str) -> str:
    return dedent(text).strip() + "\n"


def _normalize(text: str) -> str:
    return " ".join((text or "").lower().replace("_", " ").split())


def is_terra_mage_third_person_aim_request(feature_request: str, task_id: str = "") -> bool:
    normalized_request = _normalize(feature_request)
    normalized_task_id = _normalize(task_id)

    if normalized_task_id == "terra-mage-third-person-aim-v005":
        return True

    has_terra_mage = "terra mage" in normalized_request
    has_camera = "third person" in normalized_request or "third-person" in feature_request.lower()
    has_aim = "aim" in normalized_request or "เล็ง" in feature_request

    return has_terra_mage and has_camera and has_aim


def is_interaction_vertical_slice_request(feature_request: str, task_id: str = "") -> bool:
    normalized_request = _normalize(feature_request)
    normalized_task_id = _normalize(task_id)

    if normalized_task_id == "feature-interaction-v1":
        return True

    has_interaction = "interact" in normalized_request or "interaction" in normalized_request
    has_player = "player" in normalized_request
    has_validation = "scene validation" in normalized_request or "vertical slice" in normalized_request
    return has_interaction and has_player and has_validation


def is_door_toggle_interaction_request(feature_request: str, task_id: str = "") -> bool:
    normalized_request = _normalize(feature_request)
    normalized_task_id = _normalize(task_id)

    if normalized_task_id == "feature-door-toggle-v1":
        return True

    has_door = "door" in normalized_request
    has_toggle = "toggle" in normalized_request or "open and closed" in normalized_request
    has_interaction = "interact" in normalized_request or "press e" in normalized_request
    return has_door and has_toggle and has_interaction


def is_inventory_pickup_request(feature_request: str, task_id: str = "") -> bool:
    normalized_request = _normalize(feature_request)
    normalized_task_id = _normalize(task_id)

    if normalized_task_id == "feature-inventory-pickup-v1":
        return True

    has_inventory = "inventory" in normalized_request
    has_pickup = "pickup" in normalized_request or "collect" in normalized_request
    has_interaction = "interact" in normalized_request or "press e" in normalized_request
    return has_inventory and has_pickup and has_interaction


def is_quest_marker_request(feature_request: str, task_id: str = "") -> bool:
    normalized_request = _normalize(feature_request)
    normalized_task_id = _normalize(task_id)

    if normalized_task_id == "feature-quest-marker-v1":
        return True

    has_quest = "quest" in normalized_request or "objective" in normalized_request
    has_marker = "marker" in normalized_request or "point" in normalized_request
    has_target = "target" in normalized_request or "reached" in normalized_request
    return has_quest and has_marker and has_target


def is_dialogue_prompt_request(feature_request: str, task_id: str = "") -> bool:
    normalized_request = _normalize(feature_request)
    normalized_task_id = _normalize(task_id)

    if normalized_task_id == "feature-dialogue-prompt-v1":
        return True

    has_dialogue = "dialogue" in normalized_request or "npc" in normalized_request
    has_prompt = "prompt" in normalized_request or "continue" in normalized_request
    has_interaction = "interact" in normalized_request or "press e" in normalized_request
    return has_dialogue and has_prompt and has_interaction


def is_terra_mage_first_wall_request(feature_request: str, task_id: str = "") -> bool:
    normalized_request = _normalize(feature_request)
    normalized_task_id = _normalize(task_id)

    if normalized_task_id == "terra-mage-first-wall-v003":
        return True

    return (
        "terra mage" in normalized_request
        and "first wall" in normalized_request
        and ("sandbox" in normalized_request or "action build" in normalized_request or "weapon wheel" in normalized_request)
    )


def is_terra_mage_first_scene_request(feature_request: str, task_id: str = "") -> bool:
    normalized_request = _normalize(feature_request)
    normalized_task_id = _normalize(task_id)

    if normalized_task_id == "terra-mage-first-scene-v004":
        return True

    return (
        "terra mage" in normalized_request
        and ("first scene" in normalized_request or "playable scene" in normalized_request)
        and ("walk" in normalized_request or "run" in normalized_request or "jump" in normalized_request)
    )


def default_interact_system() -> str:
    return _clean(
        """
        using System.Collections.Generic;
        using UnityEngine;

        public class InteractSystem : MonoBehaviour
        {
            [SerializeField] private float interactRange = 2.5f;
            [SerializeField] private KeyCode interactKey = KeyCode.E;
            [SerializeField] private string promptText = "Press E to Interact";

            private readonly List<InteractableObject> objectsInRange = new();
            private InteractableObject currentTarget;

            private void Update()
            {
                currentTarget = FindClosestInteractable();
                UpdatePromptFeedback(currentTarget);

                if (currentTarget != null && Input.GetKeyDown(interactKey))
                {
                    currentTarget.Interact();
                }
            }

            private InteractableObject FindClosestInteractable()
            {
                InteractableObject closest = null;
                float closestDistance = float.MaxValue;

                foreach (var candidate in objectsInRange)
                {
                    if (candidate == null || !candidate.CanInteract)
                    {
                        continue;
                    }

                    float distance = Vector3.Distance(transform.position, candidate.transform.position);
                    if (distance <= interactRange && distance < closestDistance)
                    {
                        closest = candidate;
                        closestDistance = distance;
                    }
                }

                return closest;
            }

            private void UpdatePromptFeedback(InteractableObject target)
            {
                if (target == null)
                {
                    Debug.Log("Interaction prompt hidden: no interactable object in range.");
                    return;
                }

                Debug.Log($"{promptText}: {target.DisplayName}");
            }

            private void OnTriggerEnter(Collider other)
            {
                var interactable = other.GetComponentInParent<InteractableObject>();
                if (interactable != null && !objectsInRange.Contains(interactable))
                {
                    objectsInRange.Add(interactable);
                }
            }

            private void OnTriggerExit(Collider other)
            {
                var interactable = other.GetComponentInParent<InteractableObject>();
                if (interactable != null)
                {
                    objectsInRange.Remove(interactable);
                }
            }
        }
        """
    )


def default_interactable_object() -> str:
    return _clean(
        """
        using UnityEngine;

        public class InteractableObject : MonoBehaviour
        {
            [SerializeField] private string displayName = "Interactable Object";
            [SerializeField] private bool canInteract = true;

            public string DisplayName => displayName;
            public bool CanInteract => canInteract;

            public void Configure(string newDisplayName, bool newCanInteract = true)
            {
                if (!string.IsNullOrWhiteSpace(newDisplayName))
                {
                    displayName = newDisplayName;
                }

                canInteract = newCanInteract;
            }

            protected bool TryBeginInteract()
            {
                if (!canInteract)
                {
                    Debug.Log($"{displayName} is currently unavailable.");
                    return false;
                }

                return true;
            }

            public virtual void Interact()
            {
                if (!TryBeginInteract())
                {
                    return;
                }

                Debug.Log($"Interaction triggered for {DisplayName}.");
            }
        }
        """
    )


def door_toggle_interactable() -> str:
    return _clean(
        """
        using UnityEngine;

        [DisallowMultipleComponent]
        public sealed class DoorToggleInteractable : InteractableObject
        {
            [SerializeField] private Transform doorHinge;
            [SerializeField] private float openAngle = 92f;
            [SerializeField] private bool startsOpen;
            [SerializeField] private Vector3 closedLocalEuler;

            private bool configured;
            private bool isOpen;

            public Transform DoorHinge => doorHinge;
            public float OpenAngle => openAngle;
            public bool IsOpen => isOpen;
            public Vector3 ClosedLocalEuler => closedLocalEuler;
            public Vector3 OpenLocalEuler => closedLocalEuler + new Vector3(0f, openAngle, 0f);

            private void Awake()
            {
                EnsureConfigured();
            }

            private void OnValidate()
            {
                if (doorHinge == null)
                {
                    doorHinge = transform;
                }

                if (!configured)
                {
                    closedLocalEuler = doorHinge.localEulerAngles;
                }
            }

            public void ConfigureDoor(Transform hinge, string doorName, float targetOpenAngle, bool openInitially = false)
            {
                doorHinge = hinge != null ? hinge : transform;
                closedLocalEuler = doorHinge.localEulerAngles;
                openAngle = Mathf.Clamp(targetOpenAngle, 15f, 170f);
                startsOpen = openInitially;
                configured = true;
                isOpen = startsOpen;
                Configure(doorName, true);
                ApplyStateImmediate();
            }

            public override void Interact()
            {
                EnsureConfigured();
                if (!TryBeginInteract())
                {
                    return;
                }

                isOpen = !isOpen;
                ApplyStateImmediate();
                Debug.Log($"Door toggled {DisplayName}: {(isOpen ? "open" : "closed")}.");
            }

            public void SetOpen(bool open)
            {
                EnsureConfigured();
                isOpen = open;
                ApplyStateImmediate();
            }

            private void EnsureConfigured()
            {
                if (doorHinge == null)
                {
                    doorHinge = transform;
                }

                if (configured)
                {
                    return;
                }

                closedLocalEuler = doorHinge.localEulerAngles;
                configured = true;
                isOpen = startsOpen;
                ApplyStateImmediate();
            }

            private void ApplyStateImmediate()
            {
                if (doorHinge == null)
                {
                    return;
                }

                doorHinge.localRotation = Quaternion.Euler(isOpen ? OpenLocalEuler : ClosedLocalEuler);
            }
        }
        """
    )


def default_interaction_scene_setup() -> str:
    return _clean(
        """
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
        """
    )


def default_interaction_scene_validator() -> str:
    return _clean(
        """
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
        """
    )


def default_interaction_report() -> str:
    return _clean(
        """
        # Interaction Vertical Slice - Implementation Report

        ## Goal

        Deliver a real Unity interaction slice that can be copied into the project, set up in the sample scene, and validated in batchmode.

        ## Implemented Programmer Outputs

        - `InteractSystem.cs`
        - `InteractableObject.cs`
        - `AIPrototypeSceneSetup.cs`
        - `AIPrototypeSceneValidator.cs`

        ## Behavior Summary

        - Detect nearby interactables through a trigger volume.
        - Select the closest valid interactable.
        - Show debug prompt feedback for the current target.
        - Trigger interaction with `E`.
        - Build and validate the sample scene through editor automation.

        ## Validation Target

        - Scene: `Assets/Scenes/SampleScene.unity`
        - Setup method: `AIPrototypeSceneSetup.SetupSampleScene`
        - Validation method: `AIPrototypeSceneValidator.ValidateSampleScene`
        """
    )


def door_toggle_scene_setup() -> str:
    return _clean(
        """
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
        """
    )


def door_toggle_scene_validator() -> str:
    return _clean(
        """
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
        """
    )


def door_toggle_report() -> str:
    return _clean(
        """
        # Door Toggle Interaction - Implementation Report

        ## Goal

        Deliver a real Unity door interaction where the player presses `E` near a prototype door to toggle between closed and open states.

        ## Implemented Programmer Outputs

        - `InteractSystem.cs`
        - `InteractableObject.cs`
        - `DoorToggleInteractable.cs`
        - `AIDoorToggleSceneSetup.cs`
        - `AIDoorToggleSceneValidator.cs`

        ## Behavior Summary

        - Reuse the shared player interaction trigger and nearest-target selection flow.
        - Detect the prototype door through `InteractSystem`.
        - Toggle the hinged door leaf open and closed on repeated `E` presses.
        - Validate that the scene starts closed, opens on first interaction, and closes on second interaction.

        ## Validation Target

        - Scene: `Assets/Scenes/DoorToggleScene.unity`
        - Setup method: `AIDoorToggleSceneSetup.SetupScene`
        - Validation method: `AIDoorToggleSceneValidator.ValidateScene`
        """
    )


def door_toggle_programmer_output_spec() -> ProgrammerOutputSpec:
    return ProgrammerOutputSpec(
        key="door_toggle_interaction",
        file_contents={
            "InteractSystem.cs": default_interact_system(),
            "InteractableObject.cs": default_interactable_object(),
            "DoorToggleInteractable.cs": door_toggle_interactable(),
            "AIDoorToggleSceneSetup.cs": door_toggle_scene_setup(),
            "AIDoorToggleSceneValidator.cs": door_toggle_scene_validator(),
            "DoorToggle_ImplementationReport.md": door_toggle_report(),
        },
        required_snippets={
            "InteractSystem.cs": [
                "FindClosestInteractable",
                "GetComponentInParent<InteractableObject>()",
                "UpdatePromptFeedback",
                "Input.GetKeyDown",
            ],
            "InteractableObject.cs": [
                "public virtual void Interact()",
                "TryBeginInteract",
                "Configure(",
            ],
            "DoorToggleInteractable.cs": [
                "ConfigureDoor",
                "ApplyStateImmediate",
                "isOpen = !isOpen",
                "Door toggled",
            ],
            "AIDoorToggleSceneSetup.cs": [
                "TryValidateExistingScene",
                "AIDoor_DoorLeaf",
                "DoorToggleInteractable",
                "AIDoorToggleSceneSetup complete.",
            ],
            "AIDoorToggleSceneValidator.cs": [
                "ValidateScene",
                "First interaction must open the door.",
                "Second interaction must close the door.",
                "AIDoorToggleSceneValidator passed.",
            ],
            "DoorToggle_ImplementationReport.md": [
                "prototype door",
                "toggle between closed and open states",
                "AIDoorToggleSceneValidator.ValidateScene",
            ],
        },
        scene_setup_method="AIDoorToggleSceneSetup.SetupScene",
        scene_validation_method="AIDoorToggleSceneValidator.ValidateScene",
    )


def inventory_state() -> str:
    return _clean(
        """
        using System.Collections.Generic;
        using UnityEngine;

        [DisallowMultipleComponent]
        public sealed class InventoryState : MonoBehaviour
        {
            private readonly List<string> collectedItemIds = new();

            public IReadOnlyList<string> CollectedItemIds => collectedItemIds;
            public int ItemCount => collectedItemIds.Count;
            public string LastCollectedItemId => ItemCount > 0 ? collectedItemIds[ItemCount - 1] : string.Empty;

            public bool ContainsItem(string itemId)
            {
                return !string.IsNullOrWhiteSpace(itemId) && collectedItemIds.Contains(itemId);
            }

            public bool AddItem(string itemId)
            {
                if (string.IsNullOrWhiteSpace(itemId) || collectedItemIds.Contains(itemId))
                {
                    return false;
                }

                collectedItemIds.Add(itemId);
                Debug.Log($"Inventory collected {itemId}. Total items: {ItemCount}.");
                return true;
            }
        }
        """
    )


def pickup_interactable() -> str:
    return _clean(
        """
        using UnityEngine;

        [DisallowMultipleComponent]
        public sealed class PickupInteractable : InteractableObject
        {
            [SerializeField] private string itemId = "sun_shard";
            [SerializeField] private InventoryState inventory;
            [SerializeField] private Collider pickupCollider;
            [SerializeField] private GameObject visualRoot;
            [SerializeField] private bool collected;

            public string ItemId => itemId;
            public InventoryState Inventory => inventory;
            public bool IsCollected => collected;
            public bool VisualVisible => visualRoot == null || visualRoot.activeSelf;

            private void Awake()
            {
                if (pickupCollider == null)
                {
                    pickupCollider = GetComponent<Collider>();
                }

                if (visualRoot == null)
                {
                    visualRoot = gameObject;
                }

                ApplyCollectedState();
            }

            public void ConfigurePickup(
                InventoryState targetInventory,
                string pickupItemId,
                string pickupName,
                Collider targetCollider,
                GameObject targetVisual)
            {
                inventory = targetInventory;
                itemId = string.IsNullOrWhiteSpace(pickupItemId) ? "sun_shard" : pickupItemId;
                pickupCollider = targetCollider != null ? targetCollider : GetComponent<Collider>();
                visualRoot = targetVisual != null ? targetVisual : gameObject;
                collected = false;
                Configure(pickupName, true);
                ApplyCollectedState();
            }

            public override void Interact()
            {
                if (!TryBeginInteract())
                {
                    return;
                }

                if (inventory == null)
                {
                    Debug.Log($"{DisplayName} cannot be collected because no inventory is assigned.");
                    return;
                }

                if (!inventory.AddItem(itemId))
                {
                    Debug.Log($"{DisplayName} was already collected.");
                    return;
                }

                collected = true;
                Configure(DisplayName, false);
                ApplyCollectedState();
                Debug.Log($"Pickup collected {DisplayName} ({itemId}).");
            }

            private void ApplyCollectedState()
            {
                if (pickupCollider != null)
                {
                    pickupCollider.enabled = !collected;
                }

                if (visualRoot != null)
                {
                    visualRoot.SetActive(!collected);
                }
            }
        }
        """
    )


def inventory_pickup_scene_setup() -> str:
    return _clean(
        """
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
        """
    )


def inventory_pickup_scene_validator() -> str:
    return _clean(
        """
        using System;
        using UnityEditor.SceneManagement;
        using UnityEngine;

        public static class AIInventoryPickupSceneValidator
        {
            private const string ScenePath = "Assets/Scenes/InventoryPickupScene.unity";

            public static void ValidateScene()
            {
                EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);

                var player = RequireObject("AIInventory_Player");
                RequireComponent<InteractSystem>(player, "AIInventory_Player");
                var inventory = RequireComponent<InventoryState>(player, "AIInventory_Player");

                var trigger = RequireComponent<SphereCollider>(player, "AIInventory_Player");
                if (!trigger.isTrigger)
                {
                    throw new InvalidOperationException("AIInventory_Player SphereCollider must be a trigger.");
                }

                var body = RequireComponent<Rigidbody>(player, "AIInventory_Player");
                if (!body.isKinematic)
                {
                    throw new InvalidOperationException("AIInventory_Player Rigidbody must be kinematic.");
                }

                RequireObject("AIInventory_Ground");
                RequireObject("AIInventory_PlayerMarker");
                var pickupObject = RequireObject("AIInventory_Pickup");
                var visual = RequireObject("AIInventory_PickupVisual");
                var pickup = RequireComponent<PickupInteractable>(pickupObject, "AIInventory_Pickup");
                var colliderComponent = RequireComponent<BoxCollider>(pickupObject, "AIInventory_Pickup");

                if (pickup.Inventory != inventory)
                {
                    throw new InvalidOperationException("Pickup must reference the player inventory.");
                }

                if (pickup.DisplayName != "Sun Shard")
                {
                    throw new InvalidOperationException("Pickup prompt should display Sun Shard.");
                }

                if (pickup.ItemId != "sun_shard")
                {
                    throw new InvalidOperationException("Pickup item id must stay deterministic.");
                }

                if (pickup.IsCollected || inventory.ItemCount != 0)
                {
                    throw new InvalidOperationException("Pickup scene must start with an empty inventory.");
                }

                if (!visual.activeSelf || !colliderComponent.enabled)
                {
                    throw new InvalidOperationException("Pickup should start visible and collectible.");
                }

                pickup.Interact();

                if (!pickup.IsCollected)
                {
                    throw new InvalidOperationException("Interacting with the pickup must collect it.");
                }

                if (inventory.ItemCount != 1 || !inventory.ContainsItem("sun_shard"))
                {
                    throw new InvalidOperationException("Collected item must be stored in the player inventory.");
                }

                if (inventory.LastCollectedItemId != "sun_shard")
                {
                    throw new InvalidOperationException("Inventory should report the last collected item.");
                }

                if (pickup.CanInteract)
                {
                    throw new InvalidOperationException("Collected pickup should no longer be interactable.");
                }

                if (visual.activeSelf || colliderComponent.enabled)
                {
                    throw new InvalidOperationException("Collected pickup should hide its visual and collider.");
                }

                Debug.Log("AIInventoryPickupSceneValidator passed.");
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
        """
    )


def inventory_pickup_report() -> str:
    return _clean(
        """
        # Inventory Pickup - Implementation Report

        ## Goal

        Deliver a real Unity interaction where the player presses `E` near a pickup placeholder and stores it in a simple inventory list.

        ## Implemented Programmer Outputs

        - `InteractSystem.cs`
        - `InteractableObject.cs`
        - `InventoryState.cs`
        - `PickupInteractable.cs`
        - `AIInventoryPickupSceneSetup.cs`
        - `AIInventoryPickupSceneValidator.cs`

        ## Behavior Summary

        - Reuse the shared trigger-based interaction flow.
        - Collect the `Sun Shard` pickup into `InventoryState`.
        - Disable the pickup after collection so it cannot be collected twice.
        - Validate inventory contents and visual state changes in batchmode.

        ## Validation Target

        - Scene: `Assets/Scenes/InventoryPickupScene.unity`
        - Setup method: `AIInventoryPickupSceneSetup.SetupScene`
        - Validation method: `AIInventoryPickupSceneValidator.ValidateScene`
        """
    )


def inventory_pickup_programmer_output_spec() -> ProgrammerOutputSpec:
    return ProgrammerOutputSpec(
        key="inventory_pickup",
        file_contents={
            "InteractSystem.cs": default_interact_system(),
            "InteractableObject.cs": default_interactable_object(),
            "InventoryState.cs": inventory_state(),
            "PickupInteractable.cs": pickup_interactable(),
            "AIInventoryPickupSceneSetup.cs": inventory_pickup_scene_setup(),
            "AIInventoryPickupSceneValidator.cs": inventory_pickup_scene_validator(),
            "InventoryPickup_ImplementationReport.md": inventory_pickup_report(),
        },
        required_snippets={
            "InteractSystem.cs": [
                "FindClosestInteractable",
                "GetComponentInParent<InteractableObject>()",
                "UpdatePromptFeedback",
                "Input.GetKeyDown",
            ],
            "InteractableObject.cs": [
                "public virtual void Interact()",
                "TryBeginInteract",
                "Configure(",
            ],
            "InventoryState.cs": [
                "CollectedItemIds",
                "ContainsItem",
                "Inventory collected",
            ],
            "PickupInteractable.cs": [
                "ConfigurePickup",
                "inventory.AddItem",
                "Pickup collected",
            ],
            "AIInventoryPickupSceneSetup.cs": [
                "TryValidateExistingScene",
                "AIInventory_Pickup",
                "InventoryState",
                "AIInventoryPickupSceneSetup complete.",
            ],
            "AIInventoryPickupSceneValidator.cs": [
                "ValidateScene",
                "must collect it",
                "sun_shard",
                "AIInventoryPickupSceneValidator passed.",
            ],
            "InventoryPickup_ImplementationReport.md": [
                "simple inventory list",
                "Sun Shard",
                "AIInventoryPickupSceneValidator.ValidateScene",
            ],
        },
        scene_setup_method="AIInventoryPickupSceneSetup.SetupScene",
        scene_validation_method="AIInventoryPickupSceneValidator.ValidateScene",
    )


def quest_marker_objective() -> str:
    return _clean(
        """
        using UnityEngine;

        [DisallowMultipleComponent]
        public sealed class QuestMarkerObjective : MonoBehaviour
        {
            [SerializeField] private string objectiveName = "Ancient Beacon";
            [SerializeField] private float reachRadius = 1.2f;
            [SerializeField] private bool reached;

            public string ObjectiveName => objectiveName;
            public float ReachRadius => reachRadius;
            public bool Reached => reached;

            public void ConfigureObjective(string targetName, float targetReachRadius)
            {
                objectiveName = string.IsNullOrWhiteSpace(targetName) ? "Ancient Beacon" : targetName;
                reachRadius = Mathf.Clamp(targetReachRadius, 0.5f, 5f);
                reached = false;
            }

            public bool EvaluateReached(Vector3 playerPosition)
            {
                if (reached)
                {
                    return true;
                }

                float distance = Vector3.Distance(playerPosition, transform.position);
                if (distance <= reachRadius)
                {
                    reached = true;
                    Debug.Log($"Quest objective reached: {objectiveName}.");
                }

                return reached;
            }
        }
        """
    )


def quest_marker_tracker() -> str:
    return _clean(
        """
        using UnityEngine;

        [DisallowMultipleComponent]
        public sealed class QuestMarkerTracker : MonoBehaviour
        {
            [SerializeField] private QuestMarkerObjective targetObjective;
            [SerializeField] private Transform markerVisual;
            [SerializeField] private Vector3 lastDirection = Vector3.forward;
            [SerializeField] private float currentDistance;
            [SerializeField] private bool markerVisible;

            public QuestMarkerObjective TargetObjective => targetObjective;
            public Transform MarkerVisual => markerVisual;
            public Vector3 LastDirection => lastDirection;
            public float CurrentDistance => currentDistance;
            public bool MarkerVisible => markerVisible;

            private void Update()
            {
                RefreshMarker();
            }

            public void Configure(QuestMarkerObjective objective, Transform visual)
            {
                targetObjective = objective;
                markerVisual = visual;
                RefreshMarker();
            }

            public void RefreshMarker()
            {
                if (targetObjective == null || markerVisual == null)
                {
                    return;
                }

                currentDistance = Vector3.Distance(transform.position, targetObjective.transform.position);
                if (targetObjective.EvaluateReached(transform.position))
                {
                    markerVisible = false;
                    markerVisual.gameObject.SetActive(false);
                    return;
                }

                var flatOffset = targetObjective.transform.position - transform.position;
                flatOffset.y = 0f;
                lastDirection = flatOffset.sqrMagnitude < 0.001f ? Vector3.forward : flatOffset.normalized;
                markerVisible = true;
                markerVisual.gameObject.SetActive(true);
                markerVisual.rotation = Quaternion.LookRotation(lastDirection, Vector3.up);
                Debug.Log($"Quest marker updated toward {targetObjective.ObjectiveName}: {currentDistance:0.00}m");
            }
        }
        """
    )


def quest_marker_scene_setup() -> str:
    return _clean(
        """
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
        """
    )


def quest_marker_scene_validator() -> str:
    return _clean(
        """
        using System;
        using UnityEditor.SceneManagement;
        using UnityEngine;

        public static class AIQuestMarkerSceneValidator
        {
            private const string ScenePath = "Assets/Scenes/QuestMarkerScene.unity";

            public static void ValidateScene()
            {
                EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);

                RequireObject("AIQuest_Ground");
                var player = RequireObject("AIQuest_Player");
                RequireObject("AIQuest_PlayerMarker");
                var markerVisual = RequireObject("AIQuest_MarkerVisual");
                var objectiveObject = RequireObject("AIQuest_Objective");

                var tracker = RequireComponent<QuestMarkerTracker>(player, "AIQuest_Player");
                var objective = RequireComponent<QuestMarkerObjective>(objectiveObject, "AIQuest_Objective");
                RequireComponent<Collider>(objectiveObject, "AIQuest_Objective");

                if (tracker.TargetObjective != objective)
                {
                    throw new InvalidOperationException("Quest marker tracker must reference the objective.");
                }

                if (tracker.MarkerVisual != markerVisual.transform)
                {
                    throw new InvalidOperationException("Quest marker tracker must reference the marker visual.");
                }

                tracker.RefreshMarker();
                if (!tracker.MarkerVisible || !markerVisual.activeSelf)
                {
                    throw new InvalidOperationException("Quest marker should be visible before the target is reached.");
                }

                if (objective.Reached)
                {
                    throw new InvalidOperationException("Objective should start unreached.");
                }

                var expectedDirection = objective.transform.position - player.transform.position;
                expectedDirection.y = 0f;
                expectedDirection.Normalize();
                if (Vector3.Dot(tracker.LastDirection, expectedDirection) < 0.99f)
                {
                    throw new InvalidOperationException("Quest marker must point from the player toward the objective.");
                }

                player.transform.position = objective.transform.position + new Vector3(0.15f, 0f, 0.15f);
                tracker.RefreshMarker();

                if (!objective.Reached)
                {
                    throw new InvalidOperationException("Objective should mark reached when the player arrives.");
                }

                if (tracker.MarkerVisible || markerVisual.activeSelf)
                {
                    throw new InvalidOperationException("Quest marker should update and hide after the target is reached.");
                }

                Debug.Log("AIQuestMarkerSceneValidator passed.");
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
        """
    )


def quest_marker_report() -> str:
    return _clean(
        """
        # Quest Marker - Implementation Report

        ## Goal

        Deliver a real Unity objective marker that points the player toward a target placeholder and updates when the target is reached.

        ## Implemented Programmer Outputs

        - `QuestMarkerObjective.cs`
        - `QuestMarkerTracker.cs`
        - `AIQuestMarkerSceneSetup.cs`
        - `AIQuestMarkerSceneValidator.cs`

        ## Behavior Summary

        - Point a marker visual from the player toward the `Ancient Beacon` objective.
        - Track the remaining distance each refresh.
        - Hide the marker once the player reaches the objective radius.
        - Validate direction, distance, and reached-state transitions in batchmode.

        ## Validation Target

        - Scene: `Assets/Scenes/QuestMarkerScene.unity`
        - Setup method: `AIQuestMarkerSceneSetup.SetupScene`
        - Validation method: `AIQuestMarkerSceneValidator.ValidateScene`
        """
    )


def quest_marker_programmer_output_spec() -> ProgrammerOutputSpec:
    return ProgrammerOutputSpec(
        key="quest_marker",
        file_contents={
            "QuestMarkerObjective.cs": quest_marker_objective(),
            "QuestMarkerTracker.cs": quest_marker_tracker(),
            "AIQuestMarkerSceneSetup.cs": quest_marker_scene_setup(),
            "AIQuestMarkerSceneValidator.cs": quest_marker_scene_validator(),
            "QuestMarker_ImplementationReport.md": quest_marker_report(),
        },
        required_snippets={
            "QuestMarkerObjective.cs": [
                "ConfigureObjective",
                "EvaluateReached",
                "Quest objective reached",
            ],
            "QuestMarkerTracker.cs": [
                "RefreshMarker",
                "Quest marker updated toward",
                "markerVisual.gameObject.SetActive(false)",
            ],
            "AIQuestMarkerSceneSetup.cs": [
                "TryValidateExistingScene",
                "AIQuest_Objective",
                "QuestMarkerTracker",
                "AIQuestMarkerSceneSetup complete.",
            ],
            "AIQuestMarkerSceneValidator.cs": [
                "ValidateScene",
                "must point from the player toward the objective",
                "hide after the target is reached",
                "AIQuestMarkerSceneValidator passed.",
            ],
            "QuestMarker_ImplementationReport.md": [
                "objective marker",
                "Ancient Beacon",
                "AIQuestMarkerSceneValidator.ValidateScene",
            ],
        },
        scene_setup_method="AIQuestMarkerSceneSetup.SetupScene",
        scene_validation_method="AIQuestMarkerSceneValidator.ValidateScene",
    )


def dialogue_prompt_state() -> str:
    return _clean(
        """
        using UnityEngine;

        [DisallowMultipleComponent]
        public sealed class DialoguePromptState : MonoBehaviour
        {
            [SerializeField] private GameObject promptPanel;
            [SerializeField] private string openingLine = "Welcome, traveler.";
            [SerializeField] private string continueLine = "The ruins are just ahead.";
            [SerializeField] private string currentLine = string.Empty;
            [SerializeField] private bool isVisible;
            [SerializeField] private bool canContinue;
            [SerializeField] private bool hasCompleted;

            public GameObject PromptPanel => promptPanel;
            public string CurrentLine => currentLine;
            public bool IsVisible => isVisible;
            public bool CanContinue => canContinue;
            public bool HasCompleted => hasCompleted;

            public void Configure(GameObject targetPanel, string firstLine, string nextLine)
            {
                promptPanel = targetPanel;
                openingLine = string.IsNullOrWhiteSpace(firstLine) ? "Welcome, traveler." : firstLine;
                continueLine = string.IsNullOrWhiteSpace(nextLine) ? "The ruins are just ahead." : nextLine;
                currentLine = string.Empty;
                isVisible = false;
                canContinue = false;
                hasCompleted = false;
                SetPanelVisible(false);
            }

            public void BeginDialogue()
            {
                currentLine = openingLine;
                isVisible = true;
                canContinue = true;
                hasCompleted = false;
                SetPanelVisible(true);
                Debug.Log($"Dialogue prompt shown: {currentLine}");
            }

            public void ContinueDialogue()
            {
                currentLine = continueLine;
                isVisible = true;
                canContinue = false;
                hasCompleted = true;
                SetPanelVisible(true);
                Debug.Log($"Dialogue prompt continued: {currentLine}");
            }

            private void SetPanelVisible(bool visible)
            {
                if (promptPanel != null)
                {
                    promptPanel.SetActive(visible);
                }
            }
        }
        """
    )


def dialogue_prompt_interactable() -> str:
    return _clean(
        """
        using UnityEngine;

        [DisallowMultipleComponent]
        public sealed class DialoguePromptInteractable : InteractableObject
        {
            [SerializeField] private DialoguePromptState dialogueState;

            public DialoguePromptState DialogueState => dialogueState;

            public void ConfigureDialogue(DialoguePromptState state, string npcName)
            {
                dialogueState = state;
                Configure(npcName, true);
            }

            public override void Interact()
            {
                if (!TryBeginInteract())
                {
                    return;
                }

                if (dialogueState == null)
                {
                    Debug.Log($"{DisplayName} cannot start dialogue because no prompt state is assigned.");
                    return;
                }

                if (!dialogueState.IsVisible)
                {
                    dialogueState.BeginDialogue();
                    return;
                }

                if (dialogueState.CanContinue)
                {
                    dialogueState.ContinueDialogue();
                    return;
                }

                Debug.Log($"Dialogue already completed for {DisplayName}.");
            }
        }
        """
    )


def dialogue_prompt_scene_setup() -> str:
    return _clean(
        """
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
        """
    )


def dialogue_prompt_scene_validator() -> str:
    return _clean(
        """
        using System;
        using UnityEditor.SceneManagement;
        using UnityEngine;

        public static class AIDialoguePromptSceneValidator
        {
            private const string ScenePath = "Assets/Scenes/DialoguePromptScene.unity";

            public static void ValidateScene()
            {
                EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);

                var player = RequireObject("AIDialogue_Player");
                RequireComponent<InteractSystem>(player, "AIDialogue_Player");
                var trigger = RequireComponent<SphereCollider>(player, "AIDialogue_Player");
                if (!trigger.isTrigger)
                {
                    throw new InvalidOperationException("AIDialogue_Player SphereCollider must be a trigger.");
                }

                var body = RequireComponent<Rigidbody>(player, "AIDialogue_Player");
                if (!body.isKinematic)
                {
                    throw new InvalidOperationException("AIDialogue_Player Rigidbody must be kinematic.");
                }

                RequireObject("AIDialogue_Ground");
                RequireObject("AIDialogue_PlayerMarker");
                RequireObject("AIDialogue_NpcVisual");
                var npc = RequireObject("AIDialogue_Npc");
                var state = RequireComponent<DialoguePromptState>(npc, "AIDialogue_Npc");
                var interactable = RequireComponent<DialoguePromptInteractable>(npc, "AIDialogue_Npc");
                var promptPanel = state.PromptPanel;

                if (promptPanel == null || promptPanel.name != "AIDialogue_PromptPanel")
                {
                    throw new InvalidOperationException("Dialogue prompt state must reference the prompt panel.");
                }

                if (interactable.DialogueState != state)
                {
                    throw new InvalidOperationException("Dialogue interactable must reference the dialogue state.");
                }

                if (interactable.DisplayName != "Guide NPC")
                {
                    throw new InvalidOperationException("NPC prompt should identify Guide NPC.");
                }

                if (promptPanel.activeSelf || state.IsVisible || state.CanContinue || state.HasCompleted)
                {
                    throw new InvalidOperationException("Dialogue scene must start with a hidden prompt.");
                }

                interactable.Interact();
                if (!state.IsVisible || !state.CanContinue)
                {
                    throw new InvalidOperationException("First interaction must open the dialogue prompt.");
                }

                if (state.CurrentLine != "Welcome, traveler.")
                {
                    throw new InvalidOperationException("First dialogue line is incorrect.");
                }

                if (!promptPanel.activeSelf)
                {
                    throw new InvalidOperationException("Prompt panel should become visible when dialogue starts.");
                }

                interactable.Interact();
                if (state.CanContinue || !state.HasCompleted)
                {
                    throw new InvalidOperationException("Second interaction must consume the single continue action.");
                }

                if (state.CurrentLine != "The ruins are just ahead.")
                {
                    throw new InvalidOperationException("Continue dialogue line is incorrect.");
                }

                if (!promptPanel.activeSelf)
                {
                    throw new InvalidOperationException("Prompt panel should remain visible after continuing dialogue.");
                }

                Debug.Log("AIDialoguePromptSceneValidator passed.");
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
        """
    )


def dialogue_prompt_report() -> str:
    return _clean(
        """
        # Dialogue Prompt - Implementation Report

        ## Goal

        Deliver a real Unity interaction where the player presses `E` near an NPC placeholder and advances through a short dialogue prompt with one continue action.

        ## Implemented Programmer Outputs

        - `InteractSystem.cs`
        - `InteractableObject.cs`
        - `DialoguePromptState.cs`
        - `DialoguePromptInteractable.cs`
        - `AIDialoguePromptSceneSetup.cs`
        - `AIDialoguePromptSceneValidator.cs`

        ## Behavior Summary

        - Reuse the shared interaction trigger for the NPC prompt.
        - Show an opening dialogue line on the first interaction.
        - Consume one continue action on the second interaction.
        - Validate prompt visibility and deterministic dialogue lines in batchmode.

        ## Validation Target

        - Scene: `Assets/Scenes/DialoguePromptScene.unity`
        - Setup method: `AIDialoguePromptSceneSetup.SetupScene`
        - Validation method: `AIDialoguePromptSceneValidator.ValidateScene`
        """
    )


def dialogue_prompt_programmer_output_spec() -> ProgrammerOutputSpec:
    return ProgrammerOutputSpec(
        key="dialogue_prompt",
        file_contents={
            "InteractSystem.cs": default_interact_system(),
            "InteractableObject.cs": default_interactable_object(),
            "DialoguePromptState.cs": dialogue_prompt_state(),
            "DialoguePromptInteractable.cs": dialogue_prompt_interactable(),
            "AIDialoguePromptSceneSetup.cs": dialogue_prompt_scene_setup(),
            "AIDialoguePromptSceneValidator.cs": dialogue_prompt_scene_validator(),
            "DialoguePrompt_ImplementationReport.md": dialogue_prompt_report(),
        },
        required_snippets={
            "InteractSystem.cs": [
                "FindClosestInteractable",
                "GetComponentInParent<InteractableObject>()",
                "UpdatePromptFeedback",
                "Input.GetKeyDown",
            ],
            "InteractableObject.cs": [
                "public virtual void Interact()",
                "TryBeginInteract",
                "Configure(",
            ],
            "DialoguePromptState.cs": [
                "BeginDialogue",
                "ContinueDialogue",
                "Dialogue prompt shown",
            ],
            "DialoguePromptInteractable.cs": [
                "ConfigureDialogue",
                "dialogueState.BeginDialogue()",
                "dialogueState.ContinueDialogue()",
            ],
            "AIDialoguePromptSceneSetup.cs": [
                "TryValidateExistingScene",
                "AIDialogue_PromptPanel",
                "DialoguePromptState",
                "AIDialoguePromptSceneSetup complete.",
            ],
            "AIDialoguePromptSceneValidator.cs": [
                "ValidateScene",
                "First interaction must open the dialogue prompt.",
                "Second interaction must consume the single continue action.",
                "AIDialoguePromptSceneValidator passed.",
            ],
            "DialoguePrompt_ImplementationReport.md": [
                "short dialogue prompt",
                "one continue action",
                "AIDialoguePromptSceneValidator.ValidateScene",
            ],
        },
        scene_setup_method="AIDialoguePromptSceneSetup.SetupScene",
        scene_validation_method="AIDialoguePromptSceneValidator.ValidateScene",
    )


def default_programmer_output_spec() -> ProgrammerOutputSpec:
    return ProgrammerOutputSpec(
        key="interaction_vertical_slice",
        file_contents={
            "InteractSystem.cs": default_interact_system(),
            "InteractableObject.cs": default_interactable_object(),
            "AIPrototypeSceneSetup.cs": default_interaction_scene_setup(),
            "AIPrototypeSceneValidator.cs": default_interaction_scene_validator(),
            "Interaction_VerticalSlice_ImplementationReport.md": default_interaction_report(),
        },
        required_snippets={
            "InteractSystem.cs": [
                "FindClosestInteractable",
                "closestDistance",
                "UpdatePromptFeedback",
                "target == null",
                "Input.GetKeyDown",
            ],
            "InteractableObject.cs": [
                "DisplayName =>",
                "CanInteract =>",
                "Interaction triggered",
            ],
            "AIPrototypeSceneSetup.cs": [
                "SetupSampleScene",
                "AIPrototype_Player",
                "InteractSystem",
            ],
            "AIPrototypeSceneValidator.cs": [
                "ValidateSampleScene",
                "AIPrototype_Interactable",
                "AIPrototypeSceneValidator passed.",
            ],
            "Interaction_VerticalSlice_ImplementationReport.md": [
                "real Unity interaction slice",
                "InteractSystem.cs",
                "AIPrototypeSceneValidator.ValidateSampleScene",
            ],
        },
        scene_setup_method="AIPrototypeSceneSetup.SetupSampleScene",
        scene_validation_method="AIPrototypeSceneValidator.ValidateSampleScene",
    )


def terra_mage_tiny_mage_controller() -> str:
    return _clean(
        """
        using UnityEngine;

        namespace TerraMageTD
        {
            [RequireComponent(typeof(CharacterController))]
            public sealed class TerraMageTinyMageController : MonoBehaviour
            {
                [SerializeField] private float walkSpeed = 2.2f;
                [SerializeField] private float runSpeed = 4.2f;
                [SerializeField] private float jumpHeight = 0.55f;
                [SerializeField] private float gravity = -9.81f;
                [SerializeField] private float coyoteTime = 0.12f;
                [SerializeField] private float jumpBufferTime = 0.14f;
                [SerializeField] private float groundedStickVelocity = -0.6f;
                [SerializeField] private Transform cameraPivot;

                private CharacterController characterController;
                private Vector3 verticalVelocity;
                private Vector3 lastMoveDirection = Vector3.forward;
                private float coyoteTimer;
                private float jumpBufferTimer;

                public bool IsGrounded => characterController != null && characterController.isGrounded;
                public Transform CameraPivot => cameraPivot;
                public Vector3 LastMoveDirection => lastMoveDirection;

                private void Awake()
                {
                    characterController = GetComponent<CharacterController>();
                }

                public void SetCameraPivot(Transform newPivot)
                {
                    cameraPivot = newPivot;
                }

                private void Update()
                {
                    UpdateJumpInput();
                    Move();
                    JumpAndGravity();
                }

                private void UpdateJumpInput()
                {
                    if (TerraMageInput.GetKeyDown(KeyCode.Space))
                    {
                        jumpBufferTimer = jumpBufferTime;
                        return;
                    }

                    jumpBufferTimer = Mathf.Max(0f, jumpBufferTimer - Time.deltaTime);
                }

                private void Move()
                {
                    float horizontal = TerraMageInput.GetAxisRaw("Horizontal");
                    float vertical = TerraMageInput.GetAxisRaw("Vertical");
                    Vector3 input = new Vector3(horizontal, 0f, vertical);
                    input = Vector3.ClampMagnitude(input, 1f);

                    Transform basis = cameraPivot != null ? cameraPivot : transform;
                    Vector3 forward = Vector3.ProjectOnPlane(basis.forward, Vector3.up).normalized;
                    Vector3 right = Vector3.ProjectOnPlane(basis.right, Vector3.up).normalized;

                    if (forward.sqrMagnitude < 0.001f)
                    {
                        forward = transform.forward;
                    }

                    if (right.sqrMagnitude < 0.001f)
                    {
                        right = transform.right;
                    }

                    Vector3 move = right * input.x + forward * input.z;
                    bool running = TerraMageInput.GetKey(KeyCode.LeftShift) || TerraMageInput.GetKey(KeyCode.RightShift);
                    float speed = running ? runSpeed : walkSpeed;
                    characterController.Move(move * speed * Time.deltaTime);

                    if (move.sqrMagnitude > 0.001f)
                    {
                        lastMoveDirection = move.normalized;
                        transform.rotation = Quaternion.Slerp(
                            transform.rotation,
                            Quaternion.LookRotation(lastMoveDirection, Vector3.up),
                            12f * Time.deltaTime);
                    }
                }

                private void JumpAndGravity()
                {
                    if (characterController.isGrounded)
                    {
                        coyoteTimer = coyoteTime;
                    }
                    else
                    {
                        coyoteTimer = Mathf.Max(0f, coyoteTimer - Time.deltaTime);
                    }

                    if (characterController.isGrounded && verticalVelocity.y < 0f)
                    {
                        verticalVelocity.y = groundedStickVelocity;
                    }

                    if (jumpBufferTimer > 0f && coyoteTimer > 0f)
                    {
                        verticalVelocity.y = Mathf.Sqrt(jumpHeight * -2f * gravity);
                        jumpBufferTimer = 0f;
                        coyoteTimer = 0f;
                    }

                    verticalVelocity.y += gravity * Time.deltaTime;
                    characterController.Move(verticalVelocity * Time.deltaTime);
                }
            }
        }
        """
    )


def terra_mage_follow_camera() -> str:
    return _clean(
        """
        using UnityEngine;

        namespace TerraMageTD
        {
            public sealed class TerraMageFollowCamera : MonoBehaviour
            {
                [SerializeField] private Transform target;
                [SerializeField] private Vector3 pivotOffset = new Vector3(0f, 1.1f, 0f);
                [SerializeField] private float distance = 3.6f;
                [SerializeField] private float yaw;
                [SerializeField] private float pitch = 16f;
                [SerializeField] private float mouseSensitivity = 120f;
                [SerializeField] private float followSharpness = 12f;
                [SerializeField] private float minPitch = -10f;
                [SerializeField] private float maxPitch = 45f;
                [SerializeField] private TerraMageWeaponWheelUI weaponWheelUI;

                public Transform Target => target;

                private void Awake()
                {
                    if (weaponWheelUI == null)
                    {
                        weaponWheelUI = Object.FindAnyObjectByType<TerraMageWeaponWheelUI>();
                    }
                }

                public void SetTarget(Transform newTarget)
                {
                    target = newTarget;
                    if (target != null)
                    {
                        yaw = target.eulerAngles.y;
                    }
                }

                public void SetWeaponWheelUI(TerraMageWeaponWheelUI newWeaponWheelUI)
                {
                    weaponWheelUI = newWeaponWheelUI;
                }

                private void Update()
                {
                    if (target == null)
                    {
                        return;
                    }

                    if (weaponWheelUI == null)
                    {
                        weaponWheelUI = Object.FindAnyObjectByType<TerraMageWeaponWheelUI>();
                    }

                    if (weaponWheelUI != null && weaponWheelUI.IsOpen)
                    {
                        return;
                    }

                    yaw += TerraMageInput.GetAxisRaw("Mouse X") * mouseSensitivity * Time.deltaTime;
                    pitch -= TerraMageInput.GetAxisRaw("Mouse Y") * mouseSensitivity * Time.deltaTime;
                    pitch = Mathf.Clamp(pitch, minPitch, maxPitch);
                }

                private void LateUpdate()
                {
                    if (target == null)
                    {
                        return;
                    }

                    Quaternion orbit = Quaternion.Euler(pitch, yaw, 0f);
                    Vector3 focusPoint = target.position + pivotOffset;
                    Vector3 desiredPosition = focusPoint - orbit * Vector3.forward * distance;
                    float blend = 1f - Mathf.Exp(-followSharpness * Time.deltaTime);

                    transform.position = Vector3.Lerp(transform.position, desiredPosition, blend);
                    transform.rotation = Quaternion.Slerp(transform.rotation, orbit, blend);
                }
            }
        }
        """
    )


def terra_mage_action_build_controller() -> str:
    return _clean(
        """
        using UnityEngine;

        namespace TerraMageTD
        {
            public sealed class TerraMageActionBuildController : MonoBehaviour
            {
                [SerializeField] private Camera aimCamera;
                [SerializeField] private float pullRange = 8f;
                [SerializeField] private float compressMultiplier = 2.5f;
                [SerializeField] private float throwForce = 14f;
                [SerializeField] private float heatPerUse = 0.55f;
                [SerializeField] private LayerMask materialMask = ~0;

                private TerraMageMaterialPayload heldPayload;
                private bool hasPayload;

                public bool HasPayload => hasPayload;
                public Camera AimCamera => aimCamera;
                public TerraMageMaterialPayload HeldPayload => heldPayload;

                private void Awake()
                {
                    if (aimCamera == null)
                    {
                        aimCamera = Camera.main;
                    }
                }

                public void SetAimCamera(Camera newAimCamera)
                {
                    aimCamera = newAimCamera;
                }

                private void Update()
                {
                    if (Input.GetKeyDown(KeyCode.Q))
                    {
                        PullMaterialFromAim();
                    }

                    if (Input.GetKeyDown(KeyCode.E))
                    {
                        CompressHeldMaterial();
                    }

                    if (Input.GetKeyDown(KeyCode.R))
                    {
                        HeatHeldMaterial();
                    }

                    if (Input.GetMouseButtonDown(0))
                    {
                        ThrowHeldMaterial();
                    }
                }

                public void PullMaterialFromAim()
                {
                    if (aimCamera == null)
                    {
                        return;
                    }

                    Ray ray = aimCamera.ScreenPointToRay(Input.mousePosition);
                    if (!Physics.Raycast(ray, out RaycastHit hit, pullRange, materialMask))
                    {
                        return;
                    }

                    heldPayload = TerraMageMaterialSystem.CreateLooseEarth(hit.point);
                    hasPayload = true;
                    Debug.Log($"Terra Mage pulled {heldPayload.Kind} from {hit.point}");
                }

                public void CompressHeldMaterial()
                {
                    if (!hasPayload)
                    {
                        return;
                    }

                    heldPayload = TerraMageMaterialSystem.Compress(heldPayload, compressMultiplier);
                    Debug.Log($"Terra Mage compressed payload into {heldPayload.Kind} mass {heldPayload.Mass:0.0}");
                }

                public void HeatHeldMaterial()
                {
                    if (!hasPayload)
                    {
                        return;
                    }

                    heldPayload = TerraMageMaterialSystem.Heat(heldPayload, heatPerUse);
                    Debug.Log($"Terra Mage heated payload into {heldPayload.Kind} heat {heldPayload.Heat:0.0}");
                }

                public void ThrowHeldMaterial()
                {
                    if (!hasPayload || aimCamera == null)
                    {
                        return;
                    }

                    Vector3 velocity = aimCamera.transform.forward * throwForce;
                    float damage = TerraMageMaterialSystem.CalculateImpactDamage(heldPayload, velocity, 1f);
                    Debug.Log($"Terra Mage threw {heldPayload.Kind} with expected physics damage {damage:0.0}");
                    hasPayload = false;
                }
            }
        }
        """
    )


def terra_mage_material_system() -> str:
    return _clean(
        """
        using UnityEngine;

        namespace TerraMageTD
        {
            public enum TerraMageMaterialKind
            {
                LooseEarth,
                SoftEarth,
                PackedEarth,
                Stone,
                MoltenGlass,
                Glass
            }

            public struct TerraMageMaterialPayload
            {
                public TerraMageMaterialKind Kind;
                public float Mass;
                public float Hardness;
                public float Heat;
                public Vector3 SourcePoint;

                public bool IsHot => Heat >= 1f || Kind == TerraMageMaterialKind.MoltenGlass;
            }

            public static class TerraMageMaterialSystem
            {
                public static TerraMageMaterialPayload CreateLooseEarth(Vector3 sourcePoint)
                {
                    return new TerraMageMaterialPayload
                    {
                        Kind = TerraMageMaterialKind.LooseEarth,
                        Mass = 1f,
                        Hardness = 0.15f,
                        Heat = 0f,
                        SourcePoint = sourcePoint
                    };
                }

                public static TerraMageMaterialPayload Compress(TerraMageMaterialPayload payload, float multiplier)
                {
                    payload.Kind = payload.Kind == TerraMageMaterialKind.Stone
                        ? TerraMageMaterialKind.Stone
                        : TerraMageMaterialKind.PackedEarth;
                    payload.Mass *= Mathf.Max(1f, multiplier);
                    payload.Hardness = Mathf.Max(payload.Hardness, 0.7f);
                    return payload;
                }

                public static TerraMageMaterialPayload Heat(TerraMageMaterialPayload payload, float heatAmount)
                {
                    payload.Heat += Mathf.Max(0f, heatAmount);
                    if ((payload.Kind == TerraMageMaterialKind.LooseEarth || payload.Kind == TerraMageMaterialKind.PackedEarth)
                        && payload.Heat >= 1f)
                    {
                        payload.Kind = TerraMageMaterialKind.MoltenGlass;
                        payload.Hardness = 0.05f;
                    }

                    return payload;
                }

                public static float CalculateImpactDamage(TerraMageMaterialPayload payload, Vector3 velocity, float impactAngle01)
                {
                    float velocityDamage = velocity.magnitude * payload.Mass;
                    float hardnessDamage = payload.Hardness * 10f;
                    float heatDamage = payload.Heat * 5f;
                    return (velocityDamage + hardnessDamage + heatDamage) * Mathf.Clamp01(impactAngle01);
                }
            }
        }
        """
    )


def terra_mage_aim_system() -> str:
    return _clean(
        """
        using UnityEngine;

        namespace TerraMageTD
        {
            [DisallowMultipleComponent]
            public sealed class TerraMageAimSystem : MonoBehaviour
            {
                [SerializeField] private Camera aimCamera;
                [SerializeField] private Transform distanceOrigin;
                [SerializeField] private Transform aimMarker;
                [SerializeField] private float maxAimDistance = 30f;
                [SerializeField] private LayerMask aimMask = ~0;
                [SerializeField] private float markerNoHitDistance = 8f;
                [SerializeField] private Color markerIdleColor = new Color(0.25f, 0.9f, 1f, 1f);
                [SerializeField] private Color markerLockedColor = new Color(1f, 0.85f, 0.15f, 1f);

                private TerraMageAimTarget currentTarget;
                private RaycastHit currentHit;
                private bool hasValidHit;
                private Renderer markerRenderer;

                public Camera AimCamera => aimCamera;
                public Transform DistanceOrigin => distanceOrigin;
                public Transform AimMarker => aimMarker;
                public TerraMageAimTarget CurrentTarget => currentTarget;
                public bool HasValidHit => hasValidHit;

                private void Awake()
                {
                    if (aimCamera == null)
                    {
                        aimCamera = GetComponent<Camera>();
                    }

                    if (aimCamera == null)
                    {
                        aimCamera = Camera.main;
                    }

                    if (aimMarker != null)
                    {
                        markerRenderer = aimMarker.GetComponent<Renderer>();
                    }
                }

                public void SetAimCamera(Camera newAimCamera)
                {
                    aimCamera = newAimCamera;
                }

                public void SetDistanceOrigin(Transform newOrigin)
                {
                    distanceOrigin = newOrigin;
                }

                public void SetAimMarker(Transform newMarker)
                {
                    aimMarker = newMarker;
                    markerRenderer = aimMarker != null ? aimMarker.GetComponent<Renderer>() : null;
                }

                private void Update()
                {
                    EvaluateAim();
                }

                private void EvaluateAim()
                {
                    if (aimCamera == null)
                    {
                        return;
                    }

                    if (currentTarget != null)
                    {
                        currentTarget.SetHighlighted(false);
                    }

                    currentTarget = null;
                    hasValidHit = false;

                    Ray ray = aimCamera.ViewportPointToRay(new Vector3(0.5f, 0.5f, 0f));
                    RaycastHit[] hits = Physics.RaycastAll(ray, maxAimDistance, aimMask, QueryTriggerInteraction.Ignore);

                    float closestDistance = float.MaxValue;
                    TerraMageAimTarget bestTarget = null;
                    RaycastHit bestHit = default;

                    foreach (RaycastHit hit in hits)
                    {
                        TerraMageAimTarget candidate =
                            hit.collider != null ? hit.collider.GetComponentInParent<TerraMageAimTarget>() : null;
                        if (candidate == null || !candidate.CanBeAimed)
                        {
                            continue;
                        }

                        if (hit.distance < closestDistance)
                        {
                            closestDistance = hit.distance;
                            bestTarget = candidate;
                            bestHit = hit;
                        }
                    }

                    if (bestTarget != null)
                    {
                        currentTarget = bestTarget;
                        currentHit = bestHit;
                        hasValidHit = true;
                        currentTarget.SetHighlighted(true);
                        UpdateMarker(currentHit.point, markerLockedColor);
                        return;
                    }

                    currentHit.point = ray.origin + ray.direction * markerNoHitDistance;
                    UpdateMarker(currentHit.point, markerIdleColor);
                }

                private void UpdateMarker(Vector3 worldPosition, Color tint)
                {
                    if (aimMarker == null)
                    {
                        return;
                    }

                    aimMarker.position = worldPosition;
                    aimMarker.localScale = Vector3.one * 0.12f;

                    if (markerRenderer == null)
                    {
                        markerRenderer = aimMarker.GetComponent<Renderer>();
                    }

                    if (markerRenderer == null)
                    {
                        return;
                    }

                    foreach (Material material in markerRenderer.materials)
                    {
                        if (material != null && material.HasProperty("_Color"))
                        {
                            material.color = tint;
                        }
                    }
                }

            }
        }
        """
    )


def terra_mage_aim_target() -> str:
    return _clean(
        """
        using UnityEngine;

        namespace TerraMageTD
        {
            [DisallowMultipleComponent]
            public sealed class TerraMageAimTarget : MonoBehaviour
            {
                [SerializeField] private string displayName = "Aim Target";
                [SerializeField] private Color baseColor = new Color(0.35f, 0.8f, 1f, 1f);
                [SerializeField] private Color highlightColor = new Color(1f, 0.85f, 0.2f, 1f);

                private Renderer[] cachedRenderers;
                private Collider[] cachedColliders;
                private bool isVisible = true;
                private bool isHighlighted;

                public string DisplayName => string.IsNullOrWhiteSpace(displayName) ? gameObject.name : displayName;
                public bool IsVisible => isVisible;
                public bool CanBeAimed => isVisible && gameObject.activeInHierarchy && HasEnabledCollider();

                private void Awake()
                {
                    CacheComponents();
                    ApplyVisual();
                }

                public void Configure(string newDisplayName, Color newBaseColor)
                {
                    displayName = newDisplayName;
                    baseColor = newBaseColor;
                    CacheComponents();
                    ApplyVisual();
                }

                public Vector3 GetAimPoint()
                {
                    CacheComponents();

                    foreach (Collider candidate in cachedColliders)
                    {
                        if (candidate != null && candidate.enabled)
                        {
                            return candidate.bounds.center;
                        }
                    }

                    return transform.position;
                }

                public void SetHighlighted(bool highlighted)
                {
                    isHighlighted = highlighted;
                    ApplyVisual();
                }

                public void SetVisible(bool visible)
                {
                    isVisible = visible;
                    CacheComponents();

                    foreach (Renderer renderer in cachedRenderers)
                    {
                        if (renderer != null)
                        {
                            renderer.enabled = visible;
                        }
                    }

                    foreach (Collider colliderComponent in cachedColliders)
                    {
                        if (colliderComponent != null)
                        {
                            colliderComponent.enabled = visible;
                        }
                    }
                }

                private void CacheComponents()
                {
                    cachedRenderers = GetComponentsInChildren<Renderer>(true);
                    cachedColliders = GetComponentsInChildren<Collider>(true);
                }

                private bool HasEnabledCollider()
                {
                    CacheComponents();

                    foreach (Collider candidate in cachedColliders)
                    {
                        if (candidate != null && candidate.enabled)
                        {
                            return true;
                        }
                    }

                    return false;
                }

                private void ApplyVisual()
                {
                    CacheComponents();
                    Color tint = isHighlighted ? highlightColor : baseColor;

                    foreach (Renderer renderer in cachedRenderers)
                    {
                        if (renderer == null)
                        {
                            continue;
                        }

                        renderer.enabled = isVisible;
                        foreach (Material material in renderer.materials)
                        {
                            if (material != null && material.HasProperty("_Color"))
                            {
                                material.color = tint;
                            }
                        }
                    }
                }
            }
        }
        """
    )


def terra_mage_aim_target_motion() -> str:
    return _clean(
        """
        using UnityEngine;

        namespace TerraMageTD
        {
            [DisallowMultipleComponent]
            public sealed class TerraMageAimTargetMotion : MonoBehaviour
            {
                [SerializeField] private Vector3 localAxis = Vector3.right;
                [SerializeField] private float amplitude = 1.5f;
                [SerializeField] private float speed = 1.2f;

                private Vector3 startPosition;

                private void Awake()
                {
                    startPosition = transform.position;
                }

                private void Update()
                {
                    Vector3 axis = localAxis.sqrMagnitude < 0.001f ? Vector3.right : localAxis.normalized;
                    transform.position = startPosition + axis * Mathf.Sin(Time.time * speed) * amplitude;
                }
            }
        }
        """
    )


def terra_mage_aim_target_visibility() -> str:
    return _clean(
        """
        using UnityEngine;

        namespace TerraMageTD
        {
            public enum TerraMageAimTargetVisibilityMode
            {
                None,
                DisappearAfterDelay,
                Blink
            }

            [DisallowMultipleComponent]
            [RequireComponent(typeof(TerraMageAimTarget))]
            public sealed class TerraMageAimTargetVisibility : MonoBehaviour
            {
                [SerializeField] private TerraMageAimTargetVisibilityMode mode = TerraMageAimTargetVisibilityMode.None;
                [SerializeField] private float initialDelay;
                [SerializeField] private float visibleDuration = 1.2f;
                [SerializeField] private float hiddenDuration = 0.6f;

                private TerraMageAimTarget aimTarget;
                private float elapsedTime;

                public TerraMageAimTargetVisibilityMode Mode => mode;

                private void Awake()
                {
                    aimTarget = GetComponent<TerraMageAimTarget>();
                }

                private void OnEnable()
                {
                    elapsedTime = 0f;
                    if (aimTarget != null)
                    {
                        aimTarget.SetVisible(true);
                    }
                }

                public void Configure(
                    TerraMageAimTargetVisibilityMode newMode,
                    float newInitialDelay,
                    float newVisibleDuration,
                    float newHiddenDuration)
                {
                    mode = newMode;
                    initialDelay = newInitialDelay;
                    visibleDuration = newVisibleDuration;
                    hiddenDuration = newHiddenDuration;
                }

                private void Update()
                {
                    if (aimTarget == null || mode == TerraMageAimTargetVisibilityMode.None)
                    {
                        return;
                    }

                    elapsedTime += Time.deltaTime;
                    if (elapsedTime < initialDelay)
                    {
                        return;
                    }

                    float activeTime = elapsedTime - initialDelay;

                    if (mode == TerraMageAimTargetVisibilityMode.DisappearAfterDelay)
                    {
                        aimTarget.SetVisible(false);
                        enabled = false;
                        return;
                    }

                    float cycleDuration = Mathf.Max(0.1f, visibleDuration + hiddenDuration);
                    bool visibleNow = (activeTime % cycleDuration) < Mathf.Max(0.05f, visibleDuration);
                    aimTarget.SetVisible(visibleNow);
                }
            }
        }
        """
    )


def terra_mage_first_scene_setup() -> str:
    return _clean(
        """
        using TerraMageTD;
        using UnityEditor;
        using UnityEditor.SceneManagement;
        using UnityEngine;

        public static class TerraMageFirstSceneSetup
        {
            private const string ScenePath = "Assets/Scenes/TerraMage_FirstScene.unity";

            public static void SetupFirstScene()
            {
                if (TryValidateExistingScene())
                {
                    Debug.Log("TerraMageFirstSceneSetup skipped rebuild because scene already matches spec.");
                    return;
                }

                var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

                CreateGround();
                CreateScaleBlocks();
                CreateCoreMarker();
                var player = CreatePlayer();
                CreateCameraRig(player);
                CreateAimTargetRange();
                CreateLight();

                EditorSceneManager.MarkSceneDirty(scene);
                EditorSceneManager.SaveScene(scene, ScenePath);
                Debug.Log("TerraMageFirstSceneSetup complete.");
            }

            private static bool TryValidateExistingScene()
            {
                if (AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath) == null)
                {
                    return false;
                }

                try
                {
                    TerraMageFirstSceneValidator.ValidateFirstScene();
                    return true;
                }
                catch (System.Exception ex)
                {
                    Debug.Log($"TerraMageFirstSceneSetup rebuilding scene: {ex.Message}");
                    return false;
                }
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
                player.AddComponent<TerraMageActionBuildController>();
                player.AddComponent<TerraMageMeleeGestureController>();

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

                var staff = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                staff.name = "TerraMage_MockStaff";
                staff.transform.SetParent(player.transform);
                staff.transform.localPosition = new Vector3(0.13f, 0.18f, 0.03f);
                staff.transform.localRotation = Quaternion.Euler(12f, 0f, 0f);
                staff.transform.localScale = new Vector3(0.015f, 0.22f, 0.015f);
                Tint(staff, new Color(0.45f, 0.28f, 0.18f));

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
        """
    )


def terra_mage_first_scene_validator() -> str:
    return _clean(
        """
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
        """
    )


def terra_mage_implementation_report() -> str:
    return _clean(
        """
        # Terra Mage Third-Person Aim v0.0.5 - Implementation Report

        ## Goal

        Upgrade the Terra Mage scene from movement-only into a third-person aiming test range.

        ## Implemented Programmer Outputs

        - `TerraMageTinyMageController.cs`
        - `TerraMageFollowCamera.cs`
        - `TerraMageActionBuildController.cs`
        - `TerraMageAimSystem.cs`
        - `TerraMageAimTarget.cs`
        - `TerraMageAimTargetMotion.cs`
        - `TerraMageAimTargetVisibility.cs`
        - `TerraMageFirstSceneSetup.cs`
        - `TerraMageFirstSceneValidator.cs`

        ## Scene Additions

        - Third-person camera with mouse orbit while holding right mouse.
        - aim helper marker driven by center-screen raycasts.
        - Left-click debug log that prints the distance to the currently aimed object.
        - Static targets for baseline aim checks.
        - Moving target for motion tracking checks.
        - Disappearing target for delayed-visibility checks.
        - Blinking target for intermittent-visibility checks.

        ## Validation Target

        - Scene: `Assets/Scenes/TerraMage_FirstScene.unity`
        - Setup method: `TerraMageFirstSceneSetup.SetupFirstScene`
        - Validation method: `TerraMageFirstSceneValidator.ValidateFirstScene`
        """
    )


def terra_mage_third_person_aim_spec() -> ProgrammerOutputSpec:
    return ProgrammerOutputSpec(
        key="terra_mage_third_person_aim",
        file_contents={
            "TerraMageTinyMageController.cs": terra_mage_tiny_mage_controller(),
            "TerraMageFollowCamera.cs": terra_mage_follow_camera(),
            "TerraMageActionBuildController.cs": terra_mage_action_build_controller(),
            "TerraMageAimSystem.cs": terra_mage_aim_system(),
            "TerraMageAimTarget.cs": terra_mage_aim_target(),
            "TerraMageAimTargetMotion.cs": terra_mage_aim_target_motion(),
            "TerraMageAimTargetVisibility.cs": terra_mage_aim_target_visibility(),
            "TerraMageFirstSceneSetup.cs": terra_mage_first_scene_setup(),
            "TerraMageFirstSceneValidator.cs": terra_mage_first_scene_validator(),
            "TerraMage_ThirdPersonAim_v005_ImplementationReport.md": terra_mage_implementation_report(),
        },
        required_snippets={
            "TerraMageTinyMageController.cs": [
                "SetCameraPivot",
                "ProjectOnPlane",
                "TerraMageInput.GetKeyDown(KeyCode.Space)",
            ],
            "TerraMageFollowCamera.cs": [
                "TerraMageInput.GetAxisRaw(\"Mouse X\")",
                "Quaternion.Euler",
                "SetTarget",
            ],
            "TerraMageActionBuildController.cs": [
                "SetAimCamera",
                "AimCamera =>",
                "Input.GetMouseButtonDown(0)",
            ],
            "TerraMageAimSystem.cs": [
                "ViewportPointToRay",
                "RaycastAll",
                "CurrentTarget",
            ],
            "TerraMageAimTarget.cs": [
                "SetHighlighted",
                "SetVisible",
                "GetAimPoint",
            ],
            "TerraMageAimTargetMotion.cs": [
                "Mathf.Sin",
                "amplitude",
            ],
            "TerraMageAimTargetVisibility.cs": [
                "DisappearAfterDelay",
                "Blink",
                "elapsedTime",
            ],
            "TerraMageFirstSceneSetup.cs": [
                "TerraMage_StaticTarget_01",
                "TerraMage_MovingTarget",
                "TerraMage_DisappearingTarget",
                "TerraMage_BlinkingTarget",
                "SetAimMarker",
                "TryValidateExistingScene",
            ],
            "TerraMageFirstSceneValidator.cs": [
                "TerraMageAimSystem",
                "TerraMage_MovingTarget",
                "TerraMage_DisappearingTarget",
                "TerraMage_BlinkingTarget",
                "TerraMageAimTargetVisibilityMode.Blink",
            ],
            "TerraMage_ThirdPersonAim_v005_ImplementationReport.md": [
                "third-person",
                "aim helper",
                "Moving target",
                "Disappearing target",
                "Blinking target",
            ],
        },
        scene_setup_method="TerraMageFirstSceneSetup.SetupFirstScene",
        scene_validation_method="TerraMageFirstSceneValidator.ValidateFirstScene",
    )


def terra_mage_weapon_family_spec() -> ProgrammerOutputSpec:
    return build_terra_mage_weapon_family_spec(
        ProgrammerOutputSpec,
        {
            "TerraMageTinyMageController.cs": terra_mage_tiny_mage_controller(),
            "TerraMageFollowCamera.cs": terra_mage_follow_camera(),
            "TerraMageAimSystem.cs": terra_mage_aim_system(),
            "TerraMageAimTarget.cs": terra_mage_aim_target(),
            "TerraMageAimTargetMotion.cs": terra_mage_aim_target_motion(),
            "TerraMageAimTargetVisibility.cs": terra_mage_aim_target_visibility(),
            "TerraMageMaterialSystem.cs": terra_mage_material_system(),
        },
    )


def terra_mage_first_scene_report() -> str:
    return _clean(
        """
        # Terra Mage First Scene v0.0.4 - Implementation Report

        ## Goal

        Deliver the first playable Terra Mage scene with a mock tiny mage character that can walk, run, and jump inside a real Unity scene.

        ## Implemented Programmer Outputs

        - `TerraMageInput.cs`
        - `TerraMagePlayerMechanics.cs`
        - `TerraMageTinyMageController.cs`
        - `TerraMageFollowCamera.cs`
        - `TerraMageFirstSceneSetup.cs`
        - `TerraMageFirstSceneValidator.cs`

        ## Foundation Summary

        - Primitive mock art only for the tiny mage and scene landmarks.
        - Real playable scene setup and validation in Unity batchmode.
        - Guardrail validation that gameplay scripts use `TerraMageInput`.
        - Guardrail validation that doubled rename identifiers such as `TerraMageTerraMageInput` fail QA.

        ## Validation Target

        - Scene: `Assets/Scenes/TerraMage_FirstScene.unity`
        - Setup method: `TerraMageFirstSceneSetup.SetupFirstScene`
        - Validation method: `TerraMageFirstSceneValidator.ValidateFirstScene`
        """
    )


def terra_mage_first_wall_report() -> str:
    return _clean(
        """
        # Terra Mage First Wall v0.0.3 - Implementation Report

        ## Goal

        Deliver the first real Terra Mage sandbox foundation slice with action-build fusion, material pull/compress/throw/heat, mouse-drag melee support, and weapon-driven range profiles inside validated Unity scripts.

        ## Implemented Programmer Outputs

        - `TerraMageInput.cs`
        - `TerraMageMaterialSystem.cs`
        - `TerraMageActionBuildController.cs`
        - `TerraMageMeleeGestureController.cs`
        - `TerraMageWeaponDefinition.cs`
        - `TerraMageWeaponLoadout.cs`
        - `TerraMageWeaponWheelUI.cs`
        - `TerraMageFirstSceneSetup.cs`
        - `TerraMageFirstSceneValidator.cs`
        - `TerraMage_FirstWall_AssetRequestNotes.md`

        ## Foundation Summary

        - Tiny mage sandbox foundation remains programmer-led.
        - Weapon wheel keeps `Bare Hands` in slot 0 and drives melee or ranged behavior.
        - Action-build flow supports pull, compress, heat, and throw interactions.
        - Asset requests stay as programmer-authored notes until specific Creator work is needed.

        ## Validation Target

        - Scene: `Assets/Scenes/TerraMage_FirstScene.unity`
        - Setup method: `TerraMageFirstSceneSetup.SetupFirstScene`
        - Validation method: `TerraMageFirstSceneValidator.ValidateFirstScene`
        """
    )


def terra_mage_first_wall_asset_request_notes() -> str:
    return _clean(
        """
        # Terra Mage First Wall v0.0.3 - Asset Request Notes

        Creator work remains secondary for this slice.

        Requested later, only if programmer validation stays green:

        - Tiny mage silhouette pass for body, hood, and staff replacements.
        - Material pickup silhouettes for loose earth, compressed shard, and heated payload variants.
        - Clean radial art pass for the Terra Mage weapon wheel ring and slot icons.
        - Simple impact and swipe VFX placeholders matched to melee and projectile timings.
        """
    )


def _copy_required_snippets(required_snippets: dict[str, list[str]]) -> dict[str, list[str]]:
    return {filename: list(snippets) for filename, snippets in required_snippets.items()}


def terra_mage_first_scene_spec() -> ProgrammerOutputSpec:
    base_spec = terra_mage_weapon_family_spec()
    file_contents = dict(base_spec.file_contents)
    file_contents.pop("TerraMage_WeaponWheelCombat_ImplementationReport.md", None)
    file_contents["TerraMage_FirstScene_v004_ImplementationReport.md"] = terra_mage_first_scene_report()

    required_snippets = _copy_required_snippets(base_spec.required_snippets)
    required_snippets.pop("TerraMage_WeaponWheelCombat_ImplementationReport.md", None)
    required_snippets["TerraMageFirstSceneValidator.cs"] = required_snippets.get("TerraMageFirstSceneValidator.cs", []) + [
        "ValidateInputGuardrails",
        "TerraMageTerraMageInput",
        "must not call UnityEngine.Input directly",
    ]
    required_snippets["TerraMage_FirstScene_v004_ImplementationReport.md"] = [
        "first playable Terra Mage scene",
        "TerraMageInput",
        "TerraMageTerraMageInput",
    ]

    return ProgrammerOutputSpec(
        key="terra_mage_first_scene",
        file_contents=file_contents,
        required_snippets=required_snippets,
        scene_setup_method=base_spec.scene_setup_method,
        scene_validation_method=base_spec.scene_validation_method,
    )


def terra_mage_first_wall_spec() -> ProgrammerOutputSpec:
    base_spec = terra_mage_weapon_family_spec()
    file_contents = dict(base_spec.file_contents)
    file_contents.pop("TerraMage_WeaponWheelCombat_ImplementationReport.md", None)
    file_contents["TerraMage_FirstWall_v003_ImplementationReport.md"] = terra_mage_first_wall_report()
    file_contents["TerraMage_FirstWall_AssetRequestNotes.md"] = terra_mage_first_wall_asset_request_notes()

    required_snippets = _copy_required_snippets(base_spec.required_snippets)
    required_snippets.pop("TerraMage_WeaponWheelCombat_ImplementationReport.md", None)
    required_snippets["TerraMageFirstSceneValidator.cs"] = required_snippets.get("TerraMageFirstSceneValidator.cs", []) + [
        "ValidateInputGuardrails",
        "TerraMageTerraMageInput",
    ]
    required_snippets["TerraMage_FirstWall_v003_ImplementationReport.md"] = [
        "action-build fusion",
        "weapon-driven range profiles",
        "TerraMage_FirstWall_AssetRequestNotes.md",
    ]
    required_snippets["TerraMage_FirstWall_AssetRequestNotes.md"] = [
        "Creator work remains secondary",
        "weapon wheel ring",
        "projectile timings",
    ]

    return ProgrammerOutputSpec(
        key="terra_mage_first_wall",
        file_contents=file_contents,
        required_snippets=required_snippets,
        scene_setup_method=base_spec.scene_setup_method,
        scene_validation_method=base_spec.scene_validation_method,
    )


def programmer_family_definitions() -> dict[str, ProgrammerFamilyDefinition]:
    return {
        "interaction_vertical_slice": ProgrammerFamilyDefinition(
            key="interaction_vertical_slice",
            title="Interaction Vertical Slice",
            support_level="supported",
            description="Real Unity interaction slice with sample scene setup and validation.",
            detector=is_interaction_vertical_slice_request,
            spec_builder=default_programmer_output_spec,
        ),
        "terra_mage_third_person_aim": ProgrammerFamilyDefinition(
            key="terra_mage_third_person_aim",
            title="Terra Mage Third-Person Aim",
            support_level="supported",
            description="Third-person camera, aiming helper, target range, and scene validation for Terra Mage.",
            detector=is_terra_mage_third_person_aim_request,
            spec_builder=terra_mage_third_person_aim_spec,
        ),
        "terra_mage_weapon_family": ProgrammerFamilyDefinition(
            key="terra_mage_weapon_family",
            title="Terra Mage Weapon Wheel and Combat",
            support_level="supported",
            description="Weapon wheel, loadout, melee/range behavior, and scene validation for Terra Mage.",
            detector=is_terra_mage_weapon_family_request,
            spec_builder=terra_mage_weapon_family_spec,
        ),
        "door_toggle_interaction": ProgrammerFamilyDefinition(
            key="door_toggle_interaction",
            title="Door Toggle Interaction",
            support_level="supported",
            description="Prototype door interaction with deterministic scene setup and validation.",
            detector=is_door_toggle_interaction_request,
            spec_builder=door_toggle_programmer_output_spec,
        ),
        "dialogue_prompt": ProgrammerFamilyDefinition(
            key="dialogue_prompt",
            title="Dialogue Prompt",
            support_level="supported",
            description="NPC dialogue prompt with deterministic scene setup and validation.",
            detector=is_dialogue_prompt_request,
            spec_builder=dialogue_prompt_programmer_output_spec,
        ),
        "inventory_pickup": ProgrammerFamilyDefinition(
            key="inventory_pickup",
            title="Inventory Pickup",
            support_level="supported",
            description="Pickup and inventory workflow with deterministic scene setup and validation.",
            detector=is_inventory_pickup_request,
            spec_builder=inventory_pickup_programmer_output_spec,
        ),
        "quest_marker": ProgrammerFamilyDefinition(
            key="quest_marker",
            title="Quest Marker",
            support_level="supported",
            description="Objective marker workflow with deterministic scene setup and validation.",
            detector=is_quest_marker_request,
            spec_builder=quest_marker_programmer_output_spec,
        ),
        "terra_mage_first_wall": ProgrammerFamilyDefinition(
            key="terra_mage_first_wall",
            title="Terra Mage First Wall",
            support_level="supported",
            description="Early Terra Mage sandbox foundation with programmer-led combat and asset request notes.",
            detector=is_terra_mage_first_wall_request,
            spec_builder=terra_mage_first_wall_spec,
        ),
        "terra_mage_first_scene": ProgrammerFamilyDefinition(
            key="terra_mage_first_scene",
            title="Terra Mage First Scene",
            support_level="supported",
            description="First playable Terra Mage scene foundation with guardrail validation.",
            detector=is_terra_mage_first_scene_request,
            spec_builder=terra_mage_first_scene_spec,
        ),
    }


def list_programmer_family_definitions() -> list[ProgrammerFamilyDefinition]:
    return list(programmer_family_definitions().values())


def get_programmer_family_definition(family: str) -> ProgrammerFamilyDefinition | None:
    normalized_family = (family or "").strip().lower().replace("-", "_").replace(" ", "_")
    return programmer_family_definitions().get(normalized_family)


def get_supported_programmer_family_keys() -> list[str]:
    return [
        family.key
        for family in list_programmer_family_definitions()
        if family.support_level == "supported"
    ]


def resolve_programmer_family_definition(
    feature_request: str,
    task_id: str = "",
    family: str = "",
) -> ProgrammerFamilyDefinition:
    explicit_family = (family or "").strip().lower().replace("-", "_").replace(" ", "_")
    definitions = programmer_family_definitions()

    if explicit_family:
        definition = definitions.get(explicit_family)
        if definition is None:
            supported = ", ".join(sorted(definitions))
            raise UnsupportedProgrammerFamilyError(
                f"Unknown task family '{explicit_family}'. Known families: {supported}"
            )
        if definition.support_level != "supported" or definition.spec_builder is None:
            raise UnsupportedProgrammerFamilyError(
                f"Task family '{explicit_family}' is registered as {definition.support_level} and has no deterministic implementation spec yet."
            )
        return definition

    matches = [
        definition
        for definition in definitions.values()
        if definition.support_level == "supported" and definition.detector(feature_request, task_id)
    ]

    if len(matches) == 1:
        return matches[0]

    if len(matches) > 1:
        family_keys = ", ".join(sorted(definition.key for definition in matches))
        raise AmbiguousProgrammerFamilyError(
            f"Feature request matches multiple supported families. Set task family explicitly. Matches: {family_keys}"
        )

    supported = ", ".join(sorted(get_supported_programmer_family_keys()))
    raise UnsupportedProgrammerFamilyError(
        "No deterministic programmer family matched this request. "
        f"Supported families: {supported}. Set an explicit supported family or scaffold a new one."
    )


def select_programmer_output_spec(
    feature_request: str,
    phase: str,
    task_id: str = "",
    family: str = "",
) -> ProgrammerOutputSpec:
    del phase
    definition = resolve_programmer_family_definition(
        feature_request=feature_request,
        task_id=task_id,
        family=family,
    )
    if definition.spec_builder is None:
        raise UnsupportedProgrammerFamilyError(
            f"Task family '{definition.key}' has no deterministic implementation spec."
        )
    return definition.spec_builder()


def validate_programmer_output_files(
    output_dir: Path,
    file_paths: list[str],
    spec: ProgrammerOutputSpec,
) -> tuple[bool, list[str]]:
    problems: list[str] = []
    actual_paths = {Path(path).resolve() for path in file_paths}

    for filename, content in spec.file_contents.items():
        expected = (output_dir / filename).resolve()

        if expected not in actual_paths:
            problems.append(f"Missing file path in state: {filename}")

        if not expected.exists():
            problems.append(f"Missing file on disk: {filename}")
            continue

        try:
            expected.relative_to(output_dir.resolve())
        except ValueError:
            problems.append(f"File outside programmer output dir: {expected}")
            continue

        disk_text = expected.read_text(encoding="utf-8", errors="replace")
        normalized_disk_text = disk_text.replace("\r\n", "\n")
        normalized_content = content.replace("\r\n", "\n")

        if normalized_disk_text != normalized_content:
            problems.append(f"Unexpected file content drift: {filename}")

        for snippet in spec.required_snippets.get(filename, []):
            if snippet not in normalized_disk_text:
                problems.append(f"{filename} missing logic marker: {snippet}")

    return not problems, problems
