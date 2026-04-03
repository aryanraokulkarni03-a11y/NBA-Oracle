from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol

from nba_oracle.config import (
    DEFAULT_STORAGE_MODE,
    RUNTIME_DIR,
    STORAGE_MODE,
    SUPABASE_PREDICTIONS_TABLE,
    SUPABASE_PROVIDER_TABLE,
    SUPABASE_RUNS_TABLE,
    SUPABASE_SERVICE_ROLE_KEY,
    SUPABASE_SNAPSHOTS_TABLE,
    SUPABASE_URL,
)
from nba_oracle.http import HttpRequestError, request_json
from nba_oracle.models import GameSnapshot, PredictionResult, ProviderResponse


def _serialize(value: Any) -> Any:
    if is_dataclass(value):
        return _serialize(asdict(value))
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize(item) for item in value]
    return value


class StorageRepository(Protocol):
    storage_mode: str

    def store_provider_responses(
        self,
        run_id: str,
        responses: tuple[ProviderResponse, ...],
        *,
        decision_time: datetime | None = None,
        snapshot_count: int | None = None,
        prediction_count: int | None = None,
    ) -> list[str]:
        ...

    def store_snapshots(self, run_id: str, snapshots: tuple[GameSnapshot, ...]) -> str:
        ...

    def store_predictions(self, run_id: str, predictions: tuple[PredictionResult, ...]) -> str:
        ...


class LocalRepository:
    storage_mode = "local"

    def __init__(self, root: Path = RUNTIME_DIR) -> None:
        self.root = root

    def prepare_run_dir(self, run_id: str) -> Path:
        run_dir = self.root / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def store_provider_responses(
        self,
        run_id: str,
        responses: tuple[ProviderResponse, ...],
        *,
        decision_time: datetime | None = None,
        snapshot_count: int | None = None,
        prediction_count: int | None = None,
    ) -> list[str]:
        run_dir = self.prepare_run_dir(run_id)
        paths: list[str] = []
        for response in responses:
            path = run_dir / f"provider_{response.kind}.json"
            path.write_text(
                json.dumps(_serialize(response), indent=2),
                encoding="utf-8",
            )
            paths.append(str(path))
        return paths

    def store_snapshots(
        self, run_id: str, snapshots: tuple[GameSnapshot, ...]
    ) -> str:
        run_dir = self.prepare_run_dir(run_id)
        path = run_dir / "snapshots.json"
        path.write_text(
            json.dumps(_serialize({"snapshots": snapshots}), indent=2),
            encoding="utf-8",
        )
        return str(path)

    def store_predictions(
        self, run_id: str, predictions: tuple[PredictionResult, ...]
    ) -> str:
        run_dir = self.prepare_run_dir(run_id)
        path = run_dir / "predictions.json"
        path.write_text(
            json.dumps(_serialize({"predictions": predictions}), indent=2),
            encoding="utf-8",
        )
        return str(path)


