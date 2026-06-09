using UnityEngine;

namespace TerraMageTD
{
    public sealed class TerraMageFollowCamera : MonoBehaviour
    {
        [SerializeField] private Transform target;
        [SerializeField] private Vector3 pivotOffset = new Vector3(0f, 1.1f, 0f);
        [SerializeField] private float distance = 3.6f;
        [SerializeField] private float yaw;
        [SerializeField] private float pitch = 16f;
        [SerializeField] private float mouseSensitivity = 120f;
        [SerializeField] private float followSharpness = 12f;
        [SerializeField] private float minPitch = -10f;
        [SerializeField] private float maxPitch = 45f;
        [SerializeField] private TerraMageWeaponWheelUI weaponWheelUI;

        private float nextWeaponWheelLookupTime;

        public Transform Target => target;

        private void Awake()
        {
            TryResolveWeaponWheel(true);
        }

        public void SetTarget(Transform newTarget)
        {
            target = newTarget;
            if (target != null)
            {
                yaw = target.eulerAngles.y;
            }
        }

        public void SetWeaponWheelUI(TerraMageWeaponWheelUI newWeaponWheelUI)
        {
            weaponWheelUI = newWeaponWheelUI;
        }

        private void Update()
        {
            if (target == null)
            {
                return;
            }

            TryResolveWeaponWheel(false);

            if (weaponWheelUI != null && weaponWheelUI.IsOpen)
            {
                return;
            }

            yaw += TerraMageInput.GetAxisRaw("Mouse X") * mouseSensitivity * Time.deltaTime;
            pitch -= TerraMageInput.GetAxisRaw("Mouse Y") * mouseSensitivity * Time.deltaTime;
            pitch = Mathf.Clamp(pitch, minPitch, maxPitch);
        }

        private void TryResolveWeaponWheel(bool force)
        {
            if (weaponWheelUI != null)
            {
                return;
            }

            if (!force && Time.unscaledTime < nextWeaponWheelLookupTime)
            {
                return;
            }

            nextWeaponWheelLookupTime = Time.unscaledTime + 0.5f;
            weaponWheelUI = Object.FindAnyObjectByType<TerraMageWeaponWheelUI>();
        }

        private void LateUpdate()
        {
            if (target == null)
            {
                return;
            }

            Quaternion orbit = Quaternion.Euler(pitch, yaw, 0f);
            Vector3 focusPoint = target.position + pivotOffset;
            Vector3 desiredPosition = focusPoint - orbit * Vector3.forward * distance;
            float blend = 1f - Mathf.Exp(-followSharpness * Time.deltaTime);

            transform.position = Vector3.Lerp(transform.position, desiredPosition, blend);
            transform.rotation = Quaternion.Slerp(transform.rotation, orbit, blend);
        }
    }
}
