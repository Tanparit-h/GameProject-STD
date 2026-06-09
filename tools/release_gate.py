import subprocess
import sys
from pathlib import Path

from tools.unity_tool import parse_unity_result_text, run_unity_batchmode
from tools.report_index import collect_status
from tools.creator_asset_validator import format_creator_validation, validate_creator_exports
from tools.task_registry import validate_registry

PROJECT_ROOT = Path(__file__).resolve().parents[1]
UNITY_PROJECT = PROJECT_ROOT / "game_project" / "STDProject"
LATEST_REPORT = PROJECT_ROOT / "workspace" / "reports" / "latest_report.md"


def run_command(command: list[str], cwd: Path) -> tuple[bool, str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output = result.stdout + result.stderr
    return result.returncode == 0, output


def git_clean(cwd: Path) -> tuple[bool, str]:
    ok, output = run_command(["git", "status", "--short"], cwd)
    if not ok:
        return False, output
    if output.strip():
        return False, output
    return True, "clean"


def latest_report_clean() -> tuple[bool, str]:
    if not LATEST_REPORT.exists():
        return False, f"Missing latest report: {LATEST_REPORT}"

    text = LATEST_REPORT.read_text(encoding="utf-8", errors="replace")
    required_markers = [
        "## Final Status",
        "ROLE_GRAPH_OK",
        "## 9.6 Unity Gate Status",
        "CLEAN_PASS",
        "Deterministic Unity QA: PASS",
    ]
    missing = [marker for marker in required_markers if marker not in text]
    if missing:
        return False, "Missing latest report markers: " + ", ".join(missing)
    return True, "latest report clean"


def dashboard_index_clean() -> tuple[bool, str]:
    status = collect_status()
    if not status["latest_report_clean"]:
        return False, "dashboard status says latest report is not clean"
    if status["unity_status"] != "clean":
        return False, f"dashboard status says Unity is dirty: {status['unity_status']}"
    return True, "dashboard status clean"


def main() -> int:
    checks: list[tuple[str, bool, str]] = []

    root_clean, root_output = git_clean(PROJECT_ROOT)
    checks.append(("root git clean", root_clean, root_output))

    unity_clean, unity_output = git_clean(UNITY_PROJECT)
    checks.append(("unity git clean", unity_clean, unity_output))

    tests_ok, tests_output = run_command([sys.executable, "-m", "unittest", "discover", "-p", "test_*.py"], PROJECT_ROOT)
    checks.append(("root unit tests", tests_ok, tests_output))

    creator_result = validate_creator_exports()
    checks.append(("creator export validation", bool(creator_result["passed"]), format_creator_validation(creator_result)))

    tasks_ok, task_problems = validate_registry()
    checks.append(("task registry validation", tasks_ok, "\n".join(task_problems) or "task registry clean"))

    unity_validation = run_unity_batchmode(log_name="unity_release_gate_validation.log")
    unity_validation_parsed = parse_unity_result_text(unity_validation)
    checks.append(("unity batchmode validation", bool(unity_validation_parsed["passed"]), unity_validation))

    scene_validation = run_unity_batchmode(
        extra_args=["-executeMethod", "AIPrototypeSceneValidator.ValidateSampleScene"],
        log_name="unity_release_gate_scene_validation.log",
    )
    scene_validation_parsed = parse_unity_result_text(scene_validation)
    checks.append(("unity scene validation", bool(scene_validation_parsed["passed"]), scene_validation))

    report_ok, report_output = latest_report_clean()
    checks.append(("latest report clean", report_ok, report_output))

    dashboard_ok, dashboard_output = dashboard_index_clean()
    checks.append(("dashboard status clean", dashboard_ok, dashboard_output))

    print("# Release Gate Report")
    print()

    all_ok = True
    for name, ok, output in checks:
        status = "PASS" if ok else "FAIL"
        print(f"## {name}: {status}")
        print(output.strip() or "(no output)")
        print()
        all_ok = all_ok and ok

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
