import json
import os
import subprocess
import sys
import threading
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from tools.approval_log import read_approvals
from tools.dashboard import write_dashboard
from tools.programmer_output_specs import (
    get_programmer_family_definition,
    list_programmer_family_definitions,
)
from tools.report_index import collect_status, write_report_index
from tools.task_registry import list_tasks
from tools.task_runner import build_task_command, load_task_data

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_ROOT / "workspace" / "logs" / "office_monitor"
LATEST_REPORT = PROJECT_ROOT / "workspace" / "reports" / "latest_report.md"
STATIC_DASHBOARD = PROJECT_ROOT / "workspace" / "dashboard" / "index.html"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765

ROLE_LABELS = {
    "manager": "Manager",
    "designer": "Designer",
    "creator": "Creator",
    "programmer": "Programmer",
    "qa": "QA",
    "unity": "Unity",
    "final": "Final",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_role_states() -> dict[str, dict[str, str]]:
    return {
        role: {
            "role": role,
            "label": label,
            "state": "idle",
            "detail": "Waiting",
            "updated_at": "",
        }
        for role, label in ROLE_LABELS.items()
    }


@dataclass
class OfficeJob:
    job_id: str
    kind: str
    title: str
    command: list[str]
    env_preview: dict[str, str]
    task_id: str = ""
    family: str = ""
    phase: str = ""
    feature_request: str = ""
    created_at: str = field(default_factory=now_iso)
    started_at: str = ""
    finished_at: str = ""
    status: str = "queued"
    exit_code: int | None = None
    pid: int | None = None
    current_role: str = "queue"
    current_step: str = "Queued"
    final_status: str = ""
    log_path: str = ""
    role_states: dict[str, dict[str, str]] = field(default_factory=build_role_states)
    output_lines: deque[str] = field(default_factory=lambda: deque(maxlen=160))

    def to_dict(self) -> dict[str, object]:
        return {
            "job_id": self.job_id,
            "kind": self.kind,
            "title": self.title,
            "command": self.command,
            "env_preview": self.env_preview,
            "task_id": self.task_id,
            "family": self.family,
            "phase": self.phase,
            "feature_request": self.feature_request,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "status": self.status,
            "exit_code": self.exit_code,
            "pid": self.pid,
            "current_role": self.current_role,
            "current_step": self.current_step,
            "final_status": self.final_status,
            "log_path": self.log_path,
            "role_states": list(self.role_states.values()),
            "output_lines": list(self.output_lines),
        }


def set_role_activity(job: OfficeJob, role: str, state: str, detail: str) -> None:
    timestamp = now_iso()
    for name, role_state in job.role_states.items():
        if name != role and role_state["state"] == "running":
            role_state["state"] = "completed"
            role_state["updated_at"] = timestamp

    target = job.role_states[role]
    target["state"] = state
    target["detail"] = detail
    target["updated_at"] = timestamp
    job.current_role = role
    job.current_step = detail


def finalize_role_states(job: OfficeJob, final_state: str) -> None:
    timestamp = now_iso()
    for role_state in job.role_states.values():
        if role_state["state"] == "running":
            role_state["state"] = final_state
            role_state["updated_at"] = timestamp
    if job.current_role in job.role_states and job.role_states[job.current_role]["state"] == "idle":
        job.role_states[job.current_role]["state"] = final_state
        job.role_states[job.current_role]["updated_at"] = timestamp


def apply_output_line(job: OfficeJob, line: str) -> None:
    if not line:
        return

    job.output_lines.append(line)

    if line.startswith("[1/11] Manager"):
        set_role_activity(job, "manager", "running", "Analyzing user input")
        return
    if line.startswith("[2/11] Designer"):
        set_role_activity(job, "designer", "running", "Creating routing and task package")
        return
    if "Skipping Creator" in line:
        set_role_activity(job, "creator", "skipped", "Designer skipped creator")
        return
    if line.startswith("[3/11] Creator"):
        set_role_activity(job, "creator", "running", "Preparing creator output")
        return
    if line.startswith("[4/11] Running Blender script"):
        set_role_activity(job, "creator", "running", "Running Blender export")
        return
    if "creator evidence gate" in line.lower() or "qa checking creator" in line.lower():
        set_role_activity(job, "qa", "running", "Checking creator evidence")
        return
    if line.startswith("[7/11] Programmer"):
        set_role_activity(job, "programmer", "running", "Building implementation outputs")
        return
    if "programmer evidence gate" in line.lower() or "qa checking programmer" in line.lower():
        set_role_activity(job, "qa", "running", "Checking programmer evidence")
        return
    if "Preparing Unity implementation stage" in line:
        set_role_activity(job, "unity", "running", "Applying Unity copy plan")
        return
    if "Running or skipping Unity batchmode validation" in line:
        set_role_activity(job, "unity", "running", "Running batchmode validation")
        return
    if "Running or skipping Unity scene setup" in line:
        set_role_activity(job, "unity", "running", "Running scene setup")
        return
    if "Running or skipping Unity scene validation" in line:
        set_role_activity(job, "unity", "running", "Running scene validation")
        return
    if "running unity evidence gate" in line.lower() or "qa checking unity automation stage" in line.lower():
        set_role_activity(job, "qa", "running", "Checking Unity evidence")
        return
    if line.startswith("[11/11] Writing report"):
        set_role_activity(job, "final", "running", "Writing final report")
        return
    if line.startswith("Creator required:"):
        job.current_step = line
        return
    if line.startswith("Programmer required:"):
        job.current_step = line
        return
    if line.startswith("STOPPED_"):
        job.final_status = line
        set_role_activity(job, "final", "blocked", line)
        return
    if "ROLE_GRAPH_OK" in line:
        job.final_status = "ROLE_GRAPH_OK"
        set_role_activity(job, "final", "completed", "Workflow completed")


class OfficeMonitorState:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._jobs: dict[str, OfficeJob] = {}
        LOG_DIR.mkdir(parents=True, exist_ok=True)

    def list_jobs(self) -> list[dict[str, object]]:
        with self._lock:
            jobs = [job.to_dict() for job in self._jobs.values()]
        jobs.sort(key=lambda item: item["created_at"], reverse=True)
        return jobs

    def get_job(self, job_id: str) -> OfficeJob | None:
        with self._lock:
            return self._jobs.get(job_id)

    def submit_task_order(self, task_id: str) -> dict[str, object]:
        task_data = load_task_data(task_id)
        family = str(task_data.get("family", ""))
        family_definition = get_programmer_family_definition(family)
        if family_definition is None or family_definition.support_level != "supported":
            raise ValueError(f"Task family is not supported for live execution: {family or 'none'}")

        command, env = build_task_command(task_id)
        return self._start_job(
            kind="task",
            title=str(task_data.get("title", task_id)),
            command=command,
            env=env,
            task_id=task_id,
            family=family,
            phase=str(task_data.get("phase", "")),
            feature_request=str(task_data.get("request", "")),
        )

    def submit_ad_hoc_order(self, feature_request: str, family: str, phase: str) -> dict[str, object]:
        if not feature_request.strip():
            raise ValueError("feature_request is required")
        family_definition = get_programmer_family_definition(family)
        if family_definition is None or family_definition.support_level != "supported":
            raise ValueError(f"Family is not supported for live execution: {family or 'none'}")

        env = os.environ.copy()
        env["AI_STUDIO_FEATURE_REQUEST"] = feature_request
        env["AI_STUDIO_TASK_FAMILY"] = family
        env["AI_STUDIO_PHASE"] = phase or "IMPLEMENTATION"
        return self._start_job(
            kind="ad_hoc",
            title=feature_request.splitlines()[0][:80] or "Ad hoc order",
            command=[sys.executable, "-m", "app.main_graph"],
            env=env,
            family=family,
            phase=env["AI_STUDIO_PHASE"],
            feature_request=feature_request,
        )

    def refresh_static_artifacts(self) -> dict[str, str]:
        index_path = write_report_index(collect_status())
        dashboard_path = write_dashboard()
        return {
            "report_index": str(index_path),
            "dashboard": str(dashboard_path),
        }

    def _start_job(
        self,
        *,
        kind: str,
        title: str,
        command: list[str],
        env: dict[str, str],
        task_id: str = "",
        family: str = "",
        phase: str = "",
        feature_request: str = "",
    ) -> dict[str, object]:
        job_id = uuid.uuid4().hex[:12]
        job = OfficeJob(
            job_id=job_id,
            kind=kind,
            title=title,
            command=command,
            env_preview={
                "AI_STUDIO_TASK_FILE": env.get("AI_STUDIO_TASK_FILE", ""),
                "AI_STUDIO_TASK_FAMILY": env.get("AI_STUDIO_TASK_FAMILY", ""),
                "AI_STUDIO_PHASE": env.get("AI_STUDIO_PHASE", ""),
            },
            task_id=task_id,
            family=family,
            phase=phase,
            feature_request=feature_request,
            log_path=str(LOG_DIR / f"{job_id}.log"),
        )
        with self._lock:
            self._jobs[job_id] = job

        thread = threading.Thread(
            target=self._run_job,
            args=(job_id, command, env),
            daemon=True,
        )
        thread.start()
        return job.to_dict()

    def _run_job(self, job_id: str, command: list[str], env: dict[str, str]) -> None:
        job = self.get_job(job_id)
        if job is None:
            return

        with self._lock:
            job.status = "running"
            job.started_at = now_iso()
            job.current_step = "Launching process"

        log_path = Path(job.log_path)
        with log_path.open("w", encoding="utf-8") as log_handle:
            process = subprocess.Popen(
                command,
                cwd=PROJECT_ROOT,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
            with self._lock:
                job.pid = process.pid

            if process.stdout is not None:
                for raw_line in process.stdout:
                    line = raw_line.rstrip()
                    log_handle.write(raw_line)
                    log_handle.flush()
                    with self._lock:
                        apply_output_line(job, line)

            exit_code = process.wait()

        with self._lock:
            job.exit_code = exit_code
            job.finished_at = now_iso()
            if job.final_status.startswith("STOPPED_"):
                job.status = "blocked"
                finalize_role_states(job, "blocked")
            elif exit_code == 0:
                job.status = "completed"
                finalize_role_states(job, "completed")
                if not job.final_status:
                    job.final_status = "ROLE_GRAPH_OK"
            else:
                job.status = "failed"
                finalize_role_states(job, "failed")
                job.final_status = job.final_status or f"EXIT_{exit_code}"

        self.refresh_static_artifacts()


def build_status_payload(state: OfficeMonitorState) -> dict[str, object]:
    system_status = collect_status()
    jobs = state.list_jobs()
    running_jobs = [job for job in jobs if job["status"] == "running"]
    approvals = read_approvals()
    families = [
        {
            "key": family.key,
            "title": family.title,
            "description": family.description,
            "support_level": family.support_level,
        }
        for family in list_programmer_family_definitions()
    ]
    return {
        "generated_at": now_iso(),
        "system": system_status,
        "jobs": jobs,
        "running_job_count": len(running_jobs),
        "approvals": approvals[-12:],
        "families": families,
        "latest_report_path": str(LATEST_REPORT),
        "dashboard_path": str(STATIC_DASHBOARD),
    }


def render_monitor_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Office Monitor</title>
  <style>
    :root {
      --bg: #efe9de;
      --paper: rgba(255, 251, 245, 0.92);
      --ink: #18202b;
      --muted: #586574;
      --line: rgba(24, 32, 43, 0.12);
      --accent: #145d75;
      --accent-soft: #dff2f8;
      --warn: #a4511f;
      --good: #1f7a4f;
      --bad: #b2332d;
      --shadow: 0 18px 40px rgba(24, 32, 43, 0.08);
      --radius: 20px;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(20, 93, 117, 0.12), transparent 30%),
        radial-gradient(circle at top right, rgba(164, 81, 31, 0.10), transparent 24%),
        linear-gradient(180deg, #f7f1e8 0%, #ebe4d8 100%);
      font-family: "Aptos", "Segoe UI Variable", "Trebuchet MS", sans-serif;
    }
    .shell {
      max-width: 1440px;
      margin: 0 auto;
      padding: 24px;
    }
    .hero, .panel {
      background: var(--paper);
      backdrop-filter: blur(14px);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }
    .hero {
      display: grid;
      grid-template-columns: minmax(0, 1.4fr) minmax(320px, 0.8fr);
      gap: 18px;
      padding: 22px;
      margin-bottom: 18px;
    }
    .hero h1 {
      margin: 0 0 8px;
      font-size: 34px;
      line-height: 1;
      letter-spacing: -0.03em;
    }
    .hero p {
      margin: 0;
      color: var(--muted);
      max-width: 62ch;
    }
    .hero-metrics {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }
    .metric {
      padding: 14px;
      border-radius: 16px;
      background: rgba(255, 255, 255, 0.7);
      border: 1px solid var(--line);
    }
    .metric-label {
      display: block;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
      margin-bottom: 6px;
    }
    .metric-value {
      font-size: 20px;
      font-weight: 700;
    }
    .grid {
      display: grid;
      grid-template-columns: minmax(340px, 0.95fr) minmax(0, 1.35fr);
      gap: 18px;
    }
    .stack {
      display: grid;
      gap: 18px;
    }
    .panel {
      padding: 18px;
      min-width: 0;
    }
    .panel h2 {
      margin: 0 0 14px;
      font-size: 18px;
      letter-spacing: -0.02em;
    }
    .panel h3 {
      margin: 0 0 10px;
      font-size: 14px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }
    .pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 999px;
      border: 1px solid currentColor;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }
    .state-good { color: var(--good); }
    .state-bad { color: var(--bad); }
    .state-warn { color: var(--warn); }
    .state-neutral { color: var(--muted); }
    .meta-grid, .latest-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }
    .meta-card {
      padding: 12px;
      border-radius: 14px;
      background: rgba(255, 255, 255, 0.72);
      border: 1px solid var(--line);
    }
    form {
      display: grid;
      gap: 10px;
      margin-bottom: 14px;
    }
    label {
      display: grid;
      gap: 6px;
      color: var(--muted);
      font-size: 13px;
    }
    input, select, textarea, button {
      font: inherit;
    }
    input, select, textarea {
      width: 100%;
      padding: 10px 12px;
      border-radius: 12px;
      border: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.9);
      color: var(--ink);
    }
    textarea {
      min-height: 140px;
      resize: vertical;
      font-family: "Consolas", "Cascadia Code", monospace;
    }
    .button-row {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }
    button {
      border: 0;
      border-radius: 999px;
      padding: 10px 16px;
      cursor: pointer;
      background: var(--accent);
      color: #fff;
      font-weight: 700;
    }
    button.secondary {
      background: rgba(20, 93, 117, 0.10);
      color: var(--accent);
      border: 1px solid rgba(20, 93, 117, 0.24);
    }
    button.warn {
      background: rgba(164, 81, 31, 0.14);
      color: var(--warn);
      border: 1px solid rgba(164, 81, 31, 0.26);
    }
    .hint {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.5;
    }
    .jobs {
      display: grid;
      gap: 10px;
      max-height: 320px;
      overflow: auto;
      padding-right: 6px;
    }
    .job-card {
      padding: 14px;
      border-radius: 14px;
      background: rgba(255, 255, 255, 0.76);
      border: 1px solid var(--line);
      cursor: pointer;
    }
    .job-card.active {
      border-color: rgba(20, 93, 117, 0.45);
      box-shadow: inset 0 0 0 1px rgba(20, 93, 117, 0.25);
      background: var(--accent-soft);
    }
    .job-top {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 6px;
    }
    .job-title {
      font-weight: 700;
    }
    .role-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
    }
    .role-card {
      padding: 12px;
      border-radius: 14px;
      background: rgba(255, 255, 255, 0.82);
      border: 1px solid var(--line);
      min-height: 104px;
    }
    .role-label {
      display: block;
      margin-bottom: 8px;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }
    .role-detail {
      font-size: 13px;
      line-height: 1.45;
    }
    .log-view {
      margin: 0;
      padding: 14px;
      border-radius: 16px;
      background: #141a22;
      color: #d7e0ea;
      min-height: 240px;
      max-height: 420px;
      overflow: auto;
      font-size: 12px;
      line-height: 1.55;
      white-space: pre-wrap;
      font-family: "Consolas", "Cascadia Code", monospace;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }
    th, td {
      text-align: left;
      padding: 8px 0;
      border-top: 1px solid var(--line);
      vertical-align: top;
    }
    .table-scroll {
      overflow: auto;
      max-height: 280px;
    }
    .toolbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      margin-bottom: 12px;
    }
    .message {
      min-height: 20px;
      color: var(--muted);
      font-size: 13px;
    }
    a {
      color: var(--accent);
      text-decoration: none;
    }
    @media (max-width: 1080px) {
      .hero, .grid { grid-template-columns: 1fr; }
      .role-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    @media (max-width: 700px) {
      .shell { padding: 12px; }
      .hero { padding: 16px; }
      .meta-grid, .latest-grid, .hero-metrics, .role-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <div>
        <h1>AI Office Monitor</h1>
        <p>Live wallboard for the local Office workflow. Watch role-by-role execution, inspect recent logs, and dispatch new orders without leaving the machine.</p>
      </div>
      <div class="hero-metrics" id="heroMetrics"></div>
    </section>

    <div class="grid">
      <div class="stack">
        <section class="panel">
          <div class="toolbar">
            <h2>Command Desk</h2>
            <button class="secondary" id="refreshArtifactsButton" type="button">Refresh Artifacts</button>
          </div>
          <form id="taskOrderForm">
            <h3>Run Registered Task</h3>
            <label>
              Task
              <select id="taskSelect" required></select>
            </label>
            <div class="button-row">
              <button type="submit">Dispatch Task</button>
            </div>
          </form>
          <form id="adHocOrderForm">
            <h3>Send Ad Hoc Order</h3>
            <label>
              Family
              <select id="familySelect" required></select>
            </label>
            <label>
              Phase
              <select id="phaseSelect">
                <option value="IMPLEMENTATION">IMPLEMENTATION</option>
              </select>
            </label>
            <label>
              Feature request
              <textarea id="featureRequestInput" placeholder="Describe the feature request to run through AI Office." required></textarea>
            </label>
            <div class="button-row">
              <button type="submit">Dispatch Order</button>
            </div>
          </form>
          <div class="message" id="formMessage"></div>
          <div class="hint">
            Supported families run immediately. Scaffold-only families stay blocked by design and should be expanded first through the deterministic family workflow.
          </div>
        </section>

        <section class="panel">
          <h2>Queue</h2>
          <div class="jobs" id="jobsList"></div>
        </section>

        <section class="panel">
          <h2>Task Registry</h2>
          <div class="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Task</th>
                  <th>Family</th>
                  <th>Status</th>
                  <th>Phase</th>
                  <th>Run</th>
                </tr>
              </thead>
              <tbody id="taskRows"></tbody>
            </table>
          </div>
        </section>
      </div>

      <div class="stack">
        <section class="panel">
          <div class="toolbar">
            <h2>Live Floor</h2>
            <a href="/api/jobs/current/log" target="_blank" id="logLink">Open full log</a>
          </div>
          <div class="meta-grid" id="selectedJobMeta"></div>
          <div class="role-grid" id="roleBoard"></div>
        </section>

        <section class="panel">
          <h2>Mission Log</h2>
          <pre class="log-view" id="logView">No active job selected.</pre>
        </section>

        <section class="panel">
          <h2>Latest Report Snapshot</h2>
          <div class="latest-grid" id="latestReport"></div>
        </section>

        <section class="panel">
          <h2>Approvals</h2>
          <div class="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Task</th>
                  <th>Decision</th>
                  <th>Owner</th>
                </tr>
              </thead>
              <tbody id="approvalRows"></tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  </div>

  <script>
    let selectedJobId = null;
    let latestPayload = null;

    function stateClass(value) {
      const text = String(value || "").toLowerCase();
      if (["completed", "clean", "true", "supported"].includes(text) || text.includes("pass")) return "state-good";
      if (["failed", "blocked", "false"].includes(text) || text.includes("fail") || text.startsWith("stopped")) return "state-bad";
      if (["running", "queued", "family_scaffold_required", "implementation_requested"].includes(text) || text.includes("need")) return "state-warn";
      return "state-neutral";
    }

    function pill(value) {
      return `<span class="pill ${stateClass(value)}">${String(value || "none")}</span>`;
    }

    function metaCard(label, value) {
      return `<div class="meta-card"><span class="metric-label">${label}</span><div>${value}</div></div>`;
    }

    function repoState(value) {
      return String(value || "").trim() === "clean" ? "clean" : "dirty";
    }

    function escapeHtml(value) {
      return String(value || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
    }

    async function fetchStatus() {
      const response = await fetch("/api/status");
      if (!response.ok) {
        throw new Error(`Status request failed: ${response.status}`);
      }
      latestPayload = await response.json();
      render(latestPayload);
    }

    function render(payload) {
      const system = payload.system;
      const latest = system.latest_report_summary || {};
      const jobs = payload.jobs || [];
      const selected = jobs.find((job) => job.job_id === selectedJobId) || jobs[0] || null;
      if (!selectedJobId && selected) {
        selectedJobId = selected.job_id;
      }

      document.getElementById("heroMetrics").innerHTML = [
        metaCard("Running jobs", `<span class="metric-value">${payload.running_job_count}</span>`),
        metaCard("Root", `${pill(repoState(system.root_status))}`),
        metaCard("Unity", `${pill(repoState(system.unity_status))}`),
        metaCard("Latest report", `${pill(latest.final_status || (system.latest_report_clean ? "clean" : "unknown"))}`),
      ].join("");

      document.getElementById("latestReport").innerHTML = [
        metaCard("Task", escapeHtml(latest.task_id || "none")),
        metaCard("Family", escapeHtml(latest.task_family || "none")),
        metaCard("Phase", pill(latest.phase || "none")),
        metaCard("Final", pill(latest.final_status || "none")),
        metaCard("Creator gate", pill(latest.creator_gate_status || "none")),
        metaCard("Programmer gate", pill(latest.programmer_gate_status || "none")),
        metaCard("Unity gate", pill(latest.unity_gate_status || "none")),
        metaCard("Artifacts", `<a href="/artifacts/latest-report" target="_blank">latest_report.md</a> | <a href="/artifacts/dashboard" target="_blank">static dashboard</a>`),
      ].join("");

      document.getElementById("jobsList").innerHTML = jobs.length
        ? jobs.map((job) => `
            <div class="job-card ${job.job_id === selectedJobId ? "active" : ""}" data-job-id="${job.job_id}">
              <div class="job-top">
                <div class="job-title">${escapeHtml(job.title)}</div>
                ${pill(job.status)}
              </div>
              <div>${escapeHtml(job.task_id || job.family || job.kind)}</div>
              <div class="hint">${escapeHtml(job.current_role)}: ${escapeHtml(job.current_step)}</div>
            </div>
          `).join("")
        : `<div class="hint">No jobs yet. Dispatch a task or ad hoc order from the command desk.</div>`;

      document.getElementById("selectedJobMeta").innerHTML = selected
        ? [
            metaCard("Title", escapeHtml(selected.title)),
            metaCard("Status", pill(selected.status)),
            metaCard("Task", escapeHtml(selected.task_id || "ad hoc")),
            metaCard("Family", escapeHtml(selected.family || "none")),
            metaCard("Phase", pill(selected.phase || "none")),
            metaCard("PID", escapeHtml(selected.pid || "none")),
            metaCard("Started", escapeHtml(selected.started_at || "not started")),
            metaCard("Final", pill(selected.final_status || "pending")),
          ].join("")
        : `<div class="hint">No selected job.</div>`;

      document.getElementById("roleBoard").innerHTML = selected
        ? (selected.role_states || []).map((role) => `
            <div class="role-card">
              <span class="role-label">${escapeHtml(role.label)}</span>
              ${pill(role.state)}
              <div class="role-detail">${escapeHtml(role.detail)}</div>
            </div>
          `).join("")
        : "";

      document.getElementById("logView").textContent = selected
        ? (selected.output_lines || []).join("\\n") || "Job started. Waiting for output..."
        : "No active job selected.";

      document.getElementById("logLink").href = selected ? `/api/jobs/${selected.job_id}/log` : "/api/jobs/current/log";

      document.getElementById("approvalRows").innerHTML = (payload.approvals || []).length
        ? payload.approvals.slice().reverse().map((approval) => `
            <tr>
              <td>${escapeHtml(approval.timestamp)}</td>
              <td>${escapeHtml(approval.task_id)}</td>
              <td>${escapeHtml(approval.decision)}</td>
              <td>${escapeHtml(approval.owner)}</td>
            </tr>
          `).join("")
        : `<tr><td colspan="4">No approvals</td></tr>`;

      const taskOptions = (system.task_details || []).map((task) => {
        const disabled = task.family_support !== "supported" ? "disabled" : "";
        return `<option value="${escapeHtml(task.id)}" ${disabled}>${escapeHtml(task.id)} | ${escapeHtml(task.title)} | ${escapeHtml(task.family_support)}</option>`;
      });
      document.getElementById("taskSelect").innerHTML = taskOptions.join("");

      const familyOptions = (payload.families || [])
        .filter((family) => family.support_level === "supported")
        .map((family) => `<option value="${escapeHtml(family.key)}">${escapeHtml(family.key)} | ${escapeHtml(family.title)}</option>`);
      document.getElementById("familySelect").innerHTML = familyOptions.join("");

      document.getElementById("taskRows").innerHTML = (system.task_details || []).map((task) => `
        <tr>
          <td>${escapeHtml(task.id)}</td>
          <td>${escapeHtml(task.family)}</td>
          <td>${pill(task.status)} ${pill(task.family_support)}</td>
          <td>${escapeHtml(task.phase)}</td>
          <td><button type="button" class="${task.family_support === "supported" ? "secondary" : "warn"}" data-run-task="${escapeHtml(task.id)}" ${task.family_support === "supported" ? "" : "disabled"}>Run</button></td>
        </tr>
      `).join("");
    }

    async function postJson(url, payload) {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload || {}),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || `Request failed: ${response.status}`);
      }
      return data;
    }

    async function dispatchTask(taskId) {
      const data = await postJson("/api/orders/task", { task_id: taskId });
      selectedJobId = data.job.job_id;
      setMessage(`Task dispatched: ${taskId}`);
      await fetchStatus();
    }

    async function dispatchAdHocOrder() {
      const featureRequest = document.getElementById("featureRequestInput").value.trim();
      const family = document.getElementById("familySelect").value;
      const phase = document.getElementById("phaseSelect").value;
      const data = await postJson("/api/orders/ad-hoc", {
        feature_request: featureRequest,
        family,
        phase,
      });
      selectedJobId = data.job.job_id;
      setMessage(`Ad hoc order dispatched for family ${family}`);
      await fetchStatus();
    }

    function setMessage(text, isError = false) {
      const node = document.getElementById("formMessage");
      node.textContent = text;
      node.style.color = isError ? "var(--bad)" : "var(--muted)";
    }

    document.addEventListener("click", async (event) => {
      const jobCard = event.target.closest("[data-job-id]");
      if (jobCard) {
        selectedJobId = jobCard.dataset.jobId;
        render(latestPayload || { system: { latest_report_summary: {} }, jobs: [], approvals: [], families: [] });
        return;
      }
      const runButton = event.target.closest("[data-run-task]");
      if (runButton) {
        try {
          await dispatchTask(runButton.dataset.runTask);
        } catch (error) {
          setMessage(error.message, true);
        }
      }
    });

    document.getElementById("taskOrderForm").addEventListener("submit", async (event) => {
      event.preventDefault();
      try {
        await dispatchTask(document.getElementById("taskSelect").value);
      } catch (error) {
        setMessage(error.message, true);
      }
    });

    document.getElementById("adHocOrderForm").addEventListener("submit", async (event) => {
      event.preventDefault();
      try {
        await dispatchAdHocOrder();
      } catch (error) {
        setMessage(error.message, true);
      }
    });

    document.getElementById("refreshArtifactsButton").addEventListener("click", async () => {
      try {
        const data = await postJson("/api/actions/refresh", {});
        setMessage(`Artifacts refreshed: ${data.report_index}`);
        await fetchStatus();
      } catch (error) {
        setMessage(error.message, true);
      }
    });

    async function loop() {
      try {
        await fetchStatus();
      } catch (error) {
        setMessage(error.message, true);
      } finally {
        window.setTimeout(loop, 2500);
      }
    }

    loop();
  </script>
