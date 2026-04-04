from __future__ import annotations

from datetime import datetime, timezone
from datetime import tzinfo

from fastapi import APIRouter, Depends

from nba_oracle.api.dependencies import require_authenticated_user
from nba_oracle.runtime.health import load_latest_live_report
from nba_oracle.runtime.prediction_views import load_latest_prediction_views_by_game


router = APIRouter(prefix="/api", tags=["today"])


@router.get("/today")
def today(_: dict[str, object] = Depends(require_authenticated_user)) -> dict[str, object]:
    report = load_latest_live_report()
    actionable_predictions, next_up_predictions = _partition_upcoming_predictions()
    return {
        "run_id": report.get("run_id"),
        "decision_time": report.get("decision_time"),
        "storage_mode": report.get("storage_mode"),
        "providers": report.get("providers", []),
        "predictions": actionable_predictions,
        "actionable_predictions": actionable_predictions,
        "next_up_predictions": next_up_predictions,
        "stored_paths": report.get("stored_paths", []),
    }


def _partition_upcoming_predictions() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    now = datetime.now(timezone.utc)
    timezone_info = _resolve_timezone()
    upcoming: list[tuple[datetime, dict[str, object]]] = []

    for prediction in load_latest_prediction_views_by_game():
        tipoff_time = _parse_datetime(prediction.get("tipoff_time"))
        if tipoff_time is None or tipoff_time <= now:
            continue
        actual_winner = prediction.get("actual_winner")
        if isinstance(actual_winner, str) and actual_winner.strip():
            continue
        upcoming.append((tipoff_time, prediction))

    if not upcoming:
        return [], []

    upcoming.sort(key=lambda item: item[0])
    available_dates: list[object] = []
    for tipoff_time, _prediction in upcoming:
        local_date = tipoff_time.astimezone(timezone_info).date()
        if local_date not in available_dates:
            available_dates.append(local_date)

    primary_date = available_dates[0]
    next_date = available_dates[1] if len(available_dates) > 1 else None

    actionable = [
        prediction
        for tipoff_time, prediction in upcoming
        if tipoff_time.astimezone(timezone_info).date() == primary_date
    ]
    next_up = [
        prediction
        for tipoff_time, prediction in upcoming
        if next_date is not None and tipoff_time.astimezone(timezone_info).date() == next_date
    ]
    return actionable, next_up


def _parse_datetime(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _resolve_timezone() -> tzinfo:
    return datetime.now().astimezone().tzinfo or timezone.utc
