using UnityEngine;

namespace TerraMageTD
{
    public enum TerraMageAimTargetVisibilityMode
    {
        None,
        DisappearAfterDelay,
        Blink
    }

    [DisallowMultipleComponent]
    [RequireComponent(typeof(TerraMageAimTarget))]
    public sealed class TerraMageAimTargetVisibility : MonoBehaviour
    {
        [SerializeField] private TerraMageAimTargetVisibilityMode mode = TerraMageAimTargetVisibilityMode.None;
        [SerializeField] private float initialDelay;
        [SerializeField] private float visibleDuration = 1.2f;
        [SerializeField] private float hiddenDuration = 0.6f;

        private TerraMageAimTarget aimTarget;
        private float elapsedTime;

        public TerraMageAimTargetVisibilityMode Mode => mode;

        private void Awake()
        {
            aimTarget = GetComponent<TerraMageAimTarget>();
        }

        private void OnEnable()
        {
            elapsedTime = 0f;
            if (aimTarget != null)
            {
                aimTarget.SetVisible(true);
            }
        }

        public void Configure(
            TerraMageAimTargetVisibilityMode newMode,
            float newInitialDelay,
            float newVisibleDuration,
            float newHiddenDuration)
        {
            mode = newMode;
            initialDelay = newInitialDelay;
            visibleDuration = newVisibleDuration;
            hiddenDuration = newHiddenDuration;
        }

        private void Update()
        {
            if (aimTarget == null || mode == TerraMageAimTargetVisibilityMode.None)
            {
                return;
            }

            elapsedTime += Time.deltaTime;
            if (elapsedTime < initialDelay)
            {
                return;
            }

            float activeTime = elapsedTime - initialDelay;

            if (mode == TerraMageAimTargetVisibilityMode.DisappearAfterDelay)
            {
                aimTarget.SetVisible(false);
                enabled = false;
                return;
            }

            float cycleDuration = Mathf.Max(0.1f, visibleDuration + hiddenDuration);
            bool visibleNow = (activeTime % cycleDuration) < Mathf.Max(0.05f, visibleDuration);
            aimTarget.SetVisible(visibleNow);
        }
    }
}
