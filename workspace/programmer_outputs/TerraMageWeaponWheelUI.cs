using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace TerraMageTD
{
    [DisallowMultipleComponent]
    public sealed class TerraMageWeaponWheelUI : MonoBehaviour
    {
        [SerializeField] private TerraMageWeaponLoadout loadout;
        [SerializeField] private Canvas wheelCanvas;
        [SerializeField] private RectTransform wheelRoot;
        [SerializeField] private float wheelDiameter = 320f;
        [SerializeField] private float labelRadius = 112f;
        [SerializeField] private KeyCode openWheelKey = KeyCode.Tab;
        [SerializeField] private Color lockedSlotColor = new Color(0.92f, 0.92f, 0.96f, 0.82f);
        [SerializeField] private Color defaultSlotColor = new Color(0.22f, 0.24f, 0.28f, 0.82f);
        [SerializeField] private Color highlightSlotColor = new Color(1f, 0.82f, 0.2f, 0.92f);

        private readonly List<Image> segmentImages = new List<Image>();
        private readonly List<Text> segmentLabels = new List<Text>();

        private Font defaultFont;
        private bool isOpen;
        private int hoverSlotIndex;

        public TerraMageWeaponLoadout Loadout => loadout;
        public KeyCode OpenWheelKey => openWheelKey;
        public bool IsOpen => isOpen;
        public int VisualSegmentCount => segmentImages.Count;
        public int HoverSlotIndex => hoverSlotIndex;
        public float CurrentSegmentSweepDegrees => CalculateSegmentSweep(loadout != null ? loadout.ActiveSlotCount : 1);

        private void Awake()
        {
            EnsureUiReferences();
            SubscribeToLoadout();
            RebuildImmediately();
            HideImmediately();
        }

        private void OnDestroy()
        {
            UnsubscribeFromLoadout();
        }

        private void Update()
        {
            if (loadout == null || wheelCanvas == null || wheelRoot == null)
            {
                return;
            }

            bool shouldOpen = TerraMageInput.GetKey(openWheelKey);
            if (shouldOpen && !isOpen)
            {
                isOpen = true;
                SetWheelVisible(true);
                hoverSlotIndex = loadout.SelectedSlotIndex;
                UpdateHoverFromMouse();
            }
            else if (!shouldOpen && isOpen)
            {
                loadout.SelectSlot(hoverSlotIndex);
                HideImmediately();
                return;
            }

            if (isOpen)
            {
                UpdateHoverFromMouse();
            }
        }

        public void Configure(TerraMageWeaponLoadout newLoadout, Canvas newCanvas, RectTransform newRoot)
        {
            UnsubscribeFromLoadout();
            loadout = newLoadout;
            wheelCanvas = newCanvas;
            wheelRoot = newRoot;
            SubscribeToLoadout();
        }

        public void HideImmediately()
        {
            isOpen = false;
            hoverSlotIndex = loadout != null ? loadout.SelectedSlotIndex : 0;
            SetWheelVisible(false);
            UpdateVisualState();
        }

        public void RebuildImmediately()
        {
            EnsureUiReferences();
            if (loadout == null || wheelRoot == null)
            {
                return;
            }

            if (defaultFont == null)
            {
                defaultFont = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            }

            ClearRootChildren();
            segmentImages.Clear();
            segmentLabels.Clear();

            int activeSlots = Mathf.Max(1, loadout.ActiveSlotCount);
            float segmentSweep = CalculateSegmentSweep(activeSlots);
            for (int slotIndex = 0; slotIndex < activeSlots; slotIndex++)
            {
                TerraMageWeaponDefinition weapon = loadout.GetWeapon(slotIndex);
                float centerAngle = GetSegmentCenterAngle(slotIndex, activeSlots);
                float startAngle = centerAngle - (segmentSweep * 0.5f);

                var segmentObject = new GameObject($"TerraMage_WeaponWheelSegment_{slotIndex}", typeof(RectTransform));
                var segmentRect = segmentObject.GetComponent<RectTransform>();
                segmentRect.SetParent(wheelRoot, false);
                segmentRect.anchorMin = new Vector2(0.5f, 0.5f);
                segmentRect.anchorMax = new Vector2(0.5f, 0.5f);
                segmentRect.pivot = new Vector2(0.5f, 0.5f);
                segmentRect.sizeDelta = new Vector2(wheelDiameter, wheelDiameter);
                segmentRect.localRotation = Quaternion.Euler(0f, 0f, -startAngle);

                var segmentImage = segmentObject.AddComponent<Image>();
                segmentImage.type = Image.Type.Simple;
                segmentImage.color = slotIndex == 0 ? lockedSlotColor : weapon.UiColor;
                segmentImages.Add(segmentImage);

                var labelObject = new GameObject($"TerraMage_WeaponWheelLabel_{slotIndex}", typeof(RectTransform));
                var labelRect = labelObject.GetComponent<RectTransform>();
                labelRect.SetParent(wheelRoot, false);
                labelRect.anchorMin = new Vector2(0.5f, 0.5f);
                labelRect.anchorMax = new Vector2(0.5f, 0.5f);
                labelRect.pivot = new Vector2(0.5f, 0.5f);
                labelRect.sizeDelta = new Vector2(120f, 42f);
                labelRect.anchoredPosition = DirectionFromAngle(centerAngle) * labelRadius;

                var label = labelObject.AddComponent<Text>();
                label.font = defaultFont;
                label.fontSize = 18;
                label.alignment = TextAnchor.MiddleCenter;
                label.color = Color.white;
                label.text = weapon.DisplayName;
                segmentLabels.Add(label);
            }

            UpdateVisualState();
        }

        public static float CalculateSegmentSweep(int activeSlotCount)
        {
            return 360f / Mathf.Max(1, activeSlotCount);
        }

        public static float GetSegmentCenterAngle(int slotIndex, int activeSlotCount)
        {
            return CalculateSegmentSweep(activeSlotCount) * Mathf.Clamp(slotIndex, 0, Mathf.Max(0, activeSlotCount - 1));
        }

        public static int GetSlotIndexFromAngle(float angleDegrees, int activeSlotCount)
        {
            int bestIndex = 0;
            float bestDelta = 361f;
            float normalizedAngle = NormalizeAngle(angleDegrees);

            for (int slotIndex = 0; slotIndex < Mathf.Max(1, activeSlotCount); slotIndex++)
            {
                float candidateAngle = GetSegmentCenterAngle(slotIndex, activeSlotCount);
                float delta = Mathf.Abs(Mathf.DeltaAngle(normalizedAngle, candidateAngle));
                if (delta < bestDelta)
                {
                    bestDelta = delta;
                    bestIndex = slotIndex;
                }
            }

            return bestIndex;
        }

        private void EnsureUiReferences()
        {
            if (loadout == null)
            {
                loadout = GetComponent<TerraMageWeaponLoadout>();
            }

            if (wheelCanvas == null)
            {
                wheelCanvas = Object.FindAnyObjectByType<Canvas>();
            }

            if (wheelRoot == null && wheelCanvas != null)
            {
                wheelRoot = wheelCanvas.GetComponentInChildren<RectTransform>(true);
            }
        }

        private void SubscribeToLoadout()
        {
            if (loadout == null)
            {
                return;
            }

            loadout.LoadoutChanged -= HandleLoadoutChanged;
            loadout.SelectionChanged -= HandleSelectionChanged;
            loadout.LoadoutChanged += HandleLoadoutChanged;
            loadout.SelectionChanged += HandleSelectionChanged;
        }

        private void UnsubscribeFromLoadout()
        {
            if (loadout == null)
            {
                return;
            }

            loadout.LoadoutChanged -= HandleLoadoutChanged;
            loadout.SelectionChanged -= HandleSelectionChanged;
        }

        private void HandleLoadoutChanged()
        {
            RebuildImmediately();
        }

        private void HandleSelectionChanged(int _, TerraMageWeaponDefinition __)
        {
            UpdateVisualState();
        }

        private void SetWheelVisible(bool visible)
        {
            if (wheelCanvas != null)
            {
                wheelCanvas.enabled = visible;
            }
        }

        private void UpdateHoverFromMouse()
        {
            Vector2 direction = (Vector2)TerraMageInput.MousePosition() - new Vector2(Screen.width * 0.5f, Screen.height * 0.5f);
            if (direction.sqrMagnitude < 16f)
            {
                hoverSlotIndex = loadout.SelectedSlotIndex;
            }
            else
            {
                float angle = NormalizeAngle(Mathf.Atan2(direction.y, direction.x) * Mathf.Rad2Deg);
                hoverSlotIndex = GetSlotIndexFromAngle(angle, loadout.ActiveSlotCount);
            }

            UpdateVisualState();
        }

        private void UpdateVisualState()
        {
            for (int slotIndex = 0; slotIndex < segmentImages.Count; slotIndex++)
            {
                TerraMageWeaponDefinition weapon = loadout != null ? loadout.GetWeapon(slotIndex) : null;
                Color baseColor = slotIndex == 0
                    ? lockedSlotColor
                    : weapon != null ? weapon.UiColor : defaultSlotColor;

                if (slotIndex == loadout.SelectedSlotIndex && !isOpen)
                {
                    baseColor = Color.Lerp(baseColor, highlightSlotColor, 0.65f);
                }

                if (isOpen && slotIndex == hoverSlotIndex)
                {
                    baseColor = Color.Lerp(baseColor, highlightSlotColor, 0.8f);
                }

                segmentImages[slotIndex].color = baseColor;

                if (slotIndex < segmentLabels.Count)
                {
                    segmentLabels[slotIndex].fontStyle = isOpen && slotIndex == hoverSlotIndex
                        ? FontStyle.Bold
                        : slotIndex == loadout.SelectedSlotIndex ? FontStyle.Italic : FontStyle.Normal;
                }
            }
        }

        private void ClearRootChildren()
        {
            for (int childIndex = wheelRoot.childCount - 1; childIndex >= 0; childIndex--)
            {
                GameObject child = wheelRoot.GetChild(childIndex).gameObject;
                if (Application.isPlaying)
                {
                    Destroy(child);
                }
                else
                {
                    DestroyImmediate(child);
                }
            }
        }

        private static Vector2 DirectionFromAngle(float angleDegrees)
        {
            float radians = angleDegrees * Mathf.Deg2Rad;
            return new Vector2(Mathf.Cos(radians), Mathf.Sin(radians));
        }

        private static float NormalizeAngle(float angleDegrees)
        {
            while (angleDegrees < 0f)
            {
                angleDegrees += 360f;
            }

            while (angleDegrees >= 360f)
            {
                angleDegrees -= 360f;
            }

            return angleDegrees;
        }
    }
}
