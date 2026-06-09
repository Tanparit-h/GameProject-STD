# Sand Mage TD - Game Structure And Production Roadmap

Source concept: `D:\Planing\Sand_Mage_TD_Backup_Roadmap.md`

## Product Definition

Sand Mage TD is a third-person multiplayer tower-defense and base-building game with a Minecraft-like sandbox/building feel. The player is not a full-size hero: they are a tiny mage, roughly 30 cm tall, moving through a world that feels huge, tactile, and physically buildable.

The world is generated from a seed system. Each seed creates a playable sandbox with terrain, resources, hazards, enemy approaches, and base-building opportunities. The core fantasy is physical: the tiny mage walks inside the generated world, lifts sand with magic, compresses it into structures, builds defenses, and survives enemy waves with friends or async invasion data.

## Core Game Structure

### 1. Player Layer

Goal: make the player feel like a tiny mage-builder inside a dangerous generated world.

Scale identity:

- Player height target: about 30 cm.
- The world should feel large and chunky, similar to the sense of scale in a Minecraft-like sandbox.
- Sand piles, rocks, cliffs, plants, and waves should feel oversized from the mage's perspective.
- Building should feel like physically shaping the environment, not placing abstract UI-only tiles.

Primary features:

- Third-person movement.
- Follow camera and over-the-shoulder aim.
- Reticle-based interact raycast.
- Magic tool controller.
- Gesture-based melee action.
- Weapon wheel for switching melee range and equipped tool style.
- Spell/tool wheel.
- Build-mode camera adjustment.
- Tactical overview mode.

Melee action controls:

- Mouse drag left: left swing.
- Mouse drag right: right swing.
- Mouse drag upward or forward: overhead strike.
- Weapon wheel changes melee range profile, such as short staff, medium pole, long reach, or heavy overhead tool.
- Melee attacks should share the same physics language as building: impact direction, hit mass, weapon reach, and material contact all matter.

Character creation and art style:

- Simple chunky cartoon characters.
- Readable class identity from silhouette first, detail second.
- Mage class example: small robed body, cloak shape, simple hood/hat, staff in hand.
- The character should feel toy-like and easy to animate, not realistic.
- Equipment should visually explain function: staff for magic, hammer/tool for compression, blade/pole for melee reach.

First playable target:

- Walk, jump, sprint, aim, interact.
- Lift sand/material.
- Place material.
- Compress material into a stable packed block.

### 2. Material Simulation Layer

Goal: make sand/material manipulation the signature mechanic.

Initial materials:

- Empty.
- DrySand.
- WetSand.
- PackedSand.
- Stone.
- Water.
- Glass.

Later materials:

- ReinforcedSand.
- GlueSand.
- CutStone.
- Wood.
- Core.

Simulation rules:

- Dry sand falls and flows.
- Wet sand is heavier and slightly sticky.
- Packed sand becomes a stable build block.
- Stone is durable and useful for walls/projectiles.
- Water flows through channels and erodes weak sand.
- Glass is fragile but enables lens/beam tech.

MVP constraint:

- Prefer a small deterministic grid simulation over full realistic 3D voxel destruction.

### 3. Building Layer

Goal: turn material manipulation into usable defensive architecture.

Features:

- Freeform placement.
- Compression spell.
- Structure validation.
- Quick block save/place.
- Resource cost check.
- Base core placement.
- Walls, gates, ramps, bridges, towers, channels, traps.

First milestone:

- Build a sand wall.
- Compress it.
- Save it as a quick block.
- Place it repeatedly with material cost.

### 4. Action-Build Fusion Layer

Goal: merge combat actions and building actions into one physical material system.

Core idea:

- The player does not only attack with fixed weapons.
- The player pulls, compresses, heats, throws, pours, melts, glues, carves, and redirects world materials.
- The same material can become a wall, projectile, trap, repair patch, molten stream, or tower component depending on the spell/action used.

Primary action verbs:

- Absorb or pull loose material from the world.
- Compress loose material into a dense block or sphere.
- Throw compressed blocks as physics projectiles.
- Swing melee weapons with directional mouse-drag attacks.
- Heat sand until it becomes molten glass material.
- Pour molten material onto enemies, terrain, or structures.
- Cool molten material into glass barriers, spikes, or lens components.
- Glue sand into sticky traps or reinforced patches.
- Push, knock back, or redirect enemies using material force.

Physics damage model:

- Damage depends on mass, velocity, material hardness, heat state, and impact angle.
- A compressed sand sphere can be thrown as a blunt projectile.
- A stone chunk does higher impact damage but is harder to lift.
- Molten sand/glass deals heat damage over time and can leave hazardous ground.
- Wet sand has lower throw damage but can slow or weigh down enemies.
- GlueSand reduces enemy movement and can bind small enemies in place.

Elemental construction model:

