using UnityEngine;

public class InteractableObject : MonoBehaviour
{
    [SerializeField] private string displayName = "Interactable Object";
    [SerializeField] private bool canInteract = true;

    public string DisplayName => displayName;
    public bool CanInteract => canInteract;

    public void Configure(string newDisplayName, bool newCanInteract = true)
    {
        if (!string.IsNullOrWhiteSpace(newDisplayName))
        {
            displayName = newDisplayName;
        }

        canInteract = newCanInteract;
    }

    protected bool TryBeginInteract()
    {
        if (!canInteract)
        {
            Debug.Log($"{displayName} is currently unavailable.");
            return false;
        }

        return true;
    }

    public virtual void Interact()
    {
        if (!TryBeginInteract())
        {
            return;
        }

        Debug.Log($"Interaction triggered for {DisplayName}.");
    }
}
