using UnityEngine;

namespace TerraMageTD
{
    public enum TerraMageMeleeGesture
    {
        None,
        Punch,
        LeftSwing,
        RightSwing,
        Overhead
    }

    public enum TerraMageMeleeRangeProfile
    {
        UnarmedPunch,
        ShortStaff,
        MediumPole,
        LongReach,
        HeavyOverhead
    }

    [DisallowMultipleComponent]
    public sealed class TerraMageMeleeGestureController : MonoBehaviour
    {
        [SerializeField] private float gestureThreshold = 48f;
        [SerializeField] private TerraMageWeaponLoadout weaponLoadout;
        [SerializeField] private TerraMageWeaponWheelUI weaponWheelUI;

        private Vector2 dragStart;
        private bool dragging;

        public TerraMageMeleeRangeProfile RangeProfile => GetCurrentWeapon().MeleeProfile;
        public float CurrentMeleeReach => Mathf.Max(0.5f, GetCurrentWeapon().MeleeReach);
        public TerraMageWeaponDefinition CurrentWeapon => GetCurrentWeapon();

        private void Awake()
        {
            if (weaponLoadout == null)
            {
                weaponLoadout = GetComponent<TerraMageWeaponLoadout>();
            }

            if (weaponWheelUI == null)
            {
                weaponWheelUI = GetComponent<TerraMageWeaponWheelUI>();
            }
        }

        private void Update()
        {
            if (weaponWheelUI != null && weaponWheelUI.IsOpen)
            {
                return;
            }

            if (TerraMageTerraMageInput.GetMouseButtonDown(1))
            {
                BeginDrag(TerraMageInput.MousePosition());
            }

            if (TerraMageTerraMageInput.GetMouseButtonUp(1))
            {
                TerraMageMeleeGesture gesture = EndDrag(TerraMageInput.MousePosition());
                if (gesture != TerraMageMeleeGesture.None)
                {
                    PerformAttack(gesture);
                }
            }
        }

        public void SetWeaponLoadout(TerraMageWeaponLoadout newLoadout)
        {
            weaponLoadout = newLoadout;
        }

        public void SetWeaponWheelUI(TerraMageWeaponWheelUI newWheelUI)
        {
            weaponWheelUI = newWheelUI;
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

            return delta.y > 0f ? TerraMageMeleeGesture.Overhead : TerraMageMeleeGesture.Punch;
        }

        public bool PerformQuickAttack()
        {
            TerraMageWeaponDefinition weapon = GetCurrentWeapon();
            if (!weapon.SupportsMelee)
            {
                Debug.Log($"Terra Mage current weapon {weapon.DisplayName} is ranged-only.");
                return false;
            }

            TerraMageMeleeGesture gesture = weapon.PrimaryGesture == TerraMageMeleeGesture.None
                ? TerraMageMeleeGesture.Punch
                : weapon.PrimaryGesture;
            return PerformAttack(gesture);
        }

        public bool PerformAttack(TerraMageMeleeGesture gesture)
        {
            TerraMageWeaponDefinition weapon = GetCurrentWeapon();
            if (!weapon.SupportsMelee)
            {
                return false;
            }

            Debug.Log(
                $"Terra Mage melee {gesture} with {weapon.DisplayName} using {RangeProfile} reach {CurrentMeleeReach:0.00}m");
            return true;
        }

        private TerraMageWeaponDefinition GetCurrentWeapon()
        {
            if (weaponLoadout != null)
            {
                return weaponLoadout.CurrentWeapon;
            }

            return TerraMageWeaponDefinition.CreateBareHands();
        }
    }
}
