# AI Game Studio Agent Instructions

## Project Goal

This project is an AI Office-style game production workflow that performs real work.

Architecture:

- LangGraph = workflow/state/router
- AutoGen = role agents
- Ollama = local LLM backend
- Blender = creator asset generation
- Unity = target game engine

## Current Operating Mode

Current phase:

```text
IMPLEMENTATION
```

Meaning:

- Creator may generate runnable Blender scripts and export real placeholder assets.
- Programmer must generate real implementation outputs under `workspace/programmer_outputs/`.
- Approved outputs may be copied into the Unity project.
- Unity batchmode validation, scene setup, and scene validation are part of the normal workflow.
- QA decisions must be based on real files, logs, and deterministic evidence.

## Roles

### Manager

Receives user input, analyzes goals/requirements/constraints, and prepares input for Designer.

### Designer

Analyzes Manager output and creates:

- Routing decision
- Creator task
- Programmer task
- Creator QA target
- Programmer QA target
- Acceptance criteria
- Edge cases
- Out of scope

Designer must always include:

```text
0. Routing decision
- Creator required: yes/no
- Programmer required: yes/no
- Reason: ...
```

### Creator

Creates asset spec, image prompt, Blender Python script, and exports assets.

Creator output should stay under:

```text
workspace/creator_outputs/
workspace/creator_outputs/exports/
```

Creator must not write into Unity directly.

### Programmer

Creates real implementation files, setup/validation support files, and implementation reports under:

```text
workspace/programmer_outputs/
```

Programmer should not emit draft-only placeholders when the task requests real implementation.

### QA

Checks Creator, Programmer, or Unity output against evidence and Designer QA targets.

QA must respond in Thai only.

If Blender run result contains `Traceback`, `Error`, `Exception`, `KeyError`, `AttributeError`, `TypeError`, or no exported files, QA must mark it as fail.

## Safety Rules

- Do not write outside project root.
- Do not delete arbitrary project content unrelated to the task.
- Do not commit or push unless explicitly requested.
- Keep root repo and Unity repo history intentional and separate.
- Prefer deterministic validation over role-text claims.

## Important Paths

```text
D:\AIStudio\ai-game-studio
D:\AIStudio\ai-game-studio\app
D:\AIStudio\ai-game-studio\prompts
D:\AIStudio\ai-game-studio\autogen_teams
D:\AIStudio\ai-game-studio\tools
D:\AIStudio\ai-game-studio\workspace
D:\AIStudio\ai-game-studio\workspace\creator_outputs
D:\AIStudio\ai-game-studio\workspace\creator_outputs\exports
D:\AIStudio\ai-game-studio\workspace\programmer_outputs
D:\AIStudio\ai-game-studio\workspace\reports\latest_report.md
D:\AIStudio\ai-game-studio\game_project\STDProject
```

## Commands

Run main workflow:

```powershell
python -m app.main_graph
```

Run a task through Office:

```powershell
.\.venv\Scripts\python.exe -m tools.office task feature-interaction-v1 --run --response-only
```

Check creator exports:

```powershell
dir workspace\creator_outputs\exports
```

Check programmer outputs:

```powershell
dir workspace\programmer_outputs
```

## Current Goal

Keep the Office workflow implementation-first, evidence-driven, and reusable across real Unity game features.
