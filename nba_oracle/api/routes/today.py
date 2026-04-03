from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Depends

from nba_oracle.api.dependencies import require_authenticated_user
from nba_oracle.config import RUNTIME_DIR
from nba_oracle.runtime.health import load_latest_live_report


router = APIRouter(prefix="/api", tags=["today"])


@router.get("/today")
def today(_: dict[str, object] = Depends(require_authenticated_user)) -> dict[str, object]:
    report = load_latest_live_report()
    return {
        "run_id": report.get("run_id"),
        "decision_time": report.get("decision_time"),
        "storage_mode": report.get("storage_mode"),
        "providers": report.get("providers", []),
        "predictions": _enrich_predictions(report.get("run_id"), report.get("predictions", [])),
        "stored_paths": report.get("stored_paths", []),
    }


def _enrich_predictions(run_id: object, predictions: object) -> list[dict[str, object]]:
    if not isinstance(predictions, list):
        return []

    snapshot_map = _load_snapshot_map(str(run_id)) if isinstance(run_id, str) and run_id else {}
    enriched: list[dict[str, object]] = []
    for item in predictions:
        if not isinstance(item, dict):
            continue
        payload = dict(item)
        game_id = payload.get("game_id")
        snapshot = snapshot_map.get(game_id) if isinstance(game_id, str) else None
        away_team = snapshot.get("away_team") if snapshot else None
        home_team = snapshot.get("home_team") if snapshot else None
        payload["away_team"] = away_team
        payload["home_team"] = home_team
        payload["matchup_label"] = _build_matchup_label(
            away_team if isinstance(away_team, str) else None,
            home_team if isinstance(home_team, str) else None,
            game_id if isinstance(game_id, str) else None,
        )
        enriched.append(payload)
    return enriched


def _load_snapshot_map(run_id: str) -> dict[str, dict[str, object]]:
    path = Path(RUNTIME_DIR) / run_id / "snapshots.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

    snapshots = payload.get("snapshots", []) if isinstance(payload, dict) else []
    snapshot_map: dict[str, dict[str, object]] = {}
    for item in snapshots:
        if not isinstance(item, dict):
            continue
        game_id = item.get("game_id")
        if isinstance(game_id, str):
            snapshot_map[game_id] = item
    return snapshot_map


def _build_matchup_label(
    away_team: str | None,
    home_team: str | None,
    game_id: str | None,
) -> str:
    if away_team and home_team:
        return f"{away_team} at {home_team}"
    return game_id or "Unknown matchup"
