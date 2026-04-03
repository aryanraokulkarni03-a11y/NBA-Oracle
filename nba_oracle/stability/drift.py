from __future__ import annotations

from dataclasses import dataclass

from nba_oracle.config import (
    CALIBRATION_MAX_BIN_ABS_GAP,
    CALIBRATION_MAX_MEAN_ABS_GAP,
    CALIBRATION_MIN_ACTIONABLE_COUNT,
    PHASE3_MAX_ACTIVE_BET_RATE_DELTA,
    PHASE3_MAX_CALIBRATION_GAP_DELTA,
    PHASE3_MAX_CLV_DELTA,
    PHASE3_MAX_EDGE_DELTA,
    PHASE3_MAX_PROVIDER_DEGRADATION_RATE,
    PHASE3_MAX_ROI_DELTA,
    PHASE3_MAX_SKIP_RATE_DELTA,
    PHASE3_MAX_SOURCE_QUALITY_DELTA,
    PHASE3_MIN_GRADED_PICKS_FOR_RETRAIN,
    PHASE3_MIN_LIVE_RUNS_FOR_DRIFT,
)
from nba_oracle.market import realized_profit
from nba_oracle.stability.baseline import BaselineSnapshot, LivePredictionSnapshot, LiveRunSnapshot


@dataclass(frozen=True)
class DriftSignal:
    name: str
    baseline_value: float
    current_value: float
    delta: float
    threshold: float
    triggered: bool
    available: bool
    sample_size: int
    note: str


@dataclass(frozen=True)
class LiveOutcomeMetrics:
    graded_bet_count: int
    graded_actionable_count: int
    roi: float | None
    average_clv: float | None
    calibration_gap: float | None


@dataclass(frozen=True)
class DriftAssessment:
    status: str
    live_runs_considered: int
    graded_predictions: int
    retraining_recommended: bool
    reasons: tuple[str, ...]
    signals: tuple[DriftSignal, ...]
    outcome_metrics: LiveOutcomeMetrics


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
            outcome_metrics=LiveOutcomeMetrics(0, 0, None, None, None),
        )

    current_active_bet_rate = _average(live_runs, "active_bet_rate")
    current_skip_rate = _average(live_runs, "skip_rate")
    current_source_quality = _average(live_runs, "average_source_quality")
    current_edge = _average(live_runs, "average_edge")
    current_provider_degradation_rate = _average(live_runs, "provider_degradation_rate")

    outcome_metrics = _build_outcome_metrics(live_runs)

    signals = (
        _build_signal(
            "roi",
            baseline.replay_roi,
            outcome_metrics.roi,
            PHASE3_MAX_ROI_DELTA,
            outcome_metrics.graded_bet_count,
            "ROI drift matters only once enough graded bets exist to trust the comparison.",
        ),
        _build_signal(
            "clv",
            baseline.replay_average_clv,
            outcome_metrics.average_clv,
            PHASE3_MAX_CLV_DELTA,
            outcome_metrics.graded_bet_count,
            "CLV drift is a core signal that the model may be losing its price edge.",
        ),
        _build_signal(
            "calibration_gap",
            baseline.replay_calibration_gap,
            outcome_metrics.calibration_gap,
            PHASE3_MAX_CALIBRATION_GAP_DELTA,
            outcome_metrics.graded_actionable_count,
            "Calibration drift means model confidence is no longer matching outcomes honestly.",
        ),
        _build_signal(
            "active_bet_rate",
            baseline.live_average_active_bet_rate,
            current_active_bet_rate,
            PHASE3_MAX_ACTIVE_BET_RATE_DELTA,
            len(live_runs),
            "Large active-bet swings can mean the gate is no longer behaving like the validated baseline.",
        ),
        _build_signal(
            "skip_rate",
            baseline.live_average_skip_rate,
            current_skip_rate,
            PHASE3_MAX_SKIP_RATE_DELTA,
            len(live_runs),
            "Skip discipline is part of the edge, so a sharp change matters even before outcomes settle.",
        ),
        _build_signal(
            "source_quality",
            baseline.live_average_source_quality,
            current_source_quality,
            PHASE3_MAX_SOURCE_QUALITY_DELTA,
            len(live_runs),
            "If source quality falls, prediction trust should fall with it.",
        ),
        _build_signal(
            "edge_vs_reference",
            baseline.live_average_edge,
            current_edge,
            PHASE3_MAX_EDGE_DELTA,
            len(live_runs),
            "Edge drift can signal stale pricing assumptions or weakened data quality.",
        ),
        _build_signal(
            "provider_degradation_rate",
            baseline.live_average_provider_degradation_rate,
            current_provider_degradation_rate,
            PHASE3_MAX_PROVIDER_DEGRADATION_RATE,
            len(live_runs),
            "Provider degradation should stay rare in normal operation.",
        ),
    )

    triggered = tuple(signal for signal in signals if signal.available and signal.triggered)
    graded_predictions = sum(run.graded_prediction_count for run in live_runs)
    retraining_recommended = bool(
        triggered
        and outcome_metrics.graded_bet_count >= PHASE3_MIN_GRADED_PICKS_FOR_RETRAIN
        and outcome_metrics.roi is not None
        and outcome_metrics.average_clv is not None
        and outcome_metrics.calibration_gap is not None
    )

    if triggered:
        status = "warning" if not retraining_recommended else "retrain_review"
        reasons = tuple(signal.note for signal in triggered)
    elif any(not signal.available for signal in signals[:3]):
        status = "insufficient_outcomes"
        reasons = ("Live outcome-based drift metrics still need more graded history.",)
    else:
        status = "stable"
        reasons = ("Recent live behavior is within configured drift thresholds.",)

    if triggered and not retraining_recommended:
        reasons = reasons + (
            "Drift is visible, but retraining stays blocked until enough graded evidence exists.",
        )

    return DriftAssessment(
        status=status,
        live_runs_considered=len(live_runs),
        graded_predictions=graded_predictions,
        retraining_recommended=retraining_recommended,
        reasons=reasons,
        signals=signals,
        outcome_metrics=outcome_metrics,
    )


