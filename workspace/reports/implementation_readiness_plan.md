# Implementation Readiness Plan

## Phase

PROTOTYPE_PLAN

## Purpose

This document prepares the future `IMPLEMENTATION` phase without modifying the Unity project yet.

## Approved Inputs

- Creator visual reference asset: `workspace/creator_outputs/exports/interactive_objects.glb`
- Programmer draft script: `workspace/programmer_outputs/InteractSystem_Draft.cs`
- Programmer draft script: `workspace/programmer_outputs/InteractableObject_Draft.cs`
- Programmer plan: `workspace/programmer_outputs/Programmer_Implementation_Plan.md`
- Programmer QA report: `workspace/reports/programmer_qa_report.md`
- Human Gate report: `workspace/reports/human_gate_approval.md`

## Future Unity Target Paths

These paths are proposed for the future `IMPLEMENTATION` phase only:

- `game_project/Assets/AIAssets/interactive_objects.glb`
- `game_project/Assets/Scripts/AIPrototype/InteractSystem.cs`
- `game_project/Assets/Scripts/AIPrototype/InteractableObject.cs`

## Proposed Implementation Patch Steps

1. Switch project phase from `PROTOTYPE_PLAN` to `IMPLEMENTATION` after explicit user approval.
2. Create Unity asset folder `Assets/AIAssets`.
3. Copy approved `.glb` visual reference into `Assets/AIAssets`.
4. Create Unity script folder `Assets/Scripts/AIPrototype`.
5. Convert draft scripts to implementation script names without `_Draft`.
6. Add final script comments noting provenance from AI Studio prototype drafts.
7. Keep scene/prefab wiring as a manual or separately approved step unless a specific Unity scene is selected.
8. Run Unity batchmode validation only after Unity executable/project path is confirmed.

## Validation Checklist For Implementation Phase

- Unity project opens without compile errors.
- `InteractSystem.cs` compiles in Unity.
- `InteractableObject.cs` compiles in Unity.
- Imported `.glb` appears under `Assets/AIAssets`.
- No ProjectSettings changes occur unless explicitly approved.
- No scene or prefab is modified unless explicitly approved.

## Current Boundary

Do not execute this plan yet. This is a readiness document only.
