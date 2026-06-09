# AI Game Studio Office User Manual

## Purpose

AI Game Studio Office coordinates role agents, local asset generation, programmer drafts, Unity implementation, validation, reports, and release gates for game feature work.

## Core Commands

Show current state:

```powershell
.\.venv\Scripts\python.exe -m tools.office status
```

List work orders:

```powershell
.\.venv\Scripts\python.exe -m tools.office tasks
```

Generate dashboard artifacts:

```powershell
.\.venv\Scripts\python.exe -m tools.office dashboard
```

Run release gate:

```powershell
.\.venv\Scripts\python.exe -m tools.office release-gate
```

Draft release notes:

```powershell
.\.venv\Scripts\python.exe -m tools.office release-notes
```

Dry-run a task:

```powershell
.\.venv\Scripts\python.exe -m tools.office task feature-door-toggle-v1
```

Run a task:

```powershell
.\.venv\Scripts\python.exe -m tools.task_runner feature-door-toggle-v1 --run
```

## Workflow Phases

### PROTOTYPE_PLAN

- Allows Creator asset drafts and Programmer draft files.
- Does not apply changes into Unity.
- Unity stage generates a dry-run copy plan and skips validation/setup.

### IMPLEMENTATION

- Applies approved assets/scripts into `game_project/STDProject`.
- Runs Unity batchmode validation.
- Runs scene setup and scene validation.
- Requires clean QA/release evidence before release.

## Work Orders

Work orders live in:

```text
workspace/tasks/
```

Registry:

```text
workspace/tasks/task_registry.json
```

Current statuses:

- `backlog`: task exists but has not been planned yet
- `prototype_planned`: task has completed PROTOTYPE_PLAN
- `release_gate_clean`: task has an implemented vertical slice that passes release gate

## Approval Records

Approval records live in:

```text
workspace/approvals/approval_log.jsonl
```

Each record stores:

- timestamp
- task id
- phase
- decision
- owner
- reason

## Generated Artifacts

Ignored generated files:

- `workspace/reports/index.md`
- `workspace/reports/status.json`
- `workspace/reports/release_notes.md`
- `workspace/dashboard/index.html`

Tracked reports:

- `workspace/reports/latest_report.md`
- `workspace/reports/production_readiness_checklist.md`
- `workspace/reports/current_capability_matrix.md`
- `workspace/reports/product_backlog.md`

## Release Gate

The release gate checks:

- root git clean
- Unity submodule git clean
- root unit tests
- Creator `.glb` export validation
- task registry validation
- Unity batchmode validation
- Unity scene validation
- latest report markers
- dashboard status

## Current User-Level Decisions

- Push/PR/release requires explicit user approval.
- Choosing the next Unity implementation feature requires product direction.
- Building a richer UI beyond generated static HTML requires product direction.
