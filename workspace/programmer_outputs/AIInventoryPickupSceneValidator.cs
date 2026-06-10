using System;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class AIInventoryPickupSceneValidator
{
    private const string ScenePath = "Assets/Scenes/InventoryPickupScene.unity";

    public static void ValidateScene()
    {
        EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);

        var player = RequireObject("AIInventory_Player");
        RequireComponent<InteractSystem>(player, "AIInventory_Player");
        var inventory = RequireComponent<InventoryState>(player, "AIInventory_Player");

        var trigger = RequireComponent<SphereCollider>(player, "AIInventory_Player");
        if (!trigger.isTrigger)
        {
            throw new InvalidOperationException("AIInventory_Player SphereCollider must be a trigger.");
        }

        var body = RequireComponent<Rigidbody>(player, "AIInventory_Player");
        if (!body.isKinematic)
        {
            throw new InvalidOperationException("AIInventory_Player Rigidbody must be kinematic.");
        }

        RequireObject("AIInventory_Ground");
        RequireObject("AIInventory_PlayerMarker");
        var pickupObject = RequireObject("AIInventory_Pickup");
        var visual = RequireObject("AIInventory_PickupVisual");
        var pickup = RequireComponent<PickupInteractable>(pickupObject, "AIInventory_Pickup");
        var colliderComponent = RequireComponent<BoxCollider>(pickupObject, "AIInventory_Pickup");

        if (pickup.Inventory != inventory)
        {
            throw new InvalidOperationException("Pickup must reference the player inventory.");
        }

        if (pickup.DisplayName != "Sun Shard")
        {
            throw new InvalidOperationException("Pickup prompt should display Sun Shard.");
        }

        if (pickup.ItemId != "sun_shard")
        {
            throw new InvalidOperationException("Pickup item id must stay deterministic.");
        }

        if (pickup.IsCollected || inventory.ItemCount != 0)
        {
            throw new InvalidOperationException("Pickup scene must start with an empty inventory.");
        }

        if (!visual.activeSelf || !colliderComponent.enabled)
        {
            throw new InvalidOperationException("Pickup should start visible and collectible.");
        }

        pickup.Interact();

        if (!pickup.IsCollected)
        {
            throw new InvalidOperationException("Interacting with the pickup must collect it.");
        }

        if (inventory.ItemCount != 1 || !inventory.ContainsItem("sun_shard"))
        {
            throw new InvalidOperationException("Collected item must be stored in the player inventory.");
        }

        if (inventory.LastCollectedItemId != "sun_shard")
        {
            throw new InvalidOperationException("Inventory should report the last collected item.");
        }

        if (pickup.CanInteract)
        {
            throw new InvalidOperationException("Collected pickup should no longer be interactable.");
        }

        if (visual.activeSelf || colliderComponent.enabled)
        {
            throw new InvalidOperationException("Collected pickup should hide its visual and collider.");
        }

        Debug.Log("AIInventoryPickupSceneValidator passed.");
    }

    private static GameObject RequireObject(string objectName)
    {
        var found = GameObject.Find(objectName);
        if (found == null)
        {
            throw new InvalidOperationException($"Required scene object is missing: {objectName}");
        }

        return found;
    }

    private static T RequireComponent<T>(GameObject target, string objectName) where T : Component
    {
        var component = target.GetComponent<T>();
        if (component == null)
        {
            throw new InvalidOperationException($"{objectName} is missing required component {typeof(T).Name}.");
        }

        return component;
    }
}
