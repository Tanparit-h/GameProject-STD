import asyncio
import json
import os
import re
from pathlib import Path

from langgraph.graph import END, StateGraph

from app.state import FeatureState
from autogen_teams.role_runner import run_role
from tools.blender_tool import run_blender_script
from tools.creator_asset_validator import validate_creator_exports
from tools.creator_file_tool import write_creator_file
from tools.programmer_file_tool import write_programmer_file
from tools.programmer_output_specs import (
    AmbiguousProgrammerFamilyError,
    UnsupportedProgrammerFamilyError,
    select_programmer_output_spec,
    validate_programmer_output_files as validate_programmer_output_spec_files,
)
from tools.unity_tool import (
    apply_copy_plan,
    get_unity_project_path,
    parse_unity_result_text,
    run_unity_batchmode,
    validate_unity_project_path,
)

ROOT = Path(__file__).resolve().parents[1]
PATTERN_DIR = ROOT / "workspace" / "generated_specs"


def _thai_list(items: list[str]) -> str:
    if not items:
        return "- \u0e44\u0e21\u0e48\u0e21\u0e35"
    return "\n".join(f"- {item}" for item in items)


def build_thai_evidence_report(
    passed: bool,
    checks: list[str],
    blockers: list[str] | None = None,
    missing: list[str] | None = None,
    edge_cases: list[str] | None = None,
    fixes: list[str] | None = None,
    recommendations: list[str] | None = None,
    evidence_blocks: list[str] | None = None,
) -> str:
    result_text = "\u0e1c\u0e48\u0e32\u0e19" if passed else "\u0e44\u0e21\u0e48\u0e1c\u0e48\u0e32\u0e19"
    report = (
        f"1. \u0e1c\u0e25\u0e15\u0e23\u0e27\u0e08: {result_text}\n"
        "2. \u0e2a\u0e34\u0e48\u0e07\u0e17\u0e35\u0e48\u0e15\u0e23\u0e27\u0e08:\n"
        f"{_thai_list(checks)}\n"
        "3. \u0e1b\u0e31\u0e0d\u0e2b\u0e32\u0e17\u0e35\u0e48\u0e1a\u0e25\u0e47\u0e2d\u0e01\u0e07\u0e32\u0e19:\n"
        f"{_thai_list(blockers or [])}\n"
        "4. Requirement \u0e17\u0e35\u0e48\u0e02\u0e32\u0e14:\n"
        f"{_thai_list(missing or [])}\n"
        "5. Edge case \u0e17\u0e35\u0e48\u0e1e\u0e1a:\n"
        f"{_thai_list(edge_cases or [])}\n"
        "6. \u0e2a\u0e34\u0e48\u0e07\u0e17\u0e35\u0e48\u0e15\u0e49\u0e2d\u0e07\u0e41\u0e01\u0e49:\n"
        f"{_thai_list(fixes or [])}\n"
        "7. \u0e04\u0e33\u0e41\u0e19\u0e30\u0e19\u0e33:\n"
        f"{_thai_list(recommendations or [])}"
    )

    if evidence_blocks:
        report += "\n\n---\n\n" + "\n\n---\n\n".join(block for block in evidence_blocks if block)

    return report


def parse_required_flag(text: str, label: str, default: bool) -> bool:
    normalized_text = re.sub(r"[*_`]", "", text)
    pattern = rf"{label}\s*required\s*:\s*(yes|no|true|false)"
    match = re.search(pattern, normalized_text, re.IGNORECASE)
    if not match:
        return default
    return match.group(1).lower() in ["yes", "true"]


def is_implementation_phase(phase: str) -> bool:
    return (phase or "").upper() == "IMPLEMENTATION"


def programmer_output_file_label(phase: str) -> str:
    return "implementation files" if is_implementation_phase(phase) else "design outputs"


def request_requires_creator(feature_request: str) -> bool:
    text = (feature_request or "").lower()
    markers = [
        "asset",
        "assets",
        "blender",
        "model",
        "mesh",
        "glb",
        "creator",
        "art",
        "placeholder asset",
    ]
    return any(marker in text for marker in markers)


