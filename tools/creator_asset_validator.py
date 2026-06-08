from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = PROJECT_ROOT / "workspace" / "creator_outputs" / "exports"
BLENDER_LOG = PROJECT_ROOT / "workspace" / "logs" / "blender_creator_run.log"

ERROR_MARKERS = [
    "Traceback",
    "Error",
    "Exception",
    "KeyError",
    "AttributeError",
    "TypeError",
]


def validate_creator_exports(export_dir: Path = EXPORT_DIR, blender_log: Path = BLENDER_LOG) -> dict[str, object]:
    exported_files = sorted(export_dir.glob("*.glb")) if export_dir.exists() else []
    log_text = blender_log.read_text(encoding="utf-8", errors="replace") if blender_log.exists() else ""
    found_errors = [marker for marker in ERROR_MARKERS if marker in log_text]
    small_files = [str(path) for path in exported_files if path.stat().st_size <= 0]

    return {
        "passed": bool(exported_files) and not found_errors and not small_files,
        "export_dir": str(export_dir),
        "blender_log": str(blender_log),
        "exported_files": [str(path) for path in exported_files],
        "error_markers": found_errors,
        "small_files": small_files,
    }


def format_creator_validation(result: dict[str, object]) -> str:
    return (
        "CREATOR_EXPORT_VALIDATION\n"
        f"Passed: {result['passed']}\n"
        f"Export dir: {result['export_dir']}\n"
        f"Blender log: {result['blender_log']}\n"
        "Exported files:\n"
        + "\n".join(result["exported_files"])
        + "\n"
        f"Error markers: {', '.join(result['error_markers']) or 'none'}\n"
        f"Small files: {', '.join(result['small_files']) or 'none'}"
    )


def main() -> int:
    result = validate_creator_exports()
    print(format_creator_validation(result))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
