# Project Status

## Current Working Stack

- Python venv under `.venv`
- LangGraph workflow in `app/main_graph.py`
- AutoGen role runner in `autogen_teams/role_runner.py`
- Ollama local model backend
- Blender creator tooling in `tools/blender_tool.py`
- Unity automation in `tools/unity_tool.py`

## Current Capability

- Manager, Designer, Creator, Programmer, QA, and Unity stages are wired.
- Task-aware programmer output specs can generate real implementation files.
- Deterministic evidence gates verify Creator, Programmer, and Unity stages.
- Office can write `workspace/reports/latest_report.md` and `workspace/reports/codex_response.md`.
- Release gate checks repo cleanliness, tests, registry validity, Unity validation, and report health.

## Current Mode

```text
IMPLEMENTATION
```

## Focus

Keep removing generic fallback behavior so Office stays reliable on real game-feature work instead of drifting back to report-only output.