def request_requires_programmer(feature_request: str) -> bool:
    text = (feature_request or "").lower()
    markers = [
        "implementation",
        "programmer",
        "unity setup",
        "logic",
        "script",
        "gameplay",
        "combat",
        "weapon",
        "scene",
        "validation",
        "ui",
        "parkour",
        "jump",
    ]
    return any(marker in text for marker in markers)


def get_programmer_output_spec_for_state(state: FeatureState):
    return select_programmer_output_spec(
        feature_request=state.get("feature_request", ""),
        phase=state.get("phase", "IMPLEMENTATION"),
        task_id=state.get("task_id", ""),
        family=state.get("task_family", ""),
    )


def write_pattern_file(filename: str, content: str) -> str:
    PATTERN_DIR.mkdir(parents=True, exist_ok=True)
    target = PATTERN_DIR / filename
    target.write_text(content, encoding="utf-8")
    return str(target)


def build_script_pattern(state: FeatureState, role: str) -> str:
    role_title = role.capitalize()
    if role == "unity":
        role_action = "Unity applies approved files into the Unity project and validates the result."
        role_scope = "Unity writes only approved targets under the Unity project `Assets/` folder."
    else:
        role_action = f"{role_title} generates only files inside its workspace output folder."
        role_scope = f"{role_title} output stays inside the allowed workspace path."

    return f"""# AI Office v2 {role_title} Pattern

## Codex Order

{state.get("feature_request", "")}

## Metadata

- task_id: {state.get("task_id", "") or "none"}
- task_family: {state.get("task_family", "") or "none"}
- phase: {state.get("phase", "IMPLEMENTATION")}

## Runtime Contract

- Active roles only: Creator, Programmer, Unity.
- Codex creates this pattern before generation.
- {role_action}
- {role_title} runs a self-reviewer pass before the next stage.
- Codex performs the final code/evidence review after Unity finishes.

## Reviewer Checklist

- Inputs are explicit and traceable to the Codex order.
- {role_scope}
- Output is implementation-ready when phase is IMPLEMENTATION.
- Risks, skipped steps, and required user approvals are stated.
"""


def default_creator_script() -> str:
    return r'''import os
import bpy

export_dir = os.getenv("AI_STUDIO_EXPORT_DIR") or os.path.join(os.getcwd(), "exports")
os.makedirs(export_dir, exist_ok=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))
asset = bpy.context.object
asset.name = "ai_office_placeholder_asset"
asset.scale = (0.6, 0.6, 0.6)

material = bpy.data.materials.new("ai_office_placeholder_material")
material.diffuse_color = (0.3, 0.7, 0.9, 1.0)
asset.data.materials.append(material)

target = os.path.join(export_dir, "ai_office_placeholder_asset.glb")
bpy.ops.export_scene.gltf(filepath=target, export_format="GLB")
print(f"EXPORTED: {target}")
'''


def write_programmer_output_files(state: FeatureState) -> list[str]:
    spec = get_programmer_output_spec_for_state(state)
    return [write_programmer_file(filename, content) for filename, content in spec.file_contents.items()]


def validate_programmer_output_files(state: FeatureState, file_paths: list[str]) -> tuple[bool, list[str]]:
    output_dir = ROOT / "workspace" / "programmer_outputs"
    spec = get_programmer_output_spec_for_state(state)
    return validate_programmer_output_spec_files(output_dir, file_paths, spec)


