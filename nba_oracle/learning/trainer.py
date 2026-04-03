from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from nba_oracle.config import LEARNING_DIR, LEARNING_MIN_GRADED_PICKS, LEARNING_REVIEW_ONLY, RUNTIME_DIR
from nba_oracle.learning.patterns import mine_patterns
from nba_oracle.learning.review import LearningReviewResult, ensure_learning_dir
from nba_oracle.learning.weights import derive_candidate_weights
from nba_oracle.models_registry.catalog import build_model_catalog
from nba_oracle.runtime.state import record_learning_review


def run_learning_review(runtime_dir: Path = RUNTIME_DIR) -> LearningReviewResult:
    ensure_learning_dir()
    created_at = datetime.now(timezone.utc)
    review_id = f"phase4a-learning-{created_at.strftime('%Y%m%dT%H%M%SZ')}"
    model_catalog = build_model_catalog()
    predictions = _load_graded_predictions(runtime_dir)
    actionable = [item for item in predictions if item.get("decision") != "SKIP"]

    reasons: list[str] = []
    status = "insufficient_data"
    candidate_model_version = None
    weights: list[dict[str, object]] = []
    patterns: list[dict[str, object]] = []

    if len(predictions) < LEARNING_MIN_GRADED_PICKS:
        reasons.append("Need more graded predictions before opening a learning review.")
    elif not actionable:
        reasons.append("No actionable graded predictions available for learning review.")
    else:
        weights = derive_candidate_weights(actionable)
        patterns = mine_patterns(actionable)
        status = "candidate_review_ready"
        candidate_model_version = f"{model_catalog['model_version']}-candidate-{created_at.strftime('%Y%m%d%H%M%S')}"
        reasons.append("Candidate-only learning review created; no silent promotion will happen.")

    result = LearningReviewResult(
        review_id=review_id,
        created_at=created_at,
        status=status,
        active_model_version=str(model_catalog["model_version"]),
        candidate_model_version=candidate_model_version,
        graded_prediction_count=len(predictions),
        actionable_prediction_count=len(actionable),
        review_only=LEARNING_REVIEW_ONLY,
        weights=tuple(weights),
        patterns=tuple(patterns),
        reasons=tuple(reasons),
        stored_paths=tuple(_store_learning_artifacts(review_id, created_at, status, candidate_model_version, predictions, weights, patterns, reasons)),
    )
    return result


def _load_graded_predictions(runtime_dir: Path) -> list[dict[str, object]]:
    predictions: list[dict[str, object]] = []
    if not runtime_dir.exists():
        return predictions
    for run_dir in sorted(runtime_dir.iterdir()):
        predictions_path = run_dir / "predictions.json"
        if not run_dir.is_dir() or not predictions_path.exists():
            continue
        try:
            payload = json.loads(predictions_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for item in payload.get("predictions", []):
            actual_winner = item.get("actual_winner")
            if actual_winner in {None, ""}:
                continue
            normalized = dict(item)
            normalized["won"] = normalized.get("selected_team") == actual_winner
            predictions.append(normalized)
    return predictions


def _store_learning_artifacts(
    review_id: str,
    created_at: datetime,
    status: str,
    candidate_model_version: str | None,
    predictions: list[dict[str, object]],
    weights: list[dict[str, object]],
    patterns: list[dict[str, object]],
    reasons: list[str],
) -> list[str]:
    ensure_learning_dir()
    review_payload = {
        "review_id": review_id,
        "created_at": created_at.isoformat(),
        "status": status,
        "candidate_model_version": candidate_model_version,
        "graded_prediction_count": len(predictions),
        "weights": weights,
        "patterns": patterns,
        "reasons": reasons,
    }
    review_path = LEARNING_DIR / f"{review_id}.json"
    review_path.write_text(json.dumps(review_payload, indent=2), encoding="utf-8")

    latest_path = LEARNING_DIR / "latest_learning_review.json"
    latest_path.write_text(json.dumps(review_payload, indent=2), encoding="utf-8")

    record_learning_review(review_payload)
    return [str(review_path), str(latest_path)]
