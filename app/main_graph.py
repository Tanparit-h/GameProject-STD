import asyncio
import json
import os
import re
from pathlib import Path
from langgraph.graph import StateGraph, END

from app.state import FeatureState
from autogen_teams.role_runner import run_role
from tools.creator_file_tool import write_creator_file
from tools.programmer_file_tool import write_programmer_file
from tools.creator_asset_validator import format_creator_validation, validate_creator_exports
from tools.programmer_output_specs import (
    select_programmer_output_spec,
    validate_programmer_output_files as validate_programmer_output_spec_files,
)
from tools.blender_tool import run_blender_script
from tools.unity_tool import (
    apply_copy_plan,
    get_unity_project_path,
    parse_unity_result_text,
    run_unity_batchmode,
    validate_unity_project_path,
)

ROOT = Path(__file__).resolve().parents[1]

MAX_CREATOR_RETRY = 2
MAX_PROGRAMMER_RETRY = 2
MAX_UNITY_RETRY = 1


def analyze_qa_gate(qa_report: str) -> str:
    """
    Return:
    - CLEAN_PASS: QA pass and no meaningful issues
    - NEED_USER_GATE: QA found issue, warning, blocker, missing requirement, required fix, or fail
    """
    text = qa_report.lower()

    is_pass = bool(re.search(r"\bpass\b|ผลตรวจ:\s*ผ่าน|ผ่าน", text))
    is_fail = bool(re.search(r"\bfail\b|ผลตรวจ:\s*ไม่ผ่าน|ไม่ผ่าน", text))

    issue_keywords = [
        "blocker",
        "blockers",
        "missing requirement",
        "missing requirements",
        "required fix",
        "required fixes",
        "risk",
        "risks",
        "issue",
        "issues",
        "ambiguity",
        "ambiguous",
        "not fully",
        "ปัญหาที่บล็อกงาน",
        "requirement ที่ขาด",
        "สิ่งที่ต้องแก้",
        "ความเสี่ยง",
        "ปัญหา",
        "ไม่ครบ",
        "ขาด",
        "ผิดพลาด",
        "ต้องแก้",
        "ไม่ชัดเจน",
    ]

    has_issue_keyword = any(keyword in text for keyword in issue_keywords)

    has_clean_blocker = (
        "ปัญหาที่บล็อกงาน:\n   - ไม่มี" in text
        or "ปัญหาที่บล็อกงาน:\r\n   - ไม่มี" in text
        or "ปัญหาที่บล็อกงาน: ไม่มี" in text
        or "blockers: none" in text
        or "blocker: none" in text
    )

    has_clean_missing = (
        "requirement ที่ขาด:\n   - ไม่มี" in text
        or "requirement ที่ขาด:\r\n   - ไม่มี" in text
        or "requirement ที่ขาด: ไม่มี" in text
        or "missing requirements: none" in text
        or "missing requirement: none" in text
    )

    has_clean_fixes = (
        "สิ่งที่ต้องแก้:\n   - ไม่มี" in text
        or "สิ่งที่ต้องแก้:\r\n   - ไม่มี" in text
        or "สิ่งที่ต้องแก้: ไม่มี" in text
        or "required fixes: none" in text
        or "required fix: none" in text
    )

    has_all_clean_none = has_clean_blocker and has_clean_missing and has_clean_fixes

    if is_fail:
        return "NEED_USER_GATE"

    if is_pass and has_all_clean_none:
        return "CLEAN_PASS"

    no_issue_markers = [
        "ไม่มี",
        "เนเธกเนเธกเธต",
        "none",
    ]
    fatal_keywords = [
        "traceback",
        "exception",
        "keyerror",
        "attributeerror",
        "typeerror",
        "error cs",
        "compilation failed",
        "blocked",
        "ต้องอนุมัติ",
    ]
    if is_pass and any(marker in text for marker in no_issue_markers):
        if not any(keyword in text for keyword in fatal_keywords):
            return "CLEAN_PASS"

    if is_pass and has_issue_keyword and not has_all_clean_none:
        return "NEED_USER_GATE"

    return "NEED_USER_GATE"


def parse_required_flag(text: str, label: str, default: bool) -> bool:
    """
    Parse lines like:
    - Creator required: yes
    - Creator required: no
    - Programmer required: yes
    - Programmer required: no
    """
    normalized_text = re.sub(r"[*_`]", "", text)
    pattern = rf"{label}\s*required\s*:\s*(yes|no|true|false)"
    match = re.search(pattern, normalized_text, re.IGNORECASE)

    if not match:
        return default

    value = match.group(1).lower()
    return value in ["yes", "true"]


def request_requires_programmer(feature_request: str) -> bool:
    """
    Keep real implementation requests from being accidentally routed away from Programmer.
    """
    text = feature_request.lower()
    programmer_keywords = [
        "implementation",
        "implementation plan",
        "programmer",
        "unity setup",
        "logic",
        "script",
        "gameplay",
        "combat",
        "weapon wheel",
        "scene validation",
        "ui",
    ]
    return any(keyword in text for keyword in programmer_keywords)


def extract_python_code_block(text: str) -> str:
    """
    Extract first Python code block from markdown.
    If no code block exists, return a safe placeholder script.
    """
    pattern = r"```(?:python|py)?\s*(.*?)```"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

    if match:
        return match.group(1).strip()

    return """# No Blender script block found from Creator output.
# TODO: Ask Creator to provide a Python code block.
print("NO_CREATOR_SCRIPT_FOUND")
"""


def extract_code_block(text: str, language: str | None = None) -> str:
    if language:
        pattern = rf"```(?:{re.escape(language)})\s*(.*?)```"
    else:
        pattern = r"```\s*(.*?)```"

    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    return ""


def get_programmer_output_spec_for_state(state: FeatureState):
    return select_programmer_output_spec(
        feature_request=state["feature_request"],
        phase=state["phase"],
        task_id=state.get("task_id", ""),
    )


