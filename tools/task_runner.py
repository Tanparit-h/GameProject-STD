import os
import subprocess
import sys
from pathlib import Path

from tools.task_registry import REGISTRY_PATH, TASKS_DIR, load_registry, validate_registry

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CODEX_RESPONSE = PROJECT_ROOT / "workspace" / "reports" / "codex_response.md"


def find_task_file(task_id: str) -> Path:
    registry = load_registry(REGISTRY_PATH)
    for entry in registry.get("tasks", []):
        if entry.get("id") == task_id:
            return TASKS_DIR / entry["file"]
    raise KeyError(f"Task id not found: {task_id}")


def build_task_command(task_id: str) -> tuple[list[str], dict[str, str]]:
    ok, problems = validate_registry()
    if not ok:
        raise ValueError("Task registry invalid: " + "; ".join(problems))

    task_file = find_task_file(task_id)
    env = os.environ.copy()
    env["AI_STUDIO_TASK_FILE"] = str(task_file.relative_to(PROJECT_ROOT))
    return [sys.executable, "-m", "app.main_graph"], env


def run_task(task_id: str, dry_run: bool = True, response_only: bool = False) -> str:
    command, env = build_task_command(task_id)
    if dry_run:
        return (
            "TASK_RUNNER_DRY_RUN\n"
            f"Task id: {task_id}\n"
            f"AI_STUDIO_TASK_FILE: {env['AI_STUDIO_TASK_FILE']}\n"
            "Command: "
            + " ".join(command)
        )

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=2400,
    )
    if response_only:
        response_text = CODEX_RESPONSE.read_text(encoding="utf-8", errors="replace") if CODEX_RESPONSE.exists() else ""
        return (
            "TASK_RUNNER_RESPONSE_ONLY\n"
            f"Task id: {task_id}\n"
            f"Exit code: {result.returncode}\n"
            f"Codex response path: {CODEX_RESPONSE}\n"
            f"{response_text}"
        )

    return (
        "TASK_RUNNER_RESULT\n"
        f"Task id: {task_id}\n"
        f"Exit code: {result.returncode}\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )


def main() -> int:
    task_id = sys.argv[1] if len(sys.argv) > 1 else "feature-interaction-v1"
    dry_run = "--run" not in sys.argv
    response_only = "--response-only" in sys.argv
    print(run_task(task_id, dry_run=dry_run, response_only=response_only))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
