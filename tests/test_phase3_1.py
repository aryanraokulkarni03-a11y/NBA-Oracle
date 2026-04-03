from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from nba_oracle.runs.review_stability import review_stability


class Phase31Tests(unittest.TestCase):
    def test_review_refreshes_incompatible_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            replay_path = root / "replay.json"
            runtime_dir = root / "runtime"
            runtime_dir.mkdir()
            baseline_path = root / "phase3_baseline.json"

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
            baseline_path.write_text(
                json.dumps(
                    {
                        "created_at": "2026-04-01T00:00:00+00:00",
                        "schema_version": "1.0",
                        "model_version": "phase2-deterministic-v1",
                        "config_fingerprint": "old",
                        "replay_report_fingerprint": "old",
                        "baseline_fingerprint": "old",
                        "creation_reason": "legacy",
                        "replay_phase1_ready": True,
                        "replay_roi": 0.1,
                        "replay_average_clv": 0.01,
                        "replay_average_edge": 0.02,
                        "replay_average_source_quality": 0.7,
                        "replay_calibration_gap": 0.2,
                        "replay_bet_count": 5,
                        "live_runs_considered": 0,
                        "live_average_prediction_count": 0.0,
                        "live_average_active_bet_rate": 0.0,
                        "live_average_skip_rate": 0.0,
                        "live_average_source_quality": 0.0,
                        "live_average_expected_value": 0.0,
                        "live_average_edge": 0.0,
                        "live_average_clv": 0.0,
                        "live_average_provider_degradation_rate": 0.0,
                        "live_schedule_fallback_rate": 0.0,
                    }
                ),
                encoding="utf-8",
            )

            result, refreshed_baseline_path, _, _ = review_stability(
                replay_report_path=replay_path,
                runtime_dir=runtime_dir,
                baseline_output_path=baseline_path,
                markdown_report_path=root / "report.md",
                json_report_path=root / "report.json",
            )

            refreshed = json.loads(refreshed_baseline_path.read_text(encoding="utf-8"))
            self.assertEqual(result.baseline_action, "refresh")
            self.assertEqual(refreshed["schema_version"], "1.1")
            self.assertTrue(refreshed["creation_reason"].startswith("automatic_refresh"))

    def test_review_records_analyst_disagreements(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            replay_path = root / "replay.json"
            runtime_dir = root / "runtime"
            runtime_dir.mkdir()
            analyst_payload_path = root / "analyst.json"

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
            _write_live_run(runtime_dir, "live-20260403T100000Z")
            analyst_payload_path.write_text(
                json.dumps(
                    {
                        "predictions": [
                            {"game_id": "live-20260403T100000Z-game-0", "decision": "BET"},
                            {"game_id": "live-20260403T100000Z-game-1", "decision": "SKIP"},
                        ]
                    }
                ),
                encoding="utf-8",
            )

            result, _, _, _ = review_stability(
                replay_report_path=replay_path,
                runtime_dir=runtime_dir,
                limit=1,
                baseline_output_path=root / "phase3_baseline.json",
                markdown_report_path=root / "report.md",
                json_report_path=root / "report.json",
                analyst_payload_path=analyst_payload_path,
            )

            self.assertEqual(result.readiness.analyst.disagreement_count, 1)
            self.assertEqual(result.readiness.analyst_logs[0].final_authority, "predictor")


def _write_live_run(runtime_dir: Path, run_id: str) -> None:
    run_dir = runtime_dir / run_id
    run_dir.mkdir(parents=True)
    source_iso = "2026-04-03T10:00:00+00:00"
    (run_dir / "provider_schedule.json").write_text(
        json.dumps(
            {
                "name": "nba_schedule_with_odds_fallback",
                "kind": "schedule",
                "source_time": source_iso,
                "source_version": "test-v1",
                "success": True,
                "degraded": False,
                "error": None,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (run_dir / "predictions.json").write_text(
        json.dumps(
            {
                "predictions": [
                    {
                        "game_id": f"{run_id}-game-0",
                        "selected_team": "Boston Celtics",
                        "stake_american": -120,
                        "decision": "SKIP",
                        "model_probability": 0.54,
                        "expected_value": -0.01,
                        "edge_vs_stake": -0.01,
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
                            }
                        ],
                        "reasons": ["edge_too_small"],
                        "actual_winner": "Boston Celtics",
                    },
                    {
                        "game_id": f"{run_id}-game-1",
                        "selected_team": "Boston Celtics",
                        "stake_american": -120,
                        "decision": "SKIP",
                        "model_probability": 0.53,
                        "expected_value": -0.01,
                        "edge_vs_stake": -0.01,
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
                            }
                        ],
                        "reasons": ["edge_too_small"],
                        "actual_winner": "Boston Celtics",
                    },
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
