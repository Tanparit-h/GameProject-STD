import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = PROJECT_ROOT / "tools" / "spec_templates"


def normalize_family_key(family_key: str) -> str:
    normalized = family_key.strip().lower().replace("-", "_").replace(" ", "_")
    if not re.fullmatch(r"[a-z0-9_]+", normalized):
        raise ValueError("family_key must contain only a-z, 0-9, underscore, hyphen, or space")
    return normalized


def scaffold_programmer_family(family_key: str, title: str | None = None) -> list[Path]:
    normalized_key = normalize_family_key(family_key)
    family_title = title or normalized_key.replace("_", " ").title()
    target_dir = TEMPLATE_ROOT / normalized_key
    target_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "README.md": f"""# {family_title}

Family key: `{normalized_key}`

## Required next steps

1. Replace placeholder C# templates with deterministic implementation files.
2. Add a spec builder for `{normalized_key}` in `tools/programmer_output_specs.py`.
3. Add task files that reference `\"family\": \"{normalized_key}\"`.
4. Add unit tests for family resolution and output validation.
5. Add Unity scene setup and scene validation coverage if the family modifies scenes.
""",
        "FamilySceneSetup.cs": f"""using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class {family_title.replace(" ", "")}SceneSetup
{{
    public static void SetupScene()
    {{
        Debug.Log("TODO: implement deterministic scene setup for {normalized_key}.");
    }}
}}
""",
        "FamilySceneValidator.cs": f"""using System;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class {family_title.replace(" ", "")}SceneValidator
{{
    public static void ValidateScene()
    {{
        throw new InvalidOperationException("TODO: implement deterministic scene validation for {normalized_key}.");
    }}
}}
""",
        "FamilyImplementationReport.md": f"""# {family_title} - Implementation Report

## Goal

TODO

## Implemented Outputs

- TODO

## Validation Target

- Setup method: `{family_title.replace(" ", "")}SceneSetup.SetupScene`
- Validation method: `{family_title.replace(" ", "")}SceneValidator.ValidateScene`
""",
    }

    written: list[Path] = []
    for filename, content in files.items():
        path = target_dir / filename
        if not path.exists():
            path.write_text(content, encoding="utf-8")
        written.append(path)

    return written


def main() -> int:
    import sys

    family_key = sys.argv[1] if len(sys.argv) > 1 else "new_family"
    for path in scaffold_programmer_family(family_key):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
