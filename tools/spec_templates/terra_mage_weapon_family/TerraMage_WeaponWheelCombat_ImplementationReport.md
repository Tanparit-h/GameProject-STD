# Terra Mage Weapon Wheel Combat - Implementation Report

## Goal

Extend Terra Mage with a weapon wheel that keeps Bare Hands locked in slot 0 and switches to a demo ranged weapon, then drive melee or ranged combat from the selected loadout entry.

## Implemented Programmer Outputs

- `TerraMageTinyMageController.cs`
- `TerraMageFollowCamera.cs`
- `TerraMageAimSystem.cs`
- `TerraMageAimTarget.cs`
- `TerraMageAimTargetMotion.cs`
- `TerraMageAimTargetVisibility.cs`
- `TerraMageMaterialSystem.cs`
- `TerraMagePlayerMechanics.cs`
- `TerraMageDamageable.cs`
- `TerraMageProjectile.cs`
- `TerraMageMeleeGestureController.cs`
- `TerraMageActionBuildController.cs`
- `TerraMageWeaponDefinition.cs`
- `TerraMageWeaponLoadout.cs`
- `TerraMageWeaponWheelUI.cs`
- `TerraMageFirstSceneSetup.cs`
- `TerraMageFirstSceneValidator.cs`

## Weapon Wheel Rules

- Hold `Tab` to open the weapon wheel.
- Slot 0 is locked to `Bare Hands`.
- Slot 1 is the `Shard Sling` ranged weapon.
- Only active assigned entries render on the wheel.
- Segment coverage always fills the full circle with no empty gaps.
- Bare hands plus one assigned weapon divide the wheel into 2 equal halves.

## Combat Integration

- Bare-hands attacks animate first, then apply damage during the middle of the swing.
- Ranged attacks launch a physical `Shard Sling` projectile from the center crosshair.
- Shared player rules live in global `TerraMagePlayerMechanics` helpers for movement, jump delay, parkour ledge grabs, melee, and ranged projectile reuse.
- Aim targets receive `TerraMageDamageable` for health, hit flash, and knockback feedback.
- scene validation checks damageable targets, projectile class availability, and melee/range behavior.

## Validation Target

- Scene: `Assets/Scenes/TerraMage_FirstScene.unity`
- Setup method: `TerraMageFirstSceneSetup.SetupFirstScene`
- Validation method: `TerraMageFirstSceneValidator.ValidateFirstScene`
