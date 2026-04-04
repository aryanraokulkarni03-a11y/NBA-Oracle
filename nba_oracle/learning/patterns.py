from __future__ import annotations

from collections import defaultdict

from nba_oracle.config import LEARNING_PATTERN_MIN_SAMPLE


def mine_patterns(predictions: list[dict[str, object]]) -> list[dict[str, object]]:
    buckets: dict[str, dict[str, int]] = defaultdict(lambda: {"wins": 0, "sample": 0})
    for prediction in predictions:
        won = bool(prediction.get("won"))
        edge = float(prediction.get("edge_vs_stake", 0.0))
        quality = float(prediction.get("source_quality", 0.0))
        decision = str(prediction.get("decision", ""))
        uncertainty = float(prediction.get("uncertainty", 0.0))
        market_segment = str(prediction.get("market_segment", "unknown"))

        labels: list[str] = []
        if decision == "BET":
            labels.append("bet_decision")
        if decision == "LEAN":
            labels.append("lean_decision")
        if quality >= 0.85:
            labels.append("high_source_quality")
        if edge >= 0.03:
            labels.append("high_edge")
        if quality >= 0.85 and edge >= 0.02:
            labels.append("high_quality_plus_edge")
        if uncertainty <= 0.2:
            labels.append("low_uncertainty")
        if uncertainty >= 0.35:
            labels.append("high_uncertainty")
        if market_segment in {"heavy_favorite", "moderate_favorite", "coin_flip", "underdog"}:
            labels.append(f"segment_{market_segment}")
        if decision == "BET" and uncertainty <= 0.22:
            labels.append("bet_low_uncertainty")

        for label in labels:
            buckets[label]["sample"] += 1
            if won:
                buckets[label]["wins"] += 1

    patterns: list[dict[str, object]] = []
    for label, bucket in buckets.items():
        sample = bucket["sample"]
        if sample < LEARNING_PATTERN_MIN_SAMPLE:
            continue
        win_rate = bucket["wins"] / sample if sample else 0.0
        patterns.append(
            {
                "pattern_name": label,
                "sample_size": sample,
                "win_rate": round(win_rate, 4),
                "conditions": {"label": label},
            }
        )
    return sorted(patterns, key=lambda item: (item["win_rate"], item["sample_size"]), reverse=True)[:10]