def validate_creator_output_evidence(state: FeatureState) -> tuple[bool, list[str], dict[str, object]]:
    problems: list[str] = []
    script_path_text = state.get("creator_script_path", "")
    if not state.get("creator_required", False):
        return True, [], {"passed": True, "exported_files": [], "error_markers": [], "small_files": []}

    if not script_path_text:
        problems.append("creator_script_path เธงเนเธฒเธ")
        return False, problems, validate_creator_exports()

    script_path = Path(script_path_text)
    if not script_path.exists():
        problems.append(f"เนเธกเนเธเธ Blender script: {script_path}")
    else:
        creator_root = (ROOT / "workspace" / "creator_outputs").resolve()
        try:
            script_path.resolve().relative_to(creator_root)
        except ValueError:
            problems.append(f"Blender script เธญเธขเธนเนเธเธญเธ workspace/creator_outputs: {script_path.resolve()}")

        script_text = script_path.read_text(encoding="utf-8", errors="replace")
        for marker in ["import bpy", "import os", "AI_STUDIO_EXPORT_DIR"]:
            if marker not in script_text:
                problems.append(f"Blender script เธเธฒเธ” marker: {marker}")

    blender_result = state.get("creator_blender_result", "")
    if "BLENDER_ERROR" in blender_result or "Exit code: 0" not in blender_result:
        problems.append("Blender run เนเธกเนเธชเธณเน€เธฃเนเธ")

    creator_validation = validate_creator_exports()
    if not creator_validation.get("passed", False):
        problems.append("Creator export validation เนเธกเนเธเนเธฒเธ")

    return not problems, problems, creator_validation


async def maybe_autogen_review(role_name: str, prompt_file: str, task: str) -> str:
    if os.getenv("AI_OFFICE_USE_AUTOGEN_REVIEWERS", "0") != "1":
        return "AUTOGEN_REVIEWER_PATTERN_READY"
    return await run_role(role_name=role_name, prompt_file=prompt_file, task=task)


async def creator_node(state: FeatureState) -> FeatureState:
    print("[1/4] Creator receiving Codex pattern and generating assets if needed...")
    state["creator_required"] = request_requires_creator(state.get("feature_request", ""))
    state["creator_pattern_path"] = write_pattern_file("creator_pattern.md", build_script_pattern(state, "creator"))

    if not state["creator_required"]:
        state["creator_output"] = "Creator skipped: request does not require asset generation."
        state["creator_gate_status"] = "SKIPPED"
        state["creator_approval_status"] = "SKIPPED"
        return state

    state["creator_script_path"] = write_creator_file("create_placeholder_assets.py", default_creator_script())
    state["creator_output"] = (
        "Creator generated a Blender script from the Codex pattern and prepared it for export. "
        f"Pattern: {state['creator_pattern_path']}"
    )
    state["creator_blender_result"] = run_blender_script(state["creator_script_path"])
    return state


async def creator_qa_node(state: FeatureState) -> FeatureState:
    print("[1/4] Creator reviewer checking asset evidence...")
    if state.get("creator_gate_status") == "SKIPPED":
        state["creator_qa_report"] = "Creator reviewer skipped: no creator work requested."
        return state

    passed, problems, validation = validate_creator_output_evidence(state)
    state["creator_gate_status"] = "CLEAN_PASS" if passed else "NEED_USER_GATE"
    state["creator_approval_status"] = "AUTO_APPROVED_BY_CREATOR_REVIEWER" if passed else "NEED_CODEX_REVIEW"
    state["creator_qa_report"] = build_thai_evidence_report(
        passed=passed,
        checks=["creator evidence gate", "Blender script path", "export validation"],
        blockers=problems,
        recommendations=["Creator reviewer gate clean"] if passed else ["Codex should inspect Creator output"],
        evidence_blocks=[json.dumps(validation, ensure_ascii=False, indent=2)],
    )
    state["creator_reviewer_output"] = await maybe_autogen_review(
        "creator_reviewer",
        "creator.md",
        f"Review creator output:\n{state.get('creator_output', '')}\n\nEvidence:\n{state.get('creator_qa_report', '')}",
    )
    return state


async def programmer_node(state: FeatureState) -> FeatureState:
    print("[2/4] Programmer receiving Codex pattern and generating implementation files...")
    state["programmer_required"] = True
    state["programmer_pattern_path"] = write_pattern_file("programmer_pattern.md", build_script_pattern(state, "programmer"))
    state["programmer_file_paths"] = write_programmer_output_files(state)
    state["programmer_output"] = (
        "Programmer generated deterministic implementation files from the Codex pattern. "
        f"Pattern: {state['programmer_pattern_path']}"
    )
    return state


