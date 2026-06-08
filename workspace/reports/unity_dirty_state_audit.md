# Unity Dirty State Audit

## Scope

Repository:

```text
D:\AIStudio\ai-game-studio\game_project\STDProject
```

This audit records uncommitted Unity changes that remain outside the AI prototype implementation commits.

## Dirty Change Groups

### Package and Unity Version Updates

Files:

- `Packages/manifest.json`
- `Packages/packages-lock.json`
- `ProjectSettings/ProjectVersion.txt`

Observed changes include package upgrades such as:

- `com.unity.ai.navigation` 2.0.10 -> 2.0.12
- `com.unity.collab-proxy` 2.11.3 -> 2.12.4
- `com.unity.ide.rider` 3.0.39 -> 3.0.40
- `com.unity.ide.visualstudio` 2.0.26 -> 2.0.27
- `com.unity.inputsystem` 1.18.0 -> 1.19.0
- `com.unity.render-pipelines.universal` 17.3.0 -> 17.4.0
- `com.unity.timeline` 1.8.10 -> 1.8.12
- `com.unity.visualscripting` 1.9.9 -> 1.9.11

Recommendation:

- Treat this as a separate Unity upgrade/change-management decision.
- Commit only after reviewing package compatibility and confirming this is intended.

### Project and Render Pipeline Settings

Files:

- `Assets/Settings/Mobile_RPAsset.asset`
- `Assets/Settings/PC_RPAsset.asset`
- `Assets/Settings/UniversalRenderPipelineGlobalSettings.asset`
- `ProjectSettings/EditorBuildSettings.asset`
- `ProjectSettings/ProjectSettings.asset`
- `ProjectSettings/ShaderGraphSettings.asset`
- `ProjectSettings/URPProjectSettings.asset`
- `ProjectSettings/SceneTemplateSettings.json`

Recommendation:

- Review in Unity Editor before committing.
- Keep separate from AI prototype implementation commits.

### Tutorial/Readme Asset Cleanup

Deleted files:

- `Assets/Readme.asset`
- `Assets/Readme.asset.meta`
- `Assets/TutorialInfo/**`

Recommendation:

- Commit as a deliberate sample cleanup if wanted.
- Otherwise restore these files before release.

## Current Implementation Commits

AI prototype implementation was already committed separately in the Unity submodule:

- `95421bb Apply AI prototype implementation assets`
- `acb0e1a Refresh implementation validation artifacts`

Root repo points to the latest implementation submodule commit.

## Release Guidance

Do not push or tag a production release while these dirty Unity changes remain unresolved. Choose one:

- Commit them as intentional Unity upgrade/sample cleanup work.
- Restore them if they are accidental editor/package churn.
- Split them into separate reviewed commits.