def _average(live_runs: tuple[LiveRunSnapshot, ...], attribute: str) -> float:
    if not live_runs:
        return 0.0
    return round(sum(getattr(run, attribute) for run in live_runs) / len(live_runs), 4)


def _build_signal(
    name: str,
    baseline_value: float,
    current_value: float | None,
    threshold: float,
    sample_size: int,
    note: str,
) -> DriftSignal:
    if current_value is None:
        return DriftSignal(
            name=name,
            baseline_value=round(baseline_value, 4),
            current_value=0.0,
            delta=0.0,
            threshold=threshold,
            triggered=False,
            available=False,
            sample_size=sample_size,
            note=note,
        )

    delta = round(current_value - baseline_value, 4)
    return DriftSignal(
        name=name,
        baseline_value=round(baseline_value, 4),
        current_value=round(current_value, 4),
        delta=delta,
        threshold=threshold,
        triggered=abs(delta) > threshold,
        available=True,
        sample_size=sample_size,
        note=note,
    )


def _build_outcome_metrics(live_runs: tuple[LiveRunSnapshot, ...]) -> LiveOutcomeMetrics:
    graded_active = [item for run in live_runs for item in run.predictions if item.is_active and item.is_graded]
    graded_actionable = [item for run in live_runs for item in run.predictions if item.is_actionable and item.is_graded]

    if graded_active:
        stake = float(len(graded_active))
        profit = sum(realized_profit(item.stake_american) if item.won else -1.0 for item in graded_active)
        roi = round(profit / stake, 4)
        average_clv = round(sum(item.clv for item in graded_active) / len(graded_active), 4)
    else:
        roi = None
        average_clv = None

    calibration_gap = _build_calibration_gap(graded_actionable)
    return LiveOutcomeMetrics(
        graded_bet_count=len(graded_active),
        graded_actionable_count=len(graded_actionable),
        roi=roi,
        average_clv=average_clv,
        calibration_gap=calibration_gap,
    )


def _build_calibration_gap(predictions: list[LivePredictionSnapshot]) -> float | None:
    if len(predictions) < CALIBRATION_MIN_ACTIONABLE_COUNT:
        return None

    gaps: list[float] = []
    max_gap = 0.0
    for start in range(50, 100, 10):
        lower = start / 100
        upper = (start + 10) / 100
        matching = [item for item in predictions if lower <= item.model_probability < upper]
        if not matching:
            continue
        average_probability = sum(item.model_probability for item in matching) / len(matching)
        hit_rate = sum(1 for item in matching if item.won) / len(matching)
        gap = abs(average_probability - hit_rate)
        gaps.append(gap)
        max_gap = max(max_gap, gap)

    if not gaps:
        return None

    mean_gap = round(sum(gaps) / len(gaps), 4)
    if max_gap > CALIBRATION_MAX_BIN_ABS_GAP and mean_gap < CALIBRATION_MAX_MEAN_ABS_GAP:
        return round(max_gap, 4)
    return mean_gap
