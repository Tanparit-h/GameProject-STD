# Codex Task

## Goal

Move the pipeline to the next production-safe step.

Creator Blender export now works and the `.glb` placeholder asset is generated successfully.

Next step: make Programmer output real draft files into `workspace/programmer_outputs/`, while still staying in `PROTOTYPE_PLAN`.

## Current Phase

```text
PROTOTYPE_PLAN
```

Rules:

- Do not modify the Unity project yet.
- Do not write into `game_project/MyUnityGame/Assets`.
- Do not apply C# files into Unity.
- Do not commit or push.
- All generated programmer files must stay inside:

```text
workspace/programmer_outputs/
```

## Task

Add Programmer file output support.

### Required behavior

Create a new tool:

```text
tools/programmer_file_tool.py
```

It should provide:

```python
write_programmer_file(filename: str, content: str) -> str
read_programmer_file(filename: str) -> str
ensure_programmer_output_dir() -> Path
```

Safety requirements:

- Only allow writing inside `workspace/programmer_outputs/`
- Block path traversal like `../../`
- Create output directory if missing
- Use UTF-8

## Update LangGraph

Update `app/state.py` to include:

```python
programmer_output_files: list[str]
```

Update `app/main_graph.py` so after `programmer_node` generates `programmer_output`, it writes one or more files into `workspace/programmer_outputs/`.

For the first version, generate these files deterministically from the Programmer output:

```text
workspace/programmer_outputs/InteractSystem_Draft.cs
workspace/programmer_outputs/InteractableObject_Draft.cs
workspace/programmer_outputs/Programmer_Implementation_Plan.md
```

These files are drafts only.

## Draft file content

### InteractSystem_Draft.cs

Must contain a PROTOTYPE_PLAN-safe draft.

Requirements:

- Use `InteractableObject` as the main interactable model
- Include `MockedPlayer`
- Include `MockedPosition`
- Include `MockedUIFeedback`
- Handle no object in range
- Handle multiple objects by selecting closest object
- Do not require real Unity project integration
- Add clear comment that this is a draft and not applied to Unity yet

### InteractableObject_Draft.cs

Requirements:

- Define an interactable object model
- Include name/display name
- Include mocked position
- Include visual asset reference name
- Include `OnInteract(MockedUIFeedback feedback)`
- Do not depend on real Blender component generation
- Explain that Blender `.glb` is visual asset reference only

### Programmer_Implementation_Plan.md

Requirements:

- Summarize implementation target
- List draft files generated
- Explain how Blender `.glb` is used as visual asset reference only
- Explain that `InteractableObject` is a code-side model/component concept
- Include validation checklist
- Include next step for future IMPLEMENTATION phase

## Update QA

Update Programmer QA prompt or QA task so it checks:

- Programmer draft files exist
- Draft files are inside `workspace/programmer_outputs/`
- Draft files do not modify Unity project
- Draft files include no-object-in-range handling
- Draft files include closest-object priority handling
- Draft files include mock UI feedback
- Blender asset is referenced as visual asset only, not as a C# component

## Update report

Update `final_node` report to include:

```md
## 6.1 Programmer Output Files

- path 1
- path 2
- path 3
```

## Expected Result

Running:

```powershell
python -m app.main_graph
```

should produce:

```text
workspace/programmer_outputs/InteractSystem_Draft.cs
workspace/programmer_outputs/InteractableObject_Draft.cs
workspace/programmer_outputs/Programmer_Implementation_Plan.md
workspace/reports/latest_report.md
```

No Unity project files should be changed.

## Do Not Do

- Do not write files to Unity `Assets/`
- Do not import GLB into Unity yet
- Do not run Unity validation yet
- Do not commit