</body>
</html>
"""


class OfficeMonitorHandler(BaseHTTPRequestHandler):
    state = OfficeMonitorState()

    def log_message(self, format: str, *args: object) -> None:
        return

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send_html(render_monitor_html())
            return
        if parsed.path == "/api/status":
            self._send_json(build_status_payload(self.state))
            return
        if parsed.path == "/api/jobs/current/log":
            jobs = self.state.list_jobs()
            if not jobs:
                self._send_text("No jobs yet.")
                return
            self._send_job_log(jobs[0]["job_id"])
            return
        if parsed.path.startswith("/api/jobs/") and parsed.path.endswith("/log"):
            job_id = parsed.path.split("/")[3]
            self._send_job_log(job_id)
            return
        if parsed.path == "/artifacts/latest-report":
            self._send_path(LATEST_REPORT, "text/markdown; charset=utf-8")
            return
        if parsed.path == "/artifacts/dashboard":
            self._send_path(STATIC_DASHBOARD, "text/html; charset=utf-8")
            return
        if parsed.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        self._send_json({"error": "Not found"}, status=404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw_body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON payload"}, status=400)
            return

        try:
            if parsed.path == "/api/orders/task":
                job = self.state.submit_task_order(str(payload.get("task_id", "")))
                self._send_json({"job": job}, status=202)
                return
            if parsed.path == "/api/orders/ad-hoc":
                job = self.state.submit_ad_hoc_order(
                    feature_request=str(payload.get("feature_request", "")),
                    family=str(payload.get("family", "")),
                    phase=str(payload.get("phase", "IMPLEMENTATION")),
                )
                self._send_json({"job": job}, status=202)
                return
            if parsed.path == "/api/actions/refresh":
                result = self.state.refresh_static_artifacts()
                self._send_json(result, status=200)
                return
        except (KeyError, ValueError) as exc:
            self._send_json({"error": str(exc)}, status=400)
            return

        self._send_json({"error": "Not found"}, status=404)

    def _send_job_log(self, job_id: str) -> None:
        job = self.state.get_job(job_id)
        if job is None:
            self._send_json({"error": "Job not found"}, status=404)
            return
        self._send_path(Path(job.log_path), "text/plain; charset=utf-8")

    def _send_path(self, path: Path, content_type: str) -> None:
        if not path.exists():
            self._send_json({"error": f"Missing file: {path.name}"}, status=404)
            return
        content = path.read_text(encoding="utf-8", errors="replace")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

    def _send_html(self, html: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _send_text(self, text: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(text.encode("utf-8"))

    def _send_json(self, payload: dict[str, object], status: int = 200) -> None:
        content = json.dumps(payload, ensure_ascii=False)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))


def serve_monitor(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> int:
    OfficeMonitorHandler.state.refresh_static_artifacts()
    server = ThreadingHTTPServer((host, port), OfficeMonitorHandler)
    print(f"AI Office Monitor running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def main() -> int:
    host = os.getenv("AI_OFFICE_MONITOR_HOST", DEFAULT_HOST)
    port = int(os.getenv("AI_OFFICE_MONITOR_PORT", str(DEFAULT_PORT)))
    return serve_monitor(host=host, port=port)


if __name__ == "__main__":
    raise SystemExit(main())
