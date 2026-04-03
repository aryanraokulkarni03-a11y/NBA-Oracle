from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from nba_oracle.models_registry.catalog import build_model_catalog
from nba_oracle.runs.review_stability import review_stability
from nba_oracle.stability.baseline import (
    BaselineSnapshot,
    build_phase3_config_fingerprint,
    load_recent_live_runs,
)
from nba_oracle.stability.drift import assess_drift
from nba_oracle.stability.readiness import assess_readiness


class Phase3Tests(unittest.TestCase):
    def test_review_stability_generates_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            replay_path = root / "replay.json"
            runtime_dir = root / "runtime"
            runtime_dir.mkdir()

            replay_path.write_text(
                json.dumps(
                    {
                        "phase1_ready": True,
                        "roi": 0.12,
                        "average_clv": 0.015,
                        "average_edge": 0.028,
                        "average_source_quality": 0.81,
                        "bet_count": 8,
                        "calibration_assessment": {"mean_absolute_gap": 0.07},
                    }
                ),
                encoding="utf-8",
            )
            _write_live_run(runtime_dir, "live-20260403T100000Z", prediction_count=3, active_count=2, graded=True)
            _write_live_run(runtime_dir, "live-20260403T110000Z", prediction_count=3, active_count=2, graded=True)
            _write_live_run(runtime_dir, "live-20260403T120000Z", prediction_count=3, active_count=2, graded=True)

            result, baseline_path, md_path, json_path = review_stability(
                replay_report_path=replay_path,
                runtime_dir=runtime_dir,
                limit=3,
                baseline_output_path=root / "phase3_baseline.json",
                markdown_report_path=root / "phase3_report.md",
                json_report_path=root / "phase3_report.json",
            )
            self.assertTrue(baseline_path.exists())
            self.assertTrue(md_path.exists())
            self.assertTrue(json_path.exists())
            self.assertIn(result.drift.status, {"stable", "insufficient_outcomes", "warning"})
            self.assertEqual(result.timing.status, "healthy")
            self.assertEqual(result.readiness.analyst.status, "contained")
            self.assertGreaterEqual(len(result.stored_paths), 4)

    def test_drift_flags_large_skip_rate_shift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            runtime_dir = Path(tmp_dir) / "runtime"
            runtime_dir.mkdir()
            _write_live_run(runtime_dir, "live-20260403T100000Z", prediction_count=4, active_count=0, graded=True)
            _write_live_run(runtime_dir, "live-20260403T110000Z", prediction_count=4, active_count=0, graded=True)
            _write_live_run(runtime_dir, "live-20260403T120000Z", prediction_count=4, active_count=0, graded=True)

            baseline = BaselineSnapshot(
                created_at=datetime(2026, 4, 3, 9, 0, tzinfo=timezone.utc),
                schema_version="1.1",
                model_version="phase2-deterministic-v1",
                config_fingerprint=build_phase3_config_fingerprint("phase2-deterministic-v1"),
                replay_report_fingerprint="replay-fingerprint",
                baseline_fingerprint="baseline-fingerprint",
                creation_reason="test",
                replay_phase1_ready=True,
                replay_roi=0.10,
                replay_average_clv=0.012,
                replay_average_edge=0.03,
                replay_average_source_quality=0.82,
                replay_calibration_gap=0.07,
                replay_bet_count=7,
                live_runs_considered=3,
                live_average_prediction_count=4.0,
                live_average_active_bet_rate=0.5,
                live_average_skip_rate=0.5,
                live_average_source_quality=0.82,
                live_average_expected_value=0.02,
                live_average_edge=0.03,
                live_average_clv=0.01,
                live_average_provider_degradation_rate=0.0,
                live_schedule_fallback_rate=0.0,
            )
            live_runs = load_recent_live_runs(runtime_dir, limit=3)
            drift = assess_drift(baseline, live_runs)

        self.assertIn(drift.status, {"warning", "retrain_review"})
        self.assertTrue(any(signal.name == "active_bet_rate" and signal.triggered for signal in drift.signals))
        self.assertTrue(any(signal.name == "skip_rate" and signal.triggered for signal in drift.signals))

    def test_readiness_keeps_non_moneyline_markets_locked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            runtime_dir = Path(tmp_dir) / "runtime"
            runtime_dir.mkdir()
            _write_live_run(runtime_dir, "live-20260403T100000Z", prediction_count=2, active_count=1, graded=True)
            live_runs = load_recent_live_runs(runtime_dir, limit=1)
            baseline = BaselineSnapshot(
                created_at=datetime(2026, 4, 3, 9, 0, tzinfo=timezone.utc),
                schema_version="1.1",
                model_version="phase2-deterministic-v1",
                config_fingerprint=build_phase3_config_fingerprint("phase2-deterministic-v1"),
                replay_report_fingerprint="replay-fingerprint",
                baseline_fingerprint="baseline-fingerprint",
                creation_reason="test",
                replay_phase1_ready=True,
                replay_roi=0.10,
                replay_average_clv=0.012,
                replay_average_edge=0.03,
                replay_average_source_quality=0.82,
                replay_calibration_gap=0.07,
                replay_bet_count=7,
                live_runs_considered=1,
                live_average_prediction_count=2.0,
                live_average_active_bet_rate=0.5,
                live_average_skip_rate=0.5,
                live_average_source_quality=0.82,
                live_average_expected_value=0.02,
                live_average_edge=0.03,
                live_average_clv=0.01,
                live_average_provider_degradation_rate=0.0,
                live_schedule_fallback_rate=0.0,
            )
            drift = assess_drift(baseline, live_runs)

        readiness = assess_readiness(
            "review-id",
            live_runs,
            build_model_catalog(),
            baseline,
            drift,
        )
        moneyline = next(item for item in readiness.markets if item.market == "moneyline")
        totals = next(item for item in readiness.markets if item.market == "totals")
        props = next(item for item in readiness.markets if item.market == "props")

        self.assertTrue(moneyline.active)
        self.assertFalse(totals.active)
        self.assertFalse(props.active)
        self.assertEqual(totals.status, "locked")
        self.assertEqual(props.status, "locked")


