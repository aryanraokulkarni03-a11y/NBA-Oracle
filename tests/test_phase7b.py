from __future__ import annotations

import unittest
from dataclasses import replace
from datetime import timedelta

from nba_oracle.config import DEFAULT_FIXTURE_PATH
from nba_oracle.learning.patterns import mine_patterns
from nba_oracle.learning.weights import derive_candidate_weights
from nba_oracle.models import MarketSnapshot, SourceSnapshot
from nba_oracle.predictor import evaluate_game
from nba_oracle.providers.injuries import _summarize_team
from nba_oracle.snapshots import load_game_snapshots


class Phase7BTests(unittest.TestCase):
    def test_predictor_emits_market_prior_uncertainty_and_segment(self) -> None:
        game = load_game_snapshots(DEFAULT_FIXTURE_PATH)[0]
        result = evaluate_game(game)

        self.assertGreaterEqual(result.market_prior_probability, 0.05)
        self.assertLessEqual(result.market_prior_probability, 0.95)
        self.assertGreaterEqual(result.uncertainty, 0.05)
        self.assertLessEqual(result.uncertainty, 0.55)
        self.assertIn(
            result.market_segment,
            {"heavy_favorite", "moderate_favorite", "coin_flip", "underdog"},
        )
        self.assertNotEqual(result.source_adjustment, 0.0)

    def test_high_uncertainty_context_can_downgrade_full_bet(self) -> None:
        game = load_game_snapshots(DEFAULT_FIXTURE_PATH)[3]
        custom_sources = tuple(
            replace(
                source,
                source_time=game.decision_time - timedelta(minutes=30),
                signal_delta=0.05 if index < 2 else 0.025,
            )
            for index, source in enumerate(game.sources)
        )
        custom_market = MarketSnapshot(
            selected_team=game.market.selected_team,
            stake_american=115,
            best_american=124,
            close_american=105,
            consensus_probability=0.47,
            reference_bookmaker=game.market.reference_bookmaker,
            market_timestamp=game.decision_time - timedelta(minutes=70),
            opening_american=None,
        )
        custom_game = replace(
            game,
            tipoff_time=game.decision_time + timedelta(minutes=25),
            market=custom_market,
            sources=custom_sources,
        )

        result = evaluate_game(custom_game)

        self.assertEqual(result.decision, "LEAN")
        self.assertIn("high_uncertainty_context", result.reasons)
        self.assertGreaterEqual(result.uncertainty, 0.4)

    def test_injury_summary_tracks_impact_not_just_counts(self) -> None:
        light = _summarize_team(["Player One", "questionable", "Player Two", "probable"])
        heavy = _summarize_team(["Player One", "out", "Player Two", "questionable"])

        self.assertGreater(float(heavy["impact_score"]), float(light["impact_score"]))
        self.assertGreater(float(heavy["top_weight"]), float(light["top_weight"]))
        self.assertGreater(int(heavy["major_flags"]), int(light["major_flags"]))

    def test_learning_patterns_and_weights_understand_segments(self) -> None:
        predictions = [
            {
                "won": True,
                "decision": "BET",
                "edge_vs_stake": 0.041,
                "source_quality": 0.88,
                "uncertainty": 0.18,
                "market_segment": "moderate_favorite",
                "market_prior_probability": 0.61,
                "model_probability": 0.658,
                "timing_adjustment": 0.004,
                "source_adjustment": 0.018,
                "source_scores": [
                    {"kind": "injury", "signal_delta": 0.022, "quality": 0.92},
                    {"kind": "stats", "signal_delta": 0.015, "quality": 0.87},
                ],
            }
            for _ in range(15)
        ]

        patterns = mine_patterns(predictions)
        weights = derive_candidate_weights(predictions)

        pattern_names = {item["pattern_name"] for item in patterns}
        weight_names = {item["kind"] for item in weights}

        self.assertIn("segment_moderate_favorite", pattern_names)
        self.assertIn("low_uncertainty", pattern_names)
        self.assertIn("bet_low_uncertainty", pattern_names)
        self.assertIn("market_prior", weight_names)
        self.assertIn("timing", weight_names)
        self.assertIn("uncertainty", weight_names)


if __name__ == "__main__":
    unittest.main()
