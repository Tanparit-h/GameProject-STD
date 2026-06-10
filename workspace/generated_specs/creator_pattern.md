# AI Office v2 Creator Pattern

## Codex Order

Update Terra Mage first scene setup and validation for the real Unity project so weapon wheel and weapon-based combat can be verified in scene. Include a demo loadout with fewer than 10 active entries so dynamic wheel segmentation can be checked. Validate that slot 0 is bare hands, active wheel segments expand to fill the full circle based on actual assigned item count, Tab opens the weapon wheel, and selected weapons change melee/range behavior in the Terra Mage scene.

## Metadata

- task_id: terra-mage-weapon-wheel-scene-validation-v008
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
