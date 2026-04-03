from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from nba_oracle.config import (
    CALIBRATION_MAX_BIN_ABS_GAP,
    CALIBRATION_MAX_MEAN_ABS_GAP,
    CALIBRATION_MIN_ACTIONABLE_COUNT,
    CALIBRATION_MIN_POPULATED_BINS,
)
from nba_oracle.market import realized_profit
from nba_oracle.models import PredictionResult, SourceScore
from nba_oracle.predictor import evaluate_game
from nba_oracle.snapshots import load_game_snapshots


@dataclass(frozen=True)
class CalibrationBin:
    label: str
    count: int
    average_probability: float
    hit_rate: float
    absolute_gap: float


@dataclass(frozen=True)
class CalibrationAssessment:
    status: str
    actionable_count: int
    populated_bins: int
    mean_absolute_gap: float
    max_absolute_gap: float
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class SourceAuditRow:
    name: str
    kind: str
    samples: int
    average_freshness: float
    average_trust: float
    average_quality: float
    average_age_minutes: float
    average_signal_delta: float


@dataclass(frozen=True)
class ReplayReport:
    fixture_path: Path
    total_games: int
    bet_count: int
    lean_count: int
    skip_count: int
    hit_rate: float
    roi: float
    average_clv: float
    average_edge: float
    average_source_quality: float
    average_stake_to_best_gap: float
    average_stake_to_close_gap: float
    calibration_bins: tuple[CalibrationBin, ...]
    calibration_assessment: CalibrationAssessment
    phase1_ready: bool
    source_audit: tuple[SourceAuditRow, ...]
    skip_reasons: dict[str, int]
    predictions: tuple[PredictionResult, ...]


def run_replay(fixture_path: Path) -> ReplayReport:
    games = load_game_snapshots(fixture_path)
    predictions = tuple(evaluate_game(game) for game in games)

    active_bets = [item for item in predictions if item.decision == "BET"]
    leans = [item for item in predictions if item.decision == "LEAN"]
    actionable = [item for item in predictions if item.decision != "SKIP"]
    skips = [item for item in predictions if item.decision == "SKIP"]

    bet_count = len(active_bets)
    stake = float(bet_count) if bet_count else 0.0
    profit = (
        sum(
            realized_profit_for_pick(item) if item.won else -1.0
            for item in active_bets
        )
        if active_bets
        else 0.0
    )
    hit_rate = (
        round(sum(1 for item in active_bets if item.won) / bet_count, 4)
        if bet_count
        else 0.0
    )
    roi = round(profit / stake, 4) if stake else 0.0
    average_clv = (
        round(
            sum(item.close_probability - item.stake_probability for item in active_bets)
            / bet_count,
            4,
        )
        if bet_count
        else 0.0
    )
    average_edge = (
        round(sum(item.edge_vs_stake for item in active_bets) / bet_count, 4)
        if bet_count
        else 0.0
    )
    average_source_quality = round(
        sum(item.source_quality for item in predictions) / len(predictions), 4
    )
    average_stake_to_best_gap = round(
        sum(abs(item.stake_probability - item.best_probability) for item in predictions)
        / len(predictions),
        4,
    )
    average_stake_to_close_gap = round(
        sum(abs(item.stake_probability - item.close_probability) for item in predictions)
        / len(predictions),
        4,
    )
    skip_reasons = Counter(
        reason for item in skips for reason in item.reasons
    )
    calibration_bins = build_calibration_bins(actionable)
    calibration_assessment = assess_calibration(calibration_bins)

    return ReplayReport(
        fixture_path=fixture_path,
        total_games=len(predictions),
        bet_count=bet_count,
        lean_count=len(leans),
        skip_count=len(skips),
        hit_rate=hit_rate,
        roi=roi,
        average_clv=average_clv,
        average_edge=average_edge,
        average_source_quality=average_source_quality,
        average_stake_to_best_gap=average_stake_to_best_gap,
        average_stake_to_close_gap=average_stake_to_close_gap,
        calibration_bins=calibration_bins,
        calibration_assessment=calibration_assessment,
        phase1_ready=calibration_assessment.status == "PASS" and bet_count > 0,
        source_audit=build_source_audit(predictions),
        skip_reasons=dict(skip_reasons),
        predictions=predictions,
    )


