using UnityEngine;

// PROTOTYPE_PLAN draft only. Do not place this file in Unity Assets yet.
public class InteractableObject_Draft : MonoBehaviour
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
