from __future__ import annotations

from dataclasses import dataclass

from nba_oracle.config import SOURCE_MAX_AGE_MINUTES
from nba_oracle.stability.baseline import LiveRunSnapshot


@dataclass(frozen=True)
class TimingAssessment:
    status: str
    runs_considered: int
    stale_source_count: int
    average_source_age_minutes: float
    average_market_age_minutes: float
    schedule_fallback_rate: float
    notes: tuple[str, ...]


def assess_timing(live_runs: tuple[LiveRunSnapshot, ...]) -> TimingAssessment:
    source_ages: list[float] = []
    market_ages: list[float] = []
    stale_source_count = 0

    for run in live_runs:
        for prediction in run.predictions:
            if prediction.market_timestamp is not None:
                market_age = (run.decision_time - prediction.market_timestamp).total_seconds() / 60
                market_ages.append(round(max(market_age, 0.0), 2))
            for score in prediction.source_scores:
                age_minutes = float(score.get("age_minutes", 0.0))
                source_ages.append(age_minutes)
                kind = str(score.get("kind", ""))
                max_age = SOURCE_MAX_AGE_MINUTES.get(kind)
                if max_age is not None and age_minutes > max_age:
                    stale_source_count += 1

    schedule_fallback_rate = 0.0
    if live_runs:
        schedule_fallback_rate = round(
            sum(1 for run in live_runs if run.schedule_fallback_used) / len(live_runs),
            4,
        )

    average_source_age = round(sum(source_ages) / len(source_ages), 2) if source_ages else 0.0
    average_market_age = round(sum(market_ages) / len(market_ages), 2) if market_ages else 0.0

    notes: list[str] = []
    if stale_source_count == 0:
        notes.append("No source entries breached their configured freshness windows in the review set.")
    else:
        notes.append("Some source entries were stale enough to weaken timing trust.")

    if schedule_fallback_rate > 0:
        notes.append("Schedule fallback was used in part of the review window; keep watching upstream freshness.")

    if stale_source_count == 0 and average_market_age <= 60:
        status = "healthy"
    elif stale_source_count <= 2:
        status = "watch"
    else:
        status = "degraded"

    return TimingAssessment(
        status=status,
        runs_considered=len(live_runs),
        stale_source_count=stale_source_count,
        average_source_age_minutes=average_source_age,
        average_market_age_minutes=average_market_age,
        schedule_fallback_rate=schedule_fallback_rate,
        notes=tuple(notes),
    )
