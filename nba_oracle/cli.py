from __future__ import annotations

import argparse
import getpass
from datetime import datetime
from pathlib import Path

from nba_oracle.auth import generate_secret_key, hash_password
from nba_oracle.config import DEFAULT_FIXTURE_PATH, DEFAULT_JSON_REPORT_PATH, DEFAULT_LIVE_BUNDLE_PATH, ROOT_DIR, RUNTIME_DIR
from nba_oracle.env import upsert_dotenv_values
from nba_oracle.learning.review import write_learning_json_report, write_learning_markdown_report
from nba_oracle.learning.trainer import run_learning_review
from nba_oracle.live_reporting import write_live_json_report, write_live_markdown_report
from nba_oracle.notifications.gmail import send_gmail_message
from nba_oracle.notifications.telegram import handle_telegram_command, send_live_digest, send_telegram_message
from nba_oracle.outcomes.reporting import write_outcome_json_report, write_outcome_markdown_report
from nba_oracle.reporting import write_json_report, write_markdown_report
from nba_oracle.replay import run_replay
from nba_oracle.runs.build_live_slate import build_live_slate
from nba_oracle.runs.grade_outcomes import grade_outcomes
from nba_oracle.runs.review_stability import review_stability
from nba_oracle.runtime.meta_scheduler import run_scheduler_once
from nba_oracle.snapshots import load_game_snapshots


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="NBA Oracle backend CLI")
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

    outcomes = subparsers.add_parser(
        "grade-outcomes",
        help="Fetch official NBA final results and backfill stored live predictions",
    )
    outcomes.add_argument(
        "--runtime-dir",
        type=Path,
        default=RUNTIME_DIR,
        help="Path to the runtime directory that contains live runs",
    )
    outcomes.add_argument(
        "--as-of",
        type=str,
        default=None,
        help="Override the grading cutoff time used to decide which games should be final (ISO-8601)",
    )
    outcomes.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of live runs to inspect",
    )

    stability = subparsers.add_parser(
        "review-stability",
        help="Review recent live runs against the replay/live baseline and emit a Phase 3 stability report",
    )
    stability.add_argument(
        "--replay-report",
        type=Path,
        default=DEFAULT_JSON_REPORT_PATH,
        help="Path to the Phase 1 replay JSON report",
    )
    stability.add_argument(
        "--runtime-dir",
        type=Path,
        default=RUNTIME_DIR,
        help="Path to the runtime directory that contains live runs",
    )
    stability.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of live runs to review",
    )
    stability.add_argument(
        "--force-refresh-baseline",
        action="store_true",
        help="Force a Phase 3 baseline refresh before running the review",
    )
    stability.add_argument(
        "--analyst-payload",
        type=Path,
        default=None,
        help="Optional JSON payload with analyst suggestions keyed by game_id",
    )
    stability.add_argument(
        "--candidate-model-version",
        type=str,
        default=None,
        help="Optional candidate model version to record in the review workflow",
    )
    stability.add_argument(
        "--promotion-reason",
        type=str,
        default=None,
        help="Optional promotion reason if a candidate model is being recorded",
    )
    stability.add_argument(
        "--rollback-reason",
        type=str,
        default=None,
        help="Optional rollback reason if the review is recording a rollback event",
    )

    learning = subparsers.add_parser(
        "review-learning",
        help="Run the Phase 4A learning review workflow",
    )
    learning.add_argument(
        "--runtime-dir",
        type=Path,
        default=RUNTIME_DIR,
        help="Path to the runtime directory that contains live runs",
    )

    auth = subparsers.add_parser(
        "bootstrap-auth",
        help="Interactively create the dashboard password hash and API secret in .env",
    )

    serve = subparsers.add_parser(
        "serve-api",
        help="Run the Phase 4A FastAPI server",
    )
    serve.add_argument("--host", type=str, default=None, help="Override API host")
    serve.add_argument("--port", type=int, default=None, help="Override API port")

    scheduler = subparsers.add_parser(
        "run-scheduler-once",
        help="Evaluate the 4A runtime scheduler and execute due jobs once",
    )
    scheduler.add_argument("--force", action="store_true", help="Run every scheduler job once regardless of due state")

    telegram = subparsers.add_parser(
        "notify-telegram-test",
        help="Send a Telegram test notification",
    )
    telegram.add_argument(
        "--message",
        type=str,
        default="NBA Oracle Telegram test notification",
        help="Message body to send",
    )

    gmail = subparsers.add_parser(
        "notify-gmail-test",
        help="Send a Gmail test notification",
    )
    gmail.add_argument(
        "--subject",
        type=str,
        default="NBA Oracle Gmail test",
        help="Email subject line",
    )
    gmail.add_argument(
        "--message",
        type=str,
        default="NBA Oracle Gmail delivery path is healthy.",
        help="Email body to send",
    )

    telegram_command = subparsers.add_parser(
        "telegram-command",
        help="Preview or send a Telegram command-style response",
    )
    telegram_command.add_argument(
        "--text",
        type=str,
        required=True,
        help="Telegram command text like /health or /picks",
    )
    telegram_command.add_argument(
        "--send",
        action="store_true",
        help="Send the generated command response to Telegram instead of only printing it",
    )

    bootstrap_runtime = subparsers.add_parser(
        "bootstrap-runtime",
        help="Install Phase 4A runtime dependencies into the project-local package cache",
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

    if args.command == "grade-outcomes":
        as_of = datetime.fromisoformat(args.as_of) if args.as_of else None
        result = grade_outcomes(
            runtime_dir=args.runtime_dir,
            as_of=as_of,
            limit=args.limit,
        )
        md_path = write_outcome_markdown_report(result)
        json_path = write_outcome_json_report(result)
        print(f"Outcome grading complete. Markdown report: {md_path}")
        print(f"Outcome grading complete. JSON report: {json_path}")
        print(f"Newly graded: {result.newly_graded}")
        print(f"Pending unfinished: {result.pending_unfinished}")
        print(f"Missing official outcomes: {result.missing_official_outcomes}")
        return

    if args.command == "review-stability":
        result, baseline_path, md_path, json_path = review_stability(
            replay_report_path=args.replay_report,
            runtime_dir=args.runtime_dir,
            limit=args.limit,
            force_refresh_baseline=bool(args.force_refresh_baseline),
            analyst_payload_path=args.analyst_payload,
            candidate_model_version=args.candidate_model_version,
            promotion_reason=args.promotion_reason,
            rollback_reason=args.rollback_reason,
        )
        print(f"Stability review complete. Baseline file: {baseline_path}")
        print(f"Stability review complete. Markdown report: {md_path}")
        print(f"Stability review complete. JSON report: {json_path}")
        print(f"Drift status: {result.drift.status}")
        print(f"Timing status: {result.timing.status}")
        print(f"Analyst containment: {result.readiness.analyst.status}")
        print(f"Model review status: {result.model_registry.review_status}")
        return

    if args.command == "review-learning":
        result = run_learning_review(runtime_dir=args.runtime_dir)
        md_path = write_learning_markdown_report(result)
        json_path = write_learning_json_report(result)
        print(f"Learning review complete. Markdown report: {md_path}")
        print(f"Learning review complete. JSON report: {json_path}")
        print(f"Status: {result.status}")
        print(f"Candidate model version: {result.candidate_model_version}")
        return

    if args.command == "bootstrap-auth":
        password = getpass.getpass("Enter dashboard password: ")
        confirm = getpass.getpass("Confirm dashboard password: ")
        if not password:
            raise SystemExit("password_cannot_be_empty")
        if password != confirm:
            raise SystemExit("passwords_do_not_match")
        env_path = upsert_dotenv_values(
            {
                "ORACLE_PASSWORD_HASH": hash_password(password),
                "ORACLE_SECRET_KEY": generate_secret_key(),
            }
        )
        print(f"Auth bootstrap complete. Updated env file: {env_path}")
        return

    if args.command == "serve-api":
        import uvicorn

        from nba_oracle.api.app import build_app
        from nba_oracle.config import ORACLE_API_HOST, ORACLE_API_PORT

        uvicorn.run(
            build_app(),
            host=args.host or ORACLE_API_HOST,
            port=args.port or ORACLE_API_PORT,
        )
        return

    if args.command == "run-scheduler-once":
        result = run_scheduler_once(force=bool(args.force))
        print(f"Scheduler run complete. Executed jobs: {len(result['executed_jobs'])}")
        print(result)
        return

    if args.command == "notify-telegram-test":
        event_id = send_telegram_message(args.message, event_type="telegram_test")
        print(f"Telegram notification sent. Event id: {event_id}")
        return

    if args.command == "notify-gmail-test":
        event_id = send_gmail_message(args.subject, args.message, event_type="gmail_test")
        print(f"Gmail notification sent. Event id: {event_id}")
        return

    if args.command == "telegram-command":
        message = handle_telegram_command(args.text)
        if args.send:
            event_id = send_telegram_message(message, event_type="telegram_command")
            print(f"Telegram command response sent. Event id: {event_id}")
        else:
            print(message)
        return

    if args.command == "bootstrap-runtime":
        import subprocess
        import sys

        target = ROOT_DIR / ".python_packages"
        target.mkdir(parents=True, exist_ok=True)
        packages = ["fastapi", "uvicorn", "bcrypt", "PyJWT", "httpx"]
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--target", str(target), *packages],
            check=True,
        )
        print(f"Runtime bootstrap complete. Installed packages into {target}")
        return

    parser.error("Unknown command")
