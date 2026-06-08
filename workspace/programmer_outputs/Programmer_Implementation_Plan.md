# Programmer Implementation Plan

## Phase

PROTOTYPE_PLAN only. These files are drafts under `workspace/programmer_outputs/` and must not be copied into Unity Assets yet.

## Draft Files

- `InteractSystem_Draft.cs`: detects nearby interactables, chooses the closest valid target, shows mock UI feedback, and triggers interaction with `E`.
- `InteractableObject_Draft.cs`: mock interactable component with display name, availability flag, and draft interaction behavior.

## Logic Notes

- No object in range: hide mock UI feedback and ignore `E`.
- Multiple objects in range: select the closest valid object by distance.
- Disabled or unavailable objects: skip them during target selection.
- Blender `.glb` output is visual reference only in this phase.

## Future Unity Setup

- Add final scripts under `Assets/Scripts/AIPrototype/` only after switching to IMPLEMENTATION phase.
- Add imported visual assets under `Assets/AIAssets/` only after explicit approval.
- Add collider/trigger setup to player and interactable prefabs during IMPLEMENTATION validation.

## Validation Plan

- Confirm all draft files exist in `workspace/programmer_outputs/`.
- Review closest-target selection and no-target behavior.
- Review mock UI feedback path.
- Confirm no file was written inside the Unity project.
