from typing import TypedDict

class FeatureState(TypedDict):
    feature_request: str
    phase: str

    manager_output: str
    designer_output: str

    creator_required: bool
    programmer_required: bool

    creator_output: str
    creator_script_path: str
    creator_blender_result: str
    creator_qa_report: str
    creator_gate_status: str
    creator_approval_status: str
    creator_approval_note: str
    creator_retry_count: int

    programmer_output: str
    programmer_file_paths: list[str]
    programmer_qa_report: str
    programmer_gate_status: str
    programmer_approval_status: str
    programmer_approval_note: str
    programmer_retry_count: int

    unity_project_path: str
    unity_implementation_result: str
    unity_validation_result: str
    unity_scene_setup_result: str
    unity_scene_validation_result: str
    unity_qa_report: str
    unity_gate_status: str
    unity_approval_status: str
    unity_approval_note: str
    unity_retry_count: int

    final_status: str
