from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Depends, Query

from nba_oracle.api.dependencies import require_authenticated_user
from nba_oracle.config import RUNTIME_DIR


router = APIRouter(prefix="/api/picks", tags=["picks"])


@router.get("/history")
def picks_history(
    limit: int = Query(default=10, ge=1, le=50),
    _: dict[str, object] = Depends(require_authenticated_user),
) -> dict[str, object]:
    items: list[dict[str, object]] = []
    if RUNTIME_DIR.exists():
        for run_dir in sorted(RUNTIME_DIR.iterdir(), reverse=True):
            if not run_dir.is_dir() or not run_dir.name.startswith("live-"):
                continue
            predictions_path = run_dir / "predictions.json"
            if not predictions_path.exists():
                continue
            payload = _load_json(predictions_path)
            predictions = payload.get("predictions", [])
            items.append(
                {
                    "run_id": run_dir.name,
                    "prediction_count": len(predictions) if isinstance(predictions, list) else 0,
                    "bet_count": sum(1 for row in predictions if isinstance(row, dict) and row.get("decision") == "BET"),
                    "lean_count": sum(1 for row in predictions if isinstance(row, dict) and row.get("decision") == "LEAN"),
                    "skip_count": sum(1 for row in predictions if isinstance(row, dict) and row.get("decision") == "SKIP"),
                    "path": str(predictions_path),
                }
            )
            if len(items) >= limit:
                break
    return {"runs": items}


def _load_json(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}
