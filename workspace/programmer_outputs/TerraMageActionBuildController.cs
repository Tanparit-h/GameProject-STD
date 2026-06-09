using UnityEngine;

namespace TerraMageTD
{
    public sealed class TerraMageActionBuildController : MonoBehaviour
    {
        [SerializeField] private Camera aimCamera;
        [SerializeField] private float pullRange = 8f;
        [SerializeField] private float compressMultiplier = 2.5f;
        [SerializeField] private float throwForce = 14f;
        [SerializeField] private float heatPerUse = 0.55f;
        [SerializeField] private LayerMask materialMask = ~0;

        private TerraMageMaterialPayload heldPayload;
        private bool hasPayload;

        public bool HasPayload => hasPayload;
        public Camera AimCamera => aimCamera;
        public TerraMageMaterialPayload HeldPayload => heldPayload;

        private void Awake()
        {
            if (aimCamera == null)
            {
                aimCamera = Camera.main;
            }
        }

        public void SetAimCamera(Camera newAimCamera)
        {
            aimCamera = newAimCamera;
        }

        private void Update()
        {
            if (Input.GetKeyDown(KeyCode.Q))
            {
                PullMaterialFromAim();
            }

            if (Input.GetKeyDown(KeyCode.E))
            {
                CompressHeldMaterial();
            }

            if (Input.GetKeyDown(KeyCode.R))
            {
                HeatHeldMaterial();
            }

            if (Input.GetMouseButtonDown(0))
            {
                ThrowHeldMaterial();
            }
        }

        public void PullMaterialFromAim()
        {
            if (aimCamera == null)
            {
                return;
            }

            Ray ray = aimCamera.ScreenPointToRay(Input.mousePosition);
            if (!Physics.Raycast(ray, out RaycastHit hit, pullRange, materialMask))
            {
                return;
            }

            heldPayload = TerraMageMaterialSystem.CreateLooseEarth(hit.point);
            hasPayload = true;
            Debug.Log($"Terra Mage pulled {heldPayload.Kind} from {hit.point}");
        }

        public void CompressHeldMaterial()
        {
            if (!hasPayload)
            {
                return;
            }

            heldPayload = TerraMageMaterialSystem.Compress(heldPayload, compressMultiplier);
            Debug.Log($"Terra Mage compressed payload into {heldPayload.Kind} mass {heldPayload.Mass:0.0}");
        }

        public void HeatHeldMaterial()
        {
            if (!hasPayload)
            {
                return;
            }

            heldPayload = TerraMageMaterialSystem.Heat(heldPayload, heatPerUse);
            Debug.Log($"Terra Mage heated payload into {heldPayload.Kind} heat {heldPayload.Heat:0.0}");
        }

        public void ThrowHeldMaterial()
        {
            if (!hasPayload || aimCamera == null)
            {
                return;
            }

            Vector3 velocity = aimCamera.transform.forward * throwForce;
            float damage = TerraMageMaterialSystem.CalculateImpactDamage(heldPayload, velocity, 1f);
            Debug.Log($"Terra Mage threw {heldPayload.Kind} with expected physics damage {damage:0.0}");
            hasPayload = false;
        }
    }
}
