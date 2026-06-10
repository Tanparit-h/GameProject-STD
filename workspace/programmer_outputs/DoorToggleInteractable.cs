using UnityEngine;

[DisallowMultipleComponent]
public sealed class DoorToggleInteractable : InteractableObject
{
    [SerializeField] private Transform doorHinge;
    [SerializeField] private float openAngle = 92f;
    [SerializeField] private bool startsOpen;
    [SerializeField] private Vector3 closedLocalEuler;

    private bool configured;
    private bool isOpen;

    public Transform DoorHinge => doorHinge;
    public float OpenAngle => openAngle;
    public bool IsOpen => isOpen;
    public Vector3 ClosedLocalEuler => closedLocalEuler;
    public Vector3 OpenLocalEuler => closedLocalEuler + new Vector3(0f, openAngle, 0f);

    private void Awake()
    {
        EnsureConfigured();
    }

    private void OnValidate()
    {
        if (doorHinge == null)
        {
            doorHinge = transform;
        }

        if (!configured)
        {
            closedLocalEuler = doorHinge.localEulerAngles;
        }
    }

    public void ConfigureDoor(Transform hinge, string doorName, float targetOpenAngle, bool openInitially = false)
    {
        doorHinge = hinge != null ? hinge : transform;
        closedLocalEuler = doorHinge.localEulerAngles;
        openAngle = Mathf.Clamp(targetOpenAngle, 15f, 170f);
        startsOpen = openInitially;
        configured = true;
        isOpen = startsOpen;
        Configure(doorName, true);
        ApplyStateImmediate();
    }

    public override void Interact()
    {
        EnsureConfigured();
        if (!TryBeginInteract())
        {
            return;
        }

        isOpen = !isOpen;
        ApplyStateImmediate();
        Debug.Log($"Door toggled {DisplayName}: {(isOpen ? "open" : "closed")}.");
    }

    public void SetOpen(bool open)
    {
        EnsureConfigured();
        isOpen = open;
        ApplyStateImmediate();
    }

    private void EnsureConfigured()
    {
        if (doorHinge == null)
        {
            doorHinge = transform;
        }

        if (configured)
        {
            return;
        }

        closedLocalEuler = doorHinge.localEulerAngles;
        configured = true;
        isOpen = startsOpen;
        ApplyStateImmediate();
    }

    private void ApplyStateImmediate()
    {
        if (doorHinge == null)
        {
            return;
        }

        doorHinge.localRotation = Quaternion.Euler(isOpen ? OpenLocalEuler : ClosedLocalEuler);
    }
}
