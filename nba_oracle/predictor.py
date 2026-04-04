from __future__ import annotations

from nba_oracle.config import (
    MAX_PRICE_GAP,
    MIN_EDGE_FOR_BET,
    MIN_EDGE_FOR_LEAN,
    MIN_EV_FOR_BET,
    MIN_SOURCE_QUALITY,
)
from nba_oracle.market import (
    american_to_probability,
    blend_probabilities,
    classify_market_segment,
    clamp_probability,
    expected_value,
)
from nba_oracle.models import GameSnapshot, PredictionResult, SourceScore, SourceSnapshot
from nba_oracle.source_scoring import (
    aggregate_source_quality,
    calculate_signal_disagreement,
    score_source,
)

SOURCE_KIND_WEIGHTS = {
    "injury": 1.15,
    "stats": 0.95,
    "sentiment": 0.35,
    "odds": 0.2,
}


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _source_kind_weight(kind: str) -> float:
    return SOURCE_KIND_WEIGHTS.get(kind, 0.5)


def _metadata_float(metadata: dict[str, object], key: str) -> float:
    raw_value = metadata.get(key, 0.0)
    try:
        return float(raw_value)
    except (TypeError, ValueError):
        return 0.0


def _source_context_multiplier(source: SourceSnapshot) -> float:
    metadata = source.metadata or {}
    if source.kind == "injury":
        impact_gap = abs(_metadata_float(metadata, "impact_gap"))
        top_weight = max(
            _metadata_float(metadata, "selected_team_top_weight"),
            _metadata_float(metadata, "opponent_team_top_weight"),
        )
        return 1.0 + min((impact_gap * 0.08) + (top_weight * 0.12), 0.35)
    if source.kind == "stats":
        strength_score = abs(_metadata_float(metadata, "team_strength_score"))
        defense_edge = abs(_metadata_float(metadata, "defense_edge"))
        return 1.0 + min((strength_score / 25.0) + (defense_edge / 30.0), 0.25)
    if source.kind == "odds":
        line_move = str(metadata.get("line_move", "")).lower()
        if line_move and line_move != "unavailable_live_snapshot":
            return 1.05
    return 1.0


def _market_prior_probability(stake_probability: float, best_probability: float, consensus_probability: float) -> float:
    return blend_probabilities(
        (consensus_probability, 0.58),
        (stake_probability, 0.27),
        (best_probability, 0.15),
    )


def _source_adjustment(scores: tuple[SourceScore, ...], sources: tuple[SourceSnapshot, ...]) -> float:
    if not scores:
        return 0.0
    weighted_sum = 0.0
    total_weight = 0.0
    for score, source in zip(scores, sources):
        weight = max(score.quality, 0.08) * _source_kind_weight(score.kind) * _source_context_multiplier(source)
        weighted_sum += score.signal_delta * weight
        total_weight += weight
    if total_weight <= 0:
        return 0.0
    return weighted_sum / total_weight


def _timing_adjustment(game: GameSnapshot, stake_probability: float, best_probability: float) -> tuple[float, float]:
    minutes_to_tipoff = max((game.tipoff_time - game.decision_time).total_seconds() / 60, 0.0)
    market_age_minutes = 15.0
    if game.market.market_timestamp is not None:
        market_age_minutes = max(
            (game.decision_time - game.market.market_timestamp).total_seconds() / 60,
            0.0,
        )

    price_gap = abs(stake_probability - best_probability)
    adjustment = 0.0

    if 75 <= minutes_to_tipoff <= 180:
        adjustment += 0.0035
    elif minutes_to_tipoff > 480:
        adjustment -= 0.003
    elif minutes_to_tipoff < 45:
        adjustment -= 0.0045

    if market_age_minutes > 45:
        adjustment -= 0.008
    elif market_age_minutes > 25:
        adjustment -= 0.004
    elif market_age_minutes <= 10:
        adjustment += 0.002

    if game.market.opening_american is not None:
        opening_probability = american_to_probability(game.market.opening_american)
        line_value_shift = opening_probability - stake_probability
        adjustment += clamp(line_value_shift * 0.18, -0.007, 0.007)
    elif price_gap > MAX_PRICE_GAP * 0.6:
        adjustment -= 0.0025

    return adjustment, market_age_minutes


def _uncertainty(
    *,
    source_quality: float,
    signal_disagreement: float,
    market_age_minutes: float,
    price_gap: float,
    minutes_to_tipoff: float,
    market_segment: str,
    has_opening_line: bool,
) -> float:
    uncertainty = 0.08
    uncertainty += (1 - source_quality) * 0.28
    uncertainty += signal_disagreement * 0.18
    uncertainty += min(price_gap / max(MAX_PRICE_GAP, 0.0001), 1.3) * 0.09

    if market_age_minutes > 45:
        uncertainty += 0.12
    elif market_age_minutes > 25:
        uncertainty += 0.06

    if minutes_to_tipoff > 480:
        uncertainty += 0.08
    elif minutes_to_tipoff > 240:
        uncertainty += 0.04
    elif minutes_to_tipoff < 45:
        uncertainty += 0.05

    if market_segment == "coin_flip":
        uncertainty += 0.05
    elif market_segment == "heavy_favorite":
        uncertainty += 0.03

    if not has_opening_line:
        uncertainty += 0.02

    return round(clamp(uncertainty, 0.05, 0.55), 4)


