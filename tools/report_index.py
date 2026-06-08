import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_DIR = PROJECT_ROOT / "workspace"
REPORTS_DIR = WORKSPACE_DIR / "reports"
TASKS_DIR = WORKSPACE_DIR / "tasks"
APPROVAL_LOG = WORKSPACE_DIR / "approvals" / "approval_log.jsonl"
UNITY_PROJECT = PROJECT_ROOT / "game_project" / "STDProject"


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
    latest_report = REPORTS_DIR / "latest_report.md"
    latest_text = latest_report.read_text(encoding="utf-8", errors="replace") if latest_report.exists() else ""

    report_files = sorted(path.name for path in REPORTS_DIR.glob("*.md")) if REPORTS_DIR.exists() else []
    task_files = sorted(path.name for path in TASKS_DIR.glob("*.json")) if TASKS_DIR.exists() else []
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
        "latest_report_clean": all(
            marker in latest_text
            for marker in [
                "ROLE_GRAPH_OK",
                "CLEAN_PASS",
                "Deterministic Unity QA: PASS",
            ]
        ),
        "reports": report_files,
        "tasks": task_files,
        "approval_count": approval_count,
    }


def write_report_index(status: dict[str, object]) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    index_path = REPORTS_DIR / "index.md"
    status_path = REPORTS_DIR / "status.json"

    status_path.write_text(json.dumps(status, indent=2), encoding="utf-8")

    reports = "\n".join(f"- `{name}`" for name in status["reports"])
    tasks = "\n".join(f"- `{name}`" for name in status["tasks"]) or "- none"

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
