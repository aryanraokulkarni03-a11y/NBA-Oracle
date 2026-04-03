from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from nba_oracle.config import SOURCE_MAX_AGE_MINUTES
from nba_oracle.stability.baseline import LiveRunSnapshot


@dataclass(frozen=True)
class TimingEvent:
    review_id: str
    run_id: str
    game_id: str
    event_type: str
    source_kind: str
    source_name: str
    source_timestamp: str
    decision_timestamp: str
    market_timestamp: str | None
    market_already_moved: bool
    predictor_changed: bool
    decision: str
    event_impact: str
    age_minutes: float
    signal_delta: float


@dataclass(frozen=True)
class TimingAssessment:
    status: str
    runs_considered: int
    stale_source_count: int
    average_source_age_minutes: float
    average_market_age_minutes: float
    schedule_fallback_rate: float
    notes: tuple[str, ...]
    events: tuple[TimingEvent, ...]


def assess_timing(review_id: str, live_runs: tuple[LiveRunSnapshot, ...]) -> TimingAssessment:
    source_ages: list[float] = []
    market_ages: list[float] = []
    stale_source_count = 0
    events: list[TimingEvent] = []

    for run in live_runs:
        for prediction in run.predictions:
            market_age = 0.0
            if prediction.market_timestamp is not None:
                market_age = max(
                    (run.decision_time - prediction.market_timestamp).total_seconds() / 60,
                    0.0,
                )
                market_ages.append(round(market_age, 2))

            for score in prediction.source_scores:
                age_minutes = float(score.get("age_minutes", 0.0))
                source_ages.append(age_minutes)
                kind = str(score.get("kind", ""))
                max_age = SOURCE_MAX_AGE_MINUTES.get(kind)
                if max_age is not None and age_minutes > max_age:
                    stale_source_count += 1

                source_timestamp = run.decision_time - timedelta(minutes=age_minutes)
                signal_delta = float(score.get("signal_delta", 0.0))
                events.append(
                    TimingEvent(
                        review_id=review_id,
                        run_id=run.run_id,
                        game_id=prediction.game_id,
                        event_type="source_observation",
                        source_kind=kind,
                        source_name=str(score.get("name", "")),
                        source_timestamp=source_timestamp.isoformat(),
                        decision_timestamp=run.decision_time.isoformat(),
                        market_timestamp=prediction.market_timestamp.isoformat()
                        if prediction.market_timestamp
                        else None,
                        market_already_moved=prediction.price_gap > 0.01 or market_age > 15,
                        predictor_changed=False,
                        decision=prediction.decision,
                        event_impact=_classify_impact(prediction.decision, signal_delta),
                        age_minutes=round(age_minutes, 2),
                        signal_delta=round(signal_delta, 4),
                    )
                )

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

    if events:
        notes.append("Timing events were recorded for each reviewed source observation.")
    else:
        notes.append("No timing events were recorded because the review window had no actionable live predictions.")

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
        events=tuple(events),
    )


def _classify_impact(decision: str, signal_delta: float) -> str:
    if abs(signal_delta) < 0.003:
        return "neutral"
    if decision == "BET" and signal_delta > 0:
        return "strengthened"
    if decision == "SKIP" and signal_delta < 0:
        return "canceled"
    if signal_delta > 0:
        return "supporting"
    return "weakening"
