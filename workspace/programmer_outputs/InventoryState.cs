using System.Collections.Generic;
using UnityEngine;

[DisallowMultipleComponent]
public sealed class InventoryState : MonoBehaviour
{
    private readonly List<string> collectedItemIds = new();

    public IReadOnlyList<string> CollectedItemIds => collectedItemIds;
    public int ItemCount => collectedItemIds.Count;
    public string LastCollectedItemId => ItemCount > 0 ? collectedItemIds[ItemCount - 1] : string.Empty;

    public bool ContainsItem(string itemId)
    {
        return !string.IsNullOrWhiteSpace(itemId) && collectedItemIds.Contains(itemId);
    }

    public bool AddItem(string itemId)
    {
        if (string.IsNullOrWhiteSpace(itemId) || collectedItemIds.Contains(itemId))
        {
            return false;
        }

        collectedItemIds.Add(itemId);
        Debug.Log($"Inventory collected {itemId}. Total items: {ItemCount}.");
        return true;
    }
}
