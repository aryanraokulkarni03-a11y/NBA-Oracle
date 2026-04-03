from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from nba_oracle.config import (
    DEFAULT_JSON_REPORT_PATH,
    PHASE3_ANALYST_LOGGING_ENABLED,
    PHASE3_AUTO_REFRESH_BASELINE,
    PHASE3_BASELINE_SCHEMA_VERSION,
    PHASE3_DRIFT_WINDOW_RUNS,
    PHASE3_MARKET_UNLOCK_MIN_SAMPLE,
    PHASE3_MARKET_UNLOCK_POLICY,
    PHASE3_MAX_ACTIVE_BET_RATE_DELTA,
    PHASE3_MAX_CALIBRATION_GAP_DELTA,
    PHASE3_MAX_CLV_DELTA,
    PHASE3_MAX_EDGE_DELTA,
    PHASE3_MAX_PROVIDER_DEGRADATION_RATE,
    PHASE3_MAX_ROI_DELTA,
    PHASE3_MAX_SKIP_RATE_DELTA,
    PHASE3_MAX_SOURCE_QUALITY_DELTA,
    PHASE3_MIN_GRADED_PICKS_FOR_RETRAIN,
    PHASE3_MIN_LIVE_RUNS_FOR_DRIFT,
    RUNTIME_DIR,
    STABILITY_DIR,
)
from nba_oracle.models import parse_dt


@dataclass(frozen=True)
class LiveProviderSnapshot:
    name: str
    kind: str
    source_time: datetime
    success: bool
    degraded: bool
    error: str | None


@dataclass(frozen=True)
class LivePredictionSnapshot:
    game_id: str
    selected_team: str
    decision: str
    stake_american: int
    model_probability: float
    expected_value: float
    edge_vs_reference: float
    source_quality: float
    stake_probability: float
    best_probability: float
    close_probability: float
    price_gap: float
    market_timestamp: datetime | None
    source_scores: tuple[dict[str, object], ...]
    reasons: tuple[str, ...]
    actual_winner: str | None

    @property
    def is_active(self) -> bool:
        return self.decision == "BET"

    @property
    def is_actionable(self) -> bool:
        return self.decision != "SKIP"

    @property
    def is_graded(self) -> bool:
        return self.actual_winner not in {None, ""}

    @property
    def won(self) -> bool:
        return self.is_graded and self.selected_team == self.actual_winner

    @property
    def clv(self) -> float:
        return round(self.close_probability - self.stake_probability, 4)


@dataclass(frozen=True)
class LiveRunSnapshot:
    run_id: str
    decision_time: datetime
    providers: tuple[LiveProviderSnapshot, ...]
    predictions: tuple[LivePredictionSnapshot, ...]
    stored_paths: tuple[str, ...]

    @property
    def prediction_count(self) -> int:
        return len(self.predictions)

    @property
    def active_bet_count(self) -> int:
        return sum(1 for item in self.predictions if item.is_active)

    @property
    def skip_count(self) -> int:
        return sum(1 for item in self.predictions if item.decision == "SKIP")

    @property
    def actionable_count(self) -> int:
        return sum(1 for item in self.predictions if item.is_actionable)

    @property
    def degraded_provider_count(self) -> int:
        return sum(1 for item in self.providers if item.degraded)

    @property
    def provider_count(self) -> int:
        return len(self.providers)

    @property
    def graded_prediction_count(self) -> int:
        return sum(1 for item in self.predictions if item.is_graded)

    @property
    def graded_active_bet_count(self) -> int:
        return sum(1 for item in self.predictions if item.is_active and item.is_graded)

    @property
    def graded_actionable_count(self) -> int:
        return sum(1 for item in self.predictions if item.is_actionable and item.is_graded)

    @property
    def schedule_fallback_used(self) -> bool:
        schedule = next((provider for provider in self.providers if provider.kind == "schedule"), None)
        if schedule is None:
            return False
        return schedule.error == "official_schedule_empty_using_odds_fallback" or "odds_fallback" in schedule.name

    @property
    def average_source_quality(self) -> float:
        if not self.predictions:
            return 0.0
        return round(sum(item.source_quality for item in self.predictions) / len(self.predictions), 4)

    @property
    def average_expected_value(self) -> float:
        if not self.predictions:
            return 0.0
        return round(sum(item.expected_value for item in self.predictions) / len(self.predictions), 4)

    @property
    def average_edge(self) -> float:
        if not self.predictions:
            return 0.0
        return round(sum(item.edge_vs_reference for item in self.predictions) / len(self.predictions), 4)

    @property
    def average_clv(self) -> float:
        active = [item for item in self.predictions if item.is_active]
        if not active:
            return 0.0
        return round(sum(item.clv for item in active) / len(active), 4)

    @property
    def average_price_gap(self) -> float:
        if not self.predictions:
            return 0.0
        return round(sum(item.price_gap for item in self.predictions) / len(self.predictions), 4)

    @property
    def active_bet_rate(self) -> float:
        if not self.predictions:
            return 0.0
        return round(self.active_bet_count / len(self.predictions), 4)

    @property
    def skip_rate(self) -> float:
        if not self.predictions:
            return 0.0
        return round(self.skip_count / len(self.predictions), 4)

    @property
    def provider_degradation_rate(self) -> float:
        if not self.providers:
            return 0.0
        return round(self.degraded_provider_count / len(self.providers), 4)


