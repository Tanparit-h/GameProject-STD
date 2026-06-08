import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CREATOR_OUTPUT_DIR = PROJECT_ROOT / "workspace" / "creator_outputs"
EXPORT_DIR = CREATOR_OUTPUT_DIR / "exports"
LOG_DIR = PROJECT_ROOT / "workspace" / "logs"


def run_blender_script(script_path: str) -> str:
    """
    Run Blender in background mode with the creator-generated Python script.
    Output/log stays inside workspace only.
    """
    blender_exe = os.getenv("BLENDER_EXE")

    if not blender_exe:
        return "BLENDER_ERROR: BLENDER_EXE is not set in .env"

    blender_path = Path(blender_exe)
    if not blender_path.exists():
        return f"BLENDER_ERROR: Blender executable not found: {blender_path}"

    script = Path(script_path)
    if not script.exists():
        return f"BLENDER_ERROR: Script not found: {script}"

    # Safety: script must be inside workspace/creator_outputs
    try:
        script.resolve().relative_to(CREATOR_OUTPUT_DIR.resolve())
    except ValueError:
        return f"BLENDER_ERROR: Script is outside creator output dir: {script.resolve()}"

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    log_path = LOG_DIR / "blender_creator_run.log"

    env = os.environ.copy()
    env["AI_STUDIO_EXPORT_DIR"] = str(EXPORT_DIR)

    try:
        result = subprocess.run(
            [
                str(blender_path),
                "--background",
                "--python",
                str(script),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
            env=env,
        )

        log_content = (
            f"Exit code: {result.returncode}\n\n"
            f"STDOUT:\n{result.stdout}\n\n"
            f"STDERR:\n{result.stderr}\n"
        )
        log_path.write_text(log_content, encoding="utf-8", errors="ignore")

        exported_files = []
        if EXPORT_DIR.exists():
            exported_files = [
                str(path)
                for path in EXPORT_DIR.iterdir()
                if path.is_file()
            ]

        return (
            f"BLENDER_RUN_RESULT\n"
            f"Exit code: {result.returncode}\n"
            f"Log path: {log_path}\n"
            f"Export dir: {EXPORT_DIR}\n"
            f"Exported files:\n"
            + "\n".join(exported_files)
            + "\n\n"
            f"STDERR tail:\n{result.stderr[-4000:]}"
        )

    except subprocess.TimeoutExpired:
        return "BLENDER_ERROR: Blender run timed out after 300 seconds"
    except Exception as exc:
        return f"BLENDER_ERROR: {type(exc).__name__}: {exc}"