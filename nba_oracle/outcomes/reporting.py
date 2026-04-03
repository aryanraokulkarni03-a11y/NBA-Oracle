from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from nba_oracle.config import DEFAULT_OUTCOME_JSON_REPORT_PATH, DEFAULT_OUTCOME_REPORT_PATH, REPORTS_DIR


@dataclass(frozen=True)
class OutcomeGradeRecord:
    run_id: str
    game_id: str
    away_team: str
    home_team: str
    selected_team: str
    decision: str
    actual_winner: str
    won: bool
    tipoff_time: datetime
    graded_at: datetime
    game_status: str
    source_name: str
    source_version: str


@dataclass(frozen=True)
class OutcomeGradingResult:
    runtime_dir: Path
    graded_at: datetime
    evaluated_runs: int
    eligible_predictions: int
    newly_graded: int
    already_graded: int
    pending_unfinished: int
    missing_official_outcomes: int
    grades: tuple[OutcomeGradeRecord, ...]
    stored_paths: tuple[str, ...]


def write_outcome_markdown_report(
    result: OutcomeGradingResult,
    path: Path = DEFAULT_OUTCOME_REPORT_PATH,
) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# NBA Oracle Phase 3 Outcome Grading Report")
    lines.append("")
    lines.append(f"- Runtime dir: `{result.runtime_dir}`")
    lines.append(f"- Graded at: `{result.graded_at.isoformat()}`")
    lines.append(f"- Evaluated runs: `{result.evaluated_runs}`")
    lines.append(f"- Eligible predictions: `{result.eligible_predictions}`")
    lines.append(f"- Newly graded: `{result.newly_graded}`")
    lines.append(f"- Already graded: `{result.already_graded}`")
    lines.append(f"- Pending unfinished: `{result.pending_unfinished}`")
    lines.append(f"- Missing official outcomes: `{result.missing_official_outcomes}`")
    lines.append("")
    lines.append("## Graded Picks")
    lines.append("")
    lines.append("| Run | Game | Pick | Decision | Winner | Won | Tipoff | Source | Status |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for grade in result.grades:
        lines.append(
            f"| {grade.run_id} | {grade.away_team} @ {grade.home_team} | {grade.selected_team} | "
            f"{grade.decision} | {grade.actual_winner} | {grade.won} | {grade.tipoff_time.isoformat()} | "
            f"{grade.source_name} | {grade.game_status} |"
        )
    lines.append("")
    lines.append("## Stored Artifacts")
    lines.append("")
    for stored_path in result.stored_paths:
        lines.append(f"- `{stored_path}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_outcome_json_report(
    result: OutcomeGradingResult,
    path: Path = DEFAULT_OUTCOME_JSON_REPORT_PATH,
) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "runtime_dir": str(result.runtime_dir),
        "graded_at": result.graded_at.isoformat(),
        "evaluated_runs": result.evaluated_runs,
        "eligible_predictions": result.eligible_predictions,
        "newly_graded": result.newly_graded,
        "already_graded": result.already_graded,
        "pending_unfinished": result.pending_unfinished,
        "missing_official_outcomes": result.missing_official_outcomes,
        "grades": [
            {
                "run_id": grade.run_id,
                "game_id": grade.game_id,
                "away_team": grade.away_team,
                "home_team": grade.home_team,
                "selected_team": grade.selected_team,
                "decision": grade.decision,
                "actual_winner": grade.actual_winner,
                "won": grade.won,
                "tipoff_time": grade.tipoff_time.isoformat(),
                "graded_at": grade.graded_at.isoformat(),
                "game_status": grade.game_status,
                "source_name": grade.source_name,
                "source_version": grade.source_version,
            }
            for grade in result.grades
        ],
        "stored_paths": list(result.stored_paths),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