@dataclass(frozen=True)
class BaselineSnapshot:
    created_at: datetime
    schema_version: str
    model_version: str
    config_fingerprint: str
    replay_report_fingerprint: str
    baseline_fingerprint: str
    creation_reason: str
    replay_phase1_ready: bool
    replay_roi: float
    replay_average_clv: float
    replay_average_edge: float
    replay_average_source_quality: float
    replay_calibration_gap: float
    replay_bet_count: int
    live_runs_considered: int
    live_average_prediction_count: float
    live_average_active_bet_rate: float
    live_average_skip_rate: float
    live_average_source_quality: float
    live_average_expected_value: float
    live_average_edge: float
    live_average_clv: float
    live_average_provider_degradation_rate: float
    live_schedule_fallback_rate: float


@dataclass(frozen=True)
class BaselineRefreshDecision:
    action: str
    reason: str
    compatible: bool


def ensure_stability_dir() -> None:
    STABILITY_DIR.mkdir(parents=True, exist_ok=True)


def load_recent_live_runs(
    runtime_dir: Path = RUNTIME_DIR,
    *,
    limit: int = PHASE3_DRIFT_WINDOW_RUNS,
) -> tuple[LiveRunSnapshot, ...]:
    if not runtime_dir.exists():
        return ()
    run_dirs = sorted(
        (path for path in runtime_dir.iterdir() if path.is_dir() and path.name.startswith("live-")),
        key=lambda path: path.name,
        reverse=True,
    )
    snapshots: list[LiveRunSnapshot] = []
    for path in run_dirs:
        if len(snapshots) >= limit:
            break
        try:
            snapshots.append(load_live_run_snapshot(path))
        except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError):
            continue
    return tuple(sorted(snapshots, key=lambda item: item.decision_time))


def load_live_run_snapshot(run_dir: Path) -> LiveRunSnapshot:
    run_id = run_dir.name
    decision_time = _parse_run_id(run_id)

    providers: list[LiveProviderSnapshot] = []
    for provider_path in sorted(run_dir.glob("provider_*.json")):
        payload = json.loads(provider_path.read_text(encoding="utf-8"))
        providers.append(
            LiveProviderSnapshot(
                name=str(payload["name"]),
                kind=str(payload["kind"]),
                source_time=parse_dt(str(payload["source_time"])),
                success=bool(payload["success"]),
                degraded=bool(payload["degraded"]),
                error=payload.get("error"),
            )
        )

    predictions_path = run_dir / "predictions.json"
    prediction_payload = json.loads(predictions_path.read_text(encoding="utf-8"))
    predictions: list[LivePredictionSnapshot] = []
    for item in prediction_payload.get("predictions", []):
        predictions.append(
            LivePredictionSnapshot(
                game_id=str(item["game_id"]),
                selected_team=str(item.get("selected_team", "")),
                decision=str(item["decision"]),
                stake_american=int(item.get("stake_american", item.get("reference_american", 0))),
                model_probability=float(item["model_probability"]),
                expected_value=float(item["expected_value"]),
                edge_vs_reference=float(item["edge_vs_stake"]),
                source_quality=float(item["source_quality"]),
                stake_probability=float(item.get("stake_probability", item.get("reference_probability", 0.0))),
                best_probability=float(item.get("best_probability", 0.0)),
                close_probability=float(item.get("close_probability", 0.0)),
                price_gap=round(abs(float(item.get("stake_probability", 0.0)) - float(item.get("best_probability", 0.0))), 4),
                market_timestamp=parse_dt(str(item["market_timestamp"])) if item.get("market_timestamp") else None,
                source_scores=tuple(dict(score) for score in item.get("source_scores", [])),
                reasons=tuple(str(reason) for reason in item.get("reasons", [])),
                actual_winner=item.get("actual_winner"),
            )
        )

    stored_paths = [str(item) for item in sorted(run_dir.iterdir()) if item.is_file()]

    return LiveRunSnapshot(
        run_id=run_id,
        decision_time=decision_time,
        providers=tuple(providers),
        predictions=tuple(predictions),
        stored_paths=tuple(stored_paths),
    )


