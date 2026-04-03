from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from nba_oracle.config import (
    DEFAULT_LEARNING_JSON_REPORT_PATH,
    DEFAULT_LEARNING_REPORT_PATH,
    LEARNING_DIR,
    REPORTS_DIR,
)


@dataclass(frozen=True)
class LearningReviewResult:
    review_id: str
    created_at: datetime
    status: str
    active_model_version: str
    candidate_model_version: str | None
    graded_prediction_count: int
    actionable_prediction_count: int
    review_only: bool
    weights: tuple[dict[str, object], ...]
    patterns: tuple[dict[str, object], ...]
    reasons: tuple[str, ...]
    stored_paths: tuple[str, ...]


def ensure_learning_dir() -> None:
    LEARNING_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def write_learning_markdown_report(
    result: LearningReviewResult,
    path: Path = DEFAULT_LEARNING_REPORT_PATH,
) -> Path:
    ensure_learning_dir()
    lines: list[str] = []
    lines.append("# NBA Oracle Phase 4A Learning Review")
    lines.append("")
    lines.append(f"- Review id: `{result.review_id}`")
    lines.append(f"- Created at: `{result.created_at.isoformat()}`")
    lines.append(f"- Status: `{result.status}`")
    lines.append(f"- Active model: `{result.active_model_version}`")
    lines.append(f"- Candidate model: `{result.candidate_model_version or 'n/a'}`")
    lines.append(f"- Graded predictions: `{result.graded_prediction_count}`")
    lines.append(f"- Actionable graded predictions: `{result.actionable_prediction_count}`")
    lines.append(f"- Review-only mode: `{result.review_only}`")
    lines.append("")
    lines.append("## Reasons")
    lines.append("")
    for reason in result.reasons:
        lines.append(f"- {reason}")
    lines.append("")
    lines.append("## Candidate Weights")
    lines.append("")
    lines.append("| Kind | Weight | Sample |")
    lines.append("|---|---:|---:|")
    for item in result.weights:
        lines.append(f"| {item.get('kind')} | {float(item.get('weight', 0.0)):.2%} | {item.get('sample_size', 0)} |")
    lines.append("")
    lines.append("## Patterns")
    lines.append("")
    lines.append("| Pattern | Win rate | Sample |")
    lines.append("|---|---:|---:|")
    for item in result.patterns:
        lines.append(
            f"| {item.get('pattern_name')} | {float(item.get('win_rate', 0.0)):.2%} | {item.get('sample_size', 0)} |"
        )
    lines.append("")
    lines.append("## Stored Artifacts")
    lines.append("")
    for item in result.stored_paths:
        lines.append(f"- `{item}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_learning_json_report(
    result: LearningReviewResult,
    path: Path = DEFAULT_LEARNING_JSON_REPORT_PATH,
) -> Path:
    ensure_learning_dir()
    payload = {
        "review_id": result.review_id,
        "created_at": result.created_at.isoformat(),
        "status": result.status,
        "active_model_version": result.active_model_version,
        "candidate_model_version": result.candidate_model_version,
        "graded_prediction_count": result.graded_prediction_count,
        "actionable_prediction_count": result.actionable_prediction_count,
        "review_only": result.review_only,
        "weights": list(result.weights),
        "patterns": list(result.patterns),
        "reasons": list(result.reasons),
        "stored_paths": list(result.stored_paths),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
