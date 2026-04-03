from __future__ import annotations

from pathlib import Path

from nba_oracle.config import DEFAULT_JSON_REPORT_PATH, PHASE3_DRIFT_WINDOW_RUNS, RUNTIME_DIR, STABILITY_DIR
from nba_oracle.models_registry.catalog import build_model_catalog
from nba_oracle.stability.baseline import (
    build_phase3_baseline,
    load_saved_phase3_baseline,
    load_recent_live_runs,
    save_phase3_baseline,
)
from nba_oracle.stability.drift import assess_drift
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
) -> tuple[StabilityReviewResult, Path, Path, Path]:
    resolved_baseline_path = baseline_output_path or (STABILITY_DIR / "phase3_baseline.json")
    if resolved_baseline_path.exists():
        baseline = load_saved_phase3_baseline(resolved_baseline_path)
        baseline_path = resolved_baseline_path
    else:
        baseline = build_phase3_baseline(
            replay_report_path=replay_report_path,
            runtime_dir=runtime_dir,
            limit=limit or PHASE3_DRIFT_WINDOW_RUNS,
        )
        baseline_path = save_phase3_baseline(
            baseline,
            path=resolved_baseline_path,
        )

    live_runs = load_recent_live_runs(runtime_dir, limit=limit or PHASE3_DRIFT_WINDOW_RUNS)
    actionable_live_runs = tuple(run for run in live_runs if run.prediction_count > 0)
    model_catalog = build_model_catalog()
    drift = assess_drift(baseline, actionable_live_runs)
    timing = assess_timing(actionable_live_runs)
    readiness = assess_readiness(actionable_live_runs, model_catalog)
    result = StabilityReviewResult(
        baseline=baseline,
        live_runs=live_runs,
        drift=drift,
        timing=timing,
        readiness=readiness,
        model_catalog=model_catalog,
        baseline_path=str(baseline_path),
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
