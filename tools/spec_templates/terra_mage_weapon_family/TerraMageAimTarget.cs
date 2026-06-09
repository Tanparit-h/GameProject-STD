using UnityEngine;

namespace TerraMageTD
{
    [DisallowMultipleComponent]
    public sealed class TerraMageAimTarget : MonoBehaviour
    {
        [SerializeField] private string displayName = "Aim Target";
        [SerializeField] private Color baseColor = new Color(0.35f, 0.8f, 1f, 1f);
        [SerializeField] private Color highlightColor = new Color(1f, 0.85f, 0.2f, 1f);

        private Renderer[] cachedRenderers;
        private Collider[] cachedColliders;
        private bool isVisible = true;
        private bool isHighlighted;

        public string DisplayName => string.IsNullOrWhiteSpace(displayName) ? gameObject.name : displayName;
        public bool IsVisible => isVisible;
        public bool CanBeAimed => isVisible && gameObject.activeInHierarchy && HasEnabledCollider();

        private void Awake()
        {
            CacheComponents();
            EnsureDamageable();
            ApplyVisual();
            RefreshDamageableColors();
        }

        public void Configure(string newDisplayName, Color newBaseColor)
        {
            displayName = newDisplayName;
            baseColor = newBaseColor;
            CacheComponents();
            ApplyVisual();
            RefreshDamageableColors();
        }

        public Vector3 GetAimPoint()
        {
            CacheComponents();

            foreach (Collider candidate in cachedColliders)
            {
                if (candidate != null && candidate.enabled)
                {
                    return candidate.bounds.center;
                }
            }

            return transform.position;
        }

        public void SetHighlighted(bool highlighted)
        {
            isHighlighted = highlighted;
            ApplyVisual();
        }

        public void SetVisible(bool visible)
        {
            isVisible = visible;
            CacheComponents();

            foreach (Renderer renderer in cachedRenderers)
            {
                if (renderer != null)
                {
                    renderer.enabled = visible;
                }
            }

            foreach (Collider colliderComponent in cachedColliders)
            {
                if (colliderComponent != null)
                {
                    colliderComponent.enabled = visible;
                }
            }
        }

        private void CacheComponents()
        {
            cachedRenderers = GetComponentsInChildren<Renderer>(true);
            cachedColliders = GetComponentsInChildren<Collider>(true);
        }

        private void EnsureDamageable()
        {
            if (GetComponent<TerraMageDamageable>() == null)
            {
                gameObject.AddComponent<TerraMageDamageable>();
            }
        }

        private void RefreshDamageableColors()
        {
            TerraMageDamageable damageable = GetComponent<TerraMageDamageable>();
            if (damageable != null)
            {
                damageable.RefreshBaseColors();
            }
        }

        private bool HasEnabledCollider()
        {
            CacheComponents();

            foreach (Collider candidate in cachedColliders)
            {
                if (candidate != null && candidate.enabled)
                {
                    return true;
                }
            }

            return false;
        }

        private void ApplyVisual()
        {
            CacheComponents();
            Color tint = isHighlighted ? highlightColor : baseColor;

            foreach (Renderer renderer in cachedRenderers)
            {
                if (renderer == null)
                {
                    continue;
                }

                renderer.enabled = isVisible;
                foreach (Material material in renderer.materials)
                {
                    if (material != null && material.HasProperty("_Color"))
                    {
                        material.color = tint;
                    }
                }
            }
        }
    }
}
