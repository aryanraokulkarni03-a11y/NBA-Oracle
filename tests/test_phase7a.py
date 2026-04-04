from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from nba_oracle.api.routes.picks import _build_accuracy_summary
from nba_oracle.api.routes.today import _partition_upcoming_predictions
from nba_oracle.runtime.prediction_views import load_latest_prediction_views_by_game


def _write_run(
    root: Path,
    run_id: str,
    *,
    predictions: list[dict[str, object]],
    snapshots: list[dict[str, object]],
) -> None:
    run_dir = root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "predictions.json").write_text(
        json.dumps({"predictions": predictions}, indent=2),
        encoding="utf-8",
    )
    (run_dir / "snapshots.json").write_text(
        json.dumps({"snapshots": snapshots}, indent=2),
        encoding="utf-8",
    )


class Phase7ATests(unittest.TestCase):
    def test_load_latest_prediction_views_by_game_ignores_synthetic_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            runtime_dir = Path(tmp_dir)
            _write_run(
                runtime_dir,
                "live-20260404T100000Z",
                predictions=[
                    {
                        "game_id": "2026-04-04-was-mia",
                        "selected_team": "Miami Heat",
                        "decision": "SKIP",
                    }
                ],
                snapshots=[
                    {
                        "game_id": "2026-04-04-was-mia",
                        "away_team": "Washington Wizards",
                        "home_team": "Miami Heat",
                        "decision_time": "2026-04-04T10:00:00+00:00",
                        "tipoff_time": "2099-04-04T19:00:00+00:00",
                        "sources": [{"source_version": "scoreboard-v1"}],
                        "market": {"reference_bookmaker": "betmgm"},
                    }
                ],
            )
            _write_run(
                runtime_dir,
                "live-20260404T110000Z",
                predictions=[
                    {
                        "game_id": "2026-04-04-was-mia",
                        "selected_team": "Washington Wizards",
                        "decision": "BET",
                    }
                ],
                snapshots=[
                    {
                        "game_id": "2026-04-04-was-mia",
                        "away_team": "Washington Wizards",
                        "home_team": "Miami Heat",
                        "decision_time": "2026-04-04T11:00:00+00:00",
                        "tipoff_time": "2099-04-04T19:00:00+00:00",
                        "sources": [{"source_version": "test-v1"}],
                        "market": {"reference_bookmaker": "reference"},
                    }
                ],
            )

            views = load_latest_prediction_views_by_game(runtime_dir=runtime_dir)

        self.assertEqual(len(views), 1)
        self.assertEqual(views[0]["selected_team"], "Miami Heat")
        self.assertEqual(views[0]["matchup_label"], "Washington Wizards at Miami Heat")
        self.assertEqual(views[0]["reference_bookmaker"], "betmgm")

    def test_partition_upcoming_predictions_splits_actionable_and_next_up(self) -> None:
        payload = [
            {
                "game_id": "g-actionable-1",
                "tipoff_time": "2099-04-04T19:00:00+00:00",
                "matchup_label": "A at B",
            },
            {
                "game_id": "g-actionable-2",
                "tipoff_time": "2099-04-04T21:00:00+00:00",
                "matchup_label": "C at D",
            },
            {
                "game_id": "g-next-up",
                "tipoff_time": "2099-04-05T19:00:00+00:00",
                "matchup_label": "E at F",
            },
            {
                "game_id": "g-completed",
                "tipoff_time": "2099-04-04T18:00:00+00:00",
                "matchup_label": "X at Y",
                "actual_winner": "Y",
            },
        ]

        with patch("nba_oracle.api.routes.today.load_latest_prediction_views_by_game", return_value=payload):
            actionable, next_up = _partition_upcoming_predictions()

        self.assertEqual([item["game_id"] for item in actionable], ["g-actionable-1", "g-actionable-2"])
        self.assertEqual([item["game_id"] for item in next_up], ["g-next-up"])

    def test_accuracy_summary_reports_overall_bet_and_lean_truth(self) -> None:
        summary = _build_accuracy_summary(
            [
                {"decision": "BET", "won": True},
                {"decision": "BET", "won": False},
                {"decision": "LEAN", "won": True},
                {"decision": "SKIP", "won": True},
            ]
        )

        self.assertEqual(summary["graded_count"], 4)
        self.assertEqual(summary["correct_count"], 3)
        self.assertAlmostEqual(summary["overall_accuracy"], 0.75)
        self.assertEqual(summary["bet_count"], 2)
        self.assertEqual(summary["bet_correct"], 1)
        self.assertAlmostEqual(summary["bet_accuracy"], 0.5)
        self.assertEqual(summary["lean_count"], 1)
        self.assertEqual(summary["lean_correct"], 1)
        self.assertAlmostEqual(summary["lean_accuracy"], 1.0)
        self.assertEqual(summary["skip_count"], 1)


if __name__ == "__main__":
    unittest.main()