def evaluate_game(game: GameSnapshot) -> PredictionResult:
    scores = tuple(score_source(source, game.decision_time) for source in game.sources)
    source_quality = aggregate_source_quality(scores)
    signal_disagreement = calculate_signal_disagreement(scores)

    stake_probability = american_to_probability(game.market.stake_american)
    best_probability = american_to_probability(game.market.best_american)
    close_probability = american_to_probability(game.market.close_american)

    market_prior_probability = _market_prior_probability(
        stake_probability,
        best_probability,
        game.market.consensus_probability,
    )
    market_segment = classify_market_segment(market_prior_probability)
    raw_source_adjustment = _source_adjustment(scores, game.sources)
    timing_adjustment, market_age_minutes = _timing_adjustment(
        game,
        stake_probability,
        best_probability,
    )
    minutes_to_tipoff = max((game.tipoff_time - game.decision_time).total_seconds() / 60, 0.0)
    price_gap = abs(stake_probability - best_probability)
    uncertainty = _uncertainty(
        source_quality=source_quality,
        signal_disagreement=signal_disagreement,
        market_age_minutes=market_age_minutes,
        price_gap=price_gap,
        minutes_to_tipoff=minutes_to_tipoff,
        market_segment=market_segment,
        has_opening_line=game.market.opening_american is not None,
    )

    source_adjustment = raw_source_adjustment * (1.12 - (uncertainty * 0.22))
    timing_adjustment *= 1 - (uncertainty * 0.35)
    underdog_bonus = 0.0
    if market_prior_probability < 0.5 and source_adjustment > 0:
        underdog_bonus += min(source_adjustment * 0.5, 0.009) * (1 - (uncertainty * 0.45))
    if market_segment == "coin_flip" and source_adjustment > 0.01:
        underdog_bonus += 0.005 * (1 - uncertainty)
    favorite_discipline_penalty = 0.0
    if market_segment == "moderate_favorite":
        favorite_discipline_penalty += max(0.0, 0.02 - raw_source_adjustment) * 0.4
        favorite_discipline_penalty += uncertainty * 0.004
    model_probability = clamp_probability(
        market_prior_probability + source_adjustment + timing_adjustment + underdog_bonus - favorite_discipline_penalty
    )

    edge_vs_stake = round(model_probability - stake_probability, 4)
    ev = round(expected_value(model_probability, game.market.stake_american), 4)

    reasons: list[str] = []
    decision = "BET"

    min_source_quality = max(MIN_SOURCE_QUALITY - 0.07, 0.47)
    lean_edge_threshold = max(MIN_EDGE_FOR_LEAN - 0.006 + (uncertainty * 0.005), 0.009)
    bet_edge_threshold = max(MIN_EDGE_FOR_BET - 0.012 + (uncertainty * 0.008), 0.018)
    bet_ev_threshold = max(MIN_EV_FOR_BET - 0.005 + (uncertainty * 0.008), 0.014)
    max_price_gap = MAX_PRICE_GAP + 0.002

    if market_segment == "heavy_favorite":
        lean_edge_threshold += 0.004
        bet_edge_threshold += 0.006
        bet_ev_threshold += 0.005
    elif market_segment == "underdog":
        bet_edge_threshold = max(bet_edge_threshold - 0.003, 0.016)
        bet_ev_threshold = max(bet_ev_threshold - 0.003, 0.012)
    elif market_segment == "coin_flip":
        lean_edge_threshold = max(lean_edge_threshold - 0.0015, 0.008)
        bet_edge_threshold = max(bet_edge_threshold - 0.002, 0.017)

    if source_quality < min_source_quality:
        decision = "SKIP"
        reasons.append("source_quality_below_threshold")

    if edge_vs_stake < lean_edge_threshold:
        decision = "SKIP"
        reasons.append("edge_too_small")

    if price_gap > max_price_gap:
        decision = "SKIP"
        reasons.append("stake_price_not_competitive")

    if ev <= 0:
        decision = "SKIP"
        reasons.append("negative_expected_value")

    if uncertainty >= 0.4 and decision != "SKIP":
        decision = "LEAN"
        reasons.append("high_uncertainty_context")

    if market_age_minutes > 35 and decision == "BET":
        decision = "LEAN"
        reasons.append("stale_market_context")

    if market_segment == "heavy_favorite" and ev < bet_ev_threshold and "negative_expected_value" not in reasons:
        reasons.append("heavy_favorite_price_risk")

    if decision != "SKIP" and (
        edge_vs_stake < bet_edge_threshold or ev < bet_ev_threshold
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
        best_american=game.market.best_american,
        close_american=game.market.close_american,
        model_probability=round(model_probability, 4),
        stake_probability=round(stake_probability, 4),
        best_probability=round(best_probability, 4),
        close_probability=round(close_probability, 4),
        expected_value=ev,
        edge_vs_stake=edge_vs_stake,
        source_quality=source_quality,
        source_scores=scores,
        reasons=tuple(dict.fromkeys(reasons)),
        actual_winner=game.actual_winner,
        reference_bookmaker=game.market.reference_bookmaker,
        market_timestamp=game.market.market_timestamp,
        opening_american=game.market.opening_american,
        market_prior_probability=round(market_prior_probability, 4),
        source_adjustment=round(source_adjustment, 4),
        timing_adjustment=round(timing_adjustment, 4),
        uncertainty=uncertainty,
        market_segment=market_segment,
    )
