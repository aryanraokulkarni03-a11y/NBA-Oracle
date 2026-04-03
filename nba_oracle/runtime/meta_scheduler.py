from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any, Callable
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from nba_oracle.config import (
    LEARNING_ENABLE_AUTO_REVIEW,
    LEARNING_MIN_GRADED_PICKS,
    ORACLE_NOTIFY_MIDNIGHT,
    ORACLE_SCHEDULER_LIVE_TARGET_MINUTES,
    ORACLE_SCHEDULER_LIVE_WINDOW_MINUTES,
    ORACLE_TIMEZONE,
)
from nba_oracle.providers.schedule import ScheduleProvider
from nba_oracle.runtime.health import (
    load_latest_learning_report,
    load_latest_live_report,
    load_latest_outcome_report,
    load_latest_stability_report,
)
from nba_oracle.runtime.jobs import (
    run_learning_review_job,
    run_live_slate_job,
    run_midnight_confirmation_job,
    run_outcome_grading_job,
    run_stability_review_job,
)
from nba_oracle.runtime.state import load_runtime_state


@dataclass(frozen=True)
class ScheduledJobDecision:
    job_name: str
    due: bool
    reason: str
    last_finished_at: str | None


def plan_scheduler_jobs(now: datetime | None = None) -> tuple[ScheduledJobDecision, ...]:
    current_time = now or datetime.now(timezone.utc)
    local_now = current_time.astimezone(_runtime_zone())
    runtime_state = load_runtime_state()
    latest_live = load_latest_live_report()
    latest_outcomes = load_latest_outcome_report()
    latest_stability = load_latest_stability_report()
    latest_learning = load_latest_learning_report()

    decisions = [
        _plan_midnight_confirmation(local_now, runtime_state),
        _plan_live_slate(current_time, local_now, runtime_state, latest_live),
        _plan_outcome_grading(current_time, runtime_state, latest_outcomes),
        _plan_stability_review(current_time, runtime_state, latest_outcomes, latest_stability),
        _plan_learning_review(current_time, runtime_state, latest_outcomes, latest_learning),
    ]
    return tuple(decisions)


def run_scheduler_once(*, now: datetime | None = None, force: bool = False) -> dict[str, Any]:
    current_time = now or datetime.now(timezone.utc)
    decisions = plan_scheduler_jobs(current_time)
    executed: list[dict[str, Any]] = []

    jobs: dict[str, Callable[[], dict[str, Any]]] = {
        "midnight_confirmation": run_midnight_confirmation_job,
        "live_slate": lambda: run_live_slate_job(use_live=True),
        "grade_outcomes": run_outcome_grading_job,
        "review_stability": run_stability_review_job,
        "learning_review": run_learning_review_job,
    }

    for decision in decisions:
        if not (force or decision.due):
            continue
        result = jobs[decision.job_name]()
        executed.append(
            {
                "job_name": decision.job_name,
                "reason": decision.reason,
                "detail": result,
            }
        )

    return {
        "ran_at": current_time.isoformat(),
        "forced": force,
        "decisions": [
            {
                "job_name": item.job_name,
                "due": item.due,
                "reason": item.reason,
                "last_finished_at": item.last_finished_at,
            }
            for item in decisions
        ],
        "executed_jobs": executed,
    }


def _plan_midnight_confirmation(local_now: datetime, runtime_state: dict[str, Any]) -> ScheduledJobDecision:
    last_finished = _last_job_finished_at(runtime_state, "midnight_confirmation")
    last_local_date = _local_date(last_finished) if last_finished else None
    due = bool(
        ORACLE_NOTIFY_MIDNIGHT
        and local_now.hour == 0
        and local_now.minute < 20
        and last_local_date != local_now.date()
    )
    reason = "daily_midnight_window_open" if due else "midnight_window_closed_or_already_sent"
    return ScheduledJobDecision("midnight_confirmation", due, reason, last_finished)


def _plan_live_slate(
    current_time: datetime,
    local_now: datetime,
    runtime_state: dict[str, Any],
    latest_live: dict[str, Any],
) -> ScheduledJobDecision:
    del local_now
    last_finished = _last_job_finished_at(runtime_state, "live_slate")
    last_run_time = _parse_dt(last_finished)
    upcoming_tipoffs = _load_upcoming_tipoffs(current_time)
    if not upcoming_tipoffs:
        return ScheduledJobDecision("live_slate", False, "no_upcoming_games_detected", last_finished)

    earliest_tipoff = min(upcoming_tipoffs)
    minutes_until_tipoff = (earliest_tipoff - current_time).total_seconds() / 60.0
    latest_report_run_id = str(latest_live.get("run_id") or "")
    report_is_today = latest_report_run_id.startswith(current_time.strftime("live-%Y%m%d"))
    stale_report = last_run_time is None or (current_time - last_run_time) >= timedelta(minutes=90)
    min_minutes = ORACLE_SCHEDULER_LIVE_TARGET_MINUTES - ORACLE_SCHEDULER_LIVE_WINDOW_MINUTES
    max_minutes = ORACLE_SCHEDULER_LIVE_TARGET_MINUTES + ORACLE_SCHEDULER_LIVE_WINDOW_MINUTES
    due = min_minutes <= minutes_until_tipoff <= max_minutes and (stale_report or not report_is_today)
    reason = (
        f"earliest_tipoff_in_{int(minutes_until_tipoff)}m_target_{ORACLE_SCHEDULER_LIVE_TARGET_MINUTES}"
        if due
        else f"live_slate_not_due_{int(minutes_until_tipoff)}m_target_{ORACLE_SCHEDULER_LIVE_TARGET_MINUTES}"
    )
    return ScheduledJobDecision("live_slate", due, reason, last_finished)


