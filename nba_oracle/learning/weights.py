from __future__ import annotations

from collections import defaultdict


def derive_candidate_weights(predictions: list[dict[str, object]]) -> list[dict[str, object]]:
    totals: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)

    for prediction in predictions:
        won = bool(prediction.get("won"))
        direction = 1.0 if won else -1.0
        for score in prediction.get("source_scores", []):
            kind = str(score.get("kind") or score.get("name") or "unknown")
            signal_delta = float(score.get("signal_delta", 0.0))
            quality = float(score.get("quality", 0.0))
            totals[kind] += direction * signal_delta * max(quality, 0.1)
            counts[kind] += 1

        market_prior = float(prediction.get("market_prior_probability", 0.0))
        model_probability = float(prediction.get("model_probability", 0.0))
        timing_adjustment = float(prediction.get("timing_adjustment", 0.0))
        source_adjustment = float(prediction.get("source_adjustment", 0.0))
        uncertainty = float(prediction.get("uncertainty", 0.0))

        totals["market_prior"] += direction * abs(model_probability - market_prior)
        counts["market_prior"] += 1
        totals["timing"] += direction * abs(timing_adjustment)
        counts["timing"] += 1
        totals["uncertainty"] += direction * max(0.0, 0.6 - uncertainty)
        counts["uncertainty"] += 1
        totals["source_adjustment"] += direction * abs(source_adjustment)
        counts["source_adjustment"] += 1

    if not totals:
        return []

    raw_weights = {kind: abs(value / max(counts[kind], 1)) for kind, value in totals.items()}
    total = sum(raw_weights.values()) or 1.0
    return [
        {
            "kind": kind,
            "weight": round(value / total, 4),
            "sample_size": counts[kind],
        }
        for kind, value in sorted(raw_weights.items(), key=lambda item: item[1], reverse=True)
    ]