def load_replay_baseline(replay_report_path: Path = DEFAULT_JSON_REPORT_PATH) -> dict[str, object]:
    return json.loads(replay_report_path.read_text(encoding="utf-8"))


def build_phase3_baseline(
    replay_report_path: Path = DEFAULT_JSON_REPORT_PATH,
    runtime_dir: Path = RUNTIME_DIR,
    *,
    limit: int = PHASE3_DRIFT_WINDOW_RUNS,
    model_version: str = "phase2-deterministic-v1",
    creation_reason: str = "initial_creation",
) -> BaselineSnapshot:
    replay = load_replay_baseline(replay_report_path)
    live_runs = tuple(run for run in load_recent_live_runs(runtime_dir, limit=limit) if run.prediction_count > 0)
    config_fingerprint = build_phase3_config_fingerprint(model_version)
    replay_report_fingerprint = fingerprint_file(replay_report_path)

    if live_runs:
        live_average_prediction_count = round(sum(run.prediction_count for run in live_runs) / len(live_runs), 4)
        live_average_active_bet_rate = round(sum(run.active_bet_rate for run in live_runs) / len(live_runs), 4)
        live_average_skip_rate = round(sum(run.skip_rate for run in live_runs) / len(live_runs), 4)
        live_average_source_quality = round(sum(run.average_source_quality for run in live_runs) / len(live_runs), 4)
        live_average_expected_value = round(sum(run.average_expected_value for run in live_runs) / len(live_runs), 4)
        live_average_edge = round(sum(run.average_edge for run in live_runs) / len(live_runs), 4)
        live_average_clv = round(sum(run.average_clv for run in live_runs) / len(live_runs), 4)
        live_average_provider_degradation_rate = round(
            sum(run.provider_degradation_rate for run in live_runs) / len(live_runs),
            4,
        )
        live_schedule_fallback_rate = round(
            sum(1 for run in live_runs if run.schedule_fallback_used) / len(live_runs),
            4,
        )
    else:
        live_average_prediction_count = 0.0
        live_average_active_bet_rate = 0.0
        live_average_skip_rate = 0.0
        live_average_source_quality = 0.0
        live_average_expected_value = 0.0
        live_average_edge = 0.0
        live_average_clv = 0.0
        live_average_provider_degradation_rate = 0.0
        live_schedule_fallback_rate = 0.0

    baseline_without_fingerprint = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "schema_version": PHASE3_BASELINE_SCHEMA_VERSION,
        "model_version": model_version,
        "config_fingerprint": config_fingerprint,
        "replay_report_fingerprint": replay_report_fingerprint,
        "creation_reason": creation_reason,
        "replay_phase1_ready": bool(replay["phase1_ready"]),
        "replay_roi": float(replay["roi"]),
        "replay_average_clv": float(replay["average_clv"]),
        "replay_average_edge": float(replay["average_edge"]),
        "replay_average_source_quality": float(replay["average_source_quality"]),
        "replay_calibration_gap": float(replay["calibration_assessment"]["mean_absolute_gap"]),
        "replay_bet_count": int(replay["bet_count"]),
        "live_runs_considered": len(live_runs),
        "live_average_prediction_count": live_average_prediction_count,
        "live_average_active_bet_rate": live_average_active_bet_rate,
        "live_average_skip_rate": live_average_skip_rate,
        "live_average_source_quality": live_average_source_quality,
        "live_average_expected_value": live_average_expected_value,
        "live_average_edge": live_average_edge,
        "live_average_clv": live_average_clv,
        "live_average_provider_degradation_rate": live_average_provider_degradation_rate,
        "live_schedule_fallback_rate": live_schedule_fallback_rate,
    }
    baseline_fingerprint = fingerprint_payload(baseline_without_fingerprint)

    return BaselineSnapshot(
        created_at=parse_dt(baseline_without_fingerprint["created_at"]),
        schema_version=PHASE3_BASELINE_SCHEMA_VERSION,
        model_version=model_version,
        config_fingerprint=config_fingerprint,
        replay_report_fingerprint=replay_report_fingerprint,
        baseline_fingerprint=baseline_fingerprint,
        creation_reason=creation_reason,
        replay_phase1_ready=bool(replay["phase1_ready"]),
        replay_roi=float(replay["roi"]),
        replay_average_clv=float(replay["average_clv"]),
        replay_average_edge=float(replay["average_edge"]),
        replay_average_source_quality=float(replay["average_source_quality"]),
        replay_calibration_gap=float(replay["calibration_assessment"]["mean_absolute_gap"]),
        replay_bet_count=int(replay["bet_count"]),
        live_runs_considered=len(live_runs),
        live_average_prediction_count=live_average_prediction_count,
        live_average_active_bet_rate=live_average_active_bet_rate,
        live_average_skip_rate=live_average_skip_rate,
        live_average_source_quality=live_average_source_quality,
        live_average_expected_value=live_average_expected_value,
        live_average_edge=live_average_edge,
        live_average_clv=live_average_clv,
        live_average_provider_degradation_rate=live_average_provider_degradation_rate,
        live_schedule_fallback_rate=live_schedule_fallback_rate,
    )


