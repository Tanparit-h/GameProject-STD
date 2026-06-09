# Current Capability Matrix

## Summary

The AI Game Studio is release-gate clean for one implemented Unity vertical slice and has a growing AI Office control surface through CLI, reports, task registry, approval records, and generated dashboard artifacts.

## Capabilities

| Capability | Status | Evidence |
| --- | --- | --- |
| Role workflow | Working | `app/main_graph.py`, `workspace/reports/latest_report.md` |
| Local LLM role execution | Working | `autogen_teams/role_runner.py`, smoke scripts |
| Creator Blender export | Working | `tools/blender_tool.py`, `workspace/creator_outputs/exports/*.glb` |
| Programmer draft files | Working | `workspace/programmer_outputs/*.cs`, implementation plan |
| Unity implementation stage | Working | `tools/unity_tool.py`, release gate |
| Unity scene validation | Working | `AIPrototypeSceneValidator.ValidateSampleScene`, release gate |
| Deterministic QA guards | Partial | Programmer, Unity, Creator export, task registry |
| Task registry | Working | `workspace/tasks/task_registry.json` |
| Task runner | Working | `tools/task_runner.py` |
| Approval records | Working | `workspace/approvals/approval_log.jsonl` |
| Office CLI | Working | `tools/office.py` |
| Dashboard | Partial | Static generated HTML through `tools/dashboard.py` |
| Release gate | Working | `tools/release_gate.py` |
| Multi-feature implementation | Partial | One implemented feature, one planned prototype, three backlog archetypes |
| Push/PR/release | Blocked | Requires explicit user approval and remote decision |

## Current User-Level Decisions

- Whether to push root and Unity submodule commits.
- Whether to implement the next backlog feature into Unity.
- Whether the dashboard should become a real web app, desktop UI, or stay static.
- Which feature archetype should become the next vertical slice.

## Recommended Next Human Decision

Choose one:

1. Push/PR/release the current clean vertical slice.
2. Implement `feature-door-toggle-v1` into Unity.
3. Build a real dashboard UI around the existing office CLI/report data.
4. Add another game feature archetype to the backlog.
