import os
import shutil
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_DIR = PROJECT_ROOT / "workspace"
LOG_DIR = WORKSPACE_DIR / "logs"
CREATOR_EXPORT_DIR = WORKSPACE_DIR / "creator_outputs" / "exports"
PROGRAMMER_OUTPUT_DIR = WORKSPACE_DIR / "programmer_outputs"
CREATOR_COPY_ALLOWLIST = PROGRAMMER_OUTPUT_DIR / "CreatorAssetCopyAllowlist.txt"

DEFAULT_UNITY_PROJECT = PROJECT_ROOT / "game_project" / "STDProject"

UNITY_ERROR_MARKERS = [
    "error CS",
    "Unhandled Exception",
    "InvalidOperationException",
    "EPERM",
    "Compilation failed",
    "Traceback",
    "KeyError",
    "AttributeError",
    "TypeError",
]

UNITY_SUCCESS_MARKERS = [
    "Tundra build success",
    "AIPrototypeSceneValidator passed.",
    "Exit code: 0",
    "return code 0",
]


def _inside(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def get_unity_project_path() -> Path:
    configured = os.getenv("UNITY_PROJECT")
    project_path = Path(configured) if configured else DEFAULT_UNITY_PROJECT
    return project_path.resolve()


def validate_unity_project_path(project_path: str | Path | None = None) -> tuple[bool, str, Path]:
    path = Path(project_path).resolve() if project_path else get_unity_project_path()
    expected_root = (PROJECT_ROOT / "game_project").resolve()

    if not _inside(path, expected_root):
        return False, f"UNITY_PROJECT_OUTSIDE_ALLOWED_ROOT: {path}", path

    if not path.exists():
        return False, f"UNITY_PROJECT_NOT_FOUND: {path}", path

    if not (path / "Assets").exists() or not (path / "ProjectSettings").exists():
        return False, f"UNITY_PROJECT_INVALID_STRUCTURE: {path}", path

    return True, f"UNITY_PROJECT_OK: {path}", path


def parse_unity_log(log_text: str, return_code: int | None = None) -> dict[str, object]:
    found_errors = [marker for marker in UNITY_ERROR_MARKERS if marker in log_text]
    found_success = [marker for marker in UNITY_SUCCESS_MARKERS if marker in log_text]

    passed = not found_errors
    if return_code is not None:
        passed = passed and return_code == 0

    return {
        "passed": passed,
        "return_code": return_code,
        "error_markers": found_errors,
        "success_markers": found_success,
    }


def parse_unity_result_text(result_text: str) -> dict[str, object]:
    return_code: int | None = None
    for line in result_text.splitlines():
        if line.startswith("Exit code:"):
            value = line.split(":", 1)[1].strip()
            try:
                return_code = int(value)
            except ValueError:
                return_code = None
            break

    return parse_unity_log(result_text, return_code)


def build_copy_plan(project_path: str | Path | None = None) -> list[tuple[Path, Path]]:
    ok, message, project = validate_unity_project_path(project_path)
    if not ok:
        raise ValueError(message)

    plan: list[tuple[Path, Path]] = []

    allowed_assets: set[str] = set()
    if CREATOR_COPY_ALLOWLIST.exists():
        allowed_assets = {
            line.strip()
            for line in CREATOR_COPY_ALLOWLIST.read_text(encoding="utf-8", errors="replace").splitlines()
            if line.strip() and not line.strip().startswith("#")
        }

    if CREATOR_EXPORT_DIR.exists() and allowed_assets:
        for source in sorted(CREATOR_EXPORT_DIR.glob("*.glb")):
            if source.name in allowed_assets:
                plan.append((source.resolve(), project / "Assets" / "AIAssets" / source.name))

    if PROGRAMMER_OUTPUT_DIR.exists():
        script_map = {
            "InteractSystem_Draft.cs": "InteractSystem.cs",
            "InteractableObject_Draft.cs": "InteractableObject.cs",
            "TerraMageMaterialSystem.cs": "TerraMageTD/TerraMageMaterialSystem.cs",
            "TerraMageActionBuildController.cs": "TerraMageTD/TerraMageActionBuildController.cs",
            "TerraMageMeleeGestureController.cs": "TerraMageTD/TerraMageMeleeGestureController.cs",
            "TerraMageTinyMageController.cs": "TerraMageTD/TerraMageTinyMageController.cs",
            "TerraMageFollowCamera.cs": "TerraMageTD/TerraMageFollowCamera.cs",
        }
        for draft_name, target_name in script_map.items():
            source = PROGRAMMER_OUTPUT_DIR / draft_name
            if source.exists():
                plan.append((source.resolve(), project / "Assets" / "Scripts" / "AIPrototype" / target_name))

    return plan


def _transform_unity_script(source: Path) -> str:
    content = source.read_text(encoding="utf-8", errors="replace")
    content = content.replace("InteractSystem_Draft", "InteractSystem")
    content = content.replace("InteractableObject_Draft", "InteractableObject")
    return content.replace(
        "// PROTOTYPE_PLAN draft only. Do not place this file in Unity Assets yet.\n",
        "",
    )


def _target_matches_source(source: Path, target: Path) -> bool:
    if not target.exists():
        return False

    if source.suffix.lower() == ".cs":
        return target.read_text(encoding="utf-8", errors="replace") == _transform_unity_script(source)

    return source.read_bytes() == target.read_bytes()


def apply_copy_plan(dry_run: bool = True, project_path: str | Path | None = None) -> str:
    plan = build_copy_plan(project_path)
    lines = ["UNITY_COPY_PLAN", f"Dry run: {dry_run}"]

    for source, target in plan:
        if not _inside(source, WORKSPACE_DIR):
            raise PermissionError(f"Blocked source outside workspace: {source}")

        ok, message, project = validate_unity_project_path(project_path)
        if not ok:
            raise ValueError(message)

        if not _inside(target, project / "Assets"):
            raise PermissionError(f"Blocked target outside Unity Assets: {target}")

        if _target_matches_source(source, target):
            lines.append(f"UNCHANGED: {source} -> {target}")
            continue

        lines.append(f"COPY: {source} -> {target}")

        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.suffix.lower() == ".cs":
                target.write_text(_transform_unity_script(source), encoding="utf-8")
            else:
                shutil.copy2(source, target)

    if not plan:
        lines.append("No approved asset/script files found to copy.")

    return "\n".join(lines)


def run_unity_batchmode(extra_args: list[str] | None = None, log_name: str = "unity_batchmode.log") -> str:
    unity_exe = os.getenv("UNITY_EXE")
    if not unity_exe:
        return "UNITY_ERROR: UNITY_EXE is not set in .env"

    unity_path = Path(unity_exe)
    if not unity_path.exists():
        return f"UNITY_ERROR: Unity executable not found: {unity_path}"

    ok, message, project = validate_unity_project_path()
    if not ok:
        return f"UNITY_ERROR: {message}"

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / log_name

    command = [
        str(unity_path),
        "-batchmode",
        "-quit",
        "-projectPath",
        str(project),
        "-logFile",
        str(log_path),
    ]
    if extra_args:
        command.extend(extra_args)

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=900,
        )
    except subprocess.TimeoutExpired:
        return "UNITY_ERROR: Unity batchmode timed out after 900 seconds"
    except Exception as exc:
        return f"UNITY_ERROR: {type(exc).__name__}: {exc}"

    log_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    parsed = parse_unity_log(log_text + result.stdout + result.stderr, result.returncode)

    return (
        "UNITY_BATCHMODE_RESULT\n"
        f"Exit code: {result.returncode}\n"
        f"Log path: {log_path}\n"
        f"Passed: {parsed['passed']}\n"
        f"Error markers: {', '.join(parsed['error_markers']) or 'none'}\n"
        f"Success markers: {', '.join(parsed['success_markers']) or 'none'}\n"
        f"STDERR tail:\n{result.stderr[-4000:]}"
    )
