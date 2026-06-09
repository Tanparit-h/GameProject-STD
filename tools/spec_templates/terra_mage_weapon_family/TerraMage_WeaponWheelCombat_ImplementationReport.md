# Terra Mage Weapon Wheel Combat - Implementation Report

## Goal

Extend Terra Mage with a weapon wheel that keeps slot 0 locked to bare hands, then drive melee or ranged combat from the selected weapon.

## Implemented Programmer Outputs

- `TerraMageTinyMageController.cs`
- `TerraMageFollowCamera.cs`
- `TerraMageAimSystem.cs`
- `TerraMageAimTarget.cs`
- `TerraMageAimTargetMotion.cs`
- `TerraMageAimTargetVisibility.cs`
- `TerraMageMaterialSystem.cs`
- `TerraMageMeleeGestureController.cs`
- `TerraMageActionBuildController.cs`
- `TerraMageWeaponDefinition.cs`
- `TerraMageWeaponLoadout.cs`
- `TerraMageWeaponWheelUI.cs`
- `TerraMageFirstSceneSetup.cs`
- `TerraMageFirstSceneValidator.cs`

## Weapon Wheel Rules

- Hold `Tab` to open the weapon wheel.
- Slot 0 stays locked to `Bare Hands`.
- Only active assigned entries render on the wheel.
- Segment coverage always fills the full circle with no empty gaps.
- Two active entries divide the wheel into 2 equal halves.
- Three active entries divide the wheel into 3 equal segments.

## Combat Integration

- `Bare Hands` uses an unarmed punch profile.
- Melee weapons change melee reach and gesture profile.
- Ranged weapons switch the primary action to ranged material attacks.
- scene validation checks that weapon selection changes melee/range behavior.

## Validation Target

- Scene: `Assets/Scenes/TerraMage_FirstScene.unity`
- Setup method: `TerraMageFirstSceneSetup.SetupFirstScene`
- Validation method: `TerraMageFirstSceneValidator.ValidateFirstScene`
