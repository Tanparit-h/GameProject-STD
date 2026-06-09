using UnityEngine;

namespace TerraMageTD
{
    [DisallowMultipleComponent]
    public sealed class TerraMageActionBuildController : MonoBehaviour
    {
        [SerializeField] private Camera aimCamera;
        [SerializeField] private float defaultPullRange = 8f;
        [SerializeField] private float defaultCompressMultiplier = 2.5f;
        [SerializeField] private float defaultThrowForce = 14f;
        [SerializeField] private float defaultHeatPerUse = 0.55f;
        [SerializeField] private LayerMask materialMask = ~0;
        [SerializeField] private TerraMageWeaponLoadout weaponLoadout;
        [SerializeField] private TerraMageMeleeGestureController meleeGestureController;
        [SerializeField] private TerraMageWeaponWheelUI weaponWheelUI;

        private TerraMageMaterialPayload heldPayload;
        private bool hasPayload;

        public bool HasPayload => hasPayload;
        public Camera AimCamera => aimCamera;
        public TerraMageMaterialPayload HeldPayload => heldPayload;
        public TerraMageWeaponAttackMode CurrentAttackMode => GetCurrentWeapon().AttackMode;
        public float CurrentPullRange
        {
            get
            {
                TerraMageWeaponDefinition weapon = GetCurrentWeapon();
                if (!weapon.SupportsRanged)
                {
                    return 0f;
                }

                return weapon.RangedPullRange > 0f ? weapon.RangedPullRange : defaultPullRange;
            }
        }
        public float CurrentThrowForce => GetCurrentWeapon().SupportsRanged ? GetCurrentWeapon().RangedThrowForce : 0f;

        private void Awake()
        {
            if (aimCamera == null)
            {
                aimCamera = Camera.main;
            }

            if (weaponLoadout == null)
            {
                weaponLoadout = GetComponent<TerraMageWeaponLoadout>();
            }

            if (meleeGestureController == null)
            {
                meleeGestureController = GetComponent<TerraMageMeleeGestureController>();
            }

            if (weaponWheelUI == null)
            {
                weaponWheelUI = GetComponent<TerraMageWeaponWheelUI>();
            }
        }

        public void SetAimCamera(Camera newAimCamera)
        {
            aimCamera = newAimCamera;
        }

        public void SetWeaponLoadout(TerraMageWeaponLoadout newLoadout)
        {
            weaponLoadout = newLoadout;
        }

        public void SetMeleeGestureController(TerraMageMeleeGestureController newController)
        {
            meleeGestureController = newController;
        }

        public void SetWeaponWheelUI(TerraMageWeaponWheelUI newWheelUI)
        {
            weaponWheelUI = newWheelUI;
        }

        private void Update()
        {
            if (weaponWheelUI != null && weaponWheelUI.IsOpen)
            {
                return;
            }

            if (TerraMageInput.GetKeyDown(KeyCode.Q))
            {
                PullMaterialFromAim();
            }

            if (TerraMageInput.GetKeyDown(KeyCode.E))
            {
                CompressHeldMaterial();
            }

            if (TerraMageInput.GetKeyDown(KeyCode.R))
            {
                HeatHeldMaterial();
            }

            if (TerraMageInput.GetMouseButtonDown(0))
            {
                UsePrimaryAction();
            }
        }

        public void UsePrimaryAction()
        {
            if (CurrentAttackMode == TerraMageWeaponAttackMode.Melee)
            {
                if (meleeGestureController != null)
                {
                    meleeGestureController.PerformQuickAttack();
                }

                return;
            }

            ThrowHeldMaterial();
        }

        public void PullMaterialFromAim()
        {
            if (CurrentAttackMode != TerraMageWeaponAttackMode.Ranged || aimCamera == null)
            {
                return;
            }

            Ray ray = aimCamera.ViewportPointToRay(new Vector3(0.5f, 0.5f, 0f));
            if (!Physics.Raycast(ray, out RaycastHit hit, Mathf.Max(1f, CurrentPullRange), materialMask))
            {
                return;
            }

            heldPayload = TerraMageMaterialSystem.CreateLooseEarth(hit.point);
            hasPayload = true;
            Debug.Log($"Terra Mage pulled {heldPayload.Kind} for {GetCurrentWeapon().DisplayName} from {hit.point}");
        }

        public void CompressHeldMaterial()
        {
            if (!hasPayload || CurrentAttackMode != TerraMageWeaponAttackMode.Ranged)
            {
                return;
            }

            float multiplier = GetCurrentWeapon().SupportsRanged
                ? GetCurrentWeapon().RangedCompressMultiplier
                : defaultCompressMultiplier;
            heldPayload = TerraMageMaterialSystem.Compress(heldPayload, multiplier);
            Debug.Log($"Terra Mage compressed payload into {heldPayload.Kind} with {GetCurrentWeapon().DisplayName}");
        }

        public void HeatHeldMaterial()
        {
            if (!hasPayload || CurrentAttackMode != TerraMageWeaponAttackMode.Ranged)
            {
                return;
            }

            float heat = GetCurrentWeapon().SupportsRanged ? GetCurrentWeapon().RangedHeatPerUse : defaultHeatPerUse;
            heldPayload = TerraMageMaterialSystem.Heat(heldPayload, heat);
            Debug.Log($"Terra Mage heated payload into {heldPayload.Kind} with {GetCurrentWeapon().DisplayName}");
        }

        public void ThrowHeldMaterial()
        {
            if (!hasPayload || aimCamera == null || CurrentAttackMode != TerraMageWeaponAttackMode.Ranged)
            {
                return;
            }

            float throwForce = GetCurrentWeapon().SupportsRanged ? GetCurrentWeapon().RangedThrowForce : defaultThrowForce;
            Vector3 velocity = aimCamera.transform.forward * throwForce;
            float damage = TerraMageMaterialSystem.CalculateImpactDamage(heldPayload, velocity, 1f);
            Debug.Log($"Terra Mage threw {heldPayload.Kind} with {GetCurrentWeapon().DisplayName} for {damage:0.0} damage");
            hasPayload = false;
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
