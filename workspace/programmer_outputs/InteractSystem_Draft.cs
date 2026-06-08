using System.Collections.Generic;
using UnityEngine;

// PROTOTYPE_PLAN draft only. Do not place this file in Unity Assets yet.
public class InteractSystem_Draft : MonoBehaviour
{
    [SerializeField] private float interactRange = 2.5f;
    [SerializeField] private KeyCode interactKey = KeyCode.E;
    [SerializeField] private string mockPromptText = "Press E to Interact";

    private readonly List<InteractableObject_Draft> objectsInRange = new();
    private InteractableObject_Draft currentTarget;

    private void Update()
    {
        currentTarget = FindClosestInteractable();
        UpdateMockFeedback(currentTarget);

        if (currentTarget != null && Input.GetKeyDown(interactKey))
        {
            currentTarget.Interact();
        }
    }

    private InteractableObject_Draft FindClosestInteractable()
    {
        InteractableObject_Draft closest = null;
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

    private void UpdateMockFeedback(InteractableObject_Draft target)
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
        var interactable = other.GetComponent<InteractableObject_Draft>();
        if (interactable != null && !objectsInRange.Contains(interactable))
        {
            objectsInRange.Add(interactable);
        }
    }

    private void OnTriggerExit(Collider other)
    {
        var interactable = other.GetComponent<InteractableObject_Draft>();
        if (interactable != null)
        {
            objectsInRange.Remove(interactable);
        }
    }
}