def is_implementation_phase(phase: str) -> bool:
    return (phase or "").upper() == "IMPLEMENTATION"


def programmer_output_file_label(phase: str) -> str:
    return "implementation files" if is_implementation_phase(phase) else "design outputs"


def _thai_list(items: list[str]) -> str:
    if not items:
        return "- ไม่มี"
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
    report = (
        f"1. ผลตรวจ: {'ผ่าน' if passed else 'ไม่ผ่าน'}\n"
        "2. สิ่งที่ตรวจ:\n"
        f"{_thai_list(checks)}\n"
        "3. ปัญหาที่บล็อกงาน:\n"
        f"{_thai_list(blockers or [])}\n"
        "4. Requirement ที่ขาด:\n"
        f"{_thai_list(missing or [])}\n"
        "5. Edge case ที่พบ:\n"
        f"{_thai_list(edge_cases or [])}\n"
        "6. สิ่งที่ต้องแก้:\n"
        f"{_thai_list(fixes or [])}\n"
        "7. คำแนะนำ:\n"
        f"{_thai_list(recommendations or [])}"
    )

    if evidence_blocks:
        report += "\n\n---\n\n" + "\n\n---\n\n".join(block for block in evidence_blocks if block)

    return report


def write_programmer_output_files(state: FeatureState) -> list[str]:
    """
    Persist Programmer output files using the task-aware deterministic spec.
    """
    spec = get_programmer_output_spec_for_state(state)
    return [
        write_programmer_file(filename, content)
        for filename, content in spec.file_contents.items()
    ]


def validate_programmer_output_files(state: FeatureState, file_paths: list[str]) -> tuple[bool, list[str]]:
    output_dir = ROOT / "workspace" / "programmer_outputs"
    spec = get_programmer_output_spec_for_state(state)
    return validate_programmer_output_spec_files(output_dir, file_paths, spec)


def validate_creator_output_evidence(state: FeatureState) -> tuple[bool, list[str], dict[str, object]]:
    problems: list[str] = []
    script_path_text = state["creator_script_path"]
    if not script_path_text:
        problems.append("creator_script_path ว่าง")
        return False, problems, validate_creator_exports()

    script_path = Path(script_path_text)
    if not script_path.exists():
        problems.append(f"ไม่พบ Blender script: {script_path}")
    else:
        creator_root = (ROOT / "workspace" / "creator_outputs").resolve()
        try:
            script_path.resolve().relative_to(creator_root)
        except ValueError:
            problems.append(f"Blender script อยู่นอก workspace/creator_outputs: {script_path.resolve()}")

        script_text = script_path.read_text(encoding="utf-8", errors="replace")
        for marker in ["import bpy", "import os", "AI_STUDIO_EXPORT_DIR"]:
            if marker not in script_text:
                problems.append(f"Blender script ขาด marker: {marker}")

    blender_result = state["creator_blender_result"]
    if "BLENDER_ERROR" in blender_result or "Exit code: 0" not in blender_result:
        problems.append("Blender run ไม่สำเร็จ")

    creator_validation = validate_creator_exports()
    if not creator_validation["passed"]:
        problems.append("Creator export validation ไม่ผ่าน")

    return not problems, problems, creator_validation


async def manager_node(state: FeatureState) -> FeatureState:
    print("[1/11] Manager analyzing user input...")

    task = f"""
User input:
{state["feature_request"]}

Current phase:
{state["phase"]}

วิเคราะห์ input นี้แล้วส่งต่อเป็น package ให้ Designer
"""

    state["manager_output"] = await run_role(
        role_name="manager",
        prompt_file="manager.md",
        task=task,
    )
    return state


async def designer_node(state: FeatureState) -> FeatureState:
    print("[2/11] Designer creating tasks, QA target, and routing decision...")

    task = f"""
Feature request:
{state["feature_request"]}

Current phase:
{state["phase"]}

Manager output:
{state["manager_output"]}

สร้าง design summary, creator task, programmer task, Creator QA target, Programmer QA target และ acceptance criteria
ต้องระบุ Out of scope ให้ตรงกับ phase

สำคัญมาก:
ต้องใส่ Routing decision เป็น section แรกเสมอ:
0. Routing decision
- Creator required: yes/no
- Programmer required: yes/no
- Reason: ...

ถ้างานไม่มี asset, picture, icon, model 3D, Blender, animation, visual mockup หรือ asset placeholder ให้ Creator required: no
ถ้างานไม่มี code, logic, Unity setup, script, integration, test, config หรือ implementation plan ให้ Programmer required: no
"""

    state["designer_output"] = await run_role(
        role_name="designer",
        prompt_file="designer.md",
        task=task,
    )

    state["creator_required"] = parse_required_flag(
        text=state["designer_output"],
        label="Creator",
        default=True,
    )

    state["programmer_required"] = parse_required_flag(
        text=state["designer_output"],
        label="Programmer",
        default=True,
    )

    if request_requires_programmer(state["feature_request"]):
        state["programmer_required"] = True

    programmer_spec = get_programmer_output_spec_for_state(state)
    if programmer_spec.key != "default_interaction":
        state["programmer_required"] = True

    print(f"Creator required: {state['creator_required']}")
    print(f"Programmer required: {state['programmer_required']}")

    return state


def route_after_designer(state: FeatureState) -> str:
    if state["creator_required"]:
        return "creator"

    return "skip_creator"


def route_after_skip_creator(state: FeatureState) -> str:
    if state["programmer_required"]:
        return "programmer"

    return "final"


def skip_creator_node(state: FeatureState) -> FeatureState:
    print("[3/11] Skipping Creator because Designer marked Creator required: no")

    state["creator_output"] = "SKIPPED: Designer marked Creator required: no"
    state["creator_script_path"] = ""
    state["creator_blender_result"] = "SKIPPED: No creator asset/model/picture required"
    state["creator_qa_report"] = "SKIPPED: Creator QA not required"
    state["creator_gate_status"] = "SKIPPED"
    state["creator_approval_status"] = "SKIPPED"
    state["creator_approval_note"] = "Creator was skipped because no asset/model/picture task was required."

    return state


