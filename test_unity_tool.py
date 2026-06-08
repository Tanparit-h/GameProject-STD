from pathlib import Path

import pytest

from tools.unity_tool import (
    PROJECT_ROOT,
    apply_copy_plan,
    parse_unity_log,
    validate_unity_project_path,
)


def test_parse_unity_log_passes_clean_return_code():
    result = parse_unity_log("Tundra build success\nExit code: 0", return_code=0)

    assert result["passed"] is True
    assert result["error_markers"] == []
    assert "Tundra build success" in result["success_markers"]


def test_parse_unity_log_fails_on_error_marker():
    result = parse_unity_log("Assets/Test.cs(1,1): error CS1002", return_code=0)

    assert result["passed"] is False
    assert "error CS" in result["error_markers"]


def test_validate_unity_project_rejects_path_outside_game_project():
    ok, message, _ = validate_unity_project_path(PROJECT_ROOT)

    assert ok is False
    assert message.startswith("UNITY_PROJECT_OUTSIDE_ALLOWED_ROOT")


def test_apply_copy_plan_dry_run_does_not_copy():
    project = PROJECT_ROOT / "game_project" / "STDProject"
    if not project.exists():
        pytest.skip("STDProject is not present in this checkout")

    result = apply_copy_plan(dry_run=True, project_path=project)

    assert "UNITY_COPY_PLAN" in result
    assert "Dry run: True" in result
