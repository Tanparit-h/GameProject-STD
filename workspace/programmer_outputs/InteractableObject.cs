using UnityEngine;

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

        Debug.Log($"Interaction triggered for {displayName}.");
    }
}
