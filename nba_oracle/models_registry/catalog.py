from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from nba_oracle.config import PHASE3_ANALYST_LOGGING_ENABLED, PHASE3_MARKET_UNLOCK_POLICY, STABILITY_DIR
from nba_oracle.models import parse_dt


MODEL_REGISTRY_PATH = STABILITY_DIR / "phase3_model_registry.json"


@dataclass(frozen=True)
class ModelReviewRecord:
    review_id: str
    created_at: datetime
    active_model_version: str
    candidate_model_version: str | None
    review_status: str
    drift_status: str
    retraining_recommended: bool
    replay_gate_required: bool
    promotion_reason: str | None
    rollback_reason: str | None
    reasons: tuple[str, ...]
    baseline_fingerprint: str


@dataclass(frozen=True)
class ModelRegistryState:
    updated_at: datetime
    active_model_version: str
    candidate_model_version: str | None
    review_status: str
    current_review_id: str | None
    analyst_layer_present: bool
    analyst_logging_enabled: bool
    predictor_authority: str
    promotion_reason: str | None
    rollback_reason: str | None
    history: tuple[ModelReviewRecord, ...]


def build_model_catalog(active_model_version: str = "phase2-deterministic-v1") -> dict[str, object]:
    state = load_model_registry(default_model_version=active_model_version)
    return {
        "model_version": state.active_model_version,
        "candidate_model_version": state.candidate_model_version,
        "active_market_family": "moneyline",
        "market_unlock_policy": PHASE3_MARKET_UNLOCK_POLICY,
        "analyst_layer_present": state.analyst_layer_present,
        "analyst_logging_enabled": state.analyst_logging_enabled,
        "retraining_policy": "manual_review_only",
        "predictor_authority": state.predictor_authority,
        "review_status": state.review_status,
        "current_review_id": state.current_review_id,
    }


def load_model_registry(default_model_version: str = "phase2-deterministic-v1") -> ModelRegistryState:
    if not MODEL_REGISTRY_PATH.exists():
        return ModelRegistryState(
            updated_at=datetime.now(timezone.utc),
            active_model_version=default_model_version,
            candidate_model_version=None,
            review_status="no_review",
            current_review_id=None,
            analyst_layer_present=False,
            analyst_logging_enabled=PHASE3_ANALYST_LOGGING_ENABLED,
            predictor_authority="strict",
            promotion_reason=None,
            rollback_reason=None,
            history=(),
        )

    try:
        payload = json.loads(MODEL_REGISTRY_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ModelRegistryState(
            updated_at=datetime.now(timezone.utc),
            active_model_version=default_model_version,
            candidate_model_version=None,
            review_status="no_review",
            current_review_id=None,
            analyst_layer_present=False,
            analyst_logging_enabled=PHASE3_ANALYST_LOGGING_ENABLED,
            predictor_authority="strict",
            promotion_reason=None,
            rollback_reason=None,
            history=(),
        )
    return ModelRegistryState(
        updated_at=parse_dt(str(payload["updated_at"])),
        active_model_version=str(payload["active_model_version"]),
        candidate_model_version=payload.get("candidate_model_version"),
        review_status=str(payload["review_status"]),
        current_review_id=payload.get("current_review_id"),
        analyst_layer_present=bool(payload.get("analyst_layer_present", False)),
        analyst_logging_enabled=bool(payload.get("analyst_logging_enabled", PHASE3_ANALYST_LOGGING_ENABLED)),
        predictor_authority=str(payload.get("predictor_authority", "strict")),
        promotion_reason=payload.get("promotion_reason"),
        rollback_reason=payload.get("rollback_reason"),
        history=tuple(_record_from_payload(item) for item in payload.get("history", [])),
    )


def save_model_registry(state: ModelRegistryState, path: Path = MODEL_REGISTRY_PATH) -> Path:
    STABILITY_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(model_registry_to_payload(state), indent=2), encoding="utf-8")
    return path


def model_registry_to_payload(state: ModelRegistryState) -> dict[str, object]:
    return {
        "updated_at": state.updated_at.isoformat(),
        "active_model_version": state.active_model_version,
        "candidate_model_version": state.candidate_model_version,
        "review_status": state.review_status,
        "current_review_id": state.current_review_id,
        "analyst_layer_present": state.analyst_layer_present,
        "analyst_logging_enabled": state.analyst_logging_enabled,
        "predictor_authority": state.predictor_authority,
        "promotion_reason": state.promotion_reason,
        "rollback_reason": state.rollback_reason,
        "history": [_record_to_payload(item) for item in state.history],
    }


