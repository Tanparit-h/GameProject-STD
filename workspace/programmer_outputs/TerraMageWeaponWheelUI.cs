using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace TerraMageTD
{
    [DisallowMultipleComponent]
    public sealed class TerraMageWeaponWheelUI : MonoBehaviour
    {
        private const int SegmentTextureSize = 192;
        private const float SegmentInnerRadius = 0.2f;
        private const float SegmentGapDegrees = 2f;

        [SerializeField] private TerraMageWeaponLoadout loadout;
        [SerializeField] private Canvas wheelCanvas;
        [SerializeField] private RectTransform wheelRoot;
        [SerializeField] private float wheelDiameter = 320f;
        [SerializeField] private float labelRadius = 112f;
        [SerializeField] private float deltaSelectionSensitivity = 1.15f;
        [SerializeField] private float minSelectionMagnitude = 18f;
        [SerializeField] private KeyCode openWheelKey = KeyCode.Tab;
        [SerializeField] private Color defaultSlotColor = new Color(0.22f, 0.24f, 0.28f, 0.82f);
        [SerializeField] private Color highlightSlotColor = new Color(1f, 0.82f, 0.2f, 0.92f);

        private readonly List<Image> segmentImages = new List<Image>();
        private readonly List<Text> segmentLabels = new List<Text>();
        private readonly List<Sprite> generatedSegmentSprites = new List<Sprite>();

        private Font defaultFont;
        private bool isOpen;
        private int hoverSlotIndex;
        private Vector2 selectionVector;

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
            DisposeGeneratedSegmentSprites();
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
                selectionVector = Vector2.zero;
                UpdateHoverFromMouseDelta();
            }
            else if (!shouldOpen && isOpen)
            {
                EquipHoveredSlot();
                HideImmediately();
                return;
            }

            if (isOpen)
            {
                UpdateHoverFromMouseDelta();
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
            SyncHoverWithSelection();
            SetWheelVisible(false);
            UpdateVisualState();
        }

        public void SyncHoverWithSelection()
        {
            hoverSlotIndex = loadout != null ? loadout.SelectedSlotIndex : 0;
            selectionVector = Vector2.zero;
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
            DisposeGeneratedSegmentSprites();
            segmentImages.Clear();
            segmentLabels.Clear();

            int activeSlots = Mathf.Max(1, loadout.ActiveSlotCount);
            float segmentSweep = CalculateSegmentSweep(activeSlots);
            for (int slotIndex = 0; slotIndex < activeSlots; slotIndex++)
            {
                TerraMageWeaponDefinition weapon = loadout.GetWeapon(slotIndex);
                float centerAngle = GetSegmentCenterAngle(slotIndex, activeSlots);

                var segmentObject = new GameObject($"TerraMage_WeaponWheelSegment_{slotIndex}", typeof(RectTransform));
                var segmentRect = segmentObject.GetComponent<RectTransform>();
                segmentRect.SetParent(wheelRoot, false);
                segmentRect.anchorMin = new Vector2(0.5f, 0.5f);
                segmentRect.anchorMax = new Vector2(0.5f, 0.5f);
                segmentRect.pivot = new Vector2(0.5f, 0.5f);
                segmentRect.sizeDelta = new Vector2(wheelDiameter, wheelDiameter);

                var segmentImage = segmentObject.AddComponent<Image>();
                segmentImage.type = Image.Type.Simple;
                Sprite segmentSprite =
                    CreateSegmentSprite($"TerraMage_WeaponWheelSegmentSprite_{slotIndex}", centerAngle, segmentSweep);
                generatedSegmentSprites.Add(segmentSprite);
                segmentImage.sprite = segmentSprite;
                segmentImage.color = weapon != null ? weapon.UiColor : defaultSlotColor;
                segmentImage.preserveAspect = true;
                segmentImage.raycastTarget = false;
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
            if (!isOpen && loadout != null)
            {
                SyncHoverWithSelection();
            }

            UpdateVisualState();
        }

        private void SetWheelVisible(bool visible)
        {
            if (wheelCanvas != null)
            {
                wheelCanvas.enabled = visible;
            }
        }

        private void UpdateHoverFromMouseDelta()
        {
            int previousHoverSlot = hoverSlotIndex;
            selectionVector += TerraMageInput.MouseDelta() * Mathf.Max(0.01f, deltaSelectionSensitivity);
            float maxMagnitude = Mathf.Max(labelRadius, wheelDiameter * 0.5f);
            selectionVector = Vector2.ClampMagnitude(selectionVector, maxMagnitude);

            if (selectionVector.sqrMagnitude < minSelectionMagnitude * minSelectionMagnitude)
            {
                hoverSlotIndex = loadout.SelectedSlotIndex;
            }
            else
            {
                float angle = NormalizeAngle(Mathf.Atan2(selectionVector.y, selectionVector.x) * Mathf.Rad2Deg);
                hoverSlotIndex = GetSlotIndexFromAngle(angle, loadout.ActiveSlotCount);
            }

            if (hoverSlotIndex != previousHoverSlot)
            {
                EquipHoveredSlot();
            }

            UpdateVisualState();
        }

        private void EquipHoveredSlot()
        {
            if (loadout == null)
            {
                return;
            }

            int previousSlot = loadout.SelectedSlotIndex;
            loadout.SelectSlot(hoverSlotIndex);
            if (previousSlot != loadout.SelectedSlotIndex)
            {
                Debug.Log($"Terra Mage equipped {loadout.CurrentWeapon.DisplayName}");
            }
        }

        private void UpdateVisualState()
        {
            for (int slotIndex = 0; slotIndex < segmentImages.Count; slotIndex++)
            {
                TerraMageWeaponDefinition weapon = loadout != null ? loadout.GetWeapon(slotIndex) : null;
                Color baseColor = weapon != null ? weapon.UiColor : defaultSlotColor;

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

        private static Sprite CreateSegmentSprite(string spriteName, float centerAngle, float segmentSweep)
        {
            var texture = new Texture2D(SegmentTextureSize, SegmentTextureSize, TextureFormat.RGBA32, false)
            {
                name = spriteName,
                filterMode = FilterMode.Bilinear,
                wrapMode = TextureWrapMode.Clamp,
                hideFlags = HideFlags.HideAndDontSave
            };

            float halfSweep = Mathf.Max(1f, segmentSweep * 0.5f - SegmentGapDegrees);
            float center = (SegmentTextureSize - 1) * 0.5f;
            var pixels = new Color32[SegmentTextureSize * SegmentTextureSize];
            var clear = new Color32(0, 0, 0, 0);
            var solid = new Color32(255, 255, 255, 235);

            for (int y = 0; y < SegmentTextureSize; y++)
            {
                for (int x = 0; x < SegmentTextureSize; x++)
                {
                    float normalizedX = (x - center) / center;
                    float normalizedY = (y - center) / center;
                    float radius = Mathf.Sqrt((normalizedX * normalizedX) + (normalizedY * normalizedY));
                    int pixelIndex = x + (y * SegmentTextureSize);

                    if (radius < SegmentInnerRadius || radius > 1f)
                    {
                        pixels[pixelIndex] = clear;
                        continue;
                    }

                    float angle = NormalizeAngle(Mathf.Atan2(normalizedY, normalizedX) * Mathf.Rad2Deg);
                    float delta = Mathf.Abs(Mathf.DeltaAngle(angle, centerAngle));
                    pixels[pixelIndex] = delta <= halfSweep ? solid : clear;
                }
            }

            texture.SetPixels32(pixels);
            texture.Apply(false, true);

            var sprite = Sprite.Create(
                texture,
                new Rect(0f, 0f, SegmentTextureSize, SegmentTextureSize),
                new Vector2(0.5f, 0.5f),
                SegmentTextureSize);
            sprite.name = spriteName;
            sprite.hideFlags = HideFlags.HideAndDontSave;
            return sprite;
        }

        private void DisposeGeneratedSegmentSprites()
        {
            foreach (Sprite sprite in generatedSegmentSprites)
            {
                if (sprite == null)
                {
                    continue;
                }

                Texture2D texture = sprite.texture;
                DestroyUnityObject(sprite);
                if (texture != null)
                {
                    DestroyUnityObject(texture);
                }
            }

            generatedSegmentSprites.Clear();
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

        private static void DestroyUnityObject(Object target)
        {
            if (target == null)
            {
                return;
            }

            if (Application.isPlaying)
            {
                Destroy(target);
            }
            else
            {
                DestroyImmediate(target);
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
