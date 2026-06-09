using UnityEngine;

namespace TerraMageTD
{
    [DisallowMultipleComponent]
    public sealed class TerraMageAimTargetMotion : MonoBehaviour
    {
        [SerializeField] private Vector3 localAxis = Vector3.right;
        [SerializeField] private float amplitude = 1.5f;
        [SerializeField] private float speed = 1.2f;

        private Vector3 startPosition;

        private void Awake()
        {
            startPosition = transform.position;
        }

        private void Update()
        {
            Vector3 axis = localAxis.sqrMagnitude < 0.001f ? Vector3.right : localAxis.normalized;
            transform.position = startPosition + axis * Mathf.Sin(Time.time * speed) * amplitude;
        }
    }
}
