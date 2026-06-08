# Codex Task

## Current Goal

Continue turning the AI Game Studio prototype into an AI Office-style game production workflow.

## Current Status

The first Unity vertical slice is release-gate clean.

The workflow can:

- Run Manager, Designer, Creator, Programmer, QA, and Unity implementation stages.
- Generate Blender placeholder `.glb` assets.
- Generate Programmer draft files under `workspace/programmer_outputs/`.
- Apply approved assets/scripts into `game_project/STDProject`.
- Run Unity batchmode validation.
- Run Unity scene setup.
- Run Unity scene validation.
- Produce `workspace/reports/latest_report.md`.
- Pass `tools.release_gate` from a clean root repo and clean Unity submodule.

## Next Productization Targets

1. Build a dashboard/report index for tasks, reports, git state, and release status.
2. Expand task/work-order queue support beyond the first vertical slice.
3. Add approval records with owner, timestamp, decision, and reason.
4. Add deterministic Creator asset validation.
5. Add multi-feature regression tests.
6. Add push/PR/release packaging only when explicitly approved.

## Safety Rules

- Keep root repo and `game_project/STDProject` submodule commits separate.
- Do not commit Unity cache folders.
- Do not rewrite git history.
- Preserve release-gate clean status after each checkpoint.
- If a step requires product direction, branding, UI approval, or push credentials, stop and record the blocker.

## Validation

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -p "test_*.py"
.\.venv\Scripts\python.exe -m tools.release_gate
```