async def programmer_qa_node(state: FeatureState) -> FeatureState:
    print("[2/4] Programmer reviewer checking implementation files...")
    passed, problems = validate_programmer_output_files(state, state.get("programmer_file_paths", []))
    spec = get_programmer_output_spec_for_state(state)
    state["programmer_gate_status"] = "CLEAN_PASS" if passed else "NEED_USER_GATE"
    state["programmer_approval_status"] = "AUTO_APPROVED_BY_PROGRAMMER_REVIEWER" if passed else "NEED_CODEX_REVIEW"
    state["programmer_qa_report"] = build_thai_evidence_report(
        passed=passed,
        checks=["DETERMINISTIC_PROGRAMMER_GATE", f"spec: {spec.key}", "workspace/programmer_outputs"],
        blockers=problems,
        recommendations=["Programmer reviewer gate clean"] if passed else ["Codex should inspect Programmer output"],
    )
    state["programmer_reviewer_output"] = await maybe_autogen_review(
        "programmer_reviewer",
        "programmer.md",
        f"Review programmer output:\n{state.get('programmer_output', '')}\n\nEvidence:\n{state.get('programmer_qa_report', '')}",
    )
    return state


def unity_node(state: FeatureState) -> FeatureState:
    print("[3/4] Unity applying approved outputs and running validation...")
    state["unity_pattern_path"] = write_pattern_file("unity_pattern.md", build_script_pattern(state, "unity"))
    ok, message, project_path = validate_unity_project_path()
    state["unity_project_path"] = str(project_path)

    if not ok:
        state["unity_implementation_result"] = f"SKIPPED_UNITY_IMPLEMENTATION: {message}"
        state["unity_gate_status"] = "NEED_USER_GATE"
        return state

    if not is_implementation_phase(state.get("phase", "")):
        state["unity_implementation_result"] = apply_copy_plan(dry_run=True, project_path=project_path)
        state["unity_validation_result"] = "SKIPPED_UNITY_VALIDATION: phase is not IMPLEMENTATION."
        state["unity_scene_setup_result"] = "SKIPPED_UNITY_SCENE_SETUP: phase is not IMPLEMENTATION."
        state["unity_scene_validation_result"] = "SKIPPED_UNITY_SCENE_VALIDATION: phase is not IMPLEMENTATION."
        return state

    spec = get_programmer_output_spec_for_state(state)
    state["unity_implementation_result"] = apply_copy_plan(dry_run=False, project_path=project_path)
    state["unity_validation_result"] = run_unity_batchmode(log_name="unity_graph_validation.log")
    state["unity_scene_setup_result"] = run_unity_batchmode(
        extra_args=["-executeMethod", spec.scene_setup_method],
        log_name="unity_graph_scene_setup.log",
    )
    state["unity_scene_validation_result"] = run_unity_batchmode(
        extra_args=["-executeMethod", spec.scene_validation_method],
        log_name="unity_graph_scene_validation.log",
    )
    return state


async def unity_qa_node(state: FeatureState) -> FeatureState:
    print("[3/4] Unity reviewer checking copy plan and validation evidence...")
    if not is_implementation_phase(state.get("phase", "")):
        state["unity_gate_status"] = "SKIPPED"
        state["unity_approval_status"] = "SKIPPED"
        state["unity_qa_report"] = "DETERMINISTIC_UNITY_GATE skipped because phase is not IMPLEMENTATION."
        return state

    validation = parse_unity_result_text(state.get("unity_validation_result", ""))
    setup = parse_unity_result_text(state.get("unity_scene_setup_result", ""))
    scene_validation = parse_unity_result_text(state.get("unity_scene_validation_result", ""))
    checks = [
        "DETERMINISTIC_UNITY_GATE",
        f"Validation passed: {validation['passed']}",
        f"Scene setup passed: {setup['passed']}",
        f"Scene validation passed: {scene_validation['passed']}",
    ]
    problems = []
    if "UNITY_COPY_PLAN" not in state.get("unity_implementation_result", ""):
        problems.append("Unity copy plan missing")
    if not validation["passed"]:
        problems.append("Unity batchmode validation failed")
    if not setup["passed"]:
        problems.append("Unity scene setup failed")
    if not scene_validation["passed"]:
        problems.append("Unity scene validation failed")

    passed = not problems
    state["unity_gate_status"] = "CLEAN_PASS" if passed else "NEED_USER_GATE"
    state["unity_approval_status"] = "AUTO_APPROVED_BY_UNITY_REVIEWER" if passed else "NEED_CODEX_REVIEW"
    state["unity_qa_report"] = build_thai_evidence_report(
        passed=passed,
        checks=checks,
        blockers=problems,
        recommendations=["Unity reviewer gate clean"] if passed else ["Codex should inspect Unity logs"],
    )
    state["unity_reviewer_output"] = await maybe_autogen_review(
        "unity_reviewer",
        "unity_implementer.md",
        f"Review Unity evidence:\n{state['unity_qa_report']}",
    )
    return state


