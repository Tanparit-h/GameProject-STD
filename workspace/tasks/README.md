# AI Office Task Queue

Task files describe work orders for the role workflow.

## Format

Use JSON for now so the workflow can parse tasks with the Python standard library.

```json
{
  "id": "feature-interaction-v1",
  "phase": "PROTOTYPE_PLAN",
  "title": "Player interaction prototype",
  "request": "Create a prototype where the player presses E to interact with nearby objects.",
  "approval": {
    "implementation": false
  }
}
```

## Run A Task

```powershell
$env:AI_STUDIO_TASK_FILE='workspace/tasks/interaction_vertical_slice.json'
.\.venv\Scripts\python.exe -m app.main_graph
```

`AI_STUDIO_PHASE` and `AI_STUDIO_FEATURE_REQUEST` still work as overrides when no task file is provided.

## Registry

Tasks are listed in:

```text
workspace/tasks/task_registry.json
```

Validate the registry:

```powershell
.\.venv\Scripts\python.exe -m tools.task_registry
```

## Approval Records

Approval decisions are recorded as JSON Lines:

```text
workspace/approvals/approval_log.jsonl
```

Each record includes timestamp, task id, phase, decision, owner, and reason.
