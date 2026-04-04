from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from nba_oracle.http import HttpRequestError
from nba_oracle.outcomes.fetcher import OfficialOutcome, fetch_official_outcomes
from nba_oracle.outcomes.persistence import LocalOutcomeRepository
from nba_oracle.runs.grade_outcomes import grade_outcomes


class Phase3OutcomeTests(unittest.TestCase):
    def test_fetch_official_outcomes_parses_completed_games(self) -> None:
        payload = {
            "resultSets": [
                {
                    "name": "GameHeader",
                    "headers": ["GAME_ID", "GAME_STATUS_ID", "GAME_STATUS_TEXT", "HOME_TEAM_ID", "VISITOR_TEAM_ID"],
                    "rowSet": [["0022500001", 3, "Final", 1610612738, 1610612741]],
                },
                {
                    "name": "LineScore",
                    "headers": ["GAME_ID", "TEAM_ID", "TEAM_ABBREVIATION", "TEAM_CITY_NAME", "TEAM_NICKNAME", "PTS"],
                    "rowSet": [
                        ["0022500001", 1610612741, "CHI", "Chicago", "Bulls", 102],
                        ["0022500001", 1610612738, "BOS", "Boston", "Celtics", 111],
                    ],
                },
            ]
        }

        with patch("nba_oracle.outcomes.fetcher.request_text", return_value=(json.dumps(payload), {})):
            outcomes = fetch_official_outcomes(datetime(2026, 4, 3, tzinfo=timezone.utc).date())

        self.assertEqual(len(outcomes), 1)
        self.assertEqual(outcomes[0].game_id, "2026-04-03-chi-bos")
        self.assertEqual(outcomes[0].actual_winner, "Boston Celtics")

    def test_grade_outcomes_backfills_runtime_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            runtime_dir = Path(tmp_dir) / "runtime"
            run_dir = runtime_dir / "live-20260403T120000Z"
            run_dir.mkdir(parents=True)

            snapshots_payload = {
                "snapshots": [
                    {
                        "game_id": "2026-04-03-chi-bos",
                        "decision_time": "2026-04-03T12:00:00+00:00",
                        "tipoff_time": "2026-04-03T23:30:00+00:00",
                        "away_team": "Chicago Bulls",
                        "home_team": "Boston Celtics",
                        "actual_winner": None,
                    }
                ]
            }
            predictions_payload = {
                "predictions": [
                    {
                        "game_id": "2026-04-03-chi-bos",
                        "selected_team": "Boston Celtics",
                        "decision": "BET",
                        "actual_winner": None,
                    }
                ]
            }
            (run_dir / "snapshots.json").write_text(json.dumps(snapshots_payload, indent=2), encoding="utf-8")
            (run_dir / "predictions.json").write_text(json.dumps(predictions_payload, indent=2), encoding="utf-8")

            outcome = OfficialOutcome(
                game_id="2026-04-03-chi-bos",
                game_date=datetime(2026, 4, 3, tzinfo=timezone.utc).date(),
                away_team="Chicago Bulls",
                home_team="Boston Celtics",
                away_score=102,
                home_score=111,
                actual_winner="Boston Celtics",
                game_status="Final",
                source_name="nba_scoreboard_v2",
                source_version="scoreboardv2-v1",
                source_time=datetime(2026, 4, 4, 4, 0, tzinfo=timezone.utc),
            )

            with patch(
                "nba_oracle.runs.grade_outcomes.fetch_official_outcomes",
                return_value=(outcome,),
            ), patch(
                "nba_oracle.runs.grade_outcomes.build_outcome_repository",
                return_value=LocalOutcomeRepository(root=runtime_dir),
            ):
                result = grade_outcomes(
                    runtime_dir=runtime_dir,
                    as_of=datetime(2026, 4, 4, 6, 0, tzinfo=timezone.utc),
                )

            updated_predictions = json.loads((run_dir / "predictions.json").read_text(encoding="utf-8"))
            updated_snapshots = json.loads((run_dir / "snapshots.json").read_text(encoding="utf-8"))
            outcome_grades = json.loads((run_dir / "outcome_grades.json").read_text(encoding="utf-8"))

            self.assertEqual(result.newly_graded, 1)
            self.assertEqual(updated_predictions["predictions"][0]["actual_winner"], "Boston Celtics")
            self.assertEqual(updated_snapshots["snapshots"][0]["actual_winner"], "Boston Celtics")
            self.assertEqual(outcome_grades["grades"][0]["actual_winner"], "Boston Celtics")

    def test_fetch_official_outcomes_falls_back_to_live_scoreboard_after_timeouts(self) -> None:
        live_payload = {
            "scoreboard": {
                "games": [
                    {
                        "gameTimeUTC": "2026-04-03T23:30:00Z",
                        "gameStatus": 3,
                        "gameStatusText": "Final",
                        "awayTeam": {
                            "teamTricode": "CHI",
                            "teamCity": "Chicago",
                            "teamName": "Bulls",
                            "score": 102,
                        },
                        "homeTeam": {
                            "teamTricode": "BOS",
                            "teamCity": "Boston",
                            "teamName": "Celtics",
                            "score": 111,
                        },
                    }
                ]
            }
        }

        with patch(
            "nba_oracle.outcomes.fetcher.request_text",
            side_effect=HttpRequestError("The read operation timed out"),
        ), patch(
            "nba_oracle.outcomes.fetcher.request_json",
            return_value=(live_payload, {}),
        ):
            outcomes = fetch_official_outcomes(datetime(2026, 4, 3, tzinfo=timezone.utc).date())

        self.assertEqual(len(outcomes), 1)
        self.assertEqual(outcomes[0].game_id, "2026-04-03-chi-bos")
        self.assertEqual(outcomes[0].source_name, "nba_scoreboard_live")
        self.assertEqual(outcomes[0].actual_winner, "Boston Celtics")


if __name__ == "__main__":
    unittest.main()