def save_phase3_baseline(
    baseline: BaselineSnapshot,
    *,
    path: Path | None = None,
) -> Path:
    ensure_stability_dir()
    output_path = path or (STABILITY_DIR / "phase3_baseline.json")
    output_path.write_text(json.dumps(baseline_to_payload(baseline), indent=2), encoding="utf-8")
    return output_path


def load_saved_phase3_baseline(path: Path) -> BaselineSnapshot:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return BaselineSnapshot(
        created_at=parse_dt(str(payload["created_at"])),
        schema_version=str(payload.get("schema_version", "1.0")),
        model_version=str(payload["model_version"]),
        config_fingerprint=str(payload.get("config_fingerprint", "")),
        replay_report_fingerprint=str(payload.get("replay_report_fingerprint", "")),
        baseline_fingerprint=str(payload.get("baseline_fingerprint", "")),
        creation_reason=str(payload.get("creation_reason", "legacy_load")),
        replay_phase1_ready=bool(payload["replay_phase1_ready"]),
        replay_roi=float(payload["replay_roi"]),
        replay_average_clv=float(payload["replay_average_clv"]),
        replay_average_edge=float(payload["replay_average_edge"]),
        replay_average_source_quality=float(payload["replay_average_source_quality"]),
        replay_calibration_gap=float(payload.get("replay_calibration_gap", 1.0)),
        replay_bet_count=int(payload["replay_bet_count"]),
        live_runs_considered=int(payload["live_runs_considered"]),
        live_average_prediction_count=float(payload["live_average_prediction_count"]),
        live_average_active_bet_rate=float(payload["live_average_active_bet_rate"]),
        live_average_skip_rate=float(payload["live_average_skip_rate"]),
        live_average_source_quality=float(payload["live_average_source_quality"]),
        live_average_expected_value=float(payload["live_average_expected_value"]),
        live_average_edge=float(payload["live_average_edge"]),
        live_average_clv=float(payload.get("live_average_clv", 0.0)),
        live_average_provider_degradation_rate=float(payload["live_average_provider_degradation_rate"]),
        live_schedule_fallback_rate=float(payload["live_schedule_fallback_rate"]),
    )


