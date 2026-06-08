# Next Steps

## Current Status

Creator Blender export is working.

The workflow can now generate `.glb` placeholder assets in:

```text
workspace/creator_outputs/exports/
```

## Next Step A: Programmer Draft Files

Generate programmer draft files into:

```text
workspace/programmer_outputs/
```

Files:

- InteractSystem_Draft.cs
- InteractableObject_Draft.cs
- Programmer_Implementation_Plan.md

No Unity project modification yet.

Status: done.

## Next Step B: QA Checks Programmer Files

QA should check:

- Files exist
- Files are in workspace only
- Logic handles no object in range
- Logic handles multiple objects by closest priority
- Mock UI feedback exists
- Blender asset is treated as visual reference only

Status: done.

## Next Step C: Human Gate

If Programmer QA finds issues:

- Ask user approval
- If rejected, retry Programmer
- If approved, continue

Current QA status: clean pass, no issues found.

Human approval status: approved to continue.

Status: done.

## Next Step D: Future Implementation Phase

After programmer draft files are stable:

- Switch phase to IMPLEMENTATION
- Generate patch for Unity project
- Copy `.glb` into `Assets/AIAssets`
- Copy C# scripts into `Assets/Scripts/AIPrototype`
- Run Unity batchmode validation

Status: current next step, waiting for explicit IMPLEMENTATION phase approval before modifying Unity.

Readiness plan:

```text
workspace/reports/implementation_readiness_plan.md
```
