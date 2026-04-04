from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query

from nba_oracle.api.dependencies import require_authenticated_user
from nba_oracle.runtime.prediction_views import load_latest_prediction_views_by_game, load_run_summaries


router = APIRouter(prefix="/api/picks", tags=["picks"])


@router.get("/history")
def picks_history(
    limit: int = Query(default=10, ge=1, le=50),
    _: dict[str, object] = Depends(require_authenticated_user),
) -> dict[str, object]:
    runs = load_run_summaries(limit=limit)
    all_results = _load_all_results()
    results = all_results[: max(limit * 3, 12)]
    return {
        "runs": runs,
        "summary": _build_accuracy_summary(all_results),
        "results": results,
    }


def _load_all_results() -> list[dict[str, Any]]:
    graded_rows: list[dict[str, Any]] = []
    for prediction in load_latest_prediction_views_by_game():
        actual_winner = prediction.get("actual_winner")
        selected_team = prediction.get("selected_team")
        if not isinstance(actual_winner, str) or not actual_winner.strip():
            continue
        if not isinstance(selected_team, str) or not selected_team.strip():
            continue

        graded_rows.append(
            {
                "run_id": prediction.get("run_id"),
                "game_id": prediction.get("game_id"),
                "matchup_label": prediction.get("matchup_label"),
                "selected_team": selected_team,
                "decision": prediction.get("decision"),
                "actual_winner": actual_winner,
                "won": selected_team == actual_winner,
                "tipoff_time": prediction.get("tipoff_time"),
                "decision_time": prediction.get("decision_time"),
            }
        )

    graded_rows.sort(
        key=lambda item: (
            _safe_datetime(item.get("tipoff_time")) or datetime.min,
            _safe_datetime(item.get("decision_time")) or datetime.min,
        ),
        reverse=True,
    )
    return graded_rows


def _build_accuracy_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(results)
    total_correct = sum(1 for item in results if item.get("won") is True)
    bet_results = [item for item in results if str(item.get("decision") or "").upper() == "BET"]
    lean_results = [item for item in results if str(item.get("decision") or "").upper() == "LEAN"]

    return {
        "graded_count": total,
        "correct_count": total_correct,
        "overall_accuracy": _ratio(total_correct, total),
        "bet_count": len(bet_results),
        "bet_correct": sum(1 for item in bet_results if item.get("won") is True),
        "bet_accuracy": _ratio(sum(1 for item in bet_results if item.get("won") is True), len(bet_results)),
        "lean_count": len(lean_results),
        "lean_correct": sum(1 for item in lean_results if item.get("won") is True),
        "lean_accuracy": _ratio(sum(1 for item in lean_results if item.get("won") is True), len(lean_results)),
        "skip_count": sum(1 for item in results if str(item.get("decision") or "").upper() == "SKIP"),
    }


def _ratio(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return numerator / denominator


def _safe_datetime(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
