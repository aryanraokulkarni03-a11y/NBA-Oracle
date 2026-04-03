from __future__ import annotations

from dataclasses import dataclass

from nba_oracle.config import (
    PHASE3_MAX_ACTIVE_BET_RATE_DELTA,
    PHASE3_MAX_EDGE_DELTA,
    PHASE3_MAX_PROVIDER_DEGRADATION_RATE,
    PHASE3_MAX_SKIP_RATE_DELTA,
    PHASE3_MAX_SOURCE_QUALITY_DELTA,
    PHASE3_MIN_GRADED_PICKS_FOR_RETRAIN,
    PHASE3_MIN_LIVE_RUNS_FOR_DRIFT,
)
from nba_oracle.stability.baseline import BaselineSnapshot, LiveRunSnapshot


@dataclass(frozen=True)
class DriftSignal:
    name: str
    baseline_value: float
    current_value: float
    delta: float
    threshold: float
    triggered: bool
    note: str


@dataclass(frozen=True)
class DriftAssessment:
    status: str
    live_runs_considered: int
    graded_predictions: int
    retraining_recommended: bool
    reasons: tuple[str, ...]
    signals: tuple[DriftSignal, ...]


def assess_drift(
    baseline: BaselineSnapshot,
    live_runs: tuple[LiveRunSnapshot, ...],
) -> DriftAssessment:
    if len(live_runs) < PHASE3_MIN_LIVE_RUNS_FOR_DRIFT:
        return DriftAssessment(
            status="insufficient_data",
            live_runs_considered=len(live_runs),
            graded_predictions=sum(run.graded_prediction_count for run in live_runs),
            retraining_recommended=False,
            reasons=("Need more live runs before drift can be judged safely.",),
            signals=(),
        )

    current_active_bet_rate = _average(live_runs, "active_bet_rate")
    current_skip_rate = _average(live_runs, "skip_rate")
    current_source_quality = _average(live_runs, "average_source_quality")
    current_edge = _average(live_runs, "average_edge")
    current_provider_degradation_rate = _average(live_runs, "provider_degradation_rate")

    signals = (
        _build_signal(
            "active_bet_rate",
            baseline.live_average_active_bet_rate,
            current_active_bet_rate,
            PHASE3_MAX_ACTIVE_BET_RATE_DELTA,
            "Large active-bet swings can mean the gate is no longer behaving like the validated baseline.",
        ),
        _build_signal(
            "skip_rate",
            baseline.live_average_skip_rate,
            current_skip_rate,
            PHASE3_MAX_SKIP_RATE_DELTA,
            "Skip discipline is part of the edge, so a sharp change matters even before outcomes settle.",
        ),
        _build_signal(
            "source_quality",
            baseline.live_average_source_quality,
            current_source_quality,
            PHASE3_MAX_SOURCE_QUALITY_DELTA,
            "If source quality falls, prediction trust should fall with it.",
        ),
        _build_signal(
            "edge_vs_reference",
            baseline.live_average_edge,
            current_edge,
            PHASE3_MAX_EDGE_DELTA,
            "Edge drift can signal stale pricing assumptions or weakened data quality.",
        ),
        _build_signal(
            "provider_degradation_rate",
            baseline.live_average_provider_degradation_rate,
            current_provider_degradation_rate,
            PHASE3_MAX_PROVIDER_DEGRADATION_RATE,
            "Provider degradation should stay rare in normal operation.",
        ),
    )

    triggered = tuple(signal for signal in signals if signal.triggered)
    graded_predictions = sum(run.graded_prediction_count for run in live_runs)
    retraining_recommended = bool(
        triggered and graded_predictions >= PHASE3_MIN_GRADED_PICKS_FOR_RETRAIN
    )

    if triggered:
        status = "warning" if not retraining_recommended else "retrain_review"
        reasons = tuple(signal.note for signal in triggered)
    else:
        status = "stable"
        reasons = ("Recent live behavior is within configured drift thresholds.",)

    if triggered and not retraining_recommended:
        reasons = reasons + (
            "Drift is visible, but retraining stays blocked until the graded sample is large enough.",
        )

    return DriftAssessment(
        status=status,
        live_runs_considered=len(live_runs),
        graded_predictions=graded_predictions,
        retraining_recommended=retraining_recommended,
        reasons=reasons,
        signals=signals,
    )


def _average(live_runs: tuple[LiveRunSnapshot, ...], attribute: str) -> float:
    if not live_runs:
        return 0.0
    return round(sum(getattr(run, attribute) for run in live_runs) / len(live_runs), 4)


def _build_signal(
    name: str,
    baseline_value: float,
    current_value: float,
    threshold: float,
    note: str,
) -> DriftSignal:
    delta = round(current_value - baseline_value, 4)
    return DriftSignal(
        name=name,
        baseline_value=round(baseline_value, 4),
        current_value=round(current_value, 4),
        delta=delta,
        threshold=threshold,
        triggered=abs(delta) > threshold,
        note=note,
    )
