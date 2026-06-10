using UnityEngine;

[DisallowMultipleComponent]
public sealed class QuestMarkerObjective : MonoBehaviour
{
    [SerializeField] private string objectiveName = "Ancient Beacon";
    [SerializeField] private float reachRadius = 1.2f;
    [SerializeField] private bool reached;

    public string ObjectiveName => objectiveName;
    public float ReachRadius => reachRadius;
    public bool Reached => reached;

    public void ConfigureObjective(string targetName, float targetReachRadius)
    {
        objectiveName = string.IsNullOrWhiteSpace(targetName) ? "Ancient Beacon" : targetName;
        reachRadius = Mathf.Clamp(targetReachRadius, 0.5f, 5f);
        reached = false;
    }

    public bool EvaluateReached(Vector3 playerPosition)
    {
        if (reached)
        {
            return true;
        }

        float distance = Vector3.Distance(playerPosition, transform.position);
        if (distance <= reachRadius)
        {
            reached = true;
            Debug.Log($"Quest objective reached: {objectiveName}.");
        }

        return reached;
    }
}
