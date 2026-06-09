from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent

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
                var interactable = other.GetComponent<InteractableObject>();
                if (interactable != null && !objectsInRange.Contains(interactable))
                {
                    objectsInRange.Add(interactable);
                }
            }

            private void OnTriggerExit(Collider other)
            {
                var interactable = other.GetComponent<InteractableObject>();
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

            public void Interact()
            {
                if (!canInteract)
                {
                    Debug.Log($"{displayName} is currently unavailable.");
                    return;
                }

                Debug.Log($"Interaction triggered for {displayName}.");
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


def default_programmer_output_spec() -> ProgrammerOutputSpec:
    return ProgrammerOutputSpec(
        key="default_interaction",
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
                [SerializeField] private Transform cameraPivot;

                private CharacterController characterController;
                private Vector3 verticalVelocity;
                private Vector3 lastMoveDirection = Vector3.forward;

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
                    Move();
                    JumpAndGravity();
                }

                private void Move()
                {
                    float horizontal = Input.GetAxisRaw("Horizontal");
                    float vertical = Input.GetAxisRaw("Vertical");
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
                    bool running = Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift);
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
                    if (characterController.isGrounded && verticalVelocity.y < 0f)
                    {
                        verticalVelocity.y = -1f;
                    }

                    if (characterController.isGrounded && Input.GetKeyDown(KeyCode.Space))
                    {
                        verticalVelocity.y = Mathf.Sqrt(jumpHeight * -2f * gravity);
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

                public Transform Target => target;

                public void SetTarget(Transform newTarget)
                {
                    target = newTarget;
                    if (target != null)
                    {
                        yaw = target.eulerAngles.y;
                    }
                }

                private void Update()
                {
                    if (target == null)
                    {
                        return;
                    }

                    if (Input.GetMouseButton(1))
                    {
                        yaw += Input.GetAxisRaw("Mouse X") * mouseSensitivity * Time.deltaTime;
                        pitch -= Input.GetAxisRaw("Mouse Y") * mouseSensitivity * Time.deltaTime;
                        pitch = Mathf.Clamp(pitch, minPitch, maxPitch);
                    }
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

                    if (Input.GetMouseButtonDown(0))
                    {
                        LogAimDistance();
                    }
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

                private void LogAimDistance()
                {
                    if (currentTarget == null || !hasValidHit)
                    {
                        Debug.Log("Aim debug: no target locked.");
                        return;
                    }

                    Transform origin = distanceOrigin != null ? distanceOrigin : aimCamera.transform;
                    float distance = Vector3.Distance(origin.position, currentTarget.GetAimPoint());
                    Debug.Log($"Aim debug: {currentTarget.DisplayName} distance = {distance:0.00}m");
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
                "Input.GetKeyDown(KeyCode.Space)",
            ],
            "TerraMageFollowCamera.cs": [
                "Input.GetMouseButton(1)",
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
                "Aim debug:",
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


def select_programmer_output_spec(
    feature_request: str,
    phase: str,
    task_id: str = "",
) -> ProgrammerOutputSpec:
    del phase

    if is_terra_mage_weapon_family_request(feature_request, task_id):
        return terra_mage_weapon_family_spec()

    if is_terra_mage_third_person_aim_request(feature_request, task_id):
        return terra_mage_third_person_aim_spec()

    return default_programmer_output_spec()


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
