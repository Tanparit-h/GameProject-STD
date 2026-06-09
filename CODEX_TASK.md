# Codex Task

## Current Goal

Keep the AI Office workflow implementation-first so it can create, validate, and hand off real Unity game features.

## Current Status

The workflow can:

- Run Manager, Designer, Creator, Programmer, QA, and Unity stages.
- Generate real files under `workspace/programmer_outputs/`.
- Copy approved assets/scripts into `game_project/STDProject`.
- Run Unity batchmode validation.
- Run task-specific scene setup and scene validation.
- Produce `workspace/reports/latest_report.md` and `workspace/reports/codex_response.md`.
- Validate gates from deterministic evidence instead of report-only QA claims.

## Validation

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -p "test_*.py"
.\.venv\Scripts\python.exe -m tools.release_gate
```
