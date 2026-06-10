# Inventory Pickup - Implementation Report

## Goal

Deliver a real Unity interaction where the player presses `E` near a pickup placeholder and stores it in a simple inventory list.

## Implemented Programmer Outputs

- `InteractSystem.cs`
- `InteractableObject.cs`
- `InventoryState.cs`
- `PickupInteractable.cs`
- `AIInventoryPickupSceneSetup.cs`
- `AIInventoryPickupSceneValidator.cs`

## Behavior Summary

- Reuse the shared trigger-based interaction flow.
- Collect the `Sun Shard` pickup into `InventoryState`.
- Disable the pickup after collection so it cannot be collected twice.
- Validate inventory contents and visual state changes in batchmode.

## Validation Target

- Scene: `Assets/Scenes/InventoryPickupScene.unity`
- Setup method: `AIInventoryPickupSceneSetup.SetupScene`
- Validation method: `AIInventoryPickupSceneValidator.ValidateScene`
