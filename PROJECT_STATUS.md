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
- Programmer draft files passed QA for `PROTOTYPE_PLAN`
- Human Gate approved continuing after Programmer QA
- Unity automation tool module added for project validation, dry-run copy planning, batchmode execution, and log parsing
- Unity implementation stage added to LangGraph with safe `PROTOTYPE_PLAN` skips
- Human approval gates no longer block unattended workflow runs; failed QA retries automatically up to retry limit
- Programmer draft file QA now has deterministic file/path/logic checks in addition to LLM QA

## Current Goal

Next step is preparing the workflow for an explicit IMPLEMENTATION phase run after human approval.

The graph now creates a dry-run Unity copy plan in `PROTOTYPE_PLAN` and skips real Unity modification, batchmode validation, scene setup, and scene validation.

## Desired Files

Expected programmer draft output files:

```text
workspace/programmer_outputs/InteractSystem_Draft.cs
workspace/programmer_outputs/InteractableObject_Draft.cs
workspace/programmer_outputs/Programmer_Implementation_Plan.md
```

Current programmer draft files have been generated in `workspace/programmer_outputs/`.

Programmer QA report:

```text
workspace/reports/programmer_qa_report.md
```

Human Gate approval report:

```text
workspace/reports/human_gate_approval.md
```

Implementation readiness plan:

```text
workspace/reports/implementation_readiness_plan.md
```

Implementation patch preview package:

```text
workspace/patches/IMPLEMENTATION_PATCH_PLAN.md
workspace/patches/InteractSystem_IMPLEMENTATION_PREVIEW.cs
workspace/patches/InteractableObject_IMPLEMENTATION_PREVIEW.cs
```

Implementation test report:

```text
workspace/reports/implementation_test_report.md
```

Real Unity project marker:

```text
workspace/reports/REAL_UNITY_PROJECT.md
```

STDProject implementation test report:

```text
workspace/reports/stdproject_implementation_test_report.md
```

Unity cache fix report:

```text
workspace/reports/unity_cache_fix_report.md
```

Unity 6000.4 validation report:

```text
workspace/reports/stdproject_6000_4_validation_report.md
```

## Current Phase

```text
PROTOTYPE_PLAN
```

## Do Not Do Yet

- Do not modify scenes or prefabs automatically
- Do not modify ProjectSettings
- Do not commit/push
- Do not claim Unity batchmode validation until a complete Unity project skeleton exists
- Use `game_project/STDProject` as the real Unity project target for future implementation work
- Do not commit Unity cache folders such as `Library/`, `Temp/`, `Logs/`, or generated solution/project files

## Latest Validation

- Unity version updated to `6000.4.9f1`
- Implementation compile validation passed
- Full UPM validation passed
- Full Unity batchmode validation passed with return code 0
- `SampleScene` wiring completed for AIPrototype objects
- Post-scene Unity batchmode validation passed with return code 0
- Automated `SampleScene` validation passed with return code 0

## Remaining Workflow Gap

Unity implementation is now represented as a reusable graph stage, but real apply/scene setup remains gated by phase and approval.

Need to add:

- Git strategy for root repo versus nested `STDProject`
- Expand Unity workflow tests beyond the current standard-library unit tests
- IMPLEMENTATION phase approval path and commit strategy
- Git strategy is documented at `workspace/reports/git_strategy.md`; root and nested Unity commits remain separate

## Latest Automation Checkpoint

Checkpoint date: 2026-06-09

- `python -m app.main_graph` was run through `.venv`
- Creator QA failed once due to generated Blender script, then unattended retry passed
- Programmer QA passed with deterministic file checks
- Unity stage generated a dry-run copy plan only
- Unity validation, scene setup, and scene validation were skipped because current phase is `PROTOTYPE_PLAN`
- No Unity project files were written by the workflow during this checkpoint
