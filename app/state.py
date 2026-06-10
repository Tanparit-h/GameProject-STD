from typing import TypedDict


class FeatureState(TypedDict, total=False):
    task_id: str
    task_file: str
    task_family: str

    feature_request: str
    phase: str

    creator_required: bool
    programmer_required: bool

    creator_output: str
    creator_pattern_path: str
    creator_script_path: str
    creator_blender_result: str
    creator_qa_report: str
    creator_gate_status: str
    creator_approval_status: str
    creator_reviewer_output: str

    programmer_output: str
    programmer_pattern_path: str
    programmer_file_paths: list[str]
    programmer_qa_report: str
    programmer_gate_status: str
    programmer_approval_status: str
    programmer_reviewer_output: str

    unity_pattern_path: str
    unity_project_path: str
    unity_implementation_result: str
    unity_validation_result: str
    unity_scene_setup_result: str
    unity_scene_validation_result: str
    unity_qa_report: str
    unity_gate_status: str
    unity_approval_status: str
    unity_reviewer_output: str

    final_status: str