async def creator_node(state: FeatureState) -> FeatureState:
    print(f"[3/11] Creator generating asset plan and Blender script draft... retry={state['creator_retry_count']}")

    retry_note = ""
    if state["creator_retry_count"] > 0:
        retry_note = f"""
Previous Creator output:
{state["creator_output"]}

Previous Creator QA report:
{state["creator_qa_report"]}

Previous Blender run result:
{state["creator_blender_result"]}

User rejection / approval note:
{state["creator_approval_note"]}

ให้แก้งาน Creator ตาม note ด้านบน
อย่าทำซ้ำแบบเดิม
"""

    task = f"""
Current phase:
{state["phase"]}

Feature request:
{state["feature_request"]}

Designer output:
{state["designer_output"]}

{retry_note}

ทำเฉพาะส่วน Creator task

ต้องสร้าง:
1. asset spec
2. image prompt
3. Blender script draft เป็น code block ภาษา python

Blender script ต้อง:
- import bpy และ os ให้ครบ
- อ่าน export folder จาก environment variable AI_STUDIO_EXPORT_DIR
- สร้าง placeholder 3 object: cube, door/rectangle, sphere
- สำหรับ door/rectangle ห้ามใช้ bpy.ops.mesh.primitive_plane_add(size=(x, y)) เพราะ size ต้องเป็น float; ให้ใช้ cube แล้ว scale เป็น rectangle แทน
- ใส่ material สีชัดเจน
- ใส่ text label บน object
- ไม่ใช้ texture ภายนอก
- ไม่ใช้ addon พิเศษ
- export อย่างน้อย 1 ไฟล์เป็น .glb หรือ .fbx ไปที่ AI_STUDIO_EXPORT_DIR
- ห้ามใช้ path นอก project

ตอบเป็นภาษาไทย แต่ code block เป็น Python ได้
"""

    state["creator_output"] = await run_role(
        role_name="creator",
        prompt_file="creator.md",
        task=task,
    )

    blender_script = extract_python_code_block(state["creator_output"])
    state["creator_script_path"] = write_creator_file(
        filename="create_placeholder_assets.py",
        content=blender_script,
    )

    return state


def creator_blender_run_node(state: FeatureState) -> FeatureState:
    print("[4/11] Running Blender script from Creator output...")

    if not state["creator_script_path"]:
        state["creator_blender_result"] = "BLENDER_SKIPPED: creator_script_path is empty"
        return state

    state["creator_blender_result"] = run_blender_script(state["creator_script_path"])
    return state


async def creator_qa_node(state: FeatureState) -> FeatureState:
    print("[5/11] QA checking creator output and Blender result...")

    task = f"""
Current phase:
{state["phase"]}

Designer output:
{state["designer_output"]}

Creator output:
{state["creator_output"]}

Creator Blender script path:
{state["creator_script_path"]}

Creator Blender run result:
{state["creator_blender_result"]}

ตรวจเฉพาะ Creator QA target จาก Designer เท่านั้น
อย่าเอา Programmer target มาตัดสิน Creator

ให้ตรวจเพิ่มว่า:
- Creator มี Blender script draft แล้ว
- Blender run สำเร็จหรือไม่
- มี exported file ใน workspace/creator_outputs/exports หรือไม่
- script สร้าง placeholder object ตาม target
- script ไม่ใช้ texture ภายนอก
- script ไม่ใช้ addon พิเศษ
- script ไม่ export ออกนอก workspace

ถ้าเจอปัญหาแม้เล็กน้อย ให้ระบุในหัวข้อ ปัญหาที่บล็อกงาน, Requirement ที่ขาด หรือ สิ่งที่ต้องแก้
ถ้าผ่านแบบไม่มีปัญหา ให้เขียนให้ชัดว่า:
1. ผลตรวจ: ผ่าน
2. ปัญหาที่บล็อกงาน:
   - ไม่มี
3. Requirement ที่ขาด:
   - ไม่มี
4. สิ่งที่ต้องแก้:
   - ไม่มี

ต้องตอบเป็นภาษาไทยทั้งหมด และใช้ format ภาษาไทยจาก system prompt เท่านั้น
"""

    state["creator_qa_report"] = await run_role(
        role_name="qa_creator_check",
        prompt_file="qa.md",
        task=task,
    )

    state["creator_gate_status"] = analyze_qa_gate(state["creator_qa_report"])
    return state


def creator_auto_approval_node(state: FeatureState) -> FeatureState:
    print("[6/11] Creator QA clean pass. Auto approving creator output...")

    state["creator_approval_status"] = "AUTO_APPROVED_BY_QA"
    state["creator_approval_note"] = "Creator QA returned clean pass. User gate skipped."

    return state


def creator_human_approval_node(state: FeatureState) -> FeatureState:
    print("[6/11] Creator QA found issue. Marking rejection for unattended retry...")

    state["creator_approval_status"] = "REJECTED_BY_QA_UNATTENDED"
    state["creator_approval_note"] = (
        "Creator QA failed or required human approval. Unattended run rejects and retries "
        "until retry limit; approval-required work is skipped after the limit."
    )
    state["creator_retry_count"] += 1
    return state


def route_after_creator_qa(state: FeatureState) -> str:
    if state["creator_gate_status"] == "CLEAN_PASS":
        return "creator_auto_approval"

    return "creator_human_approval"


