# AI Office v2 Creator Pattern

## Codex Order

Implement a weapon wheel for the real Terra Mage Unity project. Open the wheel when holding Tab. Maximum total slots is 10. Slot 0 must always be locked to bare hands and bare hands must be able to punch. The player must be able to assign weapons into the remaining wheel slots. If the wheel has fewer than 10 assigned entries, do not leave empty arc gaps. Instead, divide the full circle evenly across only the active assigned entries. Example: bare hands only plus 1 assigned weapon = 2 equal left/right halves. Bare hands plus 2 assigned weapons = 3 equal segments. Continue scaling this way up to 10 total active slots. Integrate this as real implementation, not prototype only.

## Metadata

- task_id: terra-mage-weapon-wheel-v006
- task_family: terra_mage_weapon_family
- phase: IMPLEMENTATION

## Runtime Contract

- Active roles only: Creator, Programmer, Unity.
- Codex creates this pattern before generation.
- Creator generates only files inside its workspace output folder.
- Creator runs a self-reviewer pass before the next stage.
- Codex performs the final code/evidence review after Unity finishes.

## Reviewer Checklist

- Inputs are explicit and traceable to the Codex order.
- Creator output stays inside the allowed workspace path.
- Output is implementation-ready when phase is IMPLEMENTATION.
- Risks, skipped steps, and required user approvals are stated.
