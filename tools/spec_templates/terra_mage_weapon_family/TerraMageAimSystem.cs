using UnityEngine;
using UnityEngine.UI;

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
        private const string CrosshairCanvasName = "TerraMage_CrosshairCanvas";

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

            EnsureCrosshairUi();
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

        private static void EnsureCrosshairUi()
        {
            if (GameObject.Find(CrosshairCanvasName) != null)
            {
                return;
            }

            var canvasObject = new GameObject(CrosshairCanvasName);
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
    }
}
