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

        labels: list[str] = []
        if decision == "BET":
            labels.append("bet_decision")
        if quality >= 0.85:
            labels.append("high_source_quality")
        if edge >= 0.03:
            labels.append("high_edge")
        if quality >= 0.85 and edge >= 0.02:
            labels.append("high_quality_plus_edge")

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
