using UnityEngine;

// IMPLEMENTATION preview only. Apply to Unity only after explicit IMPLEMENTATION phase approval.
// Generated from workspace/programmer_outputs/InteractableObject_Draft.cs.
public class InteractableObject : MonoBehaviour
{
    [SerializeField] private string displayName = "Interactable Object";
    [SerializeField] private bool canInteract = true;

    public string DisplayName => displayName;
    public bool CanInteract => canInteract;

    public void Interact()
    {
        if (!canInteract)
        {
            Debug.Log($"{displayName} is currently unavailable.");
            return;
        }

        Debug.Log($"Mock interaction triggered for {displayName}.");
    }
}
