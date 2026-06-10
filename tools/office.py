import argparse
import subprocess
import sys

from tools.family_scaffold import scaffold_programmer_family
from tools.dashboard import write_dashboard
from tools.office_monitor import DEFAULT_HOST, DEFAULT_PORT, serve_monitor
from tools.programmer_output_specs import list_programmer_family_definitions
from tools.report_index import refresh_report_index
from tools.release_notes import write_release_notes
from tools.task_registry import list_tasks
from tools.task_runner import run_task


def print_status() -> int:
    status, _ = refresh_report_index()
    for key in [
        "root_head",
        "root_status",
        "unity_head",
        "unity_status",
        "latest_report_clean",
        "approval_count",
    ]:
        print(f"{key}: {status[key]}")
    return 0


def run_release_gate() -> int:
    return subprocess.call([sys.executable, "-m", "tools.release_gate"])


def print_tasks() -> int:
    for task in list_tasks():
        print(
            f"{task['id']} | {task['status']} | {task['family']} | {task['family_support']} | "
            f"{task['phase']} | {task['title']}"
        )
    return 0


def print_families() -> int:
    for family in list_programmer_family_definitions():
        print(f"{family.key} | {family.support_level} | {family.title} | {family.description}")
    return 0


def scaffold_family(family_key: str) -> int:
    for path in scaffold_programmer_family(family_key):
        print(path)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="office", description="AI Game Studio office command center")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status")
    subparsers.add_parser("dashboard")
    subparsers.add_parser("release-gate")
    subparsers.add_parser("release-notes")
    subparsers.add_parser("tasks")
    subparsers.add_parser("families")
    monitor_parser = subparsers.add_parser("monitor")
    monitor_parser.add_argument("--host", default=DEFAULT_HOST)
    monitor_parser.add_argument("--port", type=int, default=DEFAULT_PORT)

    scaffold_parser = subparsers.add_parser("scaffold-family")
    scaffold_parser.add_argument("family_key")

    task_parser = subparsers.add_parser("task")
    task_parser.add_argument("task_id")
    task_parser.add_argument("--run", action="store_true")
    task_parser.add_argument("--response-only", action="store_true")

    args = parser.parse_args()

    if args.command == "status":
        return print_status()
    if args.command == "dashboard":
        _, index_path = refresh_report_index()
        dashboard_path = write_dashboard()
        print(f"Report index written: {index_path}")
        print(f"Dashboard written: {dashboard_path}")
        return 0
    if args.command == "release-gate":
        return run_release_gate()
    if args.command == "release-notes":
        path = write_release_notes()
        print(f"Release notes written: {path}")
        return 0
    if args.command == "tasks":
        return print_tasks()
    if args.command == "families":
        return print_families()
    if args.command == "monitor":
        return serve_monitor(host=args.host, port=args.port)
    if args.command == "scaffold-family":
        return scaffold_family(args.family_key)
    if args.command == "task":
        output = run_task(args.task_id, dry_run=not args.run, response_only=args.response_only)
        print(output)
        return 1 if output.startswith("TASK_RUNNER_BLOCKED") else 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
