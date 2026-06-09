using UnityEngine;

namespace TerraMageTD
{
    public enum TerraMageMeleeGesture
    {
        None,
        LeftSwing,
        RightSwing,
        Overhead
    }

    public enum TerraMageMeleeRangeProfile
    {
        ShortStaff,
        MediumPole,
        LongReach,
        HeavyOverhead
    }

    public sealed class TerraMageMeleeGestureController : MonoBehaviour
    {
        [SerializeField] private float gestureThreshold = 48f;
        [SerializeField] private TerraMageMeleeRangeProfile rangeProfile = TerraMageMeleeRangeProfile.ShortStaff;

        private Vector2 dragStart;
        private bool dragging;

        public TerraMageMeleeRangeProfile RangeProfile => rangeProfile;

        private void Update()
        {
            if (Input.GetMouseButtonDown(1))
            {
                BeginDrag(Input.mousePosition);
            }

            if (Input.GetMouseButtonUp(1))
            {
                TerraMageMeleeGesture gesture = EndDrag(Input.mousePosition);
                if (gesture != TerraMageMeleeGesture.None)
                {
                    Debug.Log($"Terra Mage melee {gesture} using {rangeProfile}");
                }
            }

            if (Input.GetKeyDown(KeyCode.Alpha1)) SelectRangeProfile(TerraMageMeleeRangeProfile.ShortStaff);
            if (Input.GetKeyDown(KeyCode.Alpha2)) SelectRangeProfile(TerraMageMeleeRangeProfile.MediumPole);
            if (Input.GetKeyDown(KeyCode.Alpha3)) SelectRangeProfile(TerraMageMeleeRangeProfile.LongReach);
            if (Input.GetKeyDown(KeyCode.Alpha4)) SelectRangeProfile(TerraMageMeleeRangeProfile.HeavyOverhead);
        }

        public void BeginDrag(Vector2 mousePosition)
        {
            dragStart = mousePosition;
            dragging = true;
        }

        public TerraMageMeleeGesture EndDrag(Vector2 mousePosition)
        {
            if (!dragging)
            {
                return TerraMageMeleeGesture.None;
            }

            dragging = false;
            Vector2 delta = mousePosition - dragStart;
            if (delta.magnitude < gestureThreshold)
            {
                return TerraMageMeleeGesture.None;
            }

            if (Mathf.Abs(delta.x) > Mathf.Abs(delta.y))
            {
                return delta.x < 0f ? TerraMageMeleeGesture.LeftSwing : TerraMageMeleeGesture.RightSwing;
            }

            return delta.y > 0f ? TerraMageMeleeGesture.Overhead : TerraMageMeleeGesture.None;
        }

        public void SelectRangeProfile(TerraMageMeleeRangeProfile profile)
        {
            rangeProfile = profile;
            Debug.Log($"Terra Mage selected melee range {rangeProfile}");
        }
    }
}
