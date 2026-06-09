from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROGRAMMER_OUTPUT_DIR = PROJECT_ROOT / "workspace" / "programmer_outputs"


def ensure_programmer_output_dir() -> Path:
    PROGRAMMER_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return PROGRAMMER_OUTPUT_DIR


def write_programmer_file(filename: str, content: str) -> str:
    """
    Write programmer-generated files into workspace/programmer_outputs only.
    """
    output_dir = ensure_programmer_output_dir()
    target = output_dir / filename

    resolved_target = target.resolve()
    resolved_output_dir = output_dir.resolve()

    try:
        resolved_target.relative_to(resolved_output_dir)
    except ValueError as exc:
        raise PermissionError(f"Blocked path outside programmer output dir: {resolved_target}") from exc

    target.write_text(content, encoding="utf-8")
    return str(target)


def read_programmer_file(filename: str) -> str:
    output_dir = ensure_programmer_output_dir()
    target = output_dir / filename

    resolved_target = target.resolve()
    resolved_output_dir = output_dir.resolve()

    try:
        resolved_target.relative_to(resolved_output_dir)
    except ValueError as exc:
        raise PermissionError(f"Blocked path outside programmer output dir: {resolved_target}") from exc

    return target.read_text(encoding="utf-8")
