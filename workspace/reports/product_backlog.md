# AI Office Product Backlog

## Current Product Slice

The current system is a release-gate-clean AI Game Studio prototype with:

- Role workflow through Manager, Designer, Creator, Programmer, QA, and Unity stages
- Task registry and task runner
- Approval log
- Static dashboard generator
- Release gate
- One implemented Unity vertical slice
- One planned backlog feature

## Product Backlog

### P0: Human-Facing Office UI

Goal:

- Replace command-only operation with a usable dashboard for tasks, approvals, artifacts, reports, and release state.

Acceptance criteria:

- Shows task registry with status, phase, title, and latest report.
- Shows release gate result.
- Shows approval records.
- Provides commands or buttons for dry-run, prototype plan, implementation run, and dashboard refresh.

Current support:

- Office CLI and generated static dashboard exist.
- User manual exists at `workspace/reports/office_user_manual.md`.

### P0: Multi-Feature Regression

Goal:

- Validate more than one feature archetype without breaking the existing vertical slice.

Acceptance criteria:

- At least five registered feature archetypes.
- Each has a task file and deterministic validation expectations.
- Release gate validates registry consistency.

### P1: Approval UX

Goal:

- Make approval decisions explicit and reviewable.

Acceptance criteria:

- Approval record includes task id, phase, owner, decision, reason, and timestamp.
- UI or CLI can list approvals.
- Implementation runs require an approval record or an explicit implementation task phase.

### P1: Creator Determinism

Goal:

- Reduce variance from generated Blender scripts/assets.

Acceptance criteria:

- Creator validation checks expected asset filenames.
- Creator validation checks minimum file sizes.
- Creator validation records Blender log path and error markers.

### P2: Push/PR/Release Packaging

Goal:

- Move clean local checkpoints into a collaborative release path.

Acceptance criteria:

- Requires explicit user approval.
- Pushes root and Unity submodule commits in the correct order.
- Creates PR or release notes with validation evidence.
