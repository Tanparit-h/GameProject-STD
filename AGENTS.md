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

## Runtime Roles

The active Office graph has only these runtime roles:

```text
Creator -> Programmer -> Unity
```

Codex receives the user order, writes role-specific script patterns under:

```text
workspace/generated_specs/
```

Those patterns replace the old Manager/Designer routing layer. Each active role performs its own reviewer pass before handing off to the next role. Codex reviews code, diffs, logs, and gameplay logic after Unity completes.

### Creator

Reads the Codex Creator pattern, creates asset spec, image prompt, Blender Python script, and exports assets when needed.

Creator output should stay under:

```text
workspace/creator_outputs/
workspace/creator_outputs/exports/
```

Creator must not write into Unity directly.

Creator must self-review:

- Blender script stays under `workspace/creator_outputs/`.
- Exports stay under `workspace/creator_outputs/exports/`.
- Blender/error evidence is deterministic.

### Programmer

Reads the Codex Programmer pattern, then creates real implementation files, setup/validation support files, and implementation reports under:

```text
workspace/programmer_outputs/
```

Programmer should not emit draft-only placeholders when the task requests real implementation.

Programmer must self-review:

- Output files stay under `workspace/programmer_outputs/`.
- Required deterministic family/spec files exist.
- Implementation is not draft-only when phase is `IMPLEMENTATION`.

### Unity

Applies approved Creator/Programmer outputs into `game_project\STDProject`, then runs batchmode validation, scene setup, and scene validation.

Unity must self-review:

- Copy plan only touches allowed Unity `Assets/` targets.
- Unity cache folders are never written by Office.
- Batchmode and scene validation evidence is captured in `workspace/logs/`.

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