- Earth/Sand: pull, place, compress, repair, build walls.
- Heat/Fire: melt sand into glass, create molten pours, weaken glue over time.
- Water: wet sand, channel flow, push enemies, power water traps.
- Wind: lift lighter material, scatter dry sand, alter projectile arcs.
- Stone: carve, reinforce, create heavy projectiles.

MVP action-build examples:

- Pull sand into a floating mass, compress it into a ball, then throw it at a Runner.
- Pull sand into a wall shape, compress it, and use it as base defense.
- Heat lifted sand into molten glass and pour it onto the ground as a temporary hazard.
- Cool molten material into a fragile glass barrier or spike.
- Drag mouse left/right/overhead to strike an enemy or hit a loose block into motion.
- Switch melee range through the weapon wheel before engaging enemies near the base wall.

Design rule:

- Every major action should either create a tactical combat effect, change the buildable world, or both.

### 5. Tower Defense Layer

Goal: make the built base matter under pressure.

Core systems:

- Core health.
- Wave spawner.
- Enemy pathfinding.
- Enemy damage vs structures/core.
- Win/lose result.
- Reward points.
- Weapon/trap activation.

MVP enemies:

- Runner.
- Tank.
- Digger optional.
- Swarm optional.

MVP defenses:

- Player-thrown compressed sand sphere.
- Sand Cannon.
- Glue Trap or Water Cannon.
- Basic wall/maze structure.

### 6. World Generation Layer

Goal: make seeds and biomes create different building problems.

Design feel:

- The world should support Minecraft-like exploration and construction clarity.
- Terrain must be readable, modular, and easy to reason about for building.
- The seed system should make each world feel like a new sandbox challenge.
- The tiny mage scale means normal terrain features become meaningful obstacles and landmarks.

Initial biome:

- Beach with sand, water, sea-wave hazard, and simple resource zones.

Expansion biomes:

- Forest.
- Waterfall.
- Rocky cliff.
- Wetland.
- Desert dunes.

Seed data:

- Seed string.
- Biome.
- Terrain height.
- Water sources.
- Sand regions.
- Stone regions.
- Forest regions.
- Enemy spawn areas.
- Base build zone.
- Weather profile.
- Resource nodes.

### 7. Weather Layer

Goal: make the environment attack the base too.

MVP weather:

- Wind.
- Wave.

Later weather:

- Rain.
- Heat.
- Storm.

Gameplay effects:

- Wind blows weak dry sand.
- Wave erodes coastal foundations.
- Rain changes sand moisture.
- Heat dries sand and supports glass tech.

### 8. Technology Layer

Goal: make progression change building strategy.

Point types:

- Defense Points.
- Research Points.
- Invasion Points.

Initial tech:

- Compression.
- Stone cutting.
- Glue trap.
- Basic glass.

Expansion tech:

- Reinforced packed sand.
- Bind spell.
- Lens tower.
- Water pressure gates.
- Auto repair.
- Resource conveyor.

### 9. Multiplayer Layer

Goal: support both safe async sharing and later live co-op.

Phase 1:

- Async JSON export/import.
- BaseData.
- EnemyWaveData.
- ReplayData.
- Local simulation score.

Phase 2:

- Live host/join prototype.
- Movement sync.
- Action sync.
- Quick block placement sync.
- Core HP sync.
- Start wave sync.

Sync principle:

- Host authoritative simulation.
- Clients send high-level actions.
- Do not sync every sand cell every frame.

## Recommended Unity Structure

```text
Assets/
  _Project/
    Art/
    Audio/
    Materials/
    Prefabs/
    Scenes/
    ScriptableObjects/
    Scripts/
      Core/
      Player/
      World/
      Sand/
      Building/
      TD/
      Weapons/
      Tech/
      Multiplayer/
      UI/
```

## First Production Vertical Slice

Name: Sand Mage First Wall

Purpose: prove the game feel before expanding scope.

Player story:

```text
The player controls a tiny 30 cm mage in a Minecraft-like seed-generated sandbox.
They walk through oversized sand, rocks, and water features, lift sand with magic,
place it into a wall, compress it into a hard block, save it as a quick block,
then compress another mass into a physics projectile and use both building and
action spells to protect a core from a small enemy wave.
```

Required systems:

- Third-person mage controller.
- Camera and aim reticle.
- Mouse-drag melee input: left, right, overhead.
- Weapon wheel range switching placeholder.
- Interact raycast.
- Beach seed test scene.
- Small sand grid.
- Lift/place/compress spell.
- Physics throw for compressed sand.
- Basic material heat action.
- PackedSand block.
- Molten sand/glass hazard placeholder.
- Quick block prototype.
- Core health.
- Runner enemy.
- Basic enemy spawner.
- Simple pathfinding toward core.
- Basic win/lose state.

Acceptance criteria:

