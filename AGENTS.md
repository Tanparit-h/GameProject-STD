# AI Game Studio Agent Instructions

## Project Goal

This project is an AI Office Game Studio prototype.

Architecture:

- LangGraph = main workflow/state/router
- AutoGen = role agents
- Ollama = local LLM backend
- Blender = creator asset generation
- Unity = target game engine, but do not modify Unity project unless explicitly approved

## Current Roles

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

Creates asset spec, image prompt, Blender Python script, and exports mock assets.

Creator output should stay under:

```text
workspace/creator_outputs/
workspace/creator_outputs/exports/
```

Creator must not write into Unity directly.

### Programmer

Creates implementation plan, code draft, pseudo-code, and future Unity setup plan.

In PROTOTYPE_PLAN phase:

- Do not modify the real Unity project
- Do not write C# files into Unity Assets yet
- Code draft is allowed
- Unity setup steps must be conceptual/mock
- Programmer draft files should be generated into `workspace/programmer_outputs/`

### QA

Checks Creator or Programmer output against Designer QA targets.

QA must respond in Thai only.

If Blender run result contains `Traceback`, `Error`, `Exception`, `KeyError`, `AttributeError`, `TypeError`, or no exported files, QA must mark it as fail.

## Current Phase

```text
PROTOTYPE_PLAN
```

Meaning:

- Creator may generate Blender script and export mock asset to workspace
- Programmer may generate code draft/pseudo-code into workspace
- No Unity project modification yet
- No real import into Unity yet

## Safety Rules

- Do not modify Unity project directly unless task explicitly says IMPLEMENTATION phase.
- Do not write outside project root.
- Do not delete files.
- Do not commit or push.
- Prefer patch/draft/report first.
- If unsure, ask for approval.

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
```

## Commands

Run main workflow:

```powershell
python -m app.main_graph
```

Check Blender log:

```powershell
notepad workspace\logs\blender_creator_run.log
```

Check creator exports:

```powershell
dir workspace\creator_outputs\exports
```

Check programmer outputs:

```powershell
dir workspace\programmer_outputs
```

## Current Known Stable Point

Creator Blender export is now working and `.glb` placeholder assets can be generated.

## Current Next Goal

Move Programmer output from report-only to real draft files under:

```text
workspace/programmer_outputs/
```

Do not write to Unity project yet.
