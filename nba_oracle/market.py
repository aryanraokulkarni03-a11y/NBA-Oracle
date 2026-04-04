from __future__ import annotations


def clamp_probability(value: float) -> float:
    return max(0.05, min(value, 0.95))


def american_to_decimal(american: int) -> float:
    if american > 0:
        return 1 + (american / 100)
    return 1 + (100 / abs(american))


def american_to_probability(american: int) -> float:
    if american > 0:
        return 100 / (american + 100)
    return abs(american) / (abs(american) + 100)


def expected_value(probability: float, american: int) -> float:
    decimal_odds = american_to_decimal(american)
    return (probability * decimal_odds) - 1


def realized_profit(american: int, stake: float = 1.0) -> float:
    decimal_odds = american_to_decimal(american)
    return round((decimal_odds - 1) * stake, 4)


def blend_probabilities(*weighted_probabilities: tuple[float, float]) -> float:
    total_weight = 0.0
    total_value = 0.0
    for probability, weight in weighted_probabilities:
        if weight <= 0:
            continue
        total_weight += weight
        total_value += probability * weight
    if total_weight <= 0:
        return 0.5
    return clamp_probability(total_value / total_weight)


def classify_market_segment(probability: float) -> str:
    if probability >= 0.68:
        return "heavy_favorite"
    if probability >= 0.57:
        return "moderate_favorite"
    if probability >= 0.46:
        return "coin_flip"
    return "underdog"
