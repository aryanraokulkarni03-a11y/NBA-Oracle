from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


def parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@dataclass(frozen=True)
class SourceSnapshot:
    name: str
    kind: str
    source_time: datetime
    source_version: str
    trust: float
    signal_delta: float
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SourceSnapshot":
        return cls(
            name=payload["name"],
            kind=payload["kind"],
            source_time=parse_dt(payload["source_time"]),
            source_version=payload["source_version"],
            trust=float(payload["trust"]),
            signal_delta=float(payload["signal_delta"]),
            metadata=dict(payload.get("metadata", {})),
        )


@dataclass(frozen=True)
class MarketSnapshot:
    selected_team: str
    stake_american: int
    best_american: int
    close_american: int
    consensus_probability: float

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "MarketSnapshot":
        return cls(
            selected_team=payload["selected_team"],
            stake_american=int(payload["stake_american"]),
            best_american=int(payload["best_american"]),
            close_american=int(payload["close_american"]),
            consensus_probability=float(payload["consensus_probability"]),
        )


@dataclass(frozen=True)
class GameSnapshot:
    game_id: str
    decision_time: datetime
    tipoff_time: datetime
    away_team: str
    home_team: str
    market: MarketSnapshot
    sources: tuple[SourceSnapshot, ...]
    actual_winner: str | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "GameSnapshot":
        sources = tuple(SourceSnapshot.from_dict(item) for item in payload["sources"])
        return cls(
            game_id=payload["game_id"],
            decision_time=parse_dt(payload["decision_time"]),
            tipoff_time=parse_dt(payload["tipoff_time"]),
            away_team=payload["away_team"],
            home_team=payload["home_team"],
            market=MarketSnapshot.from_dict(payload["market"]),
            sources=sources,
            actual_winner=payload.get("actual_winner"),
        )


@dataclass(frozen=True)
class SourceScore:
    name: str
    kind: str
    freshness: float
    trust: float
    quality: float
    age_minutes: float
    signal_delta: float


@dataclass(frozen=True)
class PredictionResult:
    game_id: str
    selected_team: str
    decision: str
    stake_american: int
    best_american: int
    close_american: int
    model_probability: float
    stake_probability: float
    best_probability: float
    close_probability: float
    expected_value: float
    edge_vs_stake: float
    source_quality: float
    source_scores: tuple[SourceScore, ...]
    reasons: tuple[str, ...]
    actual_winner: str

    @property
    def is_active(self) -> bool:
        return self.decision == "BET"

    @property
    def won(self) -> bool:
        return self.actual_winner is not None and self.selected_team == self.actual_winner


@dataclass(frozen=True)
class ProviderRecord:
    game_id: str
    data: dict[str, Any]


@dataclass(frozen=True)
class ProviderResponse:
    name: str
    kind: str
    source_time: datetime
    source_version: str
    trust: float
    success: bool
    degraded: bool
    records: tuple[ProviderRecord, ...]
    raw_payload: dict[str, Any]
    error: str | None = None

    @property
    def record_map(self) -> dict[str, dict[str, Any]]:
        return {record.game_id: record.data for record in self.records}


@dataclass(frozen=True)
class LiveRunResult:
    run_id: str
    decision_time: datetime
    storage_mode: str
    providers: tuple[ProviderResponse, ...]
    snapshots: tuple[GameSnapshot, ...]
    predictions: tuple[PredictionResult, ...]
    stored_paths: tuple[str, ...]
