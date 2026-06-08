using System.Collections.Generic;
using UnityEngine;

// IMPLEMENTATION preview only. Apply to Unity only after explicit IMPLEMENTATION phase approval.
// Generated from workspace/programmer_outputs/InteractSystem_Draft.cs.
public class InteractSystem : MonoBehaviour
{
    [SerializeField] private float interactRange = 2.5f;
    [SerializeField] private KeyCode interactKey = KeyCode.E;
    [SerializeField] private string mockPromptText = "Press E to Interact";

    private readonly List<InteractableObject> objectsInRange = new();
    private InteractableObject currentTarget;

    private void Update()
    {
        currentTarget = FindClosestInteractable();
        UpdateMockFeedback(currentTarget);

        if (currentTarget != null && Input.GetKeyDown(interactKey))
        {
            currentTarget.Interact();
        }
    }

    private InteractableObject FindClosestInteractable()
    {
        InteractableObject closest = null;
        float closestDistance = float.MaxValue;

        foreach (var candidate in objectsInRange)
        {
            if (candidate == null || !candidate.CanInteract)
            {
                continue;
            }

            float distance = Vector3.Distance(transform.position, candidate.transform.position);
            if (distance <= interactRange && distance < closestDistance)
            {
                closest = candidate;
                closestDistance = distance;
            }
        }

        return closest;
    }

    private void UpdateMockFeedback(InteractableObject target)
    {
        if (target == null)
        {
            Debug.Log("Mock UI hidden: no interactable object in range.");
            return;
        }

        Debug.Log($"{mockPromptText}: {target.DisplayName}");
    }

    private void OnTriggerEnter(Collider other)
    {
        var interactable = other.GetComponent<InteractableObject>();
        if (interactable != null && !objectsInRange.Contains(interactable))
        {
            objectsInRange.Add(interactable);
        }
    }

    private void OnTriggerExit(Collider other)
    {
        var interactable = other.GetComponent<InteractableObject>();
        if (interactable != null)
        {
            objectsInRange.Remove(interactable);
        }
    }
}
