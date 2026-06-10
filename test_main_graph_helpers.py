import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.main_graph import (
    build_thai_evidence_report,
    creator_qa_node,
    final_node,
    is_implementation_phase,
    programmer_output_file_label,
    programmer_qa_node,
    unity_qa_node,
    write_blocked_family_reports,
)


class MainGraphHelperTests(unittest.TestCase):
    def test_is_implementation_phase(self):
        self.assertTrue(is_implementation_phase("IMPLEMENTATION"))
        self.assertFalse(is_implementation_phase("DESIGN_ONLY"))

    def test_programmer_output_file_label(self):
        self.assertEqual(programmer_output_file_label("IMPLEMENTATION"), "implementation files")
        self.assertEqual(programmer_output_file_label("DESIGN_ONLY"), "design outputs")

    def test_build_thai_evidence_report_renders_none_sections(self):
        report = build_thai_evidence_report(
            passed=True,
            checks=["ตรวจไฟล์ output"],
            recommendations=["ผ่านตาม evidence gate ไม่ต้องแก้เพิ่ม"],
        )

        self.assertIn("1. ผลตรวจ: ผ่าน", report)
        self.assertIn("3. ปัญหาที่บล็อกงาน:\n- ไม่มี", report)
        self.assertIn("7. คำแนะนำ:\n- ผ่านตาม evidence gate ไม่ต้องแก้เพิ่ม", report)

    def test_creator_qa_node_no_longer_calls_role_model(self):
        state = {
            "phase": "IMPLEMENTATION",
            "creator_script_path": "workspace/creator_outputs/create_placeholder_assets.py",
            "creator_qa_report": "",
            "creator_gate_status": "",
        }
        with patch("app.main_graph.run_role", side_effect=AssertionError("run_role should not be called")):
            with patch(
                "app.main_graph.validate_creator_output_evidence",
                return_value=(True, [], {"passed": True, "export_dir": "x", "blender_log": "y", "exported_files": ["a.glb"], "error_markers": [], "small_files": []}),
            ):
                result = asyncio.run(creator_qa_node(state))

        self.assertEqual(result["creator_gate_status"], "CLEAN_PASS")
        self.assertIn("evidence gate", result["creator_qa_report"])

    def test_programmer_qa_node_no_longer_calls_role_model(self):
        state = {
            "phase": "IMPLEMENTATION",
            "feature_request": "terra mage weapon wheel implementation",
            "task_id": "terra-mage-weapon-wheel-v006",
            "programmer_file_paths": ["workspace/programmer_outputs/TerraMageWeaponWheelUI.cs"],
            "programmer_qa_report": "",
            "programmer_gate_status": "",
        }
        with patch("app.main_graph.run_role", side_effect=AssertionError("run_role should not be called")):
            with patch("app.main_graph.validate_programmer_output_files", return_value=(True, [])):
                result = asyncio.run(programmer_qa_node(state))

        self.assertEqual(result["programmer_gate_status"], "CLEAN_PASS")
        self.assertIn("DETERMINISTIC_PROGRAMMER_GATE", result["programmer_qa_report"])

    def test_unity_qa_node_no_longer_calls_role_model(self):
        state = {
            "phase": "IMPLEMENTATION",
            "unity_implementation_result": "UNITY_COPY_PLAN\nDry run: False\nCOPY: a -> b",
            "unity_validation_result": "UNITY_BATCHMODE_RESULT\nExit code: 0\nPassed: True\nError markers: none\nSuccess markers: return code 0",
            "unity_scene_setup_result": "UNITY_BATCHMODE_RESULT\nExit code: 0\nPassed: True\nError markers: none\nSuccess markers: return code 0",
            "unity_scene_validation_result": "UNITY_BATCHMODE_RESULT\nExit code: 0\nPassed: True\nError markers: none\nSuccess markers: return code 0",
            "unity_qa_report": "",
            "unity_gate_status": "",
        }
        with patch("app.main_graph.run_role", side_effect=AssertionError("run_role should not be called")):
            result = asyncio.run(unity_qa_node(state))

        self.assertEqual(result["unity_gate_status"], "CLEAN_PASS")
        self.assertIn("DETERMINISTIC_UNITY_GATE", result["unity_qa_report"])

    def test_final_node_refreshes_report_index(self):
        state = {
            "feature_request": "Validate Terra Mage scene.",
            "task_id": "terra-mage-weapon-wheel-scene-validation-v008",
            "task_file": "workspace/tasks/terra_mage_weapon_wheel_scene_validation_v008.json",
            "task_family": "terra_mage_weapon_family",
            "phase": "IMPLEMENTATION",
            "creator_pattern_path": "workspace/generated_specs/creator_pattern.md",
            "creator_output": "Creator skipped",
            "creator_qa_report": "Creator reviewer skipped",
            "creator_gate_status": "SKIPPED",
            "programmer_pattern_path": "workspace/generated_specs/programmer_pattern.md",
            "programmer_output": "Programmer generated files",
            "programmer_file_paths": ["workspace/programmer_outputs/TerraMageWeaponWheelUI.cs"],
            "programmer_qa_report": "Programmer clean",
            "programmer_gate_status": "CLEAN_PASS",
            "unity_pattern_path": "workspace/generated_specs/unity_pattern.md",
            "unity_project_path": "game_project/STDProject",
            "unity_implementation_result": "UNITY_COPY_PLAN",
            "unity_validation_result": "UNITY_BATCHMODE_RESULT",
            "unity_scene_setup_result": "UNITY_BATCHMODE_RESULT",
            "unity_scene_validation_result": "UNITY_BATCHMODE_RESULT",
            "unity_qa_report": "Unity clean",
            "unity_gate_status": "CLEAN_PASS",
            "final_status": "ROLE_GRAPH_OK",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("app.main_graph.ROOT", Path(temp_dir)):
                with patch("app.main_graph.refresh_report_index") as mocked_refresh:
                    result = final_node(state)

        self.assertIn("ROLE_GRAPH_OK", result["final_status"])
        mocked_refresh.assert_called_once_with()

    def test_blocked_family_reports_refresh_report_index(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("app.main_graph.ROOT", Path(temp_dir)):
                with patch("app.main_graph.refresh_report_index") as mocked_refresh:
                    write_blocked_family_reports(
                        task_id="feature-door-toggle-v1",
                        task_file="workspace/tasks/door_toggle_v1.json",
                        task_family="door_toggle_interaction",
                        feature_request="Implement door toggle interaction.",
                        phase="IMPLEMENTATION",
                        status="STOPPED_UNSUPPORTED",
                        message="Unsupported family",
                    )

        mocked_refresh.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
