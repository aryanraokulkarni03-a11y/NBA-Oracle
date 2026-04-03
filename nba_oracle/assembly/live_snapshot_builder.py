from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from nba_oracle.models import GameSnapshot, MarketSnapshot, ProviderResponse, SourceSnapshot, parse_dt


def load_bundle_metadata(bundle_path: Path) -> dict[str, object]:
    payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    return dict(payload.get("meta", {}))


def build_live_snapshots(
    decision_time: datetime,
    providers: tuple[ProviderResponse, ...],
) -> tuple[GameSnapshot, ...]:
    schedule_provider = next(
        provider for provider in providers if provider.kind == "schedule"
    )
    provider_map = {provider.kind: provider for provider in providers}

    snapshots: list[GameSnapshot] = []
    for game_id, schedule_row in schedule_provider.record_map.items():
        odds_row = provider_map["odds"].record_map.get(game_id)
        injury_row = provider_map["injury"].record_map.get(game_id)
        stats_row = provider_map["stats"].record_map.get(game_id)
        sentiment_row = provider_map.get("sentiment").record_map.get(game_id) if provider_map.get("sentiment") else None

        if odds_row is None:
            continue

        market = MarketSnapshot(
            selected_team=odds_row["selected_team"],
            stake_american=int(odds_row["stake_american"]),
            best_american=int(odds_row["best_american"]),
            close_american=int(odds_row.get("close_american", odds_row["best_american"])),
            consensus_probability=float(odds_row["consensus_probability"]),
        )
        sources = [
            _build_source(provider_map["odds"], odds_row),
            _build_source_or_placeholder(provider_map["injury"], injury_row),
            _build_source_or_placeholder(provider_map["stats"], stats_row),
        ]
        if sentiment_row and provider_map.get("sentiment") and provider_map["sentiment"].success:
            sources.append(_build_source(provider_map["sentiment"], sentiment_row))

        snapshots.append(
            GameSnapshot(
                game_id=game_id,
                decision_time=decision_time,
                tipoff_time=parse_dt(schedule_row["tipoff_time"]),
                away_team=schedule_row["away_team"],
                home_team=schedule_row["home_team"],
                market=market,
                sources=tuple(sources),
                actual_winner=schedule_row.get("actual_winner"),
            )
        )
    return tuple(snapshots)


def _build_source(provider: ProviderResponse, row: dict[str, object]) -> SourceSnapshot:
    return SourceSnapshot(
        name=provider.name,
        kind=provider.kind,
        source_time=provider.source_time,
        source_version=provider.source_version,
        trust=provider.trust,
        signal_delta=float(row.get("signal_delta", 0.0)),
        metadata={k: v for k, v in row.items() if k not in {"game_id", "signal_delta"}},
    )


def _build_source_or_placeholder(
    provider: ProviderResponse,
    row: dict[str, object] | None,
) -> SourceSnapshot:
    if row is not None:
        return _build_source(provider, row)

    return SourceSnapshot(
        name=provider.name,
        kind=provider.kind,
        source_time=provider.source_time,
        source_version=provider.source_version,
        trust=min(provider.trust, 0.35),
        signal_delta=0.0,
        metadata={
            "placeholder": True,
            "reason": "provider_record_missing",
            "provider_error": provider.error,
        },
    )
