# Codex Handoff Package

Workspace:

```text
D:\AIStudio\ai-game-studio
```

Read first:

```text
AGENTS.md
PROJECT_STATUS.md
NEXT_STEPS.md
CODEX_TASK.md
workspace/reports/index.md
workspace/reports/latest_report.md
workspace/reports/codex_response.md
```

Recommended validation:

```powershell
cd D:\AIStudio\ai-game-studio
.\.venv\Scripts\python.exe -m unittest discover -p "test_*.py"
.\.venv\Scripts\python.exe -m tools.release_gate
```

Office CLI:

```powershell
.\.venv\Scripts\python.exe -m tools.office status
.\.venv\Scripts\python.exe -m tools.office dashboard
.\.venv\Scripts\python.exe -m tools.office release-gate
.\.venv\Scripts\python.exe -m tools.office tasks
.\.venv\Scripts\python.exe -m tools.office task feature-interaction-v1
```

Useful workflow commands:

```powershell
$env:AI_STUDIO_PHASE='IMPLEMENTATION'
.\.venv\Scripts\python.exe -m app.main_graph

$env:AI_STUDIO_TASK_FILE='workspace/tasks/interaction_vertical_slice.json'
.\.venv\Scripts\python.exe -m app.main_graph
```
