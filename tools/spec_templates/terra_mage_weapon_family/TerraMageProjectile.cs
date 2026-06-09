using UnityEngine;

namespace TerraMageTD
{
    [RequireComponent(typeof(Rigidbody))]
    [RequireComponent(typeof(Collider))]
    public sealed class TerraMageProjectile : MonoBehaviour
    {
        [SerializeField] private float lifetime = 4f;
        [SerializeField] private float impactDamage = 8f;
        [SerializeField] private string sourceName = "Shard Sling";

        private Rigidbody cachedRigidbody;
        private bool hasImpacted;

        private void Awake()
        {
            cachedRigidbody = GetComponent<Rigidbody>();
            cachedRigidbody.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;
        }

        private void Update()
        {
            lifetime -= Time.deltaTime;
            if (lifetime <= 0f)
            {
                Destroy(gameObject);
            }
        }

        public void Launch(Vector3 velocity, float damage, string source)
        {
            if (cachedRigidbody == null)
            {
                cachedRigidbody = GetComponent<Rigidbody>();
            }

            impactDamage = Mathf.Max(0f, damage);
            sourceName = string.IsNullOrWhiteSpace(source) ? sourceName : source;
            SetVelocity(cachedRigidbody, velocity);
        }

        private void OnCollisionEnter(Collision collision)
        {
            if (hasImpacted)
            {
                return;
            }

            hasImpacted = true;
            ContactPoint contact = collision.contactCount > 0 ? collision.GetContact(0) : default;
            TerraMageDamageable damageable = collision.collider.GetComponentInParent<TerraMageDamageable>();
            if (damageable != null)
            {
                Vector3 impulse = cachedRigidbody != null ? GetVelocity(cachedRigidbody) : Vector3.zero;
                damageable.ApplyDamage(impactDamage, contact.point, impulse, sourceName);
            }

            Debug.Log($"Terra Mage projectile hit {collision.collider.gameObject.name} with {sourceName}");
            Destroy(gameObject);
        }

        private static void SetVelocity(Rigidbody target, Vector3 velocity)
        {
#if UNITY_6000_0_OR_NEWER
            target.linearVelocity = velocity;
#else
            target.velocity = velocity;
#endif
        }

        private static Vector3 GetVelocity(Rigidbody target)
        {
#if UNITY_6000_0_OR_NEWER
            return target.linearVelocity;
#else
            return target.velocity;
#endif
        }
    }
}