def final_node(state: FeatureState) -> FeatureState:
    print("[4/4] Writing Codex handoff report...")
    reports_dir = ROOT / "workspace" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    final_status = state.get("final_status", "") or "ROLE_GRAPH_OK"

    report = f"""# AI Office v2 Report

## Feature Request

{state.get("feature_request", "")}

---

## Task Metadata

Task id: {state.get("task_id", "") or "none"}

Task file: {state.get("task_file", "") or "none"}

Task family: {state.get("task_family", "") or "none"}

---

## Phase

{state.get("phase", "")}

---

## Active Runtime Roles

- Creator
- Programmer
- Unity

---

## Creator Pattern

{state.get("creator_pattern_path", "")}

## Creator Output

{state.get("creator_output", "")}

## Creator Evidence Report

{state.get("creator_qa_report", "")}

## Creator Gate Status

{state.get("creator_gate_status", "") or "SKIPPED"}

---

## Programmer Pattern

{state.get("programmer_pattern_path", "")}

## Programmer Output

{state.get("programmer_output", "")}

## Programmer Output File Paths

{chr(10).join(state.get("programmer_file_paths", []))}

## Programmer Evidence Report

{state.get("programmer_qa_report", "")}

## Programmer Gate Status

{state.get("programmer_gate_status", "")}

---

## Unity Pattern

{state.get("unity_pattern_path", "")}

## Unity Project Path

{state.get("unity_project_path", "")}

## Unity Implementation Result

{state.get("unity_implementation_result", "")}

## Unity Validation Result

{state.get("unity_validation_result", "")}

## Unity Scene Setup Result

{state.get("unity_scene_setup_result", "")}

## Unity Scene Validation Result

{state.get("unity_scene_validation_result", "")}

## Unity Evidence Report

{state.get("unity_qa_report", "")}

## 9.6 Unity Gate Status

{state.get("unity_gate_status", "")}

---

## Codex Review Contract

Codex must inspect generated code, Unity diffs, logs, and gameplay logic after this Office run before committing production work.

## Final Status

{final_status}
"""
    report_path = reports_dir / "latest_report.md"
    report_path.write_text(report, encoding="utf-8")

    codex_response = f"""# AI Office Response To Codex

## Status

{final_status}

## Runtime

AI_OFFICE_V2_CREATOR_PROGRAMMER_UNITY

## Phase

{state.get("phase", "")}

## Gate Summary

- Creator gate: {state.get("creator_gate_status", "") or "SKIPPED"}
- Programmer gate: {state.get("programmer_gate_status", "") or "SKIPPED"}
- Unity gate: {state.get("unity_gate_status", "") or "SKIPPED"}

## Output Files

{chr(10).join(f"- {path}" for path in state.get("programmer_file_paths", [])) or "- none"}

## Codex Next Action

Review generated code, Unity diffs, logs, and gameplay logic before commit.
"""
    (reports_dir / "codex_response.md").write_text(codex_response, encoding="utf-8")
    state["final_status"] = f"{final_status} | Report written: {report_path}"
    return state


def write_blocked_family_reports(
    *,
    task_id: str,
    task_file: str,
    task_family: str,
    feature_request: str,
    phase: str,
    status: str,
    message: str,
) -> None:
    reports_dir = ROOT / "workspace" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report = f"""# AI Office v2 Blocked Report

## Feature Request

{feature_request}

## Task Metadata

Task id: {task_id or "none"}

Task file: {task_file or "none"}

Task family: {task_family or "none"}

## Phase

{phase}

## Final Status

{status}

## Reason

{message}
"""
    (reports_dir / "latest_report.md").write_text(report, encoding="utf-8")
    (reports_dir / "codex_response.md").write_text(report, encoding="utf-8")


