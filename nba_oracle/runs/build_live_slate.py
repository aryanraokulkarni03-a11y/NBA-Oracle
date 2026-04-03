from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from nba_oracle.assembly.live_snapshot_builder import build_live_snapshots, load_bundle_metadata
from nba_oracle.config import STORAGE_MODE
from nba_oracle.models import LiveRunResult
from nba_oracle.predictor import evaluate_game
from nba_oracle.providers.injuries import InjuryProvider
from nba_oracle.providers.odds import OddsProvider
from nba_oracle.providers.schedule import ScheduleProvider
from nba_oracle.providers.sentiment import SentimentProvider
from nba_oracle.providers.stats import StatsProvider
from nba_oracle.storage.repository import build_repository


def build_live_slate(
    bundle_path: Path | None = None,
    *,
    use_live: bool = False,
    decision_time: datetime | None = None,
) -> LiveRunResult:
    if use_live:
        resolved_decision_time = decision_time or datetime.now(timezone.utc)
        run_id = resolved_decision_time.strftime("live-%Y%m%dT%H%M%SZ")
        active_bundle_path = None
    else:
        if bundle_path is None:
            raise ValueError("bundle_path is required when use_live is False")
        meta = load_bundle_metadata(bundle_path)
        resolved_decision_time = datetime.fromisoformat(str(meta["decision_time"]))
        run_id = str(meta["run_id"])
        active_bundle_path = bundle_path

    provider_context = {}
    schedule = ScheduleProvider().fetch(active_bundle_path, resolved_decision_time, provider_context)
    provider_context["schedule"] = schedule
    odds = OddsProvider().fetch(active_bundle_path, resolved_decision_time, provider_context)
    provider_context["odds"] = odds
    injuries = InjuryProvider().fetch(active_bundle_path, resolved_decision_time, provider_context)
    provider_context["injury"] = injuries
    stats = StatsProvider().fetch(active_bundle_path, resolved_decision_time, provider_context)
    provider_context["stats"] = stats
    sentiment = SentimentProvider().fetch(active_bundle_path, resolved_decision_time, provider_context)
    provider_context["sentiment"] = sentiment

    providers = (schedule, odds, injuries, stats, sentiment)
    snapshots = build_live_snapshots(resolved_decision_time, providers)
    predictions = tuple(evaluate_game(snapshot) for snapshot in snapshots)

    repository = build_repository()
    stored_paths = []
    stored_paths.extend(
        repository.store_provider_responses(
            run_id,
            providers,
            decision_time=resolved_decision_time,
            snapshot_count=len(snapshots),
            prediction_count=len(predictions),
        )
    )
    stored_paths.append(repository.store_snapshots(run_id, snapshots))
    stored_paths.append(repository.store_predictions(run_id, predictions))

    return LiveRunResult(
        run_id=run_id,
        decision_time=resolved_decision_time,
        storage_mode=repository.storage_mode,
        providers=providers,
        snapshots=snapshots,
        predictions=predictions,
        stored_paths=tuple(stored_paths),
    )
