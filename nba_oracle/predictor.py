from __future__ import annotations

from nba_oracle.config import (
    MAX_PRICE_GAP,
    MIN_EDGE_FOR_BET,
    MIN_EDGE_FOR_LEAN,
    MIN_EV_FOR_BET,
    MIN_SOURCE_QUALITY,
)
from nba_oracle.market import american_to_probability, expected_value
from nba_oracle.models import GameSnapshot, PredictionResult
from nba_oracle.source_scoring import (
    aggregate_signal_delta,
    aggregate_source_quality,
    score_source,
)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def evaluate_game(game: GameSnapshot) -> PredictionResult:
    scores = tuple(score_source(source, game.decision_time) for source in game.sources)
    source_quality = aggregate_source_quality(scores)
    signal_delta = aggregate_signal_delta(scores)

    stake_probability = american_to_probability(game.market.stake_american)
    best_probability = american_to_probability(game.market.best_american)
    close_probability = american_to_probability(game.market.close_american)

    base_probability = game.market.consensus_probability
    model_probability = clamp(
        base_probability + (signal_delta * (1 + source_quality)),
        0.05,
        0.95,
    )
    edge_vs_stake = round(model_probability - stake_probability, 4)
    ev = round(expected_value(model_probability, game.market.stake_american), 4)
    price_gap = abs(stake_probability - best_probability)

    reasons: list[str] = []
    decision = "BET"

    if source_quality < MIN_SOURCE_QUALITY:
        decision = "SKIP"
        reasons.append("source_quality_below_threshold")

    if edge_vs_stake < MIN_EDGE_FOR_LEAN:
        decision = "SKIP"
        reasons.append("edge_too_small")

    if price_gap > MAX_PRICE_GAP:
        decision = "SKIP"
        reasons.append("stake_price_not_competitive")

    if ev <= 0:
        decision = "SKIP"
        reasons.append("negative_expected_value")

    if decision != "SKIP" and (
        edge_vs_stake < MIN_EDGE_FOR_BET or ev < MIN_EV_FOR_BET
    ):
        decision = "LEAN"
        reasons.append("edge_is_real_but_not_strong")

    if not reasons:
        reasons.append("all_gates_passed")

    return PredictionResult(
        game_id=game.game_id,
        selected_team=game.market.selected_team,
        decision=decision,
        stake_american=game.market.stake_american,
        model_probability=round(model_probability, 4),
        stake_probability=round(stake_probability, 4),
        best_probability=round(best_probability, 4),
        close_probability=round(close_probability, 4),
        expected_value=ev,
        edge_vs_stake=edge_vs_stake,
        source_quality=source_quality,
        source_scores=scores,
        reasons=tuple(reasons),
        actual_winner=game.actual_winner,
    )