def _plan_outcome_grading(
    current_time: datetime,
    runtime_state: dict[str, Any],
    latest_outcomes: dict[str, Any],
) -> ScheduledJobDecision:
    last_finished = _last_job_finished_at(runtime_state, "grade_outcomes")
    last_run_time = _parse_dt(last_finished)
    pending_unfinished = int(latest_outcomes.get("pending_unfinished") or 0)
    newly_graded = int(latest_outcomes.get("newly_graded") or 0)
    due = pending_unfinished > 0 and (last_run_time is None or (current_time - last_run_time) >= timedelta(hours=2))
    reason = (
        f"pending_unfinished_{pending_unfinished}"
        if due
        else f"grading_wait_pending_{pending_unfinished}_new_{newly_graded}"
    )
    return ScheduledJobDecision("grade_outcomes", due, reason, last_finished)


def _plan_stability_review(
    current_time: datetime,
    runtime_state: dict[str, Any],
    latest_outcomes: dict[str, Any],
    latest_stability: dict[str, Any],
) -> ScheduledJobDecision:
    last_finished = _last_job_finished_at(runtime_state, "review_stability")
    last_run_time = _parse_dt(last_finished)
    latest_outcome_time = _parse_dt(str(latest_outcomes.get("graded_at") or "")) if latest_outcomes else None
    drift_status = str(latest_stability.get("drift", {}).get("status") or "")
    due = bool(
        latest_outcome_time
        and (last_run_time is None or latest_outcome_time > last_run_time)
        and (drift_status in {"", "insufficient_data", "insufficient_outcomes", "warning", "stable"})
    )
    reason = "outcome_grading_ahead_of_stability_review" if due else "stability_review_current"
    return ScheduledJobDecision("review_stability", due, reason, last_finished)


def _plan_learning_review(
    current_time: datetime,
    runtime_state: dict[str, Any],
    latest_outcomes: dict[str, Any],
    latest_learning: dict[str, Any],
) -> ScheduledJobDecision:
    last_finished = _last_job_finished_at(runtime_state, "learning_review")
    last_run_time = _parse_dt(last_finished)
    if not LEARNING_ENABLE_AUTO_REVIEW:
        return ScheduledJobDecision("learning_review", False, "learning_auto_review_disabled", last_finished)

    eligible_count = int(
        latest_learning.get("graded_prediction_count")
        or latest_outcomes.get("eligible_predictions")
        or 0
    )
    due = eligible_count >= LEARNING_MIN_GRADED_PICKS and (
        last_run_time is None or (current_time - last_run_time) >= timedelta(hours=12)
    )
    reason = (
        f"graded_predictions_ready_{eligible_count}"
        if due
        else f"learning_waiting_for_more_graded_predictions_{eligible_count}"
    )
    return ScheduledJobDecision("learning_review", due, reason, last_finished)


def _last_job_finished_at(runtime_state: dict[str, Any], job_name: str) -> str | None:
    last_jobs = runtime_state.get("last_jobs", {})
    payload = last_jobs.get(job_name, {}) if isinstance(last_jobs, dict) else {}
    value = payload.get("finished_at") if isinstance(payload, dict) else None
    return str(value) if value else None


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _local_date(value: str | None) -> date | None:
    parsed = _parse_dt(value)
    if parsed is None:
        return None
    return parsed.astimezone(_runtime_zone()).date()


def _load_upcoming_tipoffs(current_time: datetime) -> list[datetime]:
    response = ScheduleProvider().fetch_live(current_time, {})
    tipoffs: list[datetime] = []
    for record in response.records:
        tipoff_text = str(record.data.get("tipoff_time") or "")
        tipoff_time = _parse_dt(tipoff_text)
        if tipoff_time is None or tipoff_time < current_time:
            continue
        tipoffs.append(tipoff_time)
    return tipoffs


def _runtime_zone() -> ZoneInfo | timezone:
    candidates = [ORACLE_TIMEZONE]
    if ORACLE_TIMEZONE == "Asia/Calcutta":
        candidates.append("Asia/Kolkata")
    for key in candidates:
        try:
            return ZoneInfo(key)
        except ZoneInfoNotFoundError:
            continue
    return timezone.utc
