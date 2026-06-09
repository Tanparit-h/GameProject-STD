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
        private const int MaxMeleeHitResults = 16;

        [SerializeField] private float gestureThreshold = 48f;
        [SerializeField] private TerraMageWeaponLoadout weaponLoadout;
        [SerializeField] private TerraMageWeaponWheelUI weaponWheelUI;
        [SerializeField] private Camera aimCamera;
        [SerializeField] private Transform weaponVisual;
        [SerializeField] private LayerMask meleeHitMask = ~0;
        [SerializeField] private float meleeHitRadius = 0.12f;
        [SerializeField] private float swingDuration = 0.18f;

        private Vector2 dragStart;
        private bool dragging;
        private readonly RaycastHit[] meleeHitResults = new RaycastHit[MaxMeleeHitResults];
        private Quaternion weaponRestLocalRotation;
        private Vector3 weaponRestLocalPosition;
        private Quaternion swingTargetLocalRotation;
        private float swingTimer;
        private bool hasWeaponRestPose;

        public TerraMageMeleeRangeProfile RangeProfile => GetCurrentWeapon().MeleeProfile;
        public float CurrentMeleeReach => Mathf.Max(0.5f, GetCurrentWeapon().MeleeReach);
        public TerraMageWeaponDefinition CurrentWeapon => GetCurrentWeapon();
        public Camera AimCamera => aimCamera;
        public Transform WeaponVisual => weaponVisual;

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

            if (weaponVisual == null)
            {
                Transform foundStaff = transform.Find("TerraMage_MockStaff");
                if (foundStaff != null)
                {
                    SetWeaponVisual(foundStaff);
                }
            }
            else
            {
                CacheWeaponRestPose();
            }
        }

        private void Update()
        {
            UpdateWeaponSwing();

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

        public void SetWeaponVisual(Transform newWeaponVisual)
        {
            weaponVisual = newWeaponVisual;
            CacheWeaponRestPose();
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

            BeginWeaponSwing(gesture);

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
            int hitCount = Physics.SphereCastNonAlloc(
                origin,
                Mathf.Max(0.01f, meleeHitRadius),
                direction,
                meleeHitResults,
                CurrentMeleeReach,
                meleeHitMask,
                QueryTriggerInteraction.Ignore);

            float closestDistance = float.MaxValue;
            bestHit = default;

            for (int hitIndex = 0; hitIndex < hitCount; hitIndex++)
            {
                RaycastHit hit = meleeHitResults[hitIndex];
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

        private void CacheWeaponRestPose()
        {
            if (weaponVisual == null)
            {
                hasWeaponRestPose = false;
                return;
            }

            weaponRestLocalPosition = weaponVisual.localPosition;
            weaponRestLocalRotation = weaponVisual.localRotation;
            swingTargetLocalRotation = weaponRestLocalRotation;
            hasWeaponRestPose = true;
        }

        private void BeginWeaponSwing(TerraMageMeleeGesture gesture)
        {
            if (weaponVisual == null)
            {
                return;
            }

            if (!hasWeaponRestPose)
            {
                CacheWeaponRestPose();
            }

            swingTimer = Mathf.Max(0.01f, swingDuration);
            swingTargetLocalRotation = weaponRestLocalRotation * GetSwingOffset(gesture);
        }

        private void UpdateWeaponSwing()
        {
            if (weaponVisual == null || !hasWeaponRestPose)
            {
                return;
            }

            if (swingTimer <= 0f)
            {
                weaponVisual.localPosition = weaponRestLocalPosition;
                weaponVisual.localRotation = weaponRestLocalRotation;
                return;
            }

            swingTimer = Mathf.Max(0f, swingTimer - Time.deltaTime);
            float normalizedTime = 1f - (swingTimer / Mathf.Max(0.01f, swingDuration));
            float strikeWeight = Mathf.Sin(normalizedTime * Mathf.PI);
            weaponVisual.localPosition = weaponRestLocalPosition + new Vector3(0f, 0f, 0.035f * strikeWeight);
            weaponVisual.localRotation = Quaternion.Slerp(weaponRestLocalRotation, swingTargetLocalRotation, strikeWeight);
        }

        private static Quaternion GetSwingOffset(TerraMageMeleeGesture gesture)
        {
            return gesture switch
            {
                TerraMageMeleeGesture.LeftSwing => Quaternion.Euler(8f, -18f, 72f),
                TerraMageMeleeGesture.RightSwing => Quaternion.Euler(8f, 18f, -72f),
                TerraMageMeleeGesture.Overhead => Quaternion.Euler(-78f, 0f, 0f),
                _ => Quaternion.Euler(-42f, 12f, -34f),
            };
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
