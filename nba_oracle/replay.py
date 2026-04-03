from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from nba_oracle.market import realized_profit
from nba_oracle.models import PredictionResult
from nba_oracle.predictor import evaluate_game
from nba_oracle.snapshots import load_game_snapshots


@dataclass(frozen=True)
class CalibrationBin:
    label: str
    count: int
    average_probability: float
    hit_rate: float


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
    calibration_bins: tuple[CalibrationBin, ...]
    skip_reasons: dict[str, int]
    predictions: tuple[PredictionResult, ...]


def run_replay(fixture_path: Path) -> ReplayReport:
    games = load_game_snapshots(fixture_path)
    predictions = tuple(evaluate_game(game) for game in games)

    active_bets = [item for item in predictions if item.decision == "BET"]
    leans = [item for item in predictions if item.decision == "LEAN"]
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
    skip_reasons = Counter(
        reason for item in skips for reason in item.reasons
    )

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
        calibration_bins=build_calibration_bins(active_bets),
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
        else:
            average_probability = 0.0
            hit_rate = 0.0
        bins.append(
            CalibrationBin(
                label=f"{start}-{end}",
                count=len(matching),
                average_probability=average_probability,
                hit_rate=hit_rate,
            )
        )
    return tuple(bins)