class SupabaseRepository:
    storage_mode = "supabase"

    def __init__(
        self,
        *,
        url: str = SUPABASE_URL or "",
        service_role_key: str = SUPABASE_SERVICE_ROLE_KEY or "",
    ) -> None:
        self.url = url.rstrip("/")
        self.service_role_key = service_role_key
        self.enabled = bool(self.url and self.service_role_key)

    def store_provider_responses(
        self,
        run_id: str,
        responses: tuple[ProviderResponse, ...],
        *,
        decision_time: datetime | None = None,
        snapshot_count: int | None = None,
        prediction_count: int | None = None,
    ) -> list[str]:
        if not self.enabled:
            return []

        if decision_time is not None:
            self._insert_rows(
                SUPABASE_RUNS_TABLE,
                [
                    {
                        "run_id": run_id,
                        "decision_time": decision_time.isoformat(),
                        "provider_count": len(responses),
                        "snapshot_count": snapshot_count or 0,
                        "prediction_count": prediction_count or 0,
                    }
                ],
            )

        rows = [
            {
                "run_id": run_id,
                "kind": response.kind,
                "provider_name": response.name,
                "source_time": response.source_time.isoformat(),
                "source_version": response.source_version,
                "trust": response.trust,
                "success": response.success,
                "degraded": response.degraded,
                "error": response.error,
                "record_count": len(response.records),
                "raw_payload": _serialize(response.raw_payload),
            }
            for response in responses
        ]
        if rows:
            self._insert_rows(SUPABASE_PROVIDER_TABLE, rows)
        return [f"supabase:{SUPABASE_PROVIDER_TABLE}:{run_id}"]

    def store_snapshots(
        self, run_id: str, snapshots: tuple[GameSnapshot, ...]
    ) -> str:
        if not self.enabled:
            return ""

        rows = [
            {
                "run_id": run_id,
                "game_id": snapshot.game_id,
                "decision_time": snapshot.decision_time.isoformat(),
                "tipoff_time": snapshot.tipoff_time.isoformat(),
                "away_team": snapshot.away_team,
                "home_team": snapshot.home_team,
                "market_payload": _serialize(snapshot.market),
                "sources_payload": _serialize(snapshot.sources),
            }
            for snapshot in snapshots
        ]
        if rows:
            self._insert_rows(SUPABASE_SNAPSHOTS_TABLE, rows)
        return f"supabase:{SUPABASE_SNAPSHOTS_TABLE}:{run_id}"

    def store_predictions(
        self, run_id: str, predictions: tuple[PredictionResult, ...]
    ) -> str:
        if not self.enabled:
            return ""

        rows = [
            {
                "run_id": run_id,
                "game_id": prediction.game_id,
                "selected_team": prediction.selected_team,
                "decision": prediction.decision,
                "reference_bookmaker": prediction.reference_bookmaker,
                "reference_american": prediction.stake_american,
                "best_american": prediction.best_american,
                "close_american": prediction.close_american,
                "opening_american": prediction.opening_american,
                "market_timestamp": prediction.market_timestamp.isoformat()
                if prediction.market_timestamp
                else None,
                "model_probability": prediction.model_probability,
                "reference_probability": prediction.stake_probability,
                "best_probability": prediction.best_probability,
                "close_probability": prediction.close_probability,
                "expected_value": prediction.expected_value,
                "edge_vs_reference": prediction.edge_vs_stake,
                "source_quality": prediction.source_quality,
                "reasons": list(prediction.reasons),
                "source_scores": _serialize(prediction.source_scores),
            }
            for prediction in predictions
        ]
        if rows:
            self._insert_rows(SUPABASE_PREDICTIONS_TABLE, rows)
        return f"supabase:{SUPABASE_PREDICTIONS_TABLE}:{run_id}"

    def _insert_rows(self, table: str, rows: list[dict[str, Any]]) -> None:
        headers = {
            "apikey": self.service_role_key,
            "Authorization": f"Bearer {self.service_role_key}",
            "Prefer": "return=minimal",
        }
        try:
            request_json(
                f"{self.url}/rest/v1/{table}",
                method="POST",
                headers=headers,
                json_body=rows,
                timeout=20,
            )
        except HttpRequestError as exc:
            raise RuntimeError(f"supabase_insert_failed:{table}:{exc}") from exc


class DualRepository:
    storage_mode = "dual"

    def __init__(
        self,
        local_repository: LocalRepository | None = None,
        supabase_repository: SupabaseRepository | None = None,
    ) -> None:
        self.local_repository = local_repository or LocalRepository()
        self.supabase_repository = supabase_repository or SupabaseRepository()

    def store_provider_responses(
        self,
        run_id: str,
        responses: tuple[ProviderResponse, ...],
        *,
        decision_time: datetime | None = None,
        snapshot_count: int | None = None,
        prediction_count: int | None = None,
    ) -> list[str]:
        stored = self.local_repository.store_provider_responses(
            run_id,
            responses,
            decision_time=decision_time,
            snapshot_count=snapshot_count,
            prediction_count=prediction_count,
        )
        try:
            remote_paths = self.supabase_repository.store_provider_responses(
                run_id,
                responses,
                decision_time=decision_time,
                snapshot_count=snapshot_count,
                prediction_count=prediction_count,
            )
            stored.extend(path for path in remote_paths if path)
        except RuntimeError as exc:
            stored.append(f"supabase_error:{exc}")
        return stored

    def store_snapshots(self, run_id: str, snapshots: tuple[GameSnapshot, ...]) -> str:
        local_path = self.local_repository.store_snapshots(run_id, snapshots)
        try:
            remote_path = self.supabase_repository.store_snapshots(run_id, snapshots)
        except RuntimeError as exc:
            remote_path = f"supabase_error:{exc}"
        return local_path if not remote_path else f"{local_path} | {remote_path}"

    def store_predictions(self, run_id: str, predictions: tuple[PredictionResult, ...]) -> str:
        local_path = self.local_repository.store_predictions(run_id, predictions)
        try:
            remote_path = self.supabase_repository.store_predictions(run_id, predictions)
        except RuntimeError as exc:
            remote_path = f"supabase_error:{exc}"
        return local_path if not remote_path else f"{local_path} | {remote_path}"


def build_repository(storage_mode: str | None = None) -> StorageRepository:
    requested_mode = (storage_mode or STORAGE_MODE or DEFAULT_STORAGE_MODE).lower()
    if requested_mode == "supabase":
        return SupabaseRepository()
    if requested_mode == "dual":
        return DualRepository()
    return LocalRepository()
