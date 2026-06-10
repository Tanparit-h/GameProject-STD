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
        [SerializeField] private Transform weaponSwingRoot;
        [SerializeField] private LayerMask meleeHitMask = ~0;
        [SerializeField] private float meleeHitRadius = 0.12f;
        [SerializeField] private float swingDuration = 0.26f;
        [SerializeField] private float meleeHitNormalizedTime = 0.52f;
        [SerializeField] private float baseMeleeDamage = 8f;

        private Vector2 dragStart;
        private bool dragging;
        private readonly RaycastHit[] meleeHitResults = new RaycastHit[MaxMeleeHitResults];
        private Quaternion swingRootRestLocalRotation;
        private Vector3 swingRootRestLocalPosition;
        private Quaternion swingTargetLocalRotation;
        private float swingTimer;
        private bool hasWeaponRestPose;
        private bool swingActive;
        private bool pendingMeleeHit;
        private bool pendingMeleeHitResolved;
        private TerraMageMeleeGesture pendingMeleeGesture;
        private string pendingMeleeWeaponName;
        private float pendingMeleeDamage;

        public TerraMageMeleeRangeProfile RangeProfile => GetCurrentWeapon().MeleeProfile;
        public float CurrentMeleeReach => Mathf.Max(0.5f, GetCurrentWeapon().MeleeReach);
        public TerraMageWeaponDefinition CurrentWeapon => GetCurrentWeapon();
        public Camera AimCamera => aimCamera;
        public Transform WeaponVisual => weaponVisual;
        public Transform WeaponSwingRoot => weaponSwingRoot;

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
            EnsureWeaponSwingRoot();
            CacheWeaponRestPose();
        }

        public void SetWeaponSwingRoot(Transform newWeaponSwingRoot)
        {
            weaponSwingRoot = newWeaponSwingRoot;
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
            return TerraMagePlayerMechanics.ClassifyMeleeGesture(delta, gestureThreshold);
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
            return true;
        }

        private bool TryFindMeleeHit(out RaycastHit bestHit)
        {
            Vector3 origin = TerraMagePlayerMechanics.BuildMeleeOrigin(transform, 0.18f);
            Vector3 direction = TerraMagePlayerMechanics.ResolveAimDirection(aimCamera, transform);
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
            EnsureWeaponSwingRoot();
            Transform animatedRoot = GetAnimatedWeaponRoot();
            if (animatedRoot == null)
            {
                hasWeaponRestPose = false;
                return;
            }

            swingRootRestLocalPosition = animatedRoot.localPosition;
            swingRootRestLocalRotation = animatedRoot.localRotation;
            swingTargetLocalRotation = swingRootRestLocalRotation;
            swingTimer = 0f;
            swingActive = false;
            hasWeaponRestPose = true;
        }

        private void BeginWeaponSwing(TerraMageMeleeGesture gesture)
        {
            Transform animatedRoot = GetAnimatedWeaponRoot();
            if (animatedRoot == null)
            {
                return;
            }

            if (!hasWeaponRestPose)
            {
                CacheWeaponRestPose();
            }

            swingTimer = CurrentSwingDuration();
            swingActive = true;
            swingTargetLocalRotation = swingRootRestLocalRotation * GetSwingOffset(gesture);
            pendingMeleeHit = true;
            pendingMeleeHitResolved = false;
            pendingMeleeGesture = gesture;
            TerraMageWeaponDefinition weapon = GetCurrentWeapon();
            pendingMeleeWeaponName = weapon.DisplayName;
            pendingMeleeDamage = TerraMagePlayerMechanics.CalculateMeleeDamage(baseMeleeDamage, weapon);
        }

        private void UpdateWeaponSwing()
        {
            if (!swingActive)
            {
                return;
            }

            Transform animatedRoot = GetAnimatedWeaponRoot();
            if (animatedRoot == null || !hasWeaponRestPose)
            {
                swingActive = false;
                return;
            }

            if (swingTimer <= 0f)
            {
                animatedRoot.localPosition = swingRootRestLocalPosition;
                animatedRoot.localRotation = swingRootRestLocalRotation;
                swingActive = false;
                return;
            }

            swingTimer = Mathf.Max(0f, swingTimer - Time.deltaTime);
            float normalizedTime = 1f - (swingTimer / CurrentSwingDuration());
            if (pendingMeleeHit && !pendingMeleeHitResolved && normalizedTime >= meleeHitNormalizedTime)
            {
                ResolvePendingMeleeHit();
            }

            float strikeWeight = Mathf.Sin(normalizedTime * Mathf.PI);
            animatedRoot.localPosition = swingRootRestLocalPosition + new Vector3(0f, 0.012f * strikeWeight, 0.08f * strikeWeight);
            animatedRoot.localRotation = Quaternion.Slerp(swingRootRestLocalRotation, swingTargetLocalRotation, strikeWeight);
        }

        private void ResolvePendingMeleeHit()
        {
            pendingMeleeHitResolved = true;
            pendingMeleeHit = false;
            if (!TryFindMeleeHit(out RaycastHit hit))
            {
                return;
            }

            TerraMageDamageable damageable = hit.collider.GetComponentInParent<TerraMageDamageable>();
            if (damageable != null)
            {
                Vector3 impulse =
                    TerraMagePlayerMechanics.ResolveAimDirection(aimCamera, transform) * pendingMeleeDamage;
                damageable.ApplyDamage(pendingMeleeDamage, hit.point, impulse, pendingMeleeWeaponName);
            }

            Debug.Log($"Terra Mage melee {pendingMeleeGesture} hit {hit.collider.gameObject.name} with {pendingMeleeWeaponName}");
        }

        private void EnsureWeaponSwingRoot()
        {
            if (weaponVisual == null || weaponSwingRoot != null)
            {
                return;
            }

            if (weaponVisual.parent != null && weaponVisual.parent.name == "TerraMage_StaffSwingRoot")
            {
                weaponSwingRoot = weaponVisual.parent;
                return;
            }

            var rootObject = new GameObject("TerraMage_StaffSwingRoot");
            Transform originalParent = weaponVisual.parent;
            rootObject.transform.SetParent(originalParent, false);
            rootObject.transform.position = weaponVisual.TransformPoint(new Vector3(0f, -0.16f, 0f));
            rootObject.transform.rotation = originalParent != null ? originalParent.rotation : Quaternion.identity;
            weaponSwingRoot = rootObject.transform;
            weaponVisual.SetParent(weaponSwingRoot, true);
        }

        private Transform GetAnimatedWeaponRoot()
        {
            return weaponSwingRoot != null ? weaponSwingRoot : weaponVisual;
        }

        private float CurrentSwingDuration()
        {
            return Mathf.Max(0.01f, swingDuration);
        }

        private static Quaternion GetSwingOffset(TerraMageMeleeGesture gesture)
        {
            return gesture switch
            {
                TerraMageMeleeGesture.LeftSwing => Quaternion.Euler(18f, -42f, 128f),
                TerraMageMeleeGesture.RightSwing => Quaternion.Euler(18f, 42f, -128f),
                TerraMageMeleeGesture.Overhead => Quaternion.Euler(-128f, 0f, 0f),
                _ => Quaternion.Euler(-82f, 26f, -72f),
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