def route_after_creator_approval(state: FeatureState) -> str:
    if state["creator_approval_status"] in [
        "AUTO_APPROVED_BY_QA",
        "APPROVED_BY_USER_WITH_QA_NOTES",
        "APPROVED_BY_USER",
    ]:
        if state["programmer_required"]:
            return "programmer"
        return "final"

    if state["creator_approval_status"] in ["REJECTED_BY_USER", "REJECTED_BY_QA_UNATTENDED"]:
        if state["creator_retry_count"] <= MAX_CREATOR_RETRY:
            return "creator"

        state["final_status"] = "STOPPED_CREATOR_RETRY_LIMIT"
        return "final"

    return "final"


async def programmer_node(state: FeatureState) -> FeatureState:
    print(f"[7/11] Programmer creating implementation outputs... retry={state['programmer_retry_count']}")

    retry_note = ""
    if state["programmer_retry_count"] > 0:
        retry_note = f"""
Previous Programmer output:
{state["programmer_output"]}

Previous Programmer QA report:
{state["programmer_qa_report"]}

User rejection / approval note:
{state["programmer_approval_note"]}

ให้แก้งาน Programmer ตาม note ด้านบน
อย่าทำซ้ำแบบเดิม
"""

    task = f"""
Current phase:
{state["phase"]}

Feature request:
{state["feature_request"]}

Designer output:
{state["designer_output"]}

Creator required:
{state["creator_required"]}

Creator output:
{state["creator_output"]}

Creator Blender script path:
{state["creator_script_path"]}

Creator Blender run result:
{state["creator_blender_result"]}

Creator QA report:
{state["creator_qa_report"]}

Creator gate status:
{state["creator_gate_status"]}

Creator approval status:
{state["creator_approval_status"]}

Creator approval note:
{state["creator_approval_note"]}

{retry_note}

ทำเฉพาะ Programmer task
ใช้ Programmer QA target จาก Designer เป็นเป้าหมาย
สร้าง output ที่พร้อมใช้จริงสำหรับ implementation
อธิบายไฟล์, setup, และ validation ให้ชัดเจน
ถ้ามี edge case จาก Designer เช่น multiple objects in range ต้องระบุวิธี handle
"""

    task += """

Additional runtime instructions:
- Treat the workflow as implementation-first unless phase explicitly equals DESIGN_ONLY.
- Do not return draft-only, pseudo-code-only, or mock-only outputs.
- Describe real files, setup steps, and validation targets.
"""

    state["programmer_output"] = await run_role(
        role_name="programmer",
        prompt_file="programmer.md",
        task=task,
    )
    state["programmer_file_paths"] = write_programmer_output_files(state)
    return state


async def programmer_qa_node(state: FeatureState) -> FeatureState:
    print("[8/11] QA checking programmer output...")
    programmer_spec = get_programmer_output_spec_for_state(state)

    task = f"""
Current phase:
{state["phase"]}

Designer output:
{state["designer_output"]}

Programmer output:
{state["programmer_output"]}

ตรวจเฉพาะ Programmer QA target จาก Designer เท่านั้น
ให้หา blocker, edge case, missing requirement ที่เกี่ยวกับ implementation

ถ้าเจอปัญหาแม้เล็กน้อย เช่น ambiguity, edge case ไม่ครบ, missing requirement
ให้ระบุในหัวข้อ ปัญหาที่บล็อกงาน, Requirement ที่ขาด หรือ สิ่งที่ต้องแก้

ถ้าผ่านแบบไม่มีปัญหา ให้เขียนให้ชัดว่า:
1. ผลตรวจ: ผ่าน
2. ปัญหาที่บล็อกงาน:
   - ไม่มี
3. Requirement ที่ขาด:
   - ไม่มี
4. สิ่งที่ต้องแก้:
   - ไม่มี

ต้องตอบเป็นภาษาไทยทั้งหมด และใช้ format ภาษาไทยจาก system prompt เท่านั้น
"""

    task += f"""

Programmer output file paths:
{chr(10).join(state["programmer_file_paths"])}

Required programmer output files:
{chr(10).join(programmer_spec.file_contents.keys())}

Additional Programmer QA checks:
- Confirm all required output files exist.
- Confirm output files are under workspace/programmer_outputs only.
- Confirm the generated files satisfy the feature-specific implementation target from Designer.
"""

    state["programmer_qa_report"] = await run_role(
        role_name="qa_programmer_check",
        prompt_file="qa.md",
        task=task,
    )

    state["programmer_gate_status"] = analyze_qa_gate(state["programmer_qa_report"])
    deterministic_pass, deterministic_problems = validate_programmer_output_files(
        state,
        state["programmer_file_paths"],
    )
    if deterministic_pass:
        state["programmer_gate_status"] = "CLEAN_PASS"
        state["programmer_qa_report"] += (
            "\n\n---\n\n"
            "Deterministic file QA: PASS\n"
            "- Required programmer output files exist under workspace/programmer_outputs.\n"
            f"- Deterministic spec matched: {programmer_spec.key}.\n"
        )
    else:
        state["programmer_gate_status"] = "NEED_USER_GATE"
        state["programmer_qa_report"] += (
            "\n\n---\n\n"
            "Deterministic file QA: FAIL\n"
            + "\n".join(f"- {problem}" for problem in deterministic_problems)
            + "\n"
        )
    return state


def programmer_auto_approval_node(state: FeatureState) -> FeatureState:
    print("[9/11] Programmer QA clean pass. Auto approving programmer output...")

    state["programmer_approval_status"] = "AUTO_APPROVED_BY_QA"
    state["programmer_approval_note"] = "Programmer QA returned clean pass. User gate skipped."

    return state


def unity_implementation_node(state: FeatureState) -> FeatureState:
    print("[10/13] Preparing Unity implementation stage...")

    ok, message, project_path = validate_unity_project_path()
    state["unity_project_path"] = str(project_path)

    if not ok:
        state["unity_implementation_result"] = f"SKIPPED_UNITY_IMPLEMENTATION: {message}"
        state["unity_gate_status"] = "NEED_USER_GATE"
        return state

    if state["phase"] != "IMPLEMENTATION":
        state["unity_implementation_result"] = (
            "SKIPPED_UNITY_IMPLEMENTATION: Current phase is "
            f"{state['phase']}. Dry-run copy plan only.\n"
            f"{apply_copy_plan(dry_run=True, project_path=project_path)}"
        )
        state["unity_gate_status"] = "SKIPPED"
        return state

    state["unity_implementation_result"] = apply_copy_plan(dry_run=False, project_path=project_path)
    return state


