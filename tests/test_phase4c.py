from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from nba_oracle.runtime.health import build_health_snapshot
from nba_oracle.runtime.startup import build_startup_sanity_report


class Phase4CTests(unittest.TestCase):
    def test_startup_sanity_reports_warning_when_hosted_values_are_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            reports = root / "reports"
            runtime = root / "runtime"
            runtime_state = root / "runtime_state"

            with (
                patch("nba_oracle.runtime.startup.ROOT_DIR", root),
                patch("nba_oracle.runtime.startup.REPORTS_DIR", reports),
                patch("nba_oracle.runtime.startup.RUNTIME_DIR", runtime),
                patch("nba_oracle.runtime.startup.RUNTIME_STATE_DIR", runtime_state),
                patch("nba_oracle.runtime.startup.SUPABASE_URL", "https://example.supabase.co"),
                patch("nba_oracle.runtime.startup.SUPABASE_SERVICE_ROLE_KEY", "service-role"),
                patch("nba_oracle.runtime.startup.ODDS_API_KEY", "odds-key"),
                patch("nba_oracle.runtime.startup.ORACLE_PASSWORD_HASH", "password-hash"),
                patch("nba_oracle.runtime.startup.ORACLE_SECRET_KEY", "secret-key"),
                patch("nba_oracle.runtime.startup.TELEGRAM_BOT_TOKEN", "telegram"),
                patch("nba_oracle.runtime.startup.TELEGRAM_CHAT_ID", "123"),
                patch("nba_oracle.runtime.startup.GMAIL_SENDER", "oracle@example.com"),
                patch("nba_oracle.runtime.startup.GMAIL_APP_PASSWORD", "gmail-secret"),
                patch("nba_oracle.runtime.startup.GMAIL_RECIPIENT", "oracle@example.com"),
                patch("nba_oracle.runtime.startup.ORACLE_PUBLIC_API_BASE_URL", ""),
                patch("nba_oracle.runtime.startup.ORACLE_ALLOWED_ORIGINS", ("http://127.0.0.1:3000",)),
            ):
                report = build_startup_sanity_report()

        self.assertEqual(report["status"], "warning")
        self.assertGreaterEqual(report["warning_count"], 1)
        self.assertTrue(any(item["name"] == "public_api_base_url" for item in report["checks"]))

    def test_health_snapshot_includes_startup_and_notifications(self) -> None:
        with (
            patch("nba_oracle.runtime.health.load_runtime_state", return_value={"updated_at": "2026-04-04T00:00:00+00:00"}),
            patch("nba_oracle.runtime.health._load_json", return_value={}),
            patch(
                "nba_oracle.runtime.health.build_startup_sanity_report",
                return_value={"status": "ready", "checks": [], "failed_count": 0, "warning_count": 0},
            ),
            patch(
                "nba_oracle.runtime.health.load_notification_events",
                return_value=[{"event_id": "notify-1", "channel": "telegram", "success": True}],
            ),
        ):
            snapshot = build_health_snapshot()

        self.assertEqual(snapshot["startup"]["status"], "ready")
        self.assertEqual(snapshot["notifications"]["latest_events"][0]["event_id"], "notify-1")


if __name__ == "__main__":
    unittest.main()
