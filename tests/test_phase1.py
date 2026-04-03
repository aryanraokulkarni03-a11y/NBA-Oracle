from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from nba_oracle.config import DEFAULT_FIXTURE_PATH
from nba_oracle.predictor import evaluate_game
from nba_oracle.replay import run_replay
from nba_oracle.snapshots import SnapshotValidationError, load_game_snapshots


class Phase1Tests(unittest.TestCase):
    def test_fixture_loads(self) -> None:
        games = load_game_snapshots(DEFAULT_FIXTURE_PATH)
        self.assertGreaterEqual(len(games), 1)

    def test_replay_is_deterministic(self) -> None:
        first = run_replay(DEFAULT_FIXTURE_PATH)
        second = run_replay(DEFAULT_FIXTURE_PATH)
        self.assertEqual(first.bet_count, second.bet_count)
        self.assertEqual(first.roi, second.roi)
        self.assertEqual(first.skip_reasons, second.skip_reasons)
        self.assertEqual(
            first.calibration_assessment.status,
            second.calibration_assessment.status,
        )

    def test_predictor_returns_skip_when_price_gap_is_bad(self) -> None:
        game = next(
            item for item in load_game_snapshots(DEFAULT_FIXTURE_PATH)
            if item.game_id == "2026-04-03-dal-min"
        )
        result = evaluate_game(game)
        self.assertEqual(result.decision, "SKIP")
        self.assertIn("stake_price_not_competitive", result.reasons)

    def test_replay_calibration_gate_passes_on_default_fixture(self) -> None:
        report = run_replay(DEFAULT_FIXTURE_PATH)
        self.assertTrue(report.phase1_ready)
        self.assertEqual(report.calibration_assessment.status, "PASS")
        self.assertGreaterEqual(report.calibration_assessment.actionable_count, 6)
        self.assertGreaterEqual(len(report.source_audit), 4)

    def test_future_source_time_is_rejected(self) -> None:
        payload = json.loads(DEFAULT_FIXTURE_PATH.read_text(encoding="utf-8"))
        payload["games"][0]["sources"][0]["source_time"] = "2026-04-03T15:31:00+00:00"
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "bad_fixture.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(SnapshotValidationError):
                load_game_snapshots(path)


if __name__ == "__main__":
    unittest.main()