def unity_batchmode_validation_node(state: FeatureState) -> FeatureState:
    print("[11/13] Running or skipping Unity batchmode validation...")

    if state["phase"] != "IMPLEMENTATION":
        state["unity_validation_result"] = (
            "SKIPPED_UNITY_VALIDATION: Current phase is "
            f"{state['phase']}. Unity batchmode requires IMPLEMENTATION phase."
        )
        return state

    state["unity_validation_result"] = run_unity_batchmode(log_name="unity_graph_validation.log")
    return state


def unity_scene_setup_node(state: FeatureState) -> FeatureState:
    print("[12/13] Running or skipping Unity scene setup...")
    programmer_spec = get_programmer_output_spec_for_state(state)

    if state["phase"] != "IMPLEMENTATION":
        state["unity_scene_setup_result"] = (
            "SKIPPED_UNITY_SCENE_SETUP: Scene/prefab modification requires IMPLEMENTATION phase "
            "and explicit approval."
        )
        return state

    state["unity_scene_setup_result"] = run_unity_batchmode(
        extra_args=["-executeMethod", programmer_spec.scene_setup_method],
        log_name="unity_graph_scene_setup.log",
    )
    return state


def unity_scene_validation_node(state: FeatureState) -> FeatureState:
    print("[13/13] Running or skipping Unity scene validation...")
    programmer_spec = get_programmer_output_spec_for_state(state)

    if state["phase"] != "IMPLEMENTATION":
        state["unity_scene_validation_result"] = (
            "SKIPPED_UNITY_SCENE_VALIDATION: Scene validation requires IMPLEMENTATION phase."
        )
        return state

    state["unity_scene_validation_result"] = run_unity_batchmode(
        extra_args=["-executeMethod", programmer_spec.scene_validation_method],
        log_name="unity_graph_scene_validation.log",
    )
    return state


async def unity_qa_node(state: FeatureState) -> FeatureState:
    print("[QA] QA checking Unity automation stage...")

    task = f"""
Current phase:
{state["phase"]}

Unity project path:
{state["unity_project_path"]}

Unity implementation result:
{state["unity_implementation_result"]}

Unity validation result:
{state["unity_validation_result"]}

Unity scene setup result:
{state["unity_scene_setup_result"]}

Unity scene validation result:
{state["unity_scene_validation_result"]}

ตรวจ Unity automation stage เท่านั้น
ถ้า phase เป็น IMPLEMENTATION ต้องตรวจว่า batchmode และ scene validation ผ่าน
ถ้าไม่ใช่ IMPLEMENTATION ให้ถือว่าเป็น design-only review และห้ามอ้างว่าแก้ Unity จริง
ต้องตอบเป็นภาษาไทยเท่านั้น
"""

    state["unity_qa_report"] = await run_role(
        role_name="qa_unity_check",
        prompt_file="qa.md",
        task=task,
    )
    state["unity_gate_status"] = analyze_qa_gate(state["unity_qa_report"])
    validation = parse_unity_result_text(state["unity_validation_result"])
    scene_setup = parse_unity_result_text(state["unity_scene_setup_result"])
    scene_validation = parse_unity_result_text(state["unity_scene_validation_result"])

    if state["phase"] == "IMPLEMENTATION":
        deterministic_results = [validation, scene_setup, scene_validation]
        if all(result["passed"] for result in deterministic_results):
            state["unity_gate_status"] = "CLEAN_PASS"
            state["unity_qa_report"] += (
                "\n\n---\n\n"
                "Deterministic Unity QA: PASS\n"
                "- Batchmode validation passed.\n"
                "- Scene setup passed.\n"
                "- Scene validation passed.\n"
            )
        else:
            state["unity_gate_status"] = "NEED_USER_GATE"
            state["unity_qa_report"] += (
                "\n\n---\n\n"
                "Deterministic Unity QA: FAIL\n"
                f"- Batchmode validation passed: {validation['passed']}\n"
                f"- Scene setup passed: {scene_setup['passed']}\n"
                f"- Scene validation passed: {scene_validation['passed']}\n"
            )
    return state


def unity_auto_approval_node(state: FeatureState) -> FeatureState:
    print("[Gate] Unity QA clean pass. Auto approving Unity stage...")

    state["unity_approval_status"] = "AUTO_APPROVED_BY_QA"
    state["unity_approval_note"] = "Unity QA returned clean pass. User gate skipped."
    return state


def unity_human_gate_node(state: FeatureState) -> FeatureState:
    print("[Gate] Unity stage needs human approval; marking skipped for unattended run...")

    state["unity_approval_status"] = "SKIPPED_NEEDS_USER_APPROVAL"
    state["unity_approval_note"] = (
        "Skipped because Unity implementation or QA required human approval during unattended run."
    )
    return state


def route_after_unity_qa(state: FeatureState) -> str:
    if state["unity_gate_status"] == "CLEAN_PASS":
        return "unity_auto_approval"
    return "unity_human_gate"


def programmer_human_approval_node(state: FeatureState) -> FeatureState:
    print("[9/11] Programmer QA found issue. Marking rejection for unattended retry...")

    state["programmer_approval_status"] = "REJECTED_BY_QA_UNATTENDED"
    state["programmer_approval_note"] = (
        "Programmer QA failed or required human approval. Unattended run rejects and retries "
        "until retry limit; approval-required work is skipped after the limit."
    )
    state["programmer_retry_count"] += 1
    return state


