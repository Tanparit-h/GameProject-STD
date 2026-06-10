import unittest
from unittest.mock import patch

from tools.office_monitor import (
    OfficeJob,
    OfficeMonitorState,
    apply_output_line,
    build_status_payload,
    render_monitor_html,
)


class OfficeMonitorTests(unittest.TestCase):
    def test_apply_output_line_tracks_role_progression(self):
        job = OfficeJob(
            job_id="job-1",
            kind="task",
            title="Interaction task",
            command=["python", "-m", "app.main_graph"],
            env_preview={},
        )

        apply_output_line(job, "[1/4] Creator receiving Codex pattern and generating assets if needed...")
        self.assertEqual(job.role_states["creator"]["state"], "running")

        apply_output_line(job, "[2/4] Programmer receiving Codex pattern and generating implementation files...")
        self.assertEqual(job.role_states["creator"]["state"], "completed")
        self.assertEqual(job.role_states["programmer"]["state"], "running")

        apply_output_line(job, "[3/4] Unity applying approved outputs and running validation...")
        self.assertEqual(job.role_states["programmer"]["state"], "completed")
        self.assertEqual(job.role_states["unity"]["state"], "running")

        apply_output_line(job, "[4/4] Writing Codex handoff report...")
        apply_output_line(job, "ROLE_GRAPH_OK | Report written: workspace/reports/latest_report.md")
        self.assertEqual(job.role_states["final"]["state"], "completed")
        self.assertEqual(job.final_status, "ROLE_GRAPH_OK")

    def test_render_monitor_html_contains_control_surface(self):
        html = render_monitor_html()

        self.assertIn("AI Office Monitor", html)
        self.assertIn("Command Desk", html)
        self.assertIn("Dispatch Task", html)
        self.assertIn("/api/orders/ad-hoc", html)

    def test_build_status_payload_contains_expected_sections(self):
        fake_status = {
            "root_status": "clean",
            "unity_status": "clean",
            "latest_report_summary": {"task_id": "feature-interaction-v1"},
            "task_details": [],
        }
        with patch("tools.office_monitor.collect_status", return_value=fake_status):
            with patch("tools.office_monitor.read_approvals", return_value=[]):
                payload = build_status_payload(OfficeMonitorState())

        self.assertIn("system", payload)
        self.assertIn("jobs", payload)
        self.assertIn("families", payload)
        self.assertEqual(payload["system"]["latest_report_summary"]["task_id"], "feature-interaction-v1")


if __name__ == "__main__":
    unittest.main()