def build_graph():
    graph = StateGraph(FeatureState)
    graph.add_node("creator", creator_node)
    graph.add_node("creator_reviewer", creator_qa_node)
    graph.add_node("programmer", programmer_node)
    graph.add_node("programmer_reviewer", programmer_qa_node)
    graph.add_node("unity", unity_node)
    graph.add_node("unity_reviewer", unity_qa_node)
    graph.add_node("final", final_node)

    graph.set_entry_point("creator")
    graph.add_edge("creator", "creator_reviewer")
    graph.add_edge("creator_reviewer", "programmer")
    graph.add_edge("programmer", "programmer_reviewer")
    graph.add_edge("programmer_reviewer", "unity")
    graph.add_edge("unity", "unity_reviewer")
    graph.add_edge("unity_reviewer", "final")
    graph.add_edge("final", END)
    return graph.compile()


def load_request_from_env() -> tuple[str, str, str, str, str]:
    default_feature_request = "Create and validate a real Unity interaction vertical slice."
    feature_request = os.getenv("AI_STUDIO_FEATURE_REQUEST", default_feature_request)
    phase = os.getenv("AI_STUDIO_PHASE", "IMPLEMENTATION")
    task_file = os.getenv("AI_STUDIO_TASK_FILE", "")
    task_id = ""
    task_family = os.getenv("AI_STUDIO_TASK_FAMILY", "")

    if task_file:
        task_path = Path(task_file)
        if not task_path.is_absolute():
            task_path = ROOT / task_path
        task_data = json.loads(task_path.read_text(encoding="utf-8"))
        task_id = str(task_data.get("id", ""))
        feature_request = str(task_data.get("request", feature_request))
        phase = str(task_data.get("phase", phase))
        task_family = str(task_data.get("family", task_family))

    return task_id, task_file, task_family, feature_request, phase


async def main():
    task_id, task_file, task_family, feature_request, phase = load_request_from_env()

    try:
        select_programmer_output_spec(
            feature_request=feature_request,
            phase=phase,
            task_id=task_id,
            family=task_family,
        )
    except (UnsupportedProgrammerFamilyError, AmbiguousProgrammerFamilyError) as exc:
        status = f"STOPPED_{type(exc).__name__.replace('ProgrammerFamilyError', '').upper() or 'FAMILY_ERROR'}"
        write_blocked_family_reports(
            task_id=task_id,
            task_file=task_file,
            task_family=task_family,
            feature_request=feature_request,
            phase=phase,
            status=status,
            message=str(exc),
        )
        print(status)
        return

    result = await build_graph().ainvoke(
        {
            "task_id": task_id,
            "task_file": task_file,
            "task_family": task_family,
            "feature_request": feature_request,
            "phase": phase,
            "creator_required": False,
            "programmer_required": True,
            "creator_output": "",
            "creator_pattern_path": "",
            "creator_script_path": "",
            "creator_blender_result": "",
            "creator_qa_report": "",
            "creator_gate_status": "",
            "creator_approval_status": "",
            "creator_reviewer_output": "",
            "programmer_output": "",
            "programmer_pattern_path": "",
            "programmer_file_paths": [],
            "programmer_qa_report": "",
            "programmer_gate_status": "",
            "programmer_approval_status": "",
            "programmer_reviewer_output": "",
            "unity_pattern_path": "",
            "unity_project_path": str(get_unity_project_path()),
            "unity_implementation_result": "",
            "unity_validation_result": "",
            "unity_scene_setup_result": "",
            "unity_scene_validation_result": "",
            "unity_qa_report": "",
            "unity_gate_status": "",
            "unity_approval_status": "",
            "unity_reviewer_output": "",
            "final_status": "",
        }
    )
    print(result["final_status"])


if __name__ == "__main__":
    asyncio.run(main())
