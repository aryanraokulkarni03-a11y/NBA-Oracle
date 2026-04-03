from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nba_oracle.config import (
    PHASE4_LEARNING_REVIEWS_TABLE,
    PHASE4_NOTIFICATION_EVENTS_TABLE,
    PHASE4_RUNTIME_JOBS_TABLE,
    RUNTIME_STATE_DIR,
    SUPABASE_SERVICE_ROLE_KEY,
    SUPABASE_URL,
)
from nba_oracle.http import HttpRequestError, request_json


RUNTIME_STATE_PATH = RUNTIME_STATE_DIR / "runtime_state.json"
RUNTIME_JOB_HISTORY_PATH = RUNTIME_STATE_DIR / "runtime_jobs.json"
NOTIFICATION_EVENTS_PATH = RUNTIME_STATE_DIR / "notification_events.json"


@dataclass(frozen=True)
class RuntimeJobRecord:
    job_id: str
    job_name: str
    status: str
    started_at: str
    finished_at: str
    detail: dict[str, Any]


def ensure_runtime_state_dir() -> None:
    RUNTIME_STATE_DIR.mkdir(parents=True, exist_ok=True)


def load_runtime_state() -> dict[str, Any]:
    ensure_runtime_state_dir()
    if not RUNTIME_STATE_PATH.exists():
        return {"updated_at": None, "last_jobs": {}, "job_history": []}
    try:
        return json.loads(RUNTIME_STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"updated_at": None, "last_jobs": {}, "job_history": []}


def save_runtime_state(state: dict[str, Any]) -> Path:
    ensure_runtime_state_dir()
    RUNTIME_STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return RUNTIME_STATE_PATH


def record_runtime_job(job_name: str, status: str, detail: dict[str, Any] | None = None) -> RuntimeJobRecord:
    ensure_runtime_state_dir()
    now = datetime.now(timezone.utc).isoformat()
    record = RuntimeJobRecord(
        job_id=f"runtime-job-{uuid.uuid4().hex[:12]}",
        job_name=job_name,
        status=status,
        started_at=now,
        finished_at=now,
        detail=detail or {},
    )

    state = load_runtime_state()
    history = list(state.get("job_history", []))
    history.insert(
        0,
        {
            "job_id": record.job_id,
            "job_name": record.job_name,
            "status": record.status,
            "started_at": record.started_at,
            "finished_at": record.finished_at,
            "detail": record.detail,
        },
    )
    state["updated_at"] = now
    state.setdefault("last_jobs", {})[job_name] = {
        "job_id": record.job_id,
        "status": status,
        "finished_at": now,
        "detail": record.detail,
    }
    state["job_history"] = history[:100]
    save_runtime_state(state)
    _append_json_record(RUNTIME_JOB_HISTORY_PATH, history[0])
    _store_remote(
        PHASE4_RUNTIME_JOBS_TABLE,
        [
            {
                "job_id": record.job_id,
                "job_name": record.job_name,
                "status": record.status,
                "started_at": record.started_at,
                "finished_at": record.finished_at,
                "detail_payload": record.detail,
            }
        ],
    )
    return record


def record_notification_event(channel: str, event_type: str, success: bool, destination: str, detail: dict[str, Any]) -> str:
    ensure_runtime_state_dir()
    payload = {
        "event_id": f"notify-{uuid.uuid4().hex[:12]}",
        "channel": channel,
        "event_type": event_type,
        "success": success,
        "destination": destination,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "detail": detail,
    }
    _append_json_record(NOTIFICATION_EVENTS_PATH, payload)
    _store_remote(
        PHASE4_NOTIFICATION_EVENTS_TABLE,
        [
            {
                "event_id": payload["event_id"],
                "channel": channel,
                "event_type": event_type,
                "success": success,
                "destination": destination,
                "created_at": payload["created_at"],
                "detail_payload": detail,
            }
        ],
    )
    return payload["event_id"]


def record_learning_review(payload: dict[str, Any]) -> str:
    review_id = str(payload["review_id"])
    _store_remote(
        PHASE4_LEARNING_REVIEWS_TABLE,
        [
            {
                "review_id": review_id,
                "created_at": payload["created_at"],
                "status": payload["status"],
                "candidate_model_version": payload.get("candidate_model_version"),
                "learning_payload": payload,
            }
        ],
    )
    return review_id


def _append_json_record(path: Path, payload: dict[str, Any]) -> None:
    ensure_runtime_state_dir()
    if path.exists():
        try:
            records = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            records = []
    else:
        records = []
    if not isinstance(records, list):
        records = []
    records.insert(0, payload)
    path.write_text(json.dumps(records[:200], indent=2), encoding="utf-8")


def _store_remote(table: str, rows: list[dict[str, Any]]) -> None:
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY or not rows:
        return
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Prefer": "resolution=merge-duplicates,return=minimal",
    }
    try:
        request_json(
            f"{SUPABASE_URL.rstrip('/')}/rest/v1/{table}",
            method="POST",
            headers=headers,
            json_body=rows,
            timeout=20,
        )
    except HttpRequestError:
        return
