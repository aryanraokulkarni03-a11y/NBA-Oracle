from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any

from nba_oracle.models import ProviderRecord, ProviderResponse, parse_dt


class ProviderError(RuntimeError):
    """Raised when a provider cannot return usable data."""


class BaseProvider(ABC):
    name: str
    kind: str

    def fetch(
        self,
        bundle_path: Path | None,
        decision_time: datetime,
        context: dict[str, ProviderResponse] | None = None,
    ) -> ProviderResponse:
        if bundle_path is not None:
            return self.fetch_bundle(bundle_path, decision_time, context or {})
        return self.fetch_live(decision_time, context or {})

    def fetch_bundle(
        self,
        bundle_path: Path,
        decision_time: datetime,
        context: dict[str, ProviderResponse],
    ) -> ProviderResponse:
        return self.degraded_response(
            decision_time,
            error="bundle_mode_not_supported",
            raw_payload={},
        )

    @abstractmethod
    def fetch_live(
        self,
        decision_time: datetime,
        context: dict[str, ProviderResponse],
    ) -> ProviderResponse:
        raise NotImplementedError

    def build_response(
        self,
        *,
        source_time: datetime,
        source_version: str,
        trust: float,
        success: bool,
        degraded: bool,
        records: tuple[ProviderRecord, ...],
        raw_payload: dict[str, Any],
        error: str | None = None,
    ) -> ProviderResponse:
        return ProviderResponse(
            name=self.name,
            kind=self.kind,
            source_time=source_time,
            source_version=source_version,
            trust=trust,
            success=success,
            degraded=degraded,
            records=records,
            raw_payload=raw_payload,
            error=error,
        )

    def degraded_response(
        self,
        decision_time: datetime,
        *,
        error: str,
        raw_payload: dict[str, Any],
        trust: float = 0.0,
        source_version: str = "live-v1",
    ) -> ProviderResponse:
        return self.build_response(
            source_time=decision_time,
            source_version=source_version,
            trust=trust,
            success=False,
            degraded=True,
            records=tuple(),
            raw_payload=raw_payload,
            error=error,
        )


class BundleProvider(BaseProvider):
    section_name: str

    def fetch_bundle(
        self,
        bundle_path: Path,
        decision_time: datetime,
        context: dict[str, ProviderResponse],
    ) -> ProviderResponse:
        import json

        payload = json.loads(bundle_path.read_text(encoding="utf-8"))
        section = payload.get(self.section_name)
        if not section:
            return ProviderResponse(
                name=self.name,
                kind=self.kind,
                source_time=decision_time,
                source_version="missing",
                trust=0.0,
                success=False,
                degraded=True,
                records=tuple(),
                raw_payload={},
                error=f"missing_section:{self.section_name}",
            )

        records = tuple(
            ProviderRecord(game_id=item["game_id"], data=dict(item))
            for item in section.get("records", [])
        )
        return ProviderResponse(
            name=section.get("provider", self.name),
            kind=self.kind,
            source_time=parse_dt(section["source_time"]),
            source_version=section["source_version"],
            trust=float(section["trust"]),
            success=bool(section.get("success", True)),
            degraded=bool(section.get("degraded", False)),
            records=records,
            raw_payload=section,
            error=section.get("error"),
        )

    def fetch_live(
        self,
        decision_time: datetime,
        context: dict[str, ProviderResponse],
    ) -> ProviderResponse:
        return self.degraded_response(
            decision_time,
            error="live_mode_not_supported",
            raw_payload={},
        )
