from __future__ import annotations

import unittest
from unittest.mock import patch

from nba_oracle.notifications.telegram import handle_telegram_command


class Phase4ANotificationTests(unittest.TestCase):
    def test_health_command_returns_health_digest(self) -> None:
        with patch(
            "nba_oracle.notifications.telegram.build_health_snapshot",
            return_value={
                "latest_live": {"run_id": "live-test", "prediction_count": 3},
                "latest_stability": {"drift_status": "stable", "timing_status": "healthy"},
                "latest_learning": {"status": "candidate_review_ready"},
                "latest_outcomes": {"pending_unfinished": 1},
            },
        ):
            message = handle_telegram_command("/health")
        self.assertIn("NBA Oracle Health", message)
        self.assertIn("live-test", message)

    def test_unknown_command_returns_help(self) -> None:
        message = handle_telegram_command("/unknown")
        self.assertIn("Supported", message)


if __name__ == "__main__":
    unittest.main()
