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
        [SerializeField] private TerraMageAimSystem aimSystem;
        [SerializeField] private float projectileSpawnOffset = 0.45f;
        [SerializeField] private float projectileScale = 0.14f;

        private TerraMageMaterialPayload heldPayload;
        private bool hasPayload;

        public bool HasPayload => hasPayload;
        public Camera AimCamera => aimCamera;
        public TerraMageAimSystem AimSystem => aimSystem;
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

                return TerraMagePlayerMechanics.ResolvePullRange(weapon, defaultPullRange);
            }
        }
        public float CurrentThrowForce => TerraMagePlayerMechanics.ResolveThrowForce(GetCurrentWeapon(), 0f);

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

            if (aimSystem == null && aimCamera != null)
            {
                aimSystem = aimCamera.GetComponent<TerraMageAimSystem>();
            }
        }

        public void SetAimCamera(Camera newAimCamera)
        {
            aimCamera = newAimCamera;
            if (aimSystem == null && aimCamera != null)
            {
                aimSystem = aimCamera.GetComponent<TerraMageAimSystem>();
            }
        }

        public void SetAimSystem(TerraMageAimSystem newAimSystem)
        {
            aimSystem = newAimSystem;
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

            float multiplier =
                TerraMagePlayerMechanics.ResolveCompressMultiplier(GetCurrentWeapon(), defaultCompressMultiplier);
            heldPayload = TerraMageMaterialSystem.Compress(heldPayload, multiplier);
            Debug.Log($"Terra Mage compressed payload into {heldPayload.Kind} with {GetCurrentWeapon().DisplayName}");
        }

        public void HeatHeldMaterial()
        {
            if (!hasPayload || CurrentAttackMode != TerraMageWeaponAttackMode.Ranged)
            {
                return;
            }

            float heat = TerraMagePlayerMechanics.ResolveHeatPerUse(GetCurrentWeapon(), defaultHeatPerUse);
            heldPayload = TerraMageMaterialSystem.Heat(heldPayload, heat);
            Debug.Log($"Terra Mage heated payload into {heldPayload.Kind} with {GetCurrentWeapon().DisplayName}");
        }

        public void ThrowHeldMaterial()
        {
            if (aimCamera == null || CurrentAttackMode != TerraMageWeaponAttackMode.Ranged)
            {
                return;
            }

            TerraMageWeaponDefinition weapon = GetCurrentWeapon();
            TerraMageMaterialPayload payload = hasPayload
                ? heldPayload
                : TerraMagePlayerMechanics.CreateDefaultRangedPayload(aimCamera.transform.position);
            float throwForce = TerraMagePlayerMechanics.ResolveThrowForce(weapon, defaultThrowForce);
            Vector3 velocity = aimCamera.transform.forward * throwForce;
            float damage = TerraMageMaterialSystem.CalculateImpactDamage(payload, velocity, 1f);
            SpawnProjectile(payload, velocity, damage, weapon.DisplayName);
            DebugRangedAimTarget();
            Debug.Log($"Terra Mage launched {payload.Kind} with {weapon.DisplayName} for {damage:0.0} damage");
            hasPayload = false;
        }

        private void SpawnProjectile(TerraMageMaterialPayload payload, Vector3 velocity, float damage, string sourceName)
        {
            Vector3 spawnPosition = TerraMagePlayerMechanics.CalculateProjectileSpawnPosition(aimCamera, projectileSpawnOffset);
            GameObject projectileObject = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            projectileObject.name = $"TerraMage_Projectile_{payload.Kind}";
            projectileObject.transform.position = spawnPosition;
            projectileObject.transform.localScale = Vector3.one * Mathf.Max(0.04f, projectileScale);
            TerraMagePlayerMechanics.ApplyProjectileTint(projectileObject, payload);

            Rigidbody body = projectileObject.AddComponent<Rigidbody>();
            body.mass = Mathf.Max(0.1f, payload.Mass);
            body.useGravity = false;

            TerraMageProjectile projectile = projectileObject.AddComponent<TerraMageProjectile>();
            projectile.Launch(velocity, damage, sourceName);
        }

        private void DebugRangedAimTarget()
        {
            TerraMageWeaponDefinition weapon = GetCurrentWeapon();
            if (aimSystem != null && aimSystem.HasValidHit && aimSystem.CurrentTarget != null)
            {
                Debug.Log($"Terra Mage ranged {weapon.DisplayName} aimed at {aimSystem.CurrentTarget.DisplayName}");
                return;
            }

            Debug.Log($"Terra Mage ranged {weapon.DisplayName} has no target under crosshair.");
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
