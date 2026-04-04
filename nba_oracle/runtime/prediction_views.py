from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from nba_oracle.config import RUNTIME_DIR


def load_prediction_views(
    *,
    runtime_dir: Path = RUNTIME_DIR,
    include_synthetic: bool = False,
) -> list[dict[str, Any]]:
    views: list[dict[str, Any]] = []
    for run_dir in _load_live_run_dirs(runtime_dir):
        run_state = _load_run_state(run_dir)
        if run_state is None:
            continue
        if not include_synthetic and _is_synthetic_run_state(run_state):
            continue
        views.extend(_build_prediction_views(run_dir.name, run_state))
    return views


def load_latest_prediction_views_by_game(
    *,
    runtime_dir: Path = RUNTIME_DIR,
    include_synthetic: bool = False,
) -> list[dict[str, Any]]:
    latest_by_game: dict[str, dict[str, Any]] = {}
    for view in load_prediction_views(runtime_dir=runtime_dir, include_synthetic=include_synthetic):
        game_id = str(view.get("game_id") or "").strip()
        if not game_id:
            continue
        existing = latest_by_game.get(game_id)
        if existing is None or _prediction_sort_key(view) > _prediction_sort_key(existing):
            latest_by_game[game_id] = view
    return sorted(
        latest_by_game.values(),
        key=lambda item: (
            _safe_datetime(item.get("tipoff_time")) or datetime.min,
            _safe_datetime(item.get("decision_time")) or datetime.min,
            str(item.get("run_id") or ""),
        ),
    )


def load_run_summaries(
    *,
    runtime_dir: Path = RUNTIME_DIR,
    limit: int = 10,
    include_synthetic: bool = False,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for run_dir in sorted(_load_live_run_dirs(runtime_dir), key=lambda item: item.name, reverse=True):
        run_state = _load_run_state(run_dir)
        if run_state is None:
            continue
        if not include_synthetic and _is_synthetic_run_state(run_state):
            continue

        predictions = run_state.get("predictions", [])
        items.append(
            {
                "run_id": run_dir.name,
                "prediction_count": len(predictions),
                "bet_count": sum(
                    1
                    for row in predictions
                    if isinstance(row, dict) and str(row.get("decision") or "").upper() == "BET"
                ),
                "lean_count": sum(
                    1
                    for row in predictions
                    if isinstance(row, dict) and str(row.get("decision") or "").upper() == "LEAN"
                ),
                "skip_count": sum(
                    1
                    for row in predictions
                    if isinstance(row, dict) and str(row.get("decision") or "").upper() == "SKIP"
                ),
                "path": str(run_dir / "predictions.json"),
            }
        )
        if len(items) >= limit:
            break
    return items


def _load_live_run_dirs(runtime_dir: Path) -> tuple[Path, ...]:
    if not runtime_dir.exists():
        return ()
    run_dirs = [
        path
        for path in runtime_dir.iterdir()
        if path.is_dir() and path.name.startswith("live-")
    ]
    return tuple(sorted(run_dirs, key=lambda item: item.name))


def _load_run_state(run_dir: Path) -> dict[str, Any] | None:
    predictions_path = run_dir / "predictions.json"
    snapshots_path = run_dir / "snapshots.json"
    if not predictions_path.exists() or not snapshots_path.exists():
        return None

    predictions_payload = _load_json(predictions_path)
    snapshots_payload = _load_json(snapshots_path)
    if not isinstance(predictions_payload, dict) or not isinstance(snapshots_payload, dict):
        return None

    predictions = predictions_payload.get("predictions", [])
    snapshots = snapshots_payload.get("snapshots", [])
    if not isinstance(predictions, list) or not isinstance(snapshots, list):
        return None

    snapshot_map = {
        str(item.get("game_id")): item
        for item in snapshots
        if isinstance(item, dict) and item.get("game_id")
    }

    return {
        "predictions": predictions,
        "snapshots": snapshots,
        "snapshot_map": snapshot_map,
    }


def _build_prediction_views(run_id: str, run_state: dict[str, Any]) -> list[dict[str, Any]]:
    snapshot_map = run_state.get("snapshot_map", {})
    if not isinstance(snapshot_map, dict):
        snapshot_map = {}

    views: list[dict[str, Any]] = []
    for item in run_state.get("predictions", []):
        if not isinstance(item, dict):
            continue
        payload = dict(item)
        game_id = str(payload.get("game_id") or "").strip()
        snapshot = snapshot_map.get(game_id) if game_id else None
        market = snapshot.get("market", {}) if isinstance(snapshot, dict) else {}
        if not isinstance(market, dict):
            market = {}

        away_team = snapshot.get("away_team") if isinstance(snapshot, dict) else None
        home_team = snapshot.get("home_team") if isinstance(snapshot, dict) else None
        selected_team = payload.get("selected_team") or market.get("selected_team")
        actual_winner = payload.get("actual_winner")
        if actual_winner in {None, ""} and isinstance(snapshot, dict):
            actual_winner = snapshot.get("actual_winner")

        payload["run_id"] = run_id
        payload["selected_team"] = selected_team
        payload["away_team"] = away_team
        payload["home_team"] = home_team
        payload["matchup_label"] = _build_matchup_label(
            away_team if isinstance(away_team, str) else None,
            home_team if isinstance(home_team, str) else None,
            game_id or None,
        )
        payload["decision_time"] = snapshot.get("decision_time") if isinstance(snapshot, dict) else None
        payload["tipoff_time"] = snapshot.get("tipoff_time") if isinstance(snapshot, dict) else None
        payload["actual_winner"] = actual_winner
        payload["reference_bookmaker"] = payload.get("reference_bookmaker") or market.get("reference_bookmaker")
        payload["stake_american"] = payload.get("stake_american", market.get("stake_american"))
        payload["best_american"] = payload.get("best_american", market.get("best_american"))
        payload["close_american"] = payload.get("close_american", market.get("close_american"))
        payload["opening_american"] = payload.get("opening_american", market.get("opening_american"))
        payload["market_timestamp"] = payload.get("market_timestamp", market.get("market_timestamp"))
        views.append(payload)
    return views


def _build_matchup_label(
    away_team: str | None,
    home_team: str | None,
    game_id: str | None,
) -> str:
    if away_team and home_team:
        return f"{away_team} at {home_team}"
    return game_id or "Unknown matchup"


def _prediction_sort_key(view: dict[str, Any]) -> tuple[datetime, str]:
    return (
        _safe_datetime(view.get("decision_time")) or datetime.min,
        str(view.get("run_id") or ""),
    )


def _safe_datetime(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _is_synthetic_run_state(run_state: dict[str, Any]) -> bool:
    snapshots = run_state.get("snapshots", [])
    if not isinstance(snapshots, list):
        return False

    source_versions: set[str] = set()
    for snapshot in snapshots:
        if not isinstance(snapshot, dict):
            continue
        sources = snapshot.get("sources", [])
        if not isinstance(sources, list):
            continue
        for source in sources:
            if not isinstance(source, dict):
                continue
            version = str(source.get("source_version") or "").strip().lower()
            if version:
                source_versions.add(version)

    if not source_versions:
        return False
    return all("test" in version or "sample" in version for version in source_versions)
