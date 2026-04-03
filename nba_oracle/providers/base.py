from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

from nba_oracle.models import ProviderRecord, ProviderResponse, parse_dt


class ProviderError(RuntimeError):
    """Raised when a provider cannot return usable data."""


class BaseProvider(ABC):
    name: str
    kind: str

    @abstractmethod
    def fetch(self, bundle_path: Path, decision_time: datetime) -> ProviderResponse:
        raise NotImplementedError


class BundleProvider(BaseProvider):
    section_name: str

    def fetch(self, bundle_path: Path, decision_time: datetime) -> ProviderResponse:
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
