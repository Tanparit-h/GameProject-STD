# Git Strategy for AI Game Studio

## Current Repositories

- Root workflow repo: `D:\AIStudio\ai-game-studio`
- Nested Unity repo: `D:\AIStudio\ai-game-studio\game_project\STDProject`

## Recommended Strategy

Keep `STDProject` as a separate nested repository for now.

Reasons:

- Root repo can evolve LangGraph, AutoGen, prompts, tools, reports, and prototype workspace outputs independently.
- Unity repo can commit engine assets, scenes, packages, and validation changes without mixing generated workflow artifacts.
- The current root `.gitignore` already excludes Unity cache/build folders.
- Converting to a submodule or flattening the repo would require explicit human approval because it changes collaboration and checkout behavior.

## Commit Rules

- Root repo commits:
  - `app/`
  - `autogen_teams/`
  - `prompts/`
  - `tools/`
  - `workspace/` reports, prototype outputs, and draft artifacts
  - project status and next-step documentation

- Unity repo commits:
  - `game_project/STDProject/Assets/`
  - `game_project/STDProject/Packages/`
  - `game_project/STDProject/ProjectSettings/`

- Never commit Unity generated cache/build folders:
  - `Library/`
  - `Temp/`
  - `Logs/`
  - `Obj/`
  - generated `.csproj`, `.sln`, `.slnx`

## Approval-Required Changes

- Flatten `STDProject` into the root repo
- Convert `STDProject` into a submodule
- Delete or rewrite either repository history
- Run an IMPLEMENTATION phase that writes into Unity project files
- Commit nested Unity repo changes from unattended mode

## Current Checkpoint

The unattended workflow should commit root repo automation work only. `game_project/STDProject` remains a separate dirty nested repo and is intentionally not staged from root.
