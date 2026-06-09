import subprocess
from datetime import datetime, timezone
from pathlib import Path

from tools.report_index import collect_status
from tools.task_registry import list_tasks
from tools.approval_log import read_approvals

PROJECT_ROOT = Path(__file__).resolve().parents[1]
UNITY_PROJECT = PROJECT_ROOT / "game_project" / "STDProject"
REPORTS_DIR = PROJECT_ROOT / "workspace" / "reports"
RELEASE_NOTES_PATH = REPORTS_DIR / "release_notes.md"


def git_log(cwd: Path, limit: int = 12) -> list[str]:
    result = subprocess.run(
        ["git", "log", "--oneline", f"-{limit}"],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        return [result.stderr.strip()]
    return [line for line in result.stdout.splitlines() if line.strip()]


def build_release_notes() -> str:
    status = collect_status()
    tasks = list_tasks()
    approvals = read_approvals()

    task_lines = "\n".join(
        f"- `{task['id']}`: `{task['status']}` `{task['family']}` `{task['family_support']}` `{task['phase']}` - {task['title']}"
        for task in tasks
    )
    approval_lines = "\n".join(
        f"- `{record.get('decision', '')}` `{record.get('task_id', '')}` "
        f"`{record.get('phase', '')}` by `{record.get('owner', '')}`: {record.get('reason', '')}"
        for record in approvals
    ) or "- none"
    root_commits = "\n".join(f"- {line}" for line in git_log(PROJECT_ROOT))
    unity_commits = "\n".join(f"- {line}" for line in git_log(UNITY_PROJECT))

    return f"""# AI Game Studio Release Notes Draft

Generated at: `{datetime.now(timezone.utc).isoformat()}`

## Release State

- Root HEAD: `{status['root_head']}`
- Root status: `{status['root_status']}`
- Unity HEAD: `{status['unity_head']}`
- Unity status: `{status['unity_status']}`
- Latest report clean: `{status['latest_report_clean']}`
- Approval records: `{status['approval_count']}`

## Included Capabilities

- Release-gate-clean Unity vertical slice for player interaction.
- Deterministic task family registry with fail-closed blocking for unsupported families.
- Multi-feature task registry.
- Approval record log.
- Static dashboard generator.
- Office CLI for status, dashboard, release gate, task runs, family inspection, and family scaffolding.
- Deterministic validation for creator exports, task registry, Unity logs, and latest reports.

## Task Status

{task_lines}

## Approval Records

{approval_lines}

## Recent Root Commits

{root_commits}

## Recent Unity Commits

{unity_commits}

## Validation Command

```powershell
.\\.venv\\Scripts\\python.exe -m tools.release_gate
```

## Release Blockers

- Push/PR/release requires explicit user approval.
- Choosing the next Unity implementation feature requires product direction.
"""


def write_release_notes() -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    RELEASE_NOTES_PATH.write_text(build_release_notes(), encoding="utf-8")
    return RELEASE_NOTES_PATH


def main() -> int:
    path = write_release_notes()
    print(f"Release notes written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
