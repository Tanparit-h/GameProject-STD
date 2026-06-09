import argparse
import subprocess
import sys

from tools.dashboard import write_dashboard
from tools.report_index import collect_status, write_report_index
from tools.release_notes import write_release_notes
from tools.task_registry import list_tasks
from tools.task_runner import run_task


def print_status() -> int:
    status = collect_status()
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
        print(f"{task['id']} | {task['status']} | {task['phase']} | {task['title']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="office", description="AI Game Studio office command center")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status")
    subparsers.add_parser("dashboard")
    subparsers.add_parser("release-gate")
    subparsers.add_parser("release-notes")
    subparsers.add_parser("tasks")

    task_parser = subparsers.add_parser("task")
    task_parser.add_argument("task_id")
    task_parser.add_argument("--run", action="store_true")
    task_parser.add_argument("--response-only", action="store_true")

    args = parser.parse_args()

    if args.command == "status":
        return print_status()
    if args.command == "dashboard":
        index_path = write_report_index(collect_status())
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
    if args.command == "task":
        print(run_task(args.task_id, dry_run=not args.run, response_only=args.response_only))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