def baseline_to_payload(baseline: BaselineSnapshot) -> dict[str, object]:
    return {
        "created_at": baseline.created_at.isoformat(),
        "schema_version": baseline.schema_version,
        "model_version": baseline.model_version,
        "config_fingerprint": baseline.config_fingerprint,
        "replay_report_fingerprint": baseline.replay_report_fingerprint,
        "baseline_fingerprint": baseline.baseline_fingerprint,
        "creation_reason": baseline.creation_reason,
        "replay_phase1_ready": baseline.replay_phase1_ready,
        "replay_roi": baseline.replay_roi,
        "replay_average_clv": baseline.replay_average_clv,
        "replay_average_edge": baseline.replay_average_edge,
        "replay_average_source_quality": baseline.replay_average_source_quality,
        "replay_calibration_gap": baseline.replay_calibration_gap,
        "replay_bet_count": baseline.replay_bet_count,
        "live_runs_considered": baseline.live_runs_considered,
        "live_average_prediction_count": baseline.live_average_prediction_count,
        "live_average_active_bet_rate": baseline.live_average_active_bet_rate,
        "live_average_skip_rate": baseline.live_average_skip_rate,
        "live_average_source_quality": baseline.live_average_source_quality,
        "live_average_expected_value": baseline.live_average_expected_value,
        "live_average_edge": baseline.live_average_edge,
        "live_average_clv": baseline.live_average_clv,
        "live_average_provider_degradation_rate": baseline.live_average_provider_degradation_rate,
        "live_schedule_fallback_rate": baseline.live_schedule_fallback_rate,
    }


def evaluate_baseline_refresh(
    baseline: BaselineSnapshot,
    *,
    replay_report_path: Path,
    model_version: str,
    force_refresh: bool = False,
) -> BaselineRefreshDecision:
    current_config_fingerprint = build_phase3_config_fingerprint(model_version)
    current_replay_fingerprint = fingerprint_file(replay_report_path)

    if force_refresh:
        return BaselineRefreshDecision("refresh", "operator_forced_refresh", False)
    if baseline.schema_version != PHASE3_BASELINE_SCHEMA_VERSION:
        return BaselineRefreshDecision("refresh", "baseline_schema_version_changed", False)
    if baseline.model_version != model_version:
        return BaselineRefreshDecision("refresh", "model_version_changed", False)
    if baseline.config_fingerprint != current_config_fingerprint:
        action = "refresh" if PHASE3_AUTO_REFRESH_BASELINE else "reject"
        return BaselineRefreshDecision(action, "config_fingerprint_changed", False)
    if baseline.replay_report_fingerprint != current_replay_fingerprint:
        action = "refresh" if PHASE3_AUTO_REFRESH_BASELINE else "reject"
        return BaselineRefreshDecision(action, "replay_report_changed", False)
    return BaselineRefreshDecision("reuse", "baseline_compatible", True)


def build_phase3_config_fingerprint(model_version: str) -> str:
    payload = {
        "schema_version": PHASE3_BASELINE_SCHEMA_VERSION,
        "model_version": model_version,
        "market_unlock_policy": PHASE3_MARKET_UNLOCK_POLICY,
        "market_unlock_min_sample": PHASE3_MARKET_UNLOCK_MIN_SAMPLE,
        "analyst_logging_enabled": PHASE3_ANALYST_LOGGING_ENABLED,
        "auto_refresh_baseline": PHASE3_AUTO_REFRESH_BASELINE,
        "drift_window_runs": PHASE3_DRIFT_WINDOW_RUNS,
        "min_graded_picks_for_retrain": PHASE3_MIN_GRADED_PICKS_FOR_RETRAIN,
        "min_live_runs_for_drift": PHASE3_MIN_LIVE_RUNS_FOR_DRIFT,
        "max_provider_degradation_rate": PHASE3_MAX_PROVIDER_DEGRADATION_RATE,
        "max_roi_delta": PHASE3_MAX_ROI_DELTA,
        "max_clv_delta": PHASE3_MAX_CLV_DELTA,
        "max_calibration_gap_delta": PHASE3_MAX_CALIBRATION_GAP_DELTA,
        "max_skip_rate_delta": PHASE3_MAX_SKIP_RATE_DELTA,
        "max_active_bet_rate_delta": PHASE3_MAX_ACTIVE_BET_RATE_DELTA,
        "max_source_quality_delta": PHASE3_MAX_SOURCE_QUALITY_DELTA,
        "max_edge_delta": PHASE3_MAX_EDGE_DELTA,
    }
    return fingerprint_payload(payload)


def fingerprint_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint_payload(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _parse_run_id(run_id: str) -> datetime:
    return datetime.strptime(run_id.replace("live-", ""), "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
