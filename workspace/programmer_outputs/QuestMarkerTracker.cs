using UnityEngine;

[DisallowMultipleComponent]
public sealed class QuestMarkerTracker : MonoBehaviour
{
    [SerializeField] private QuestMarkerObjective targetObjective;
    [SerializeField] private Transform markerVisual;
    [SerializeField] private Vector3 lastDirection = Vector3.forward;
    [SerializeField] private float currentDistance;
    [SerializeField] private bool markerVisible;

    public QuestMarkerObjective TargetObjective => targetObjective;
    public Transform MarkerVisual => markerVisual;
    public Vector3 LastDirection => lastDirection;
    public float CurrentDistance => currentDistance;
    public bool MarkerVisible => markerVisible;

    private void Update()
    {
        RefreshMarker();
    }

    public void Configure(QuestMarkerObjective objective, Transform visual)
    {
        targetObjective = objective;
        markerVisual = visual;
        RefreshMarker();
    }

    public void RefreshMarker()
    {
        if (targetObjective == null || markerVisual == null)
        {
            return;
        }

        currentDistance = Vector3.Distance(transform.position, targetObjective.transform.position);
        if (targetObjective.EvaluateReached(transform.position))
        {
            markerVisible = false;
            markerVisual.gameObject.SetActive(false);
            return;
        }

        var flatOffset = targetObjective.transform.position - transform.position;
        flatOffset.y = 0f;
        lastDirection = flatOffset.sqrMagnitude < 0.001f ? Vector3.forward : flatOffset.normalized;
        markerVisible = true;
        markerVisual.gameObject.SetActive(true);
        markerVisual.rotation = Quaternion.LookRotation(lastDirection, Vector3.up);
        Debug.Log($"Quest marker updated toward {targetObjective.ObjectiveName}: {currentDistance:0.00}m");
    }
}
