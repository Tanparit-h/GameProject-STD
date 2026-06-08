# Implementation Patch Plan

## Current Phase

PROTOTYPE_PLAN

## Status

Prepared only. Do not apply until the user explicitly approves `IMPLEMENTATION` phase.

## Source Files

- `workspace/creator_outputs/exports/interactive_objects.glb`
- `workspace/programmer_outputs/InteractSystem_Draft.cs`
- `workspace/programmer_outputs/InteractableObject_Draft.cs`

## Future Unity Destination Files

- `game_project/Assets/AIAssets/interactive_objects.glb`
- `game_project/Assets/Scripts/AIPrototype/InteractSystem.cs`
- `game_project/Assets/Scripts/AIPrototype/InteractableObject.cs`

## Patch Actions To Apply In IMPLEMENTATION Phase

1. Create `game_project/Assets/AIAssets/`.
2. Copy `workspace/creator_outputs/exports/interactive_objects.glb` to `game_project/Assets/AIAssets/interactive_objects.glb`.
3. Create `game_project/Assets/Scripts/AIPrototype/`.
4. Copy and rename `InteractSystem_Draft.cs` to `InteractSystem.cs`.
5. Copy and rename `InteractableObject_Draft.cs` to `InteractableObject.cs`.
6. Remove `_Draft` suffix from class names before Unity compile validation.
7. Keep scene and prefab wiring manual unless the user selects a specific scene/prefab to modify.
8. Run Unity batchmode validation only after Unity executable path and project path are confirmed.

## Expected Code Adjustments

- `InteractSystem_Draft` becomes `InteractSystem`.
- `InteractableObject_Draft` becomes `InteractableObject`.
- Type references from `InteractableObject_Draft` become `InteractableObject`.
- Comments should keep provenance note: generated from AI Game Studio prototype plan.

## Safety Boundary

This patch plan does not modify Unity files. It exists so the next IMPLEMENTATION step can be reviewed before applying changes.
