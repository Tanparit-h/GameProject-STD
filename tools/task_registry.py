import json
from pathlib import Path
from tools.programmer_output_specs import get_programmer_family_definition

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = PROJECT_ROOT / "workspace" / "tasks"
REGISTRY_PATH = TASKS_DIR / "task_registry.json"

REQUIRED_TASK_FIELDS = ["id", "family", "phase", "title", "request", "approval"]


def load_registry(path: Path = REGISTRY_PATH) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_task_file(path: Path) -> tuple[bool, list[str]]:
    problems: list[str] = []
    data = json.loads(path.read_text(encoding="utf-8"))
    for field in REQUIRED_TASK_FIELDS:
        if field not in data:
            problems.append(f"{path.name} missing field: {field}")
    family = data.get("family", "")
    if family and get_programmer_family_definition(family) is None:
        problems.append(f"{path.name} uses unknown family: {family}")
    if "approval" in data and "implementation" not in data["approval"]:
        problems.append(f"{path.name} missing approval.implementation")
    return not problems, problems


def validate_registry(path: Path = REGISTRY_PATH) -> tuple[bool, list[str]]:
    problems: list[str] = []
    registry = load_registry(path)
    seen_ids: set[str] = set()

    for entry in registry.get("tasks", []):
        task_id = entry.get("id", "")
        task_file = entry.get("file", "")
        if not task_id:
            problems.append("registry entry missing id")
        if task_id in seen_ids:
            problems.append(f"duplicate task id: {task_id}")
        seen_ids.add(task_id)

        task_path = TASKS_DIR / task_file
        if not task_path.exists():
            problems.append(f"registered task file missing: {task_file}")
            continue

        ok, task_problems = validate_task_file(task_path)
        problems.extend(task_problems)
        if ok:
            task_data = json.loads(task_path.read_text(encoding="utf-8"))
            if task_data["id"] != task_id:
                problems.append(f"registry id mismatch for {task_file}: {task_id} != {task_data['id']}")

    return not problems, problems


def list_tasks(path: Path = REGISTRY_PATH) -> list[dict[str, str]]:
    registry = load_registry(path)
    tasks: list[dict[str, str]] = []
    for entry in registry.get("tasks", []):
        task_path = TASKS_DIR / entry.get("file", "")
        task_data = {}
        if task_path.exists():
            task_data = json.loads(task_path.read_text(encoding="utf-8"))
        tasks.append(
            {
                "id": entry.get("id", ""),
                "file": entry.get("file", ""),
                "status": entry.get("status", ""),
                "family": task_data.get("family", ""),
                "family_support": (
                    get_programmer_family_definition(task_data.get("family", "")).support_level
                    if get_programmer_family_definition(task_data.get("family", "")) is not None
                    else ""
                ),
                "phase": task_data.get("phase", ""),
                "title": task_data.get("title", ""),
            }
        )
    return tasks


def main() -> int:
    ok, problems = validate_registry()
    print("TASK_REGISTRY_VALIDATION")
    print(f"Passed: {ok}")
    if problems:
        print("Problems:")
        for problem in problems:
            print(f"- {problem}")
    else:
        print("Problems: none")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