def build_review_record(
    *,
    review_id: str,
    drift_status: str,
    retraining_recommended: bool,
    active_model_version: str,
    baseline_fingerprint: str,
    reasons: tuple[str, ...],
    candidate_model_version: str | None = None,
    promotion_reason: str | None = None,
    rollback_reason: str | None = None,
) -> ModelReviewRecord:
    if rollback_reason:
        review_status = "rolled_back"
    elif candidate_model_version and promotion_reason:
        review_status = "eligible_for_promotion"
    elif candidate_model_version:
        review_status = "candidate_waiting_for_replay"
    elif drift_status in {"warning", "retrain_review"}:
        review_status = "review_open"
    else:
        review_status = "no_review"

    return ModelReviewRecord(
        review_id=review_id,
        created_at=datetime.now(timezone.utc),
        active_model_version=active_model_version,
        candidate_model_version=candidate_model_version,
        review_status=review_status,
        drift_status=drift_status,
        retraining_recommended=retraining_recommended,
        replay_gate_required=True,
        promotion_reason=promotion_reason,
        rollback_reason=rollback_reason,
        reasons=reasons,
        baseline_fingerprint=baseline_fingerprint,
    )


def update_model_registry(
    current: ModelRegistryState,
    review_record: ModelReviewRecord,
) -> ModelRegistryState:
    history = tuple([review_record, *current.history][:50])
    active_model_version = current.active_model_version
    candidate_model_version = review_record.candidate_model_version
    promotion_reason = current.promotion_reason
    rollback_reason = current.rollback_reason

    if review_record.review_status == "eligible_for_promotion" and review_record.candidate_model_version:
        active_model_version = review_record.candidate_model_version
        candidate_model_version = None
        promotion_reason = review_record.promotion_reason

    if review_record.review_status == "rolled_back":
        candidate_model_version = None
        rollback_reason = review_record.rollback_reason

    return ModelRegistryState(
        updated_at=datetime.now(timezone.utc),
        active_model_version=active_model_version,
        candidate_model_version=candidate_model_version,
        review_status=review_record.review_status,
        current_review_id=review_record.review_id,
        analyst_layer_present=current.analyst_layer_present,
        analyst_logging_enabled=current.analyst_logging_enabled,
        predictor_authority=current.predictor_authority,
        promotion_reason=promotion_reason,
        rollback_reason=rollback_reason,
        history=history,
    )


def _record_to_payload(record: ModelReviewRecord) -> dict[str, object]:
    return {
        "review_id": record.review_id,
        "created_at": record.created_at.isoformat(),
        "active_model_version": record.active_model_version,
        "candidate_model_version": record.candidate_model_version,
        "review_status": record.review_status,
        "drift_status": record.drift_status,
        "retraining_recommended": record.retraining_recommended,
        "replay_gate_required": record.replay_gate_required,
        "promotion_reason": record.promotion_reason,
        "rollback_reason": record.rollback_reason,
        "reasons": list(record.reasons),
        "baseline_fingerprint": record.baseline_fingerprint,
    }


def _record_from_payload(payload: dict[str, object]) -> ModelReviewRecord:
    return ModelReviewRecord(
        review_id=str(payload["review_id"]),
        created_at=parse_dt(str(payload["created_at"])),
        active_model_version=str(payload["active_model_version"]),
        candidate_model_version=payload.get("candidate_model_version"),  # type: ignore[arg-type]
        review_status=str(payload["review_status"]),
        drift_status=str(payload["drift_status"]),
        retraining_recommended=bool(payload["retraining_recommended"]),
        replay_gate_required=bool(payload.get("replay_gate_required", True)),
        promotion_reason=payload.get("promotion_reason"),  # type: ignore[arg-type]
        rollback_reason=payload.get("rollback_reason"),  # type: ignore[arg-type]
        reasons=tuple(str(item) for item in payload.get("reasons", [])),
        baseline_fingerprint=str(payload["baseline_fingerprint"]),
    )