def realized_profit_for_pick(prediction: PredictionResult) -> float:
    return realized_profit(prediction.stake_american)


def build_calibration_bins(predictions: list[PredictionResult]) -> tuple[CalibrationBin, ...]:
    bins: list[CalibrationBin] = []
    for start in range(50, 100, 10):
        end = start + 10
        lower = start / 100
        upper = end / 100
        matching = [
            item for item in predictions
            if lower <= item.model_probability < upper
        ]
        if matching:
            average_probability = round(
                sum(item.model_probability for item in matching) / len(matching), 4
            )
            hit_rate = round(
                sum(1 for item in matching if item.won) / len(matching), 4
            )
            absolute_gap = round(abs(average_probability - hit_rate), 4)
        else:
            average_probability = 0.0
            hit_rate = 0.0
            absolute_gap = 0.0
        bins.append(
            CalibrationBin(
                label=f"{start}-{end}",
                count=len(matching),
                average_probability=average_probability,
                hit_rate=hit_rate,
                absolute_gap=absolute_gap,
            )
        )
    return tuple(bins)


def assess_calibration(bins: tuple[CalibrationBin, ...]) -> CalibrationAssessment:
    actionable_count = sum(bucket.count for bucket in bins)
    populated_bins = [bucket for bucket in bins if bucket.count > 0]
    reasons: list[str] = []

    if actionable_count < CALIBRATION_MIN_ACTIONABLE_COUNT:
        reasons.append("not_enough_actionable_predictions")

    if len(populated_bins) < CALIBRATION_MIN_POPULATED_BINS:
        reasons.append("not_enough_populated_calibration_bins")

    if populated_bins:
        mean_absolute_gap = round(
            sum(bucket.absolute_gap for bucket in populated_bins) / len(populated_bins),
            4,
        )
        max_absolute_gap = round(
            max(bucket.absolute_gap for bucket in populated_bins),
            4,
        )
    else:
        mean_absolute_gap = 1.0
        max_absolute_gap = 1.0

    if mean_absolute_gap > CALIBRATION_MAX_MEAN_ABS_GAP:
        reasons.append("mean_calibration_gap_above_threshold")

    if max_absolute_gap > CALIBRATION_MAX_BIN_ABS_GAP:
        reasons.append("bin_calibration_gap_above_threshold")

    status = "PASS" if not reasons else "FAIL"
    return CalibrationAssessment(
        status=status,
        actionable_count=actionable_count,
        populated_bins=len(populated_bins),
        mean_absolute_gap=mean_absolute_gap,
        max_absolute_gap=max_absolute_gap,
        reasons=tuple(reasons or ["calibration_gate_passed"]),
    )


def build_source_audit(
    predictions: tuple[PredictionResult, ...],
) -> tuple[SourceAuditRow, ...]:
    grouped: dict[tuple[str, str], list[SourceScore]] = {}
    for prediction in predictions:
        for score in prediction.source_scores:
            key = (score.name, score.kind)
            grouped.setdefault(key, []).append(score)

    rows: list[SourceAuditRow] = []
    for (name, kind), scores in sorted(grouped.items()):
        count = len(scores)
        rows.append(
            SourceAuditRow(
                name=name,
                kind=kind,
                samples=count,
                average_freshness=round(
                    sum(score.freshness for score in scores) / count,
                    4,
                ),
                average_trust=round(
                    sum(score.trust for score in scores) / count,
                    4,
                ),
                average_quality=round(
                    sum(score.quality for score in scores) / count,
                    4,
                ),
                average_age_minutes=round(
                    sum(score.age_minutes for score in scores) / count,
                    2,
                ),
                average_signal_delta=round(
                    sum(score.signal_delta for score in scores) / count,
                    4,
                ),
            )
        )
    return tuple(rows)
