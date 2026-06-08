import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APPROVAL_DIR = PROJECT_ROOT / "workspace" / "approvals"
APPROVAL_LOG = APPROVAL_DIR / "approval_log.jsonl"

VALID_DECISIONS = {"approved", "rejected", "skipped"}


def append_approval(
    task_id: str,
    phase: str,
    decision: str,
    owner: str,
    reason: str,
) -> Path:
    if decision not in VALID_DECISIONS:
        raise ValueError(f"Invalid approval decision: {decision}")
    if not task_id.strip():
        raise ValueError("task_id is required")
    if not phase.strip():
        raise ValueError("phase is required")
    if not owner.strip():
        raise ValueError("owner is required")
    if not reason.strip():
        raise ValueError("reason is required")

    APPROVAL_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task_id": task_id,
        "phase": phase,
        "decision": decision,
        "owner": owner,
        "reason": reason,
    }
    with APPROVAL_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return APPROVAL_LOG


def read_approvals() -> list[dict[str, str]]:
    if not APPROVAL_LOG.exists():
        return []
    records: list[dict[str, str]] = []
    for line in APPROVAL_LOG.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def main() -> int:
    path = append_approval(
        task_id="feature-interaction-v1",
        phase="IMPLEMENTATION",
        decision="approved",
        owner="codex",
        reason="Implementation vertical slice passed release gate.",
    )
    print(f"Approval recorded: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
