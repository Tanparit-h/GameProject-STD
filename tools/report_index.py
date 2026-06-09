import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from tools.task_registry import list_tasks

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_DIR = PROJECT_ROOT / "workspace"
REPORTS_DIR = WORKSPACE_DIR / "reports"
TASKS_DIR = WORKSPACE_DIR / "tasks"
APPROVAL_LOG = WORKSPACE_DIR / "approvals" / "approval_log.jsonl"
LATEST_REPORT = REPORTS_DIR / "latest_report.md"
UNITY_PROJECT = PROJECT_ROOT / "game_project" / "STDProject"


def extract_report_section(text: str, heading: str) -> str:
    pattern = rf"## {re.escape(heading)}\s*\n\n(.*?)(?:\n\n---|\Z)"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return ""
    return match.group(1).strip()


def parse_latest_report_summary(text: str) -> dict[str, object]:
    def metadata_value(label: str) -> str:
        match = re.search(rf"{re.escape(label)}:\s*(.+)", text)
        return match.group(1).strip() if match else ""

    return {
        "task_id": metadata_value("Task id"),
        "task_file": metadata_value("Task file"),
        "task_family": metadata_value("Task family"),
        "phase": extract_report_section(text, "Phase"),
        "creator_required": metadata_value("Creator required"),
        "programmer_required": metadata_value("Programmer required"),
        "creator_gate_status": extract_report_section(text, "4.1 Creator Gate Status"),
        "creator_approval_status": extract_report_section(text, "5. Creator Approval Status"),
        "programmer_gate_status": extract_report_section(text, "7.1 Programmer Gate Status"),
        "programmer_approval_status": extract_report_section(text, "8. Programmer Approval Status"),
        "unity_gate_status": extract_report_section(text, "9.6 Unity Gate Status"),
        "unity_approval_status": extract_report_section(text, "9.7 Unity Approval Status"),
        "final_status": extract_report_section(text, "Final Status"),
    }


def run_git(args: list[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        return result.stderr.strip()
    return result.stdout.strip()


def collect_status() -> dict[str, object]:
    latest_report = LATEST_REPORT
    latest_text = latest_report.read_text(encoding="utf-8", errors="replace") if latest_report.exists() else ""
    latest_report_summary = parse_latest_report_summary(latest_text) if latest_text else {}

    report_files = sorted(path.name for path in REPORTS_DIR.glob("*.md")) if REPORTS_DIR.exists() else []
    task_files = sorted(path.name for path in TASKS_DIR.glob("*.json")) if TASKS_DIR.exists() else []
    task_details = list_tasks() if (TASKS_DIR / "task_registry.json").exists() else []
    approval_count = 0
    if APPROVAL_LOG.exists():
        approval_count = len([line for line in APPROVAL_LOG.read_text(encoding="utf-8").splitlines() if line.strip()])

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root_head": run_git(["log", "--oneline", "-1"], PROJECT_ROOT),
        "root_status": run_git(["status", "--short"], PROJECT_ROOT) or "clean",
        "unity_head": run_git(["log", "--oneline", "-1"], UNITY_PROJECT),
        "unity_status": run_git(["status", "--short"], UNITY_PROJECT) or "clean",
        "latest_report_exists": latest_report.exists(),
        "latest_report_clean": (
            "ROLE_GRAPH_OK" in latest_text
            and "CLEAN_PASS" in latest_text
            and "## Phase\n\nIMPLEMENTATION" in latest_text
            and "DETERMINISTIC_UNITY_GATE" in latest_text
            and "Validation passed: True" in latest_text
            and "Scene setup passed: True" in latest_text
            and "Scene validation passed: True" in latest_text
        ),
        "reports": report_files,
        "tasks": task_files,
        "task_details": task_details,
        "approval_count": approval_count,
        "latest_report_summary": latest_report_summary,
    }


def write_report_index(status: dict[str, object]) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    index_path = REPORTS_DIR / "index.md"
    status_path = REPORTS_DIR / "status.json"

    status_path.write_text(json.dumps(status, indent=2), encoding="utf-8")

    reports = "\n".join(f"- `{name}`" for name in status["reports"])
    tasks = "\n".join(
        f"- `{task['id']}` `{task['status']}` `{task['family']}` `{task['family_support']}` `{task['phase']}` - {task['title']}"
        for task in status["task_details"]
    ) or "- none"

    content = f"""# AI Game Studio Dashboard Index

## Current Status

- Generated at: `{status["generated_at"]}`
- Root HEAD: `{status["root_head"]}`
- Root status: `{status["root_status"]}`
- Unity HEAD: `{status["unity_head"]}`
- Unity status: `{status["unity_status"]}`
- Latest report exists: `{status["latest_report_exists"]}`
- Latest report clean: `{status["latest_report_clean"]}`
- Approval records: `{status["approval_count"]}`

## Latest Run

- Task id: `{status["latest_report_summary"].get("task_id", "none") or "none"}`
- Task family: `{status["latest_report_summary"].get("task_family", "none") or "none"}`
- Phase: `{status["latest_report_summary"].get("phase", "none") or "none"}`
- Final status: `{status["latest_report_summary"].get("final_status", "none") or "none"}`
- Creator gate: `{status["latest_report_summary"].get("creator_gate_status", "none") or "none"}`
- Programmer gate: `{status["latest_report_summary"].get("programmer_gate_status", "none") or "none"}`
- Unity gate: `{status["latest_report_summary"].get("unity_gate_status", "none") or "none"}`

## Task Queue

{tasks}

## Reports

{reports}

## Release Gate

Run:

```powershell
.\\.venv\\Scripts\\python.exe -m tools.release_gate
```
"""
    index_path.write_text(content, encoding="utf-8")
    return index_path


def main() -> int:
    index_path = write_report_index(collect_status())
    print(f"Report index written: {index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
