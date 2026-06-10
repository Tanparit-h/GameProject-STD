using UnityEngine;

[DisallowMultipleComponent]
public sealed class PickupInteractable : InteractableObject
{
    [SerializeField] private string itemId = "sun_shard";
    [SerializeField] private InventoryState inventory;
    [SerializeField] private Collider pickupCollider;
    [SerializeField] private GameObject visualRoot;
    [SerializeField] private bool collected;

    public string ItemId => itemId;
    public InventoryState Inventory => inventory;
    public bool IsCollected => collected;
    public bool VisualVisible => visualRoot == null || visualRoot.activeSelf;

    private void Awake()
    {
        if (pickupCollider == null)
        {
            pickupCollider = GetComponent<Collider>();
        }

        if (visualRoot == null)
        {
            visualRoot = gameObject;
        }

        ApplyCollectedState();
    }

    public void ConfigurePickup(
        InventoryState targetInventory,
        string pickupItemId,
        string pickupName,
        Collider targetCollider,
        GameObject targetVisual)
    {
        inventory = targetInventory;
        itemId = string.IsNullOrWhiteSpace(pickupItemId) ? "sun_shard" : pickupItemId;
        pickupCollider = targetCollider != null ? targetCollider : GetComponent<Collider>();
        visualRoot = targetVisual != null ? targetVisual : gameObject;
        collected = false;
        Configure(pickupName, true);
        ApplyCollectedState();
    }

    public override void Interact()
    {
        if (!TryBeginInteract())
        {
            return;
        }

        if (inventory == null)
        {
            Debug.Log($"{DisplayName} cannot be collected because no inventory is assigned.");
            return;
        }

        if (!inventory.AddItem(itemId))
        {
            Debug.Log($"{DisplayName} was already collected.");
            return;
        }

        collected = true;
        Configure(DisplayName, false);
        ApplyCollectedState();
        Debug.Log($"Pickup collected {DisplayName} ({itemId}).");
    }

    private void ApplyCollectedState()
    {
        if (pickupCollider != null)
        {
            pickupCollider.enabled = !collected;
        }

        if (visualRoot != null)
        {
            visualRoot.SetActive(!collected);
        }
    }
}
