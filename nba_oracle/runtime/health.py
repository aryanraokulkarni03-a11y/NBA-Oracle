from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nba_oracle.config import (
    DEFAULT_LEARNING_JSON_REPORT_PATH,
    DEFAULT_LIVE_JSON_REPORT_PATH,
    DEFAULT_OUTCOME_JSON_REPORT_PATH,
    DEFAULT_STABILITY_JSON_REPORT_PATH,
    GMAIL_APP_PASSWORD,
    GMAIL_RECIPIENT,
    GMAIL_SENDER,
    ORACLE_API_HOST,
    ORACLE_API_PORT,
    ORACLE_TIMEZONE,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
)
from nba_oracle.runtime.state import load_runtime_state


def build_health_snapshot() -> dict[str, Any]:
    runtime_state = load_runtime_state()
    live = _load_json(DEFAULT_LIVE_JSON_REPORT_PATH)
    stability = _load_json(DEFAULT_STABILITY_JSON_REPORT_PATH)
    learning = _load_json(DEFAULT_LEARNING_JSON_REPORT_PATH)
    outcomes = _load_json(DEFAULT_OUTCOME_JSON_REPORT_PATH)
    return {
        "api": {
            "host": ORACLE_API_HOST,
            "port": ORACLE_API_PORT,
            "timezone": ORACLE_TIMEZONE,
        },
        "services": {
            "telegram_configured": bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID),
            "gmail_configured": bool(GMAIL_SENDER and GMAIL_APP_PASSWORD and GMAIL_RECIPIENT),
        },
        "runtime_state": runtime_state,
        "latest_live": {
            "run_id": live.get("run_id"),
            "prediction_count": len(live.get("predictions", [])),
            "provider_count": len(live.get("providers", [])),
            "storage_mode": live.get("storage_mode"),
        } if live else None,
        "latest_stability": {
            "review_id": stability.get("review_id"),
            "drift_status": stability.get("drift", {}).get("status"),
            "timing_status": stability.get("timing", {}).get("status"),
        } if stability else None,
        "latest_learning": {
            "review_id": learning.get("review_id"),
            "status": learning.get("status"),
            "graded_prediction_count": learning.get("graded_prediction_count"),
        } if learning else None,
        "latest_outcomes": {
            "newly_graded": outcomes.get("newly_graded"),
            "pending_unfinished": outcomes.get("pending_unfinished"),
        } if outcomes else None,
    }


def load_latest_live_report() -> dict[str, Any]:
    return _load_json(DEFAULT_LIVE_JSON_REPORT_PATH)


def load_latest_stability_report() -> dict[str, Any]:
    return _load_json(DEFAULT_STABILITY_JSON_REPORT_PATH)


def load_latest_learning_report() -> dict[str, Any]:
    return _load_json(DEFAULT_LEARNING_JSON_REPORT_PATH)


def load_latest_outcome_report() -> dict[str, Any]:
    return _load_json(DEFAULT_OUTCOME_JSON_REPORT_PATH)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}
