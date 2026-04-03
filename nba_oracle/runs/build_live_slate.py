from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from nba_oracle.assembly.live_snapshot_builder import build_live_snapshots, load_bundle_metadata
from nba_oracle.config import DEFAULT_STORAGE_MODE
from nba_oracle.models import LiveRunResult
from nba_oracle.predictor import evaluate_game
from nba_oracle.providers.injuries import InjuryProvider
from nba_oracle.providers.odds import OddsProvider
from nba_oracle.providers.schedule import ScheduleProvider
from nba_oracle.providers.sentiment import SentimentProvider
from nba_oracle.providers.stats import StatsProvider
from nba_oracle.storage.repository import LocalRepository


def build_live_slate(bundle_path: Path) -> LiveRunResult:
    meta = load_bundle_metadata(bundle_path)
    decision_time = datetime.fromisoformat(str(meta["decision_time"]))
    run_id = str(meta["run_id"])

    providers = (
        ScheduleProvider().fetch(bundle_path, decision_time),
        OddsProvider().fetch(bundle_path, decision_time),
        InjuryProvider().fetch(bundle_path, decision_time),
        StatsProvider().fetch(bundle_path, decision_time),
        SentimentProvider().fetch(bundle_path, decision_time),
    )
    snapshots = build_live_snapshots(bundle_path, providers)
    predictions = tuple(evaluate_game(snapshot) for snapshot in snapshots)

    repository = LocalRepository()
    stored_paths = []
    stored_paths.extend(str(path) for path in repository.store_provider_responses(run_id, providers))
    stored_paths.append(str(repository.store_snapshots(run_id, snapshots)))
    stored_paths.append(str(repository.store_predictions(run_id, predictions)))

    return LiveRunResult(
        run_id=run_id,
        decision_time=decision_time,
        storage_mode=DEFAULT_STORAGE_MODE,
        providers=providers,
        snapshots=snapshots,
        predictions=predictions,
        stored_paths=tuple(stored_paths),
    )