def route_after_programmer_qa(state: FeatureState) -> str:
    if state["programmer_gate_status"] == "CLEAN_PASS":
        return "programmer_auto_approval"

    return "programmer_human_approval"


def route_after_programmer_approval(state: FeatureState) -> str:
    if state["programmer_approval_status"] in [
        "AUTO_APPROVED_BY_QA",
        "APPROVED_BY_USER_WITH_QA_NOTES",
        "APPROVED_BY_USER",
    ]:
        return "unity_implementation"

    if state["programmer_approval_status"] in ["REJECTED_BY_USER", "REJECTED_BY_QA_UNATTENDED"]:
        if state["programmer_retry_count"] <= MAX_PROGRAMMER_RETRY:
            return "programmer"

        state["final_status"] = "STOPPED_PROGRAMMER_RETRY_LIMIT"
        return "final"

    return "final"


async def creator_qa_node(state: FeatureState) -> FeatureState:
    print("[5/11] Running creator evidence gate...")

    passed, problems, creator_validation = validate_creator_output_evidence(state)
    checks = [
        f"ตรวจ Creator output ใน phase {state['phase']}",
        f"ตรวจ Blender script path: {state['creator_script_path'] or 'none'}",
        "ตรวจ Blender run result",
        "ตรวจ exported files ใต้ workspace/creator_outputs/exports",
        "ตรวจ marker ขั้นต่ำของ Blender script",
    ]

    state["creator_qa_report"] = build_thai_evidence_report(
        passed=passed,
        checks=checks,
        blockers=problems if not passed else [],
        fixes=problems if not passed else [],
        recommendations=[
            "ผ่านตาม evidence gate ไม่ต้องแก้เพิ่ม"
            if passed
            else "แก้ Blender script หรือ export flow ตามรายการที่ fail แล้วรันใหม่"
        ],
        evidence_blocks=[format_creator_validation(creator_validation)],
    )
    state["creator_gate_status"] = "CLEAN_PASS" if passed else "NEED_USER_GATE"
    return state


async def programmer_qa_node(state: FeatureState) -> FeatureState:
    print("[8/11] Running programmer evidence gate...")
    programmer_spec = get_programmer_output_spec_for_state(state)
    file_label = programmer_output_file_label(state["phase"])

    deterministic_pass, deterministic_problems = validate_programmer_output_files(
        state,
        state["programmer_file_paths"],
    )

    checks = [
        f"ตรวจ Programmer output ใน phase {state['phase']}",
        f"ตรวจ deterministic spec: {programmer_spec.key}",
        f"ตรวจ required programmer {file_label} ใต้ workspace/programmer_outputs",
        "ตรวจ snippet marker ที่จำเป็นในแต่ละไฟล์",
    ]

    evidence_block = (
        "DETERMINISTIC_PROGRAMMER_GATE\n"
        f"Passed: {deterministic_pass}\n"
        f"Spec: {programmer_spec.key}\n"
        f"File kind: {file_label}\n"
        "Output files:\n"
        + "\n".join(state["programmer_file_paths"])
    )

    state["programmer_qa_report"] = build_thai_evidence_report(
        passed=deterministic_pass,
        checks=checks,
        blockers=deterministic_problems if not deterministic_pass else [],
        fixes=deterministic_problems if not deterministic_pass else [],
        recommendations=[
            "ผ่านตาม evidence gate ไม่ต้องแก้เพิ่ม"
            if deterministic_pass
            else "แก้ programmer output ให้ตรง deterministic spec แล้วรันใหม่"
        ],
        evidence_blocks=[evidence_block],
    )
    state["programmer_gate_status"] = "CLEAN_PASS" if deterministic_pass else "NEED_USER_GATE"
    return state


async def unity_qa_node(state: FeatureState) -> FeatureState:
    print("[QA] Running unity evidence gate...")

    if not is_implementation_phase(state["phase"]):
        implementation_skipped = state["unity_implementation_result"].startswith("SKIPPED_UNITY_IMPLEMENTATION")
        validation_skipped = state["unity_validation_result"].startswith("SKIPPED_UNITY_VALIDATION")
        scene_setup_skipped = state["unity_scene_setup_result"].startswith("SKIPPED_UNITY_SCENE_SETUP")
        scene_validation_skipped = state["unity_scene_validation_result"].startswith("SKIPPED_UNITY_SCENE_VALIDATION")
        passed = implementation_skipped and validation_skipped and scene_setup_skipped and scene_validation_skipped

        state["unity_qa_report"] = build_thai_evidence_report(
            passed=passed,
            checks=[
                f"ตรวจ Unity stage ใน phase {state['phase']}",
                "ตรวจว่าระบบ skip Unity implementation/validation ตาม phase ถูกต้อง",
            ],
            blockers=[] if passed else ["Unity stage ไม่ได้ skip ตาม phase ที่คาดไว้"],
            fixes=[] if passed else ["แก้ route หรือ phase handling ของ Unity stage"],
            recommendations=[
                "ผ่านตาม evidence gate"
                if passed
                else "ตรวจ phase handling ของ Unity stage อีกครั้ง"
            ],
        )
        state["unity_gate_status"] = "CLEAN_PASS" if passed else "NEED_USER_GATE"
        return state

    validation = parse_unity_result_text(state["unity_validation_result"])
    scene_setup = parse_unity_result_text(state["unity_scene_setup_result"])
    scene_validation = parse_unity_result_text(state["unity_scene_validation_result"])

    deterministic_results = [
        ("batchmode validation", validation),
        ("scene setup", scene_setup),
        ("scene validation", scene_validation),
    ]
    failed_steps = [
        f"{name} failed (return_code={result['return_code']}, errors={', '.join(result['error_markers']) or 'none'})"
        for name, result in deterministic_results
        if not result["passed"]
    ]
    passed = not failed_steps

    evidence_block = (
        "DETERMINISTIC_UNITY_GATE\n"
        f"Validation passed: {validation['passed']}\n"
        f"Scene setup passed: {scene_setup['passed']}\n"
        f"Scene validation passed: {scene_validation['passed']}"
    )

    state["unity_qa_report"] = build_thai_evidence_report(
        passed=passed,
        checks=[
            "ตรวจ Unity copy/apply stage",
            "ตรวจ batchmode validation",
            "ตรวจ scene setup",
            "ตรวจ scene validation",
        ],
        blockers=failed_steps,
        fixes=failed_steps,
        recommendations=[
            "ผ่านตาม evidence gate ไม่ต้องแก้เพิ่ม"
            if passed
            else "เปิด log ของ step ที่ fail แล้วแก้เฉพาะจุด"
        ],
        evidence_blocks=[evidence_block],
    )
    state["unity_gate_status"] = "CLEAN_PASS" if passed else "NEED_USER_GATE"
    return state


