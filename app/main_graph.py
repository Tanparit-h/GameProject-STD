import asyncio
import re
from pathlib import Path
from langgraph.graph import StateGraph, END

from app.state import FeatureState
from autogen_teams.role_runner import run_role
from tools.creator_file_tool import write_creator_file
from tools.blender_tool import run_blender_script

ROOT = Path(__file__).resolve().parents[1]

MAX_CREATOR_RETRY = 2
MAX_PROGRAMMER_RETRY = 2


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
    pattern = rf"{label}\s*required\s*:\s*(yes|no|true|false)"
    match = re.search(pattern, text, re.IGNORECASE)

    if not match:
        return default

    value = match.group(1).lower()
    return value in ["yes", "true"]


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
    print("[6/11] Creator QA found issue. Human approval required...")

    print("\n================ CREATOR OUTPUT ================\n")
    print(state["creator_output"])

    print("\n================ CREATOR BLENDER RESULT ================\n")
    print(state["creator_blender_result"])

    print("\n================ CREATOR QA REPORT ================\n")
    print(state["creator_qa_report"])

    print("\n====================================================\n")

    while True:
        decision = input("Approve creator output anyway? Type 'y' to approve, 'n' to reject and retry: ").strip().lower()

        if decision == "y":
            state["creator_approval_status"] = "APPROVED_BY_USER_WITH_QA_NOTES"
            state["creator_approval_note"] = "User approved creator output despite QA notes."
            return state

        if decision == "n":
            note = input("Reason for rejection / fix instruction: ").strip()
            state["creator_approval_status"] = "REJECTED_BY_USER"
            state["creator_approval_note"] = note
            state["creator_retry_count"] += 1
            return state

        print("Invalid input. Please type 'y' or 'n'.")


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

    if state["creator_approval_status"] == "REJECTED_BY_USER":
        if state["creator_retry_count"] <= MAX_CREATOR_RETRY:
            return "creator"

        state["final_status"] = "STOPPED_CREATOR_RETRY_LIMIT"
        return "final"

    return "final"


async def programmer_node(state: FeatureState) -> FeatureState:
    print(f"[7/11] Programmer creating implementation plan... retry={state['programmer_retry_count']}")

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
ใน phase PROTOTYPE_PLAN อนุญาตให้สร้าง code draft, pseudo-code, Unity setup steps ได้
แต่ยังไม่ต้องแก้ Unity project จริง

ถ้ามี edge case จาก Designer เช่น multiple objects in range ต้องระบุวิธี handle
หลีกเลี่ยงตัวแปรที่ดูเหมือน real Unity dependency ถ้าเป็น pseudo-code ให้ตั้งชื่อเป็น MockedPlayer, MockedObject
"""

    state["programmer_output"] = await run_role(
        role_name="programmer",
        prompt_file="programmer.md",
        task=task,
    )
    return state


async def programmer_qa_node(state: FeatureState) -> FeatureState:
    print("[8/11] QA checking programmer output...")

    task = f"""
Current phase:
{state["phase"]}

Designer output:
{state["designer_output"]}

Programmer output:
{state["programmer_output"]}

ตรวจเฉพาะ Programmer QA target จาก Designer เท่านั้น
อย่า fail เพราะมี code draft ถ้า phase = PROTOTYPE_PLAN
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

    state["programmer_qa_report"] = await run_role(
        role_name="qa_programmer_check",
        prompt_file="qa.md",
        task=task,
    )

    state["programmer_gate_status"] = analyze_qa_gate(state["programmer_qa_report"])
    return state


def programmer_auto_approval_node(state: FeatureState) -> FeatureState:
    print("[9/11] Programmer QA clean pass. Auto approving programmer output...")

    state["programmer_approval_status"] = "AUTO_APPROVED_BY_QA"
    state["programmer_approval_note"] = "Programmer QA returned clean pass. User gate skipped."

    return state


def programmer_human_approval_node(state: FeatureState) -> FeatureState:
    print("[9/11] Programmer QA found issue. Human approval required...")

    print("\n================ PROGRAMMER OUTPUT ================\n")
    print(state["programmer_output"])

    print("\n================ PROGRAMMER QA REPORT ================\n")
    print(state["programmer_qa_report"])

    print("\n======================================================\n")

    while True:
        decision = input("Approve programmer output anyway? Type 'y' to approve, 'n' to reject and retry: ").strip().lower()

        if decision == "y":
            state["programmer_approval_status"] = "APPROVED_BY_USER_WITH_QA_NOTES"
            state["programmer_approval_note"] = "User approved programmer output despite QA notes."
            return state

        if decision == "n":
            note = input("Reason for rejection / fix instruction: ").strip()
            state["programmer_approval_status"] = "REJECTED_BY_USER"
            state["programmer_approval_note"] = note
            state["programmer_retry_count"] += 1
            return state

        print("Invalid input. Please type 'y' or 'n'.")


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
        return "final"

    if state["programmer_approval_status"] == "REJECTED_BY_USER":
        if state["programmer_retry_count"] <= MAX_PROGRAMMER_RETRY:
            return "programmer"

        state["final_status"] = "STOPPED_PROGRAMMER_RETRY_LIMIT"
        return "final"

    return "final"


def final_node(state: FeatureState) -> FeatureState:
    print("[11/11] Writing report...")

    output_dir = ROOT / "workspace" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    final_status = state["final_status"] or "ROLE_GRAPH_OK"

    report = f"""# AI Studio Role-based Report

## Feature Request

{state["feature_request"]}

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

## 4. Creator QA Report

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

## 7. Programmer QA Report

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

## Final Status

{final_status}
"""

    report_path = output_dir / "latest_report.md"
    report_path.write_text(report, encoding="utf-8")

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
        },
    )

    graph.add_conditional_edges(
        "programmer_human_approval",
        route_after_programmer_approval,
        {
            "final": "final",
            "programmer": "programmer",
        },
    )

    graph.add_edge("final", END)

    return graph.compile()


async def main():
    app = build_graph()

    result = await app.ainvoke({
        "feature_request": """
สร้างระบบ prototype:
Player กด E เพื่อ interact กับ object ใกล้ตัว
ต้องมี asset placeholder สำหรับ object ที่ interact ได้
ยังไม่ต้องแก้ Unity project จริง
ขอ design spec, asset plan, implementation plan, และ QA checklist
""",
        "phase": "PROTOTYPE_PLAN",
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
        "programmer_qa_report": "",
        "programmer_gate_status": "",
        "programmer_approval_status": "",
        "programmer_approval_note": "",
        "programmer_retry_count": 0,
        "final_status": "",
    })

    print(result["final_status"])


if __name__ == "__main__":
    asyncio.run(main())