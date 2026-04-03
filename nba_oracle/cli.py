from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from nba_oracle.config import DEFAULT_FIXTURE_PATH, DEFAULT_LIVE_BUNDLE_PATH
from nba_oracle.live_reporting import write_live_json_report, write_live_markdown_report
from nba_oracle.reporting import write_json_report, write_markdown_report
from nba_oracle.replay import run_replay
from nba_oracle.runs.build_live_slate import build_live_slate
from nba_oracle.snapshots import load_game_snapshots


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="NBA Oracle Phase 1 CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    replay = subparsers.add_parser("replay", help="Run Phase 1 replay on a fixture slate")
    replay.add_argument(
        "--fixture",
        type=Path,
        default=DEFAULT_FIXTURE_PATH,
        help="Path to the fixture JSON file",
    )

    validate = subparsers.add_parser("validate-fixture", help="Validate snapshot timing")
    validate.add_argument(
        "--fixture",
        type=Path,
        default=DEFAULT_FIXTURE_PATH,
        help="Path to the fixture JSON file",
    )

    live = subparsers.add_parser(
        "build-live-slate",
        help="Build a live-style slate from provider inputs and run the Phase 1 predictor",
    )
    live.add_argument(
        "--bundle",
        type=Path,
        default=DEFAULT_LIVE_BUNDLE_PATH,
        help="Path to the live provider bundle JSON file",
    )
    live.add_argument(
        "--live",
        action="store_true",
        help="Fetch live providers instead of using a bundle file",
    )
    live.add_argument(
        "--decision-time",
        type=str,
        default=None,
        help="Override the decision time used for live mode (ISO-8601)",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "validate-fixture":
        games = load_game_snapshots(args.fixture)
        print(f"Fixture valid. Loaded {len(games)} games from {args.fixture}.")
        return

    if args.command == "replay":
        report = run_replay(args.fixture)
        md_path = write_markdown_report(report)
        json_path = write_json_report(report)
        print(f"Replay complete. Markdown report: {md_path}")
        print(f"Replay complete. JSON report: {json_path}")
        return

    if args.command == "build-live-slate":
        decision_time = datetime.fromisoformat(args.decision_time) if args.decision_time else None
        result = build_live_slate(
            None if args.live else args.bundle,
            use_live=bool(args.live),
            decision_time=decision_time,
        )
        md_path = write_live_markdown_report(result)
        json_path = write_live_json_report(result)
        print(f"Live slate build complete. Markdown report: {md_path}")
        print(f"Live slate build complete. JSON report: {json_path}")
        return

    parser.error("Unknown command")
