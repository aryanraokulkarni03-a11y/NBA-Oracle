from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from nba_oracle.api.dependencies import require_authenticated_user
from nba_oracle.runtime.jobs import (
    run_learning_review_job,
    run_live_slate_job,
    run_outcome_grading_job,
    run_stability_review_job,
)
from nba_oracle.runtime.meta_scheduler import run_scheduler_once


router = APIRouter(prefix="/api/operator", tags=["operator"])


class LiveSlateRequest(BaseModel):
    live: bool = True


class StabilityRequest(BaseModel):
    force_refresh_baseline: bool = False


class SchedulerRequest(BaseModel):
    force: bool = False


@router.post("/run-live-slate")
def operator_run_live_slate(
    payload: LiveSlateRequest,
    _: dict[str, object] = Depends(require_authenticated_user),
) -> dict[str, object]:
    return run_live_slate_job(use_live=payload.live)


@router.post("/grade-outcomes")
def operator_grade_outcomes(_: dict[str, object] = Depends(require_authenticated_user)) -> dict[str, object]:
    return run_outcome_grading_job()


@router.post("/review-stability")
def operator_review_stability(
    payload: StabilityRequest,
    _: dict[str, object] = Depends(require_authenticated_user),
) -> dict[str, object]:
    return run_stability_review_job(force_refresh_baseline=payload.force_refresh_baseline)


@router.post("/run-learning-review")
def operator_run_learning_review(_: dict[str, object] = Depends(require_authenticated_user)) -> dict[str, object]:
    return run_learning_review_job()


@router.post("/run-scheduler-once")
def operator_run_scheduler_once(
    payload: SchedulerRequest,
    _: dict[str, object] = Depends(require_authenticated_user),
) -> dict[str, object]:
    return run_scheduler_once(now=datetime.now(timezone.utc), force=payload.force)
