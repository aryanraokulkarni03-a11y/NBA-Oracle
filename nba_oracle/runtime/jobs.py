from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nba_oracle.config import (
    DEFAULT_JSON_REPORT_PATH,
    ORACLE_NOTIFY_COMPLETION,
    ORACLE_NOTIFY_FAILURE,
    ORACLE_NOTIFY_MIDNIGHT,
)
from nba_oracle.learning.review import write_learning_json_report, write_learning_markdown_report
from nba_oracle.learning.trainer import run_learning_review
from nba_oracle.notifications.formatters import format_health_digest, format_live_digest
from nba_oracle.notifications.gmail import send_gmail_message
from nba_oracle.notifications.telegram import send_telegram_message
from nba_oracle.runtime.health import build_health_snapshot, load_latest_live_report
from nba_oracle.runtime.state import record_runtime_job
from nba_oracle.runs.build_live_slate import build_live_slate
from nba_oracle.runs.grade_outcomes import grade_outcomes
from nba_oracle.runs.review_stability import review_stability
from nba_oracle.live_reporting import write_live_json_report, write_live_markdown_report
from nba_oracle.outcomes.reporting import write_outcome_json_report, write_outcome_markdown_report


def run_live_slate_job(*, use_live: bool = True, bundle_path: Path | None = None) -> dict[str, Any]:
    try:
        result = build_live_slate(bundle_path if not use_live else None, use_live=use_live, decision_time=datetime.now(timezone.utc))
        md_path = write_live_markdown_report(result)
        json_path = write_live_json_report(result)
        detail = {
            "run_id": result.run_id,
            "prediction_count": len(result.predictions),
            "markdown_report": str(md_path),
            "json_report": str(json_path),
        }
        record_runtime_job("live_slate", "success", detail)
        if ORACLE_NOTIFY_COMPLETION:
            digest = format_live_digest(load_latest_live_report())
            _safe_notify("completion_live_slate", digest, "NBA Oracle analysis complete")
        return detail
    except Exception as exc:
        detail = {"error": str(exc), "bundle_path": str(bundle_path) if bundle_path else None}
        record_runtime_job("live_slate", "failed", detail)
        if ORACLE_NOTIFY_FAILURE:
            _safe_notify("failure_live_slate", str(exc), "NBA Oracle live slate failure")
        raise


def run_outcome_grading_job() -> dict[str, Any]:
    try:
        result = grade_outcomes()
        md_path = write_outcome_markdown_report(result)
        json_path = write_outcome_json_report(result)
        detail = {
            "newly_graded": result.newly_graded,
            "pending_unfinished": result.pending_unfinished,
            "markdown_report": str(md_path),
            "json_report": str(json_path),
        }
        record_runtime_job("grade_outcomes", "success", detail)
        return detail
    except Exception as exc:
        detail = {"error": str(exc)}
        record_runtime_job("grade_outcomes", "failed", detail)
        if ORACLE_NOTIFY_FAILURE:
            _safe_notify("failure_grade_outcomes", str(exc), "NBA Oracle outcome grading failure")
        raise


def run_stability_review_job(*, force_refresh_baseline: bool = False) -> dict[str, Any]:
    try:
        result, baseline_path, md_path, json_path = review_stability(
            replay_report_path=DEFAULT_JSON_REPORT_PATH,
            force_refresh_baseline=force_refresh_baseline,
        )
        detail = {
            "review_id": result.review_id,
            "baseline_path": str(baseline_path),
            "markdown_report": str(md_path),
            "json_report": str(json_path),
            "drift_status": result.drift.status,
        }
        record_runtime_job("review_stability", "success", detail)
        return detail
    except Exception as exc:
        detail = {"error": str(exc)}
        record_runtime_job("review_stability", "failed", detail)
        if ORACLE_NOTIFY_FAILURE:
            _safe_notify("failure_review_stability", str(exc), "NBA Oracle stability review failure")
        raise


def run_learning_review_job() -> dict[str, Any]:
    try:
        result = run_learning_review()
        md_path = write_learning_markdown_report(result)
        json_path = write_learning_json_report(result)
        detail = {
            "review_id": result.review_id,
            "status": result.status,
            "candidate_model_version": result.candidate_model_version,
            "markdown_report": str(md_path),
            "json_report": str(json_path),
        }
        record_runtime_job("learning_review", "success", detail)
        return detail
    except Exception as exc:
        detail = {"error": str(exc)}
        record_runtime_job("learning_review", "failed", detail)
        if ORACLE_NOTIFY_FAILURE:
            _safe_notify("failure_learning_review", str(exc), "NBA Oracle learning review failure")
        raise


def run_midnight_confirmation_job() -> dict[str, Any]:
    snapshot = build_health_snapshot()
    message = format_health_digest(snapshot)
    if ORACLE_NOTIFY_MIDNIGHT:
        _safe_notify("midnight_status", message, "NBA Oracle midnight status")
    detail = {"message": message}
    record_runtime_job("midnight_confirmation", "success", detail)
    return detail


def _safe_notify(event_type: str, message: str, subject: str) -> None:
    try:
        send_telegram_message(message, event_type=event_type)
    except Exception:
        pass
    try:
        send_gmail_message(subject, message, event_type=event_type)
    except Exception:
        pass