def _write_live_run(
    runtime_dir: Path,
    run_id: str,
    *,
    prediction_count: int,
    active_count: int,
    graded: bool,
) -> None:
    run_dir = runtime_dir / run_id
    run_dir.mkdir(parents=True)
    source_time = run_id.replace("live-", "")
    source_iso = (
        f"{source_time[0:4]}-{source_time[4:6]}-{source_time[6:8]}T"
        f"{source_time[9:11]}:{source_time[11:13]}:{source_time[13:15]}+00:00"
    )
    provider_payload = {
        "name": "nba_schedule_with_odds_fallback",
        "kind": "schedule",
        "source_time": source_iso,
        "source_version": "test-v1",
        "success": True,
        "degraded": False,
        "error": None,
    }
    (run_dir / "provider_schedule.json").write_text(
        json.dumps(provider_payload, indent=2),
        encoding="utf-8",
    )

    predictions = []
    for index in range(prediction_count):
        decision = "BET" if index < active_count else "SKIP"
        selected_team = "Boston Celtics"
        actual_winner = selected_team if graded else None
        predictions.append(
            {
                "game_id": f"{run_id}-game-{index}",
                "selected_team": selected_team,
                "stake_american": -120 if decision == "BET" else 105,
                "decision": decision,
                "model_probability": 0.61 if decision == "BET" else 0.54,
                "expected_value": 0.031 if decision == "BET" else -0.004,
                "edge_vs_stake": 0.035 if decision == "BET" else -0.002,
                "source_quality": 0.82,
                "stake_probability": 0.58,
                "best_probability": 0.57,
                "close_probability": 0.60,
                "market_timestamp": source_iso,
                "source_scores": [
                    {
                        "name": "the_odds_api",
                        "kind": "odds",
                        "age_minutes": 12.0,
                        "freshness": 0.9,
                        "trust": 0.95,
                        "quality": 0.92,
                        "signal_delta": 0.0,
                    },
                    {
                        "name": "espn_injuries",
                        "kind": "injury",
                        "age_minutes": 45.0,
                        "freshness": 0.8,
                        "trust": 0.82,
                        "quality": 0.81,
                        "signal_delta": 0.01,
                    },
                ],
                "reasons": ["all_gates_passed"] if decision == "BET" else ["edge_too_small"],
                "actual_winner": actual_winner,
            }
        )

    (run_dir / "predictions.json").write_text(
        json.dumps({"predictions": predictions}, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