def creator_auto_approval_node(state: FeatureState) -> FeatureState:
    print("[6/11] Creator evidence gate clean pass. Auto approving creator output...")

    state["creator_approval_status"] = "AUTO_APPROVED_BY_QA"
    state["creator_approval_note"] = "Creator evidence gate passed. User gate skipped."
    return state


def programmer_auto_approval_node(state: FeatureState) -> FeatureState:
    print("[9/11] Programmer evidence gate clean pass. Auto approving programmer output...")

    state["programmer_approval_status"] = "AUTO_APPROVED_BY_QA"
    state["programmer_approval_note"] = "Programmer evidence gate passed. User gate skipped."
    return state


def unity_auto_approval_node(state: FeatureState) -> FeatureState:
    print("[Gate] Unity evidence gate clean pass. Auto approving Unity stage...")

    state["unity_approval_status"] = "AUTO_APPROVED_BY_QA"
    state["unity_approval_note"] = "Unity evidence gate passed. User gate skipped."
    return state


def final_node(state: FeatureState) -> FeatureState:
    print("[11/11] Writing report...")

    output_dir = ROOT / "workspace" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    final_status = state["final_status"] or "ROLE_GRAPH_OK"
    programmer_file_heading = (
        "Programmer Output File Paths" if is_implementation_phase(state["phase"]) else "Programmer Draft File Paths"
    )

    report = f"""# AI Studio Role-based Report

## Feature Request

{state["feature_request"]}

---

## Task Metadata

Task id: {state.get("task_id", "") or "none"}

Task file: {state.get("task_file", "") or "none"}

---

## Phase

{state["phase"]}

---

## 1. Manager Output

{state["manager_output"]}

---

## 2. Designer Output

{state["designer_output"]}

---

## 2.1 Routing Decision

Creator required: {state["creator_required"]}

Programmer required: {state["programmer_required"]}

---

## 3. Creator Output

{state["creator_output"]}

---

## 3.1 Creator Blender Script Path

{state["creator_script_path"]}

---

## 3.2 Creator Blender Result

{state["creator_blender_result"]}

---

## 4. Creator Evidence Report

{state["creator_qa_report"]}

---

## 4.1 Creator Gate Status

{state["creator_gate_status"]}

---

## 4.2 Creator Retry Count

{state["creator_retry_count"]}

---

## 5. Creator Approval Status

{state["creator_approval_status"]}

---

## 5.1 Creator Approval Note

{state["creator_approval_note"]}

---

## 6. Programmer Output

{state["programmer_output"]}

---

## 6.1 {programmer_file_heading}

{chr(10).join(state["programmer_file_paths"])}

---

## 7. Programmer Evidence Report

{state["programmer_qa_report"]}

---

## 7.1 Programmer Gate Status

{state["programmer_gate_status"]}

---

## 7.2 Programmer Retry Count

{state["programmer_retry_count"]}

---

## 8. Programmer Approval Status

{state["programmer_approval_status"]}

---

## 8.1 Programmer Approval Note

{state["programmer_approval_note"]}

---

## 9. Unity Project Path

{state["unity_project_path"]}

---

## 9.1 Unity Implementation Result

{state["unity_implementation_result"]}

---

## 9.2 Unity Validation Result

{state["unity_validation_result"]}

---

## 9.3 Unity Scene Setup Result

{state["unity_scene_setup_result"]}

---

## 9.4 Unity Scene Validation Result

{state["unity_scene_validation_result"]}

---

## 9.5 Unity Evidence Report

{state["unity_qa_report"]}

---

## 9.6 Unity Gate Status

{state["unity_gate_status"]}

---

## 9.7 Unity Approval Status

{state["unity_approval_status"]}

---

## 9.8 Unity Approval Note

{state["unity_approval_note"]}

---

## Final Status

{final_status}
"""

    report_path = output_dir / "latest_report.md"
    report_path.write_text(report, encoding="utf-8")

    codex_response = f"""# AI Office Response To Codex

## Status

{final_status}

## Phase

{state["phase"]}

## Gate Summary

- Creator gate: {state["creator_gate_status"] or "SKIPPED"}
- Programmer gate: {state["programmer_gate_status"] or "SKIPPED"}
- Unity gate: {state["unity_gate_status"] or "SKIPPED"}

## Approval Summary

- Creator approval: {state["creator_approval_status"] or "SKIPPED"}
- Programmer approval: {state["programmer_approval_status"] or "SKIPPED"}
- Unity approval: {state["unity_approval_status"] or "SKIPPED"}

## Output Files

{chr(10).join(f"- {path}" for path in state["programmer_file_paths"]) or "- none"}

## Codex Next Action

Read `workspace/reports/latest_report.md` only if detailed role output is needed. Otherwise use this response as the complete Office AI handoff after evidence gate review.
"""

    codex_response_path = output_dir / "codex_response.md"
    codex_response_path.write_text(codex_response, encoding="utf-8")

    state["final_status"] = f"{final_status} | Report written: {report_path}"
    return state