- Player can move and aim reliably.
- Player scale reads as a small mage, roughly 30 cm tall, inside a large generated world.
- The scene communicates a Minecraft-like sandbox/building feel without using a block-only camera builder format.
- Player character reads as a simple chunky cartoon mage with robe/cloak/staff class identity.
- Mouse drag can trigger left swing, right swing, and overhead melee actions.
- Weapon wheel can switch at least two melee range profiles.
- Player can lift/place sand using the reticle.
- Player can compress sand into a stable wall block.
- Player can compress loose material into a throwable sphere.
- Thrown compressed material can damage or knock back a basic enemy.
- Heating sand can create a simple molten/glass hazard placeholder.
- Player can save/place one quick block template.
- Enemy can spawn, move toward the core, and damage it.
- A built wall can slow or block the enemy route.
- The scene can be validated by Unity batchmode without errors.

Out of scope for this slice:

- Full multiplayer.
- Full fluid simulation.
- Huge terrain generation.
- Persistent shared worlds.
- PvP balancing.
- Marketplace/economy.
- Large enemy roster.

## 8-Week Production Plan

### Week 1: Mage Controller Foundation

Deliver:

- Third-person controller.
- Follow camera.
- Aim reticle.
- Interact raycast.
- Basic tool/spell input.

Exit:

- Player can move through a test scene and interact with target points.

### Week 2: Sand Interaction Prototype

Deliver:

- Small sand/material grid.
- DrySand placement.
- Lift material action.
- Place material action.
- Compress action.

Exit:

- Player can create a simple wall from sand and compress it.

### Week 3: Building And Quick Blocks

Deliver:

- PackedSand block.
- Quick block save data.
- Quick block placement.
- Resource cost placeholder.
- Build preview.

Exit:

- Player can save and reuse one useful built structure.

### Week 4: Seed Beach Scene

Deliver:

- Deterministic seed input.
- Beach test terrain.
- Water boundary.
- Stone/sand resource areas.
- Core placement zone.

Exit:

- Same seed produces the same test layout.

### Week 5: TD Core Loop

Deliver:

- Core HP.
- Runner enemy.
- Enemy spawner.
- Simple pathfinding.
- Win/lose state.
- Wave start UI placeholder.

Exit:

- Enemy wave can attack the core and produce a result.

### Week 6: First Defenses And Weather

Deliver:

- Sand Cannon.
- Glue Trap or Water Cannon.
- Wind hazard.
- Wave erosion prototype.

Exit:

- Player-built defenses affect wave outcome.

### Week 7: Progression And Async Data

Deliver:

- Defense points.
- Basic tech unlock placeholder.
- BaseData export.
- EnemyWaveData export.
- Local async simulation stub.

Exit:

- A base and wave can be serialized and replay-tested locally.

### Week 8: Vertical Slice Packaging

Deliver:

- Main menu placeholder.
- Playable loop from seed to defense result.
- Basic VFX/SFX placeholders.
- QA checklist.
- Release gate validation.

Exit:

- New player can understand the game fantasy in 10 minutes.

## AI Office Execution Pipeline

Use this sequence for each feature:

```text
Manager brief
-> Designer routing decision
-> Creator asset/spec task
-> Programmer draft/implementation task
-> QA in Thai
-> Unity apply only after approved implementation scope
-> Unity validation
-> release gate
-> commit checkpoint
```

## Immediate Next AI Office Tasks

### Task 1: Create First Wall Feature Plan

Phase: PROTOTYPE_PLAN

Outputs:

- Designer routing.
- Creator asset list for mage, sand, wall, core, runner.
- Programmer Unity implementation plan.
- QA targets.

### Task 2: Draft Unity Architecture For Sand Mage First Wall

Phase: PROTOTYPE_PLAN

Outputs under `workspace/programmer_outputs/`:

- Player controller draft.
- Sand grid draft.
- Build controller draft.
- TD core loop draft.
- Scene setup plan.

### Task 3: Generate Placeholder Assets

Phase: PROTOTYPE_PLAN

Outputs under `workspace/creator_outputs/`:

- Tiny sand mage placeholder.
- Sand cell/block placeholders.
- Core placeholder.
- Runner enemy placeholder.
- Simple cannon/trap placeholders.

### Task 4: Apply First Wall Vertical Slice

Phase: IMPLEMENTATION

Requires explicit production-scope approval before modifying Unity project.

Outputs:

- Unity scripts under `_Project/Scripts`.
- Test scene.
- Validation script.
- Release gate pass.

## Production Readiness Decision

The AI Office is ready to receive the Sand Mage TD production command. The correct next production command should define:

- Target slice: `Sand Mage First Wall`.
- Allowed phase: `PROTOTYPE_PLAN` or `IMPLEMENTATION`.
- Unity modification approval: yes/no.
- Art style target.
- First target platform.
- Time budget for the first playable.
