using UnityEngine;

namespace SandMageTD
{
    public enum SandMageMeleeGesture
    {
        None,
        LeftSwing,
        RightSwing,
        Overhead
    }

    public enum SandMageMeleeRangeProfile
    {
        ShortStaff,
        MediumPole,
        LongReach,
        HeavyOverhead
    }

    public sealed class SandMageMeleeGestureController : MonoBehaviour
    {
        [SerializeField] private float gestureThreshold = 48f;
        [SerializeField] private SandMageMeleeRangeProfile rangeProfile = SandMageMeleeRangeProfile.ShortStaff;

        private Vector2 dragStart;
        private bool dragging;

        public SandMageMeleeRangeProfile RangeProfile => rangeProfile;

        private void Update()
        {
            if (Input.GetMouseButtonDown(1))
            {
                BeginDrag(Input.mousePosition);
            }

            if (Input.GetMouseButtonUp(1))
            {
                SandMageMeleeGesture gesture = EndDrag(Input.mousePosition);
                if (gesture != SandMageMeleeGesture.None)
                {
                    Debug.Log($"Sand Mage melee {gesture} using {rangeProfile}");
                }
            }

            if (Input.GetKeyDown(KeyCode.Alpha1)) SelectRangeProfile(SandMageMeleeRangeProfile.ShortStaff);
            if (Input.GetKeyDown(KeyCode.Alpha2)) SelectRangeProfile(SandMageMeleeRangeProfile.MediumPole);
            if (Input.GetKeyDown(KeyCode.Alpha3)) SelectRangeProfile(SandMageMeleeRangeProfile.LongReach);
            if (Input.GetKeyDown(KeyCode.Alpha4)) SelectRangeProfile(SandMageMeleeRangeProfile.HeavyOverhead);
        }

        public void BeginDrag(Vector2 mousePosition)
        {
            dragStart = mousePosition;
            dragging = true;
        }

        public SandMageMeleeGesture EndDrag(Vector2 mousePosition)
        {
            if (!dragging)
            {
                return SandMageMeleeGesture.None;
            }

            dragging = false;
            Vector2 delta = mousePosition - dragStart;
            if (delta.magnitude < gestureThreshold)
            {
                return SandMageMeleeGesture.None;
            }

            if (Mathf.Abs(delta.x) > Mathf.Abs(delta.y))
            {
                return delta.x < 0f ? SandMageMeleeGesture.LeftSwing : SandMageMeleeGesture.RightSwing;
            }

            return delta.y > 0f ? SandMageMeleeGesture.Overhead : SandMageMeleeGesture.None;
        }

        public void SelectRangeProfile(SandMageMeleeRangeProfile profile)
        {
            rangeProfile = profile;
            Debug.Log($"Sand Mage selected melee range {rangeProfile}");
        }
    }
}