def build_graph():
    graph = StateGraph(FeatureState)

    graph.add_node("manager", manager_node)
    graph.add_node("designer", designer_node)
    graph.add_node("skip_creator", skip_creator_node)
    graph.add_node("creator", creator_node)
    graph.add_node("creator_blender_run", creator_blender_run_node)
    graph.add_node("creator_qa", creator_qa_node)
    graph.add_node("creator_auto_approval", creator_auto_approval_node)
    graph.add_node("creator_human_approval", creator_human_approval_node)
    graph.add_node("programmer", programmer_node)
    graph.add_node("programmer_qa", programmer_qa_node)
    graph.add_node("programmer_auto_approval", programmer_auto_approval_node)
    graph.add_node("programmer_human_approval", programmer_human_approval_node)
    graph.add_node("unity_implementation", unity_implementation_node)
    graph.add_node("unity_batchmode_validation", unity_batchmode_validation_node)
    graph.add_node("unity_scene_setup", unity_scene_setup_node)
    graph.add_node("unity_scene_validation", unity_scene_validation_node)
    graph.add_node("unity_qa", unity_qa_node)
    graph.add_node("unity_auto_approval", unity_auto_approval_node)
    graph.add_node("unity_human_gate", unity_human_gate_node)
    graph.add_node("final", final_node)

    graph.set_entry_point("manager")

    graph.add_edge("manager", "designer")

    graph.add_conditional_edges(
        "designer",
        route_after_designer,
        {
            "creator": "creator",
            "skip_creator": "skip_creator",
        },
    )

    graph.add_conditional_edges(
        "skip_creator",
        route_after_skip_creator,
        {
            "programmer": "programmer",
            "final": "final",
        },
    )

    graph.add_edge("creator", "creator_blender_run")
    graph.add_edge("creator_blender_run", "creator_qa")

    graph.add_conditional_edges(
        "creator_qa",
        route_after_creator_qa,
        {
            "creator_auto_approval": "creator_auto_approval",
            "creator_human_approval": "creator_human_approval",
        },
    )

    graph.add_conditional_edges(
        "creator_auto_approval",
        route_after_creator_approval,
        {
            "programmer": "programmer",
            "creator": "creator",
            "final": "final",
        },
    )

    graph.add_conditional_edges(
        "creator_human_approval",
        route_after_creator_approval,
        {
            "programmer": "programmer",
            "creator": "creator",
            "final": "final",
        },
    )

    graph.add_edge("programmer", "programmer_qa")

    graph.add_conditional_edges(
        "programmer_qa",
        route_after_programmer_qa,
        {
            "programmer_auto_approval": "programmer_auto_approval",
            "programmer_human_approval": "programmer_human_approval",
        },
    )

    graph.add_conditional_edges(
        "programmer_auto_approval",
        route_after_programmer_approval,
        {
            "final": "final",
            "programmer": "programmer",
            "unity_implementation": "unity_implementation",
        },
    )

    graph.add_conditional_edges(
        "programmer_human_approval",
        route_after_programmer_approval,
        {
            "final": "final",
            "programmer": "programmer",
            "unity_implementation": "unity_implementation",
        },
    )

    graph.add_edge("unity_implementation", "unity_batchmode_validation")
    graph.add_edge("unity_batchmode_validation", "unity_scene_setup")
    graph.add_edge("unity_scene_setup", "unity_scene_validation")
    graph.add_edge("unity_scene_validation", "unity_qa")

    graph.add_conditional_edges(
        "unity_qa",
        route_after_unity_qa,
        {
            "unity_auto_approval": "unity_auto_approval",
            "unity_human_gate": "unity_human_gate",
        },
    )

    graph.add_edge("unity_auto_approval", "final")
    graph.add_edge("unity_human_gate", "final")

    graph.add_edge("final", END)

    return graph.compile()


async def main():
    app = build_graph()
    default_feature_request = """
Create and validate a real Unity interaction vertical slice.
The player should press E to interact with nearby objects.
Include placeholder assets, implementation scripts, scene setup, scene validation, and QA-ready reports.
"""

    feature_request = os.getenv("AI_STUDIO_FEATURE_REQUEST", default_feature_request)
    phase = os.getenv("AI_STUDIO_PHASE", "IMPLEMENTATION")
    task_file = os.getenv("AI_STUDIO_TASK_FILE")
    task_id = ""

    if task_file:
        task_path = Path(task_file)
        if not task_path.is_absolute():
            task_path = ROOT / task_path
        task_data = json.loads(task_path.read_text(encoding="utf-8"))
        task_id = task_data.get("id", "")
        feature_request = task_data.get("request", feature_request)
        phase = task_data.get("phase", phase)

    result = await app.ainvoke({
        "task_id": task_id,
        "task_file": task_file or "",
        "feature_request": feature_request,
        "phase": phase,
        "manager_output": "",
        "designer_output": "",
        "creator_required": True,
        "programmer_required": True,
        "creator_output": "",
        "creator_script_path": "",
        "creator_blender_result": "",
        "creator_qa_report": "",
        "creator_gate_status": "",
        "creator_approval_status": "",
        "creator_approval_note": "",
        "creator_retry_count": 0,
        "programmer_output": "",
        "programmer_file_paths": [],
        "programmer_qa_report": "",
        "programmer_gate_status": "",
        "programmer_approval_status": "",
        "programmer_approval_note": "",
        "programmer_retry_count": 0,
        "unity_project_path": str(get_unity_project_path()),
        "unity_implementation_result": "",
        "unity_validation_result": "",
        "unity_scene_setup_result": "",
        "unity_scene_validation_result": "",
        "unity_qa_report": "",
        "unity_gate_status": "",
        "unity_approval_status": "",
        "unity_approval_note": "",
        "unity_retry_count": 0,
        "final_status": "",
    })

    print(result["final_status"])


if __name__ == "__main__":
    asyncio.run(main())
