from html import escape
from pathlib import Path

from tools.report_index import collect_status
from tools.approval_log import read_approvals

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = PROJECT_ROOT / "workspace" / "dashboard"
DASHBOARD_PATH = DASHBOARD_DIR / "index.html"


def status_class(value: object) -> str:
    text = str(value).lower()
    if text in {"clean", "true"} or "pass" in text:
        return "good"
    if text in {"false"} or "fail" in text:
        return "bad"
    return "neutral"


def h(value: object) -> str:
    return escape(str(value))


def render_dashboard() -> str:
    status = collect_status()
    approvals = read_approvals()

    tasks = "".join(
        "<li>"
        f"<strong>{h(task['id'])}</strong> "
        f"<span class='pill neutral'>{h(task['status'])}</span> "
        f"<span class='pill neutral'>{h(task['family'])}</span> "
        f"<span class='pill {status_class(task['family_support'] == 'supported')}'>{h(task['family_support'])}</span> "
        f"{h(task['phase'])} - {h(task['title'])}"
        "</li>"
        for task in status["task_details"]
    ) or "<li>none</li>"
    reports = "".join(f"<li>{escape(report)}</li>" for report in status["reports"]) or "<li>none</li>"
    approval_rows = "".join(
        "<tr>"
        f"<td>{h(record.get('timestamp', ''))}</td>"
        f"<td>{h(record.get('task_id', ''))}</td>"
        f"<td>{h(record.get('phase', ''))}</td>"
        f"<td>{h(record.get('decision', ''))}</td>"
        f"<td>{h(record.get('owner', ''))}</td>"
        f"<td>{h(record.get('reason', ''))}</td>"
        "</tr>"
        for record in approvals
    ) or "<tr><td colspan='6'>No approval records</td></tr>"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Game Studio Dashboard</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f7f4;
      --ink: #1d2329;
      --muted: #66707a;
      --line: #d8d9d3;
      --panel: #ffffff;
      --good: #157347;
      --bad: #b42318;
      --neutral: #52606d;
      --accent: #1f6f8b;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Segoe UI, Arial, sans-serif;
      font-size: 14px;
      line-height: 1.45;
    }}
    header {{
      padding: 20px 28px 12px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }}
    h1, h2 {{ margin: 0; letter-spacing: 0; }}
    h1 {{ font-size: 24px; }}
    h2 {{ font-size: 16px; margin-bottom: 10px; }}
    main {{
      display: grid;
      grid-template-columns: repeat(12, 1fr);
      gap: 14px;
      padding: 16px 28px 28px;
    }}
    section {{
      grid-column: span 6;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 14px;
      min-width: 0;
    }}
    section.wide {{ grid-column: span 12; }}
    dl {{
      display: grid;
      grid-template-columns: 150px minmax(0, 1fr);
      gap: 8px 12px;
      margin: 0;
    }}
    dt {{ color: var(--muted); }}
    dd {{ margin: 0; overflow-wrap: anywhere; }}
    .pill {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 999px;
      border: 1px solid currentColor;
      font-weight: 600;
    }}
    .good {{ color: var(--good); }}
    .bad {{ color: var(--bad); }}
    .neutral {{ color: var(--neutral); }}
    ul {{ margin: 0; padding-left: 18px; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
    }}
    th, td {{
      border-top: 1px solid var(--line);
      padding: 8px;
      text-align: left;
      vertical-align: top;
      overflow-wrap: anywhere;
    }}
    th {{ color: var(--muted); font-weight: 600; }}
    @media (max-width: 800px) {{
      main {{ grid-template-columns: 1fr; padding: 12px; }}
      section, section.wide {{ grid-column: span 1; }}
      dl {{ grid-template-columns: 1fr; }}
      header {{ padding: 16px 12px 10px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>AI Game Studio Dashboard</h1>
    <div>Generated at {h(status["generated_at"])}</div>
  </header>
  <main>
    <section>
      <h2>Repository</h2>
      <dl>
        <dt>Root HEAD</dt><dd>{h(status["root_head"])}</dd>
        <dt>Root status</dt><dd><span class="pill {status_class(status["root_status"])}">{h(status["root_status"])}</span></dd>
        <dt>Unity HEAD</dt><dd>{h(status["unity_head"])}</dd>
        <dt>Unity status</dt><dd><span class="pill {status_class(status["unity_status"])}">{h(status["unity_status"])}</span></dd>
      </dl>
    </section>
    <section>
      <h2>Release State</h2>
      <dl>
        <dt>Latest report</dt><dd><span class="pill {status_class(status["latest_report_exists"])}">{h(status["latest_report_exists"])}</span></dd>
        <dt>Report clean</dt><dd><span class="pill {status_class(status["latest_report_clean"])}">{h(status["latest_report_clean"])}</span></dd>
        <dt>Approvals</dt><dd>{h(status["approval_count"])}</dd>
      </dl>
    </section>
    <section>
      <h2>Task Queue</h2>
      <ul>{tasks}</ul>
    </section>
    <section>
      <h2>Reports</h2>
      <ul>{reports}</ul>
    </section>
    <section class="wide">
      <h2>Approvals</h2>
      <table>
        <thead><tr><th>Time</th><th>Task</th><th>Phase</th><th>Decision</th><th>Owner</th><th>Reason</th></tr></thead>
        <tbody>{approval_rows}</tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""


def write_dashboard() -> Path:
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    DASHBOARD_PATH.write_text(render_dashboard(), encoding="utf-8")
    return DASHBOARD_PATH


def main() -> int:
    path = write_dashboard()
    print(f"Dashboard written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
