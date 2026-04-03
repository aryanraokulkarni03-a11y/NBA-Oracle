from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from nba_oracle.assembly.live_snapshot_builder import build_live_snapshots
from nba_oracle.config import DEFAULT_LIVE_BUNDLE_PATH
from nba_oracle.models import ProviderRecord, ProviderResponse
from nba_oracle.providers.injuries import InjuryProvider
from nba_oracle.providers.odds import OddsProvider
from nba_oracle.providers.schedule import ScheduleProvider
from nba_oracle.providers.sentiment import SentimentProvider
from nba_oracle.providers.stats import StatsProvider
from nba_oracle.runs.build_live_slate import build_live_slate


class Phase2Tests(unittest.TestCase):
    def test_build_live_slate_creates_predictions(self) -> None:
        result = build_live_slate(DEFAULT_LIVE_BUNDLE_PATH)
        self.assertEqual(len(result.snapshots), 3)
        self.assertEqual(len(result.predictions), 3)
        self.assertTrue(any(item.decision == "BET" for item in result.predictions))

    def test_sentiment_can_fail_without_stopping_slate_build(self) -> None:
        payload = json.loads(DEFAULT_LIVE_BUNDLE_PATH.read_text(encoding="utf-8"))
        payload["sentiment"]["success"] = False
        payload["sentiment"]["degraded"] = True
        payload["sentiment"]["error"] = "sentiment_down"
        payload["sentiment"]["records"] = []
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "bundle.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = build_live_slate(path)
            self.assertEqual(len(result.snapshots), 3)
            self.assertTrue(any(provider.kind == "sentiment" and provider.degraded for provider in result.providers))

    def test_live_mode_uses_provider_chain(self) -> None:
        decision_time = datetime(2026, 4, 5, 15, 30, tzinfo=timezone.utc)
        schedule = _provider_response(
            "schedule",
            "nba_scoreboard_live",
            decision_time,
            (
                {
                    "game_id": "2026-04-05-bos-nyk",
                    "away_team": "Boston Celtics",
                    "home_team": "New York Knicks",
                    "tipoff_time": "2026-04-05T17:30:00+00:00",
                },
            ),
        )
        odds = _provider_response(
            "odds",
            "the_odds_api",
            decision_time,
            (
                {
                    "game_id": "2026-04-05-bos-nyk",
                    "selected_team": "Boston Celtics",
                    "stake_american": -140,
                    "best_american": -135,
                    "close_american": -140,
                    "consensus_probability": 0.59,
                    "signal_delta": 0.0,
                },
            ),
            trust=0.95,
        )
        injuries = _provider_response(
            "injury",
            "espn_injuries",
            decision_time,
            (
                {
                    "game_id": "2026-04-05-bos-nyk",
                    "signal_delta": 0.015,
                    "summary": "Boston healthier",
                    "confirmation_level": "reported",
                },
            ),
            trust=0.85,
        )
        stats = _provider_response(
            "stats",
            "nba_team_estimated_metrics",
            decision_time,
            (
                {
                    "game_id": "2026-04-05-bos-nyk",
                    "signal_delta": 0.014,
                    "summary": "Boston net rating edge",
                    "rest_edge": 0,
                },
            ),
            trust=0.91,
        )
        sentiment = _provider_response("sentiment", "reddit_sentiment", decision_time, tuple(), success=False, degraded=True)

        with (
            patch.object(ScheduleProvider, "fetch_live", autospec=True, return_value=schedule) as schedule_fetch,
            patch.object(OddsProvider, "fetch_live", autospec=True, return_value=odds) as odds_fetch,
            patch.object(InjuryProvider, "fetch_live", autospec=True, return_value=injuries) as injury_fetch,
            patch.object(StatsProvider, "fetch_live", autospec=True, return_value=stats) as stats_fetch,
            patch.object(SentimentProvider, "fetch_live", autospec=True, return_value=sentiment) as sentiment_fetch,
        ):
            result = build_live_slate(use_live=True, decision_time=decision_time)

        self.assertEqual(len(result.snapshots), 1)
        self.assertEqual(len(result.predictions), 1)
        self.assertEqual(result.providers[0].kind, "schedule")
        self.assertEqual(schedule_fetch.call_args.args[1], decision_time)
        self.assertEqual(schedule_fetch.call_args.args[2], {})
        self.assertEqual(odds_fetch.call_args.args[2]["schedule"], schedule)
        self.assertEqual(injury_fetch.call_args.args[2]["odds"], odds)
        self.assertEqual(stats_fetch.call_args.args[2]["injury"], injuries)
        self.assertEqual(sentiment_fetch.call_args.args[2]["stats"], stats)

    def test_degraded_injury_provider_uses_placeholder_source(self) -> None:
        decision_time = datetime(2026, 4, 5, 15, 30, tzinfo=timezone.utc)
        schedule = _provider_response(
            "schedule",
            "nba_scoreboard_live",
            decision_time,
            (
                {
                    "game_id": "2026-04-05-bos-nyk",
                    "away_team": "Boston Celtics",
                    "home_team": "New York Knicks",
                    "tipoff_time": "2026-04-05T17:30:00+00:00",
                },
            ),
        )
        odds = _provider_response(
            "odds",
            "the_odds_api",
            decision_time,
            (
                {
                    "game_id": "2026-04-05-bos-nyk",
                    "selected_team": "Boston Celtics",
                    "stake_american": -140,
                    "best_american": -135,
                    "close_american": -140,
                    "consensus_probability": 0.59,
                    "signal_delta": 0.0,
                },
            ),
            trust=0.95,
        )
        injuries = _provider_response(
            "injury",
            "espn_injuries",
            decision_time,
            tuple(),
            trust=0.25,
            success=False,
            degraded=True,
            error="injury_source_down",
        )
        stats = _provider_response(
            "stats",
            "nba_team_estimated_metrics",
            decision_time,
            (
                {
                    "game_id": "2026-04-05-bos-nyk",
                    "signal_delta": 0.014,
                    "summary": "Boston net rating edge",
                    "rest_edge": 0,
                },
            ),
            trust=0.91,
        )
        sentiment = _provider_response("sentiment", "reddit_sentiment", decision_time, tuple(), success=False, degraded=True)

        snapshots = build_live_snapshots(decision_time, (schedule, odds, injuries, stats, sentiment))
        self.assertEqual(len(snapshots), 1)
        injury_source = next(source for source in snapshots[0].sources if source.kind == "injury")
        self.assertEqual(injury_source.signal_delta, 0.0)
        self.assertTrue(injury_source.metadata["placeholder"])


if __name__ == "__main__":
    unittest.main()


def _provider_response(
    kind: str,
    name: str,
    source_time: datetime,
    rows: tuple[dict[str, object], ...],
    *,
    trust: float = 0.99,
    success: bool = True,
    degraded: bool = False,
    error: str | None = None,
) -> ProviderResponse:
    return ProviderResponse(
        name=name,
        kind=kind,
        source_time=source_time,
        source_version="test-v1",
        trust=trust,
        success=success,
        degraded=degraded,
        records=tuple(
            ProviderRecord(game_id=str(row["game_id"]), data=dict(row))
            for row in rows
        ),
        raw_payload={"rows": list(rows)},
        error=error,
    )
