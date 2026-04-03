from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from nba_oracle.config import DEFAULT_JSON_REPORT_PATH, PHASE3_DRIFT_WINDOW_RUNS, RUNTIME_DIR, STABILITY_DIR
from nba_oracle.models_registry.catalog import (
    build_model_catalog,
    build_review_record,
    load_model_registry,
    model_registry_to_payload,
    save_model_registry,
    update_model_registry,
)
from nba_oracle.stability.baseline import (
    baseline_to_payload,
    build_phase3_baseline,
    evaluate_baseline_refresh,
    load_saved_phase3_baseline,
    load_recent_live_runs,
    save_phase3_baseline,
)
from nba_oracle.stability.drift import assess_drift
from nba_oracle.stability.persistence import build_stability_repository
from nba_oracle.stability.readiness import assess_readiness
from nba_oracle.stability.reporting import (
    StabilityReviewResult,
    write_stability_json_report,
    write_stability_markdown_report,
)
from nba_oracle.stability.timing import assess_timing


def review_stability(
    *,
    replay_report_path: Path = DEFAULT_JSON_REPORT_PATH,
    runtime_dir: Path = RUNTIME_DIR,
    limit: int | None = None,
    baseline_output_path: Path | None = None,
    markdown_report_path: Path | None = None,
    json_report_path: Path | None = None,
    force_refresh_baseline: bool = False,
    analyst_payload_path: Path | None = None,
    candidate_model_version: str | None = None,
    promotion_reason: str | None = None,
    rollback_reason: str | None = None,
) -> tuple[StabilityReviewResult, Path, Path, Path]:
    resolved_baseline_path = baseline_output_path or (STABILITY_DIR / "phase3_baseline.json")
    current_registry = load_model_registry()
    active_model_version = current_registry.active_model_version

    if resolved_baseline_path.exists():
        saved_baseline = load_saved_phase3_baseline(resolved_baseline_path)
        refresh_decision = evaluate_baseline_refresh(
            saved_baseline,
            replay_report_path=replay_report_path,
            model_version=active_model_version,
            force_refresh=force_refresh_baseline,
        )
        if refresh_decision.action == "reject":
            raise RuntimeError(f"phase3_baseline_incompatible:{refresh_decision.reason}")
        if refresh_decision.action == "refresh":
            baseline = build_phase3_baseline(
                replay_report_path=replay_report_path,
                runtime_dir=runtime_dir,
                limit=limit or PHASE3_DRIFT_WINDOW_RUNS,
                model_version=active_model_version,
                creation_reason=f"automatic_refresh:{refresh_decision.reason}",
            )
            baseline_path = save_phase3_baseline(baseline, path=resolved_baseline_path)
        else:
            baseline = saved_baseline
            baseline_path = resolved_baseline_path
    else:
        refresh_decision = None
        baseline = build_phase3_baseline(
            replay_report_path=replay_report_path,
            runtime_dir=runtime_dir,
            limit=limit or PHASE3_DRIFT_WINDOW_RUNS,
            model_version=active_model_version,
            creation_reason="initial_creation",
        )
        baseline_path = save_phase3_baseline(baseline, path=resolved_baseline_path)

    live_runs = load_recent_live_runs(runtime_dir, limit=limit or PHASE3_DRIFT_WINDOW_RUNS)
    actionable_live_runs = tuple(run for run in live_runs if run.prediction_count > 0)
    analyst_payload = _load_analyst_payload(analyst_payload_path)

    review_id = f"phase3-review-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    timing = assess_timing(review_id, actionable_live_runs)
    model_catalog = build_model_catalog(active_model_version=active_model_version)
    drift = assess_drift(baseline, actionable_live_runs)
    readiness = assess_readiness(
        review_id,
        actionable_live_runs,
        model_catalog,
        baseline,
        drift,
        analyst_payload,
    )

    review_record = build_review_record(
        review_id=review_id,
        drift_status=drift.status,
        retraining_recommended=drift.retraining_recommended,
        active_model_version=active_model_version,
        baseline_fingerprint=baseline.baseline_fingerprint,
        reasons=drift.reasons,
        candidate_model_version=candidate_model_version,
        promotion_reason=promotion_reason,
        rollback_reason=rollback_reason,
    )
    updated_registry = update_model_registry(current_registry, review_record)
    save_model_registry(updated_registry)

    repository = build_stability_repository()
    baseline_stored = repository.store_baseline(baseline_to_payload(baseline))

    result = StabilityReviewResult(
        review_id=review_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        baseline=baseline,
        baseline_action=refresh_decision.action if refresh_decision else "created",
        baseline_reason=refresh_decision.reason if refresh_decision else "baseline_created",
        live_runs=live_runs,
        drift=drift,
        timing=timing,
        readiness=readiness,
        model_catalog=model_catalog,
        model_registry=updated_registry,
        baseline_path=str(baseline_path),
        stored_paths=(),
    )

    review_payload = _review_payload_from_result(result)
    stored_paths = list(baseline_stored if isinstance(baseline_stored, list) else [baseline_stored])
    stored_paths.extend(
        repository.store_review_bundle(
            review_id,
            review_payload,
            [_timing_event_to_payload(item) for item in timing.events],
            [_analyst_log_to_payload(item) for item in readiness.analyst_logs],
            model_registry_to_payload(updated_registry),
        )
    )

    result = StabilityReviewResult(
        review_id=result.review_id,
        created_at=result.created_at,
        baseline=result.baseline,
        baseline_action=result.baseline_action,
        baseline_reason=result.baseline_reason,
        live_runs=result.live_runs,
        drift=result.drift,
        timing=result.timing,
        readiness=result.readiness,
        model_catalog=result.model_catalog,
        model_registry=result.model_registry,
        baseline_path=result.baseline_path,
        stored_paths=tuple(stored_paths),
    )

    if markdown_report_path is not None:
        md_path = write_stability_markdown_report(result, path=markdown_report_path)
    else:
        md_path = write_stability_markdown_report(result)

    if json_report_path is not None:
        json_path = write_stability_json_report(result, path=json_report_path)
    else:
        json_path = write_stability_json_report(result)
    return result, baseline_path, md_path, json_path


