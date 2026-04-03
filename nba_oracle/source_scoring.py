from __future__ import annotations

from datetime import datetime

from nba_oracle.config import SOURCE_MAX_AGE_MINUTES
from nba_oracle.models import SourceScore, SourceSnapshot


def _max_age_minutes(kind: str) -> int:
    return SOURCE_MAX_AGE_MINUTES.get(kind, 120)


def score_source(source: SourceSnapshot, decision_time: datetime) -> SourceScore:
    age_minutes = max((decision_time - source.source_time).total_seconds() / 60, 0)
    max_age = _max_age_minutes(source.kind)
    freshness = max(0.0, 1.0 - (age_minutes / max_age))
    quality = round(freshness * source.trust, 4)
    return SourceScore(
        name=source.name,
        freshness=round(freshness, 4),
        trust=source.trust,
        quality=quality,
        age_minutes=round(age_minutes, 2),
        signal_delta=source.signal_delta,
    )


def aggregate_source_quality(scores: tuple[SourceScore, ...]) -> float:
    if not scores:
        return 0.0
    return round(sum(score.quality for score in scores) / len(scores), 4)


def aggregate_signal_delta(scores: tuple[SourceScore, ...]) -> float:
    if not scores:
        return 0.0
    weighted_sum = sum(score.signal_delta * score.quality for score in scores)
    normalizer = sum(score.quality for score in scores)
    if normalizer == 0:
        return 0.0
    return round(weighted_sum / normalizer, 4)

