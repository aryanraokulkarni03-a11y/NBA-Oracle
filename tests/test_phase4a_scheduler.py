from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from nba_oracle.runtime.meta_scheduler import plan_scheduler_jobs, run_scheduler_once


class Phase4ASchedulerTests(unittest.TestCase):
    def test_plan_scheduler_marks_live_slate_due_when_tipoff_is_near(self) -> None:
        now = datetime(2026, 4, 4, 16, 0, tzinfo=timezone.utc)
        with patch("nba_oracle.runtime.meta_scheduler.load_runtime_state", return_value={"last_jobs": {}}), patch(
            "nba_oracle.runtime.meta_scheduler.load_latest_live_report",
            return_value={},
        ), patch(
            "nba_oracle.runtime.meta_scheduler.load_latest_outcome_report",
            return_value={},
        ), patch(
            "nba_oracle.runtime.meta_scheduler.load_latest_stability_report",
            return_value={},
        ), patch(
            "nba_oracle.runtime.meta_scheduler.load_latest_learning_report",
            return_value={},
        ), patch(
            "nba_oracle.runtime.meta_scheduler._load_upcoming_tipoffs",
            return_value=[datetime(2026, 4, 4, 18, 0, tzinfo=timezone.utc)],
        ):
            decisions = plan_scheduler_jobs(now)

        decision_map = {item.job_name: item for item in decisions}
        self.assertTrue(decision_map["live_slate"].due)
        self.assertIn("target_120", decision_map["live_slate"].reason)

    def test_plan_scheduler_skips_live_slate_outside_two_hour_window(self) -> None:
        now = datetime(2026, 4, 4, 16, 0, tzinfo=timezone.utc)
        with patch("nba_oracle.runtime.meta_scheduler.load_runtime_state", return_value={"last_jobs": {}}), patch(
            "nba_oracle.runtime.meta_scheduler.load_latest_live_report",
            return_value={},
        ), patch(
            "nba_oracle.runtime.meta_scheduler.load_latest_outcome_report",
            return_value={},
        ), patch(
            "nba_oracle.runtime.meta_scheduler.load_latest_stability_report",
            return_value={},
        ), patch(
            "nba_oracle.runtime.meta_scheduler.load_latest_learning_report",
            return_value={},
        ), patch(
            "nba_oracle.runtime.meta_scheduler._load_upcoming_tipoffs",
            return_value=[datetime(2026, 4, 4, 20, 0, tzinfo=timezone.utc)],
        ):
            decisions = plan_scheduler_jobs(now)

        decision_map = {item.job_name: item for item in decisions}
        self.assertFalse(decision_map["live_slate"].due)

    def test_run_scheduler_once_executes_due_jobs(self) -> None:
        now = datetime(2026, 4, 4, 16, 0, tzinfo=timezone.utc)
        with patch(
            "nba_oracle.runtime.meta_scheduler.plan_scheduler_jobs",
            return_value=(
                type("Decision", (), {"job_name": "live_slate", "due": True, "reason": "test", "last_finished_at": None})(),
                type("Decision", (), {"job_name": "grade_outcomes", "due": False, "reason": "skip", "last_finished_at": None})(),
                type("Decision", (), {"job_name": "review_stability", "due": False, "reason": "skip", "last_finished_at": None})(),
                type("Decision", (), {"job_name": "learning_review", "due": False, "reason": "skip", "last_finished_at": None})(),
                type("Decision", (), {"job_name": "midnight_confirmation", "due": False, "reason": "skip", "last_finished_at": None})(),
            ),
        ), patch(
            "nba_oracle.runtime.meta_scheduler.run_live_slate_job",
            return_value={"run_id": "live-test"},
        ):
            result = run_scheduler_once(now=now)

        self.assertEqual(len(result["executed_jobs"]), 1)
        self.assertEqual(result["executed_jobs"][0]["job_name"], "live_slate")

    def test_learning_scheduler_uses_learning_threshold(self) -> None:
        now = datetime(2026, 4, 4, 16, 0, tzinfo=timezone.utc)
        with patch("nba_oracle.runtime.meta_scheduler.load_runtime_state", return_value={"last_jobs": {}}), patch(
            "nba_oracle.runtime.meta_scheduler.load_latest_live_report",
            return_value={},
        ), patch(
            "nba_oracle.runtime.meta_scheduler.load_latest_outcome_report",
            return_value={},
        ), patch(
            "nba_oracle.runtime.meta_scheduler.load_latest_stability_report",
            return_value={},
        ), patch(
            "nba_oracle.runtime.meta_scheduler.load_latest_learning_report",
            return_value={"graded_prediction_count": 100},
        ), patch(
            "nba_oracle.runtime.meta_scheduler._load_upcoming_tipoffs",
            return_value=[],
        ):
            decisions = plan_scheduler_jobs(now)

        decision_map = {item.job_name: item for item in decisions}
        self.assertTrue(decision_map["learning_review"].due)


if __name__ == "__main__":
    unittest.main()