def _load_analyst_payload(path: Path | None) -> dict[str, dict[str, object]] | None:
    if path is None or not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and "predictions" in payload:
        rows = payload["predictions"]
    else:
        rows = payload
    if not isinstance(rows, list):
        return None
    return {
        str(item["game_id"]): dict(item)
        for item in rows
        if isinstance(item, dict) and item.get("game_id")
    }


def _review_payload_from_result(result: StabilityReviewResult) -> dict[str, object]:
    return {
        "review_id": result.review_id,
        "created_at": result.created_at,
        "baseline_action": result.baseline_action,
        "baseline_reason": result.baseline_reason,
        "baseline": baseline_to_payload(result.baseline),
        "baseline_path": result.baseline_path,
        "drift": {
            "status": result.drift.status,
            "live_runs_considered": result.drift.live_runs_considered,
            "graded_predictions": result.drift.graded_predictions,
            "retraining_recommended": result.drift.retraining_recommended,
            "reasons": list(result.drift.reasons),
            "outcome_metrics": {
                "graded_bet_count": result.drift.outcome_metrics.graded_bet_count,
                "graded_actionable_count": result.drift.outcome_metrics.graded_actionable_count,
                "roi": result.drift.outcome_metrics.roi,
                "average_clv": result.drift.outcome_metrics.average_clv,
                "calibration_gap": result.drift.outcome_metrics.calibration_gap,
            },
            "signals": [
                {
                    "name": signal.name,
                    "baseline_value": signal.baseline_value,
                    "current_value": signal.current_value,
                    "delta": signal.delta,
                    "threshold": signal.threshold,
                    "triggered": signal.triggered,
                    "available": signal.available,
                    "sample_size": signal.sample_size,
                    "note": signal.note,
                }
                for signal in result.drift.signals
            ],
        },
        "timing": {
            "status": result.timing.status,
            "runs_considered": result.timing.runs_considered,
            "stale_source_count": result.timing.stale_source_count,
            "average_source_age_minutes": result.timing.average_source_age_minutes,
            "average_market_age_minutes": result.timing.average_market_age_minutes,
            "schedule_fallback_rate": result.timing.schedule_fallback_rate,
            "notes": list(result.timing.notes),
        },
        "readiness": {
            "unlock_policy": result.readiness.unlock_policy,
            "graded_predictions": result.readiness.graded_predictions,
            "analyst_status": result.readiness.analyst.status,
            "analyst_disagreement_count": result.readiness.analyst.disagreement_count,
        },
        "model_catalog": result.model_catalog,
        "model_registry": model_registry_to_payload(result.model_registry),
    }


def _timing_event_to_payload(event: object) -> dict[str, object]:
    return {
        "review_id": event.review_id,
        "run_id": event.run_id,
        "game_id": event.game_id,
        "event_type": event.event_type,
        "source_kind": event.source_kind,
        "source_name": event.source_name,
        "source_timestamp": event.source_timestamp,
        "decision_timestamp": event.decision_timestamp,
        "market_timestamp": event.market_timestamp,
        "market_already_moved": event.market_already_moved,
        "predictor_changed": event.predictor_changed,
        "decision": event.decision,
        "event_impact": event.event_impact,
        "age_minutes": event.age_minutes,
        "signal_delta": event.signal_delta,
    }


def _analyst_log_to_payload(log: object) -> dict[str, object]:
    return {
        "review_id": log.review_id,
        "game_id": log.game_id,
        "disagreement_type": log.disagreement_type,
        "predictor_decision": log.predictor_decision,
        "analyst_decision": log.analyst_decision,
        "final_authority": log.final_authority,
        "note": log.note,
    }
