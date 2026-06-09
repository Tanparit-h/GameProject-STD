using UnityEngine;

namespace TerraMageTD
{
    [DisallowMultipleComponent]
    public sealed class TerraMageDamageable : MonoBehaviour
    {
        [SerializeField] private float maxHealth = 30f;
        [SerializeField] private float knockbackScale = 0.08f;
        [SerializeField] private float hitFlashDuration = 0.12f;
        [SerializeField] private Color hitFlashColor = new Color(1f, 0.92f, 0.22f, 1f);

        private Renderer[] cachedRenderers;
        private Color[][] baseMaterialColors;
        private float currentHealth;
        private float flashTimer;

        public float CurrentHealth => currentHealth;
        public float MaxHealth => maxHealth;
        public bool IsAlive => currentHealth > 0f;

        private void Awake()
        {
            currentHealth = Mathf.Max(1f, maxHealth);
            CacheRenderers();
        }

        private void Update()
        {
            if (flashTimer <= 0f)
            {
                return;
            }

            flashTimer = Mathf.Max(0f, flashTimer - Time.deltaTime);
            if (flashTimer <= 0f)
            {
                RestoreBaseColors();
            }
        }

        public void Configure(float newMaxHealth)
        {
            maxHealth = Mathf.Max(1f, newMaxHealth);
            currentHealth = maxHealth;
            CacheRenderers();
        }

        public void RefreshBaseColors()
        {
            CacheRenderers();
        }

        public void ApplyDamage(float amount, Vector3 hitPoint, Vector3 impulse, string source)
        {
            float damage = Mathf.Max(0f, amount);
            if (damage <= 0f)
            {
                return;
            }

            currentHealth = Mathf.Max(0f, currentHealth - damage);
            ApplyHitFlash();
            ApplyKnockback(impulse);

            string displaySource = string.IsNullOrWhiteSpace(source) ? "unknown source" : source;
            Debug.Log(
                $"Terra Mage damage: {name} took {damage:0.0} from {displaySource} at {hitPoint} ({currentHealth:0.0}/{maxHealth:0.0})");
        }

        private void CacheRenderers()
        {
            cachedRenderers = GetComponentsInChildren<Renderer>(true);
            baseMaterialColors = new Color[cachedRenderers.Length][];

            for (int rendererIndex = 0; rendererIndex < cachedRenderers.Length; rendererIndex++)
            {
                Material[] materials = cachedRenderers[rendererIndex].materials;
                baseMaterialColors[rendererIndex] = new Color[materials.Length];
                for (int materialIndex = 0; materialIndex < materials.Length; materialIndex++)
                {
                    Material material = materials[materialIndex];
                    baseMaterialColors[rendererIndex][materialIndex] =
                        material != null && material.HasProperty("_Color") ? material.color : Color.white;
                }
            }
        }

        private void ApplyHitFlash()
        {
            flashTimer = Mathf.Max(0.01f, hitFlashDuration);
            SetRendererColor(hitFlashColor);
        }

        private void RestoreBaseColors()
        {
            if (cachedRenderers == null || baseMaterialColors == null)
            {
                return;
            }

            for (int rendererIndex = 0; rendererIndex < cachedRenderers.Length; rendererIndex++)
            {
                Renderer rendererComponent = cachedRenderers[rendererIndex];
                if (rendererComponent == null)
                {
                    continue;
                }

                Material[] materials = rendererComponent.materials;
                for (int materialIndex = 0; materialIndex < materials.Length; materialIndex++)
                {
                    Material material = materials[materialIndex];
                    if (material != null && material.HasProperty("_Color"))
                    {
                        material.color = baseMaterialColors[rendererIndex][materialIndex];
                    }
                }
            }
        }

        private void SetRendererColor(Color color)
        {
            if (cachedRenderers == null)
            {
                CacheRenderers();
            }

            foreach (Renderer rendererComponent in cachedRenderers)
            {
                if (rendererComponent == null)
                {
                    continue;
                }

                foreach (Material material in rendererComponent.materials)
                {
                    if (material != null && material.HasProperty("_Color"))
                    {
                        material.color = color;
                    }
                }
            }
        }

        private void ApplyKnockback(Vector3 impulse)
        {
            Vector3 planarImpulse = Vector3.ProjectOnPlane(impulse, Vector3.up);
            if (planarImpulse.sqrMagnitude < 0.0001f)
            {
                return;
            }

            transform.position += planarImpulse.normalized * Mathf.Min(0.35f, planarImpulse.magnitude * knockbackScale);
        }
    }
}
