# Project Status

## Current Working Stack

- Python venv is active under `.venv`
- LangGraph workflow runs from `app/main_graph.py`
- AutoGen role runner is in `autogen_teams/role_runner.py`
- Ollama model is used locally
- Current model: qwen3:14b
- Blender run tool exists in `tools/blender_tool.py`
- Creator file tool exists in `tools/creator_file_tool.py`

## Completed

- Ollama model test passed
- AutoGen single-agent test passed
- AutoGen multi-agent test passed
- LangGraph mock passed
- Role-based graph works
- Manager, Designer, Creator, Programmer, QA roles exist
- QA output changed to Thai
- User gate exists
- Retry loop exists
- Designer routing can skip Creator when Creator is not required
- Creator can write Blender script to workspace
- Blender can be called from workflow
- Creator Blender export now works
- `.glb` placeholder asset export has been tested and passed
- Programmer draft file output now writes files into `workspace/programmer_outputs/`

## Current Goal

Next step is QA checking Programmer draft files.

Programmer should write draft files into:

```text
workspace/programmer_outputs/
```

No Unity project modifications yet.

## Desired Files

Expected programmer draft output files:

```text
workspace/programmer_outputs/InteractSystem_Draft.cs
workspace/programmer_outputs/InteractableObject_Draft.cs
workspace/programmer_outputs/Programmer_Implementation_Plan.md
```

Current programmer draft files have been generated in `workspace/programmer_outputs/`.

## Current Phase

```text
PROTOTYPE_PLAN
```

## Do Not Do Yet

- Do not import GLB into Unity automatically
- Do not write C# files into Unity project
- Do not modify ProjectSettings
- Do not commit/push
- Do not run Unity validation yet
