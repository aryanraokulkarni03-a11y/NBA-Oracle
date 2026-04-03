from __future__ import annotations


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
