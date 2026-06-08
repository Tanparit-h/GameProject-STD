# Next Steps

## Current Status

The AI Office prototype can create and validate a small Unity game feature end-to-end, but the Unity implementation stage is not yet fully inside the LangGraph workflow.

Completed:

- Manager, Designer, Creator, Programmer, and QA roles run through LangGraph/AutoGen/Ollama.
- Creator can generate Blender scripts and export `.glb` placeholder assets.
- Programmer can write draft files into `workspace/programmer_outputs/`.
- QA and Human Gate reports exist.
- Real Unity target is marked as `game_project/STDProject`.
- Implementation files were applied to `STDProject`.
- Unity `6000.4.9f1` full batchmode validation passed.
- `SampleScene` was wired with `AIPrototype_Player`, `AIPrototype_Interactable`, and `AIPrototype_VisualReference`.
- Automated Unity scene validation passed with return code `0`.

## Current Gap

The Unity implementation stage now exists as an automated graph node and has passed an approved IMPLEMENTATION run.

The remaining production blocker is unrelated dirty Unity project state that must be reviewed before push/release.

To make the AI Office workflow truly reusable, the graph needs a dedicated Unity implementation stage that can:

- Apply approved Programmer/Creator outputs into the real Unity project.
- Run Unity batchmode validation.
- Run scene setup and scene validation.
- Parse logs into reports.
- Route failures back through QA/Human Gate.

## Next Step A: Add Unity Tool Module

Create:

```text
tools/unity_tool.py
```

Responsibilities:

- Read `UNITY_EXE` and `UNITY_PROJECT` from `.env`.
- Validate the Unity project path.
- Copy approved `.glb` assets into `Assets/AIAssets/`.
- Copy approved scripts into `Assets/Scripts/AIPrototype/`.
- Run Unity batchmode validation.
- Run Unity `-executeMethod` commands.
- Parse Unity logs for `error CS`, `Exception`, `EPERM`, `Compilation failed`, `Tundra build success`, and return code evidence.
- Keep logs in `workspace/logs/`.

Status: complete.

## Next Step B: Add Unity Implementer Graph Nodes

Update:

```text
app/main_graph.py
app/state.py
```

Add nodes:

- `unity_implementation`
- `unity_batchmode_validation`
- `unity_scene_setup`
- `unity_scene_validation`
- `unity_qa`
- `unity_human_gate`

State fields to add:

- `unity_project_path`
- `unity_implementation_result`
- `unity_validation_result`
- `unity_scene_setup_result`
- `unity_scene_validation_result`
- `unity_qa_report`
- `unity_gate_status`
- `unity_approval_status`
- `unity_retry_count`

Status: complete.

## Next Step C: Add Unity Role/Prompt Rules

Create or update:

```text
prompts/unity_implementer.md
prompts/qa.md
```

Rules:

- Use `game_project/STDProject` as the real Unity target.
- Never commit Unity cache folders.
- Do not modify scenes/prefabs unless Designer or Human Gate approves it.
- Always generate an implementation report.
- QA must check both compile validation and scene validation.
- QA remains Thai-only.

Status: complete.

## Next Step D: Convert Manual Scene Setup Into Workflow Asset

Current manual Unity files:

```text
game_project/STDProject/Assets/Scripts/AIPrototype/Editor/AIPrototypeSceneSetup.cs
game_project/STDProject/Assets/Scripts/AIPrototype/Editor/AIPrototypeSceneValidator.cs
```

Workflow should be able to:

- Generate these editor scripts when needed.
- Execute `AIPrototypeSceneSetup.SetupSampleScene`.
- Execute `AIPrototypeSceneValidator.ValidateSampleScene`.
- Report pass/fail automatically.

Status: partially complete. Existing editor scripts can be executed by graph nodes in IMPLEMENTATION phase; generation of new editor scripts remains future work.

## Next Step E: Add Tests For Workflow Automation

Add tests that do not require changing Unity scenes unless explicitly enabled:

- Unit test for Unity log parser.
- Unit test for `unity_tool.py` path safety.
- Dry-run test for file copy plan.
- Optional integration test for Unity batchmode when `UNITY_PROJECT` exists.

Status: complete for current scope. `test_unity_tool.py` uses `unittest`, so it runs without installing pytest. Current tests also cover idempotent Unity copy planning.

## Next Step G: IMPLEMENTATION Approval Run

Blocked until explicit human approval:

- Switch phase from `PROTOTYPE_PLAN` to `IMPLEMENTATION`, for example by setting `AI_STUDIO_PHASE=IMPLEMENTATION`
- Apply approved assets/scripts into `game_project/STDProject`
- Run Unity batchmode validation
- Run scene setup and scene validation
- Commit nested Unity repo changes according to chosen git strategy

Status: complete. Latest IMPLEMENTATION run passed Unity validation, scene setup, and scene validation.

## Next Step F: Git Strategy

Current repo structure:

- Root repo: `D:\AIStudio\ai-game-studio`
- Nested Unity repo: `D:\AIStudio\ai-game-studio\game_project\STDProject`

Decision needed:

- Keep `STDProject` as a separate Git repo and do not track it from root.
- Or convert it into a proper submodule.
- Or flatten it into root repo.

Recommended for now:

- Keep `STDProject` separate.
- Commit Unity implementation work inside `STDProject`.
- Commit workflow/reports in root repo.

Status: documented in `workspace/reports/git_strategy.md`; final structural changes still require human approval.

## Latest Saved Commits

Root repo:

```text
e4a1fc3 Document Unity implementation validation
```

STDProject repo:

```text
0b510e8 Add AI prototype scene wiring
```
