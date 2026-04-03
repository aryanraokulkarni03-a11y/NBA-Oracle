from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from nba_oracle.config import RUNTIME_DIR
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


class LocalRepository:
    def __init__(self, root: Path = RUNTIME_DIR) -> None:
        self.root = root

    def prepare_run_dir(self, run_id: str) -> Path:
        run_dir = self.root / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def store_provider_responses(
        self, run_id: str, responses: tuple[ProviderResponse, ...]
    ) -> list[Path]:
        run_dir = self.prepare_run_dir(run_id)
        paths: list[Path] = []
        for response in responses:
            path = run_dir / f"provider_{response.kind}.json"
            path.write_text(
                json.dumps(_serialize(response), indent=2),
                encoding="utf-8",
            )
            paths.append(path)
        return paths

    def store_snapshots(
        self, run_id: str, snapshots: tuple[GameSnapshot, ...]
    ) -> Path:
        run_dir = self.prepare_run_dir(run_id)
        path = run_dir / "snapshots.json"
        path.write_text(
            json.dumps(_serialize({"snapshots": snapshots}), indent=2),
            encoding="utf-8",
        )
        return path

    def store_predictions(
        self, run_id: str, predictions: tuple[PredictionResult, ...]
    ) -> Path:
        run_dir = self.prepare_run_dir(run_id)
        path = run_dir / "predictions.json"
        path.write_text(
            json.dumps(_serialize({"predictions": predictions}), indent=2),
            encoding="utf-8",
        )
        return path
