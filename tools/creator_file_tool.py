from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CREATOR_OUTPUT_DIR = PROJECT_ROOT / "workspace" / "creator_outputs"


def ensure_creator_output_dir() -> Path:
    CREATOR_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return CREATOR_OUTPUT_DIR


def write_creator_file(filename: str, content: str) -> str:
    """
    Write creator-generated files into workspace/creator_outputs only.
    """
    output_dir = ensure_creator_output_dir()
    target = output_dir / filename

    resolved_target = target.resolve()
    resolved_output_dir = output_dir.resolve()

    try:
        resolved_target.relative_to(resolved_output_dir)
    except ValueError as exc:
        raise PermissionError(f"Blocked path outside creator output dir: {resolved_target}") from exc

    target.write_text(content, encoding="utf-8")
    return str(target)


def read_creator_file(filename: str) -> str:
    output_dir = ensure_creator_output_dir()
    target = output_dir / filename

    resolved_target = target.resolve()
    resolved_output_dir = output_dir.resolve()

    try:
        resolved_target.relative_to(resolved_output_dir)
    except ValueError as exc:
        raise PermissionError(f"Blocked path outside creator output dir: {resolved_target}") from exc

    return target.read_text(encoding="utf-8")