from __future__ import annotations

import unittest
from unittest.mock import patch

try:
    from fastapi.testclient import TestClient
except ImportError:  # pragma: no cover - dependency installed during Phase 4A setup
    TestClient = None

from nba_oracle.auth import hash_password


@unittest.skipIf(TestClient is None, "FastAPI test dependencies are not installed")
class Phase4AApiTests(unittest.TestCase):
    def setUp(self) -> None:
        from nba_oracle.api.app import build_app

        self.client = TestClient(build_app())
        self.password_hash = hash_password("oracle-secret")
        self.secret_key = "phase4a-test-secret-key-material-0123456789"

        self.patcher_auth_hash = patch("nba_oracle.api.routes.auth.ORACLE_PASSWORD_HASH", self.password_hash)
        self.patcher_dep_hash = patch("nba_oracle.api.dependencies.ORACLE_PASSWORD_HASH", self.password_hash)
        self.patcher_secret = patch("nba_oracle.auth.ORACLE_SECRET_KEY", self.secret_key)
        self.patcher_login_allowed = patch(
            "nba_oracle.api.routes.auth.check_login_allowed",
            return_value=type("Decision", (), {"allowed": True, "reason": "allowed"})(),
        )
        self.patcher_auth_rate_limit = patch(
            "nba_oracle.api.routes.auth.check_rate_limit",
            return_value=type("Decision", (), {"allowed": True, "reason": "allowed", "retry_after_seconds": 0})(),
        )
        self.patcher_clear_failed = patch("nba_oracle.api.routes.auth.clear_failed_logins")
        self.patcher_record_failed = patch("nba_oracle.api.routes.auth.record_failed_login")
        self.patcher_log_event = patch("nba_oracle.api.routes.auth.log_auth_event")
        self.patcher_rate_limit = patch(
            "nba_oracle.api.dependencies.check_rate_limit",
            return_value=type("Decision", (), {"allowed": True, "reason": "allowed", "retry_after_seconds": 0})(),
        )

        for item in (
            self.patcher_auth_hash,
            self.patcher_dep_hash,
            self.patcher_secret,
            self.patcher_login_allowed,
            self.patcher_auth_rate_limit,
            self.patcher_clear_failed,
            self.patcher_record_failed,
            self.patcher_log_event,
            self.patcher_rate_limit,
        ):
            item.start()
            self.addCleanup(item.stop)

    def test_health_route_is_public(self) -> None:
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertIn("api", response.json())

    def test_login_and_protected_today_route(self) -> None:
        login_response = self.client.post("/api/auth/login", json={"password": "oracle-secret"})
        self.assertEqual(login_response.status_code, 200)
        token = login_response.json()["access_token"]

        with patch(
            "nba_oracle.api.routes.today.load_latest_live_report",
            return_value={"run_id": "live-test", "predictions": [{"game_id": "g-1"}], "providers": []},
        ):
            today_response = self.client.get(
                "/api/today",
                headers={"Authorization": f"Bearer {token}"},
            )
        self.assertEqual(today_response.status_code, 200)
        self.assertEqual(today_response.json()["run_id"], "live-test")

    def test_operator_scheduler_route_requires_auth(self) -> None:
        response = self.client.post("/api/operator/run-scheduler-once", json={"force": False})
        self.assertEqual(response.status_code, 401)

    def test_rate_limit_returns_429(self) -> None:
        self.patcher_rate_limit.stop()
        self.patcher_auth_rate_limit.stop()
        with patch(
            "nba_oracle.api.routes.auth.check_rate_limit",
            return_value=type("Decision", (), {"allowed": False, "reason": "rate_limited", "retry_after_seconds": 12})(),
        ):
            response = self.client.post("/api/auth/login", json={"password": "oracle-secret"})
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.headers["Retry-After"], "12")


if __name__ == "__main__":
    unittest.main()
