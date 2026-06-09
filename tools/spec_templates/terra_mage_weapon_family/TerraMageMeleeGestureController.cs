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
        [SerializeField] private Camera aimCamera;
        [SerializeField] private LayerMask meleeHitMask = ~0;
        [SerializeField] private float meleeHitRadius = 0.12f;

        private Vector2 dragStart;
        private bool dragging;

        public TerraMageMeleeRangeProfile RangeProfile => GetCurrentWeapon().MeleeProfile;
        public float CurrentMeleeReach => Mathf.Max(0.5f, GetCurrentWeapon().MeleeReach);
        public TerraMageWeaponDefinition CurrentWeapon => GetCurrentWeapon();
        public Camera AimCamera => aimCamera;

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

            if (aimCamera == null)
            {
                aimCamera = Camera.main;
            }
        }

        private void Update()
        {
            if (weaponWheelUI != null && weaponWheelUI.IsOpen)
            {
                return;
            }

            if (TerraMageInput.GetMouseButtonDown(1))
            {
                BeginDrag(TerraMageInput.MousePosition());
            }

            if (TerraMageInput.GetMouseButtonUp(1))
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

        public void SetAimCamera(Camera newAimCamera)
        {
            aimCamera = newAimCamera;
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

            if (!TryFindMeleeHit(out RaycastHit hit))
            {
                return false;
            }

            Debug.Log($"Terra Mage melee {gesture} hit {hit.collider.gameObject.name} with {weapon.DisplayName}");
            return true;
        }

        private bool TryFindMeleeHit(out RaycastHit bestHit)
        {
            Vector3 origin = transform.position + Vector3.up * 0.18f;
            Vector3 direction = aimCamera != null ? aimCamera.transform.forward : transform.forward;
            RaycastHit[] hits = Physics.SphereCastAll(
                origin,
                Mathf.Max(0.01f, meleeHitRadius),
                direction,
                CurrentMeleeReach,
                meleeHitMask,
                QueryTriggerInteraction.Ignore);

            float closestDistance = float.MaxValue;
            bestHit = default;

            foreach (RaycastHit hit in hits)
            {
                if (hit.collider == null || hit.collider.transform.IsChildOf(transform))
                {
                    continue;
                }

                if (hit.distance < closestDistance)
                {
                    closestDistance = hit.distance;
                    bestHit = hit;
                }
            }

            return closestDistance < float.MaxValue;
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
