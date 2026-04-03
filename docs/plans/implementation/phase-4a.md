# NBA Oracle Phase 4A Implementation Plan

## Purpose
Phase 4A is the operating core.

This is the backend-first completion pass that builds everything needed for the product to run without the dashboard:
- API
- auth
- scheduler/runtime
- delivery channels
- learning engine execution
- operator-facing backend surfaces

## Source of Truth
This plan is derived from:
- [master-spec.md](../../spec/master-spec.md)
- [project-status-matrix.md](../../status/project-status-matrix.md)
- [changes-matrix.md](../../status/changes-matrix.md)
- [phase-4.md](./phase-4.md)

## Phase 4A Goal
Build the full operating core that can answer this question:

> Can NBA Oracle run on schedule, expose secure backend APIs, deliver picks and status updates, and execute the learning loop without needing the frontend to exist first?

## In Scope
- FastAPI app
- auth and password bootstrap
- protected route layer
- health and operator routes
- scheduler/meta-scheduler
- Telegram integration
- Gmail integration
- learning engine execution path
- backend deployment/startup hardening

## Out of Scope
- React/Vite dashboard UI
- frontend route design
- full system integration testing across every surface

## What Phase 4A Must Prove

1. The backend can run as a real application, not just CLI commands.
2. Auth exists and protects operator routes.
3. Scheduled jobs can run the live workflow safely.
4. Telegram and Gmail can deliver operational outputs.
5. Learning can run as a controlled backend workflow.
6. The operator can inspect system health without code tracing.

## Major Workstreams

### Workstream 1: FastAPI Application Layer
Build:
- app bootstrap
- route modules
- dependency layer
- error handling
- health endpoint

Core routes:
- `POST /api/auth/login`
- `GET /api/health`
- `GET /api/today`
- `GET /api/picks/history`
- `GET /api/stability/latest`
- `GET /api/learning/status`
- `GET /api/providers/health`
- `POST /api/operator/run-live-slate`
- `POST /api/operator/grade-outcomes`
- `POST /api/operator/review-stability`

### Workstream 2: Auth and Security
Build:
- password setup bootstrap
- bcrypt password hash storage
- JWT sessions
- protected routes
- failed login logging
- rate limiting
- session-expiry logic

### Workstream 3: Runtime and Scheduler
Build:
- midnight slate check
- T-minus-two-hours scheduling
- postgame grading
- stability review cadence
- learning-cycle trigger
- runtime state log and job history

### Workstream 4: Telegram and Gmail
Build:
- Telegram pick-card sender
- Telegram digest sender
- Telegram command handlers
- Gmail midnight/status/failure notifications

### Workstream 5: Learning Engine First Execution
Build:
- weight optimizer runner
- pattern miner runner
- learning history persistence
- learning review state
- replay-gated candidate update path

### Workstream 6: Backend Runbooks and Startup
Build:
- startup command/runbook
- auto-start guidance
- runtime logging
- failure recovery guidance

## Recommended Files

- `nba_oracle/api/app.py`
- `nba_oracle/api/routes/*.py`
- `nba_oracle/api/dependencies.py`
- `nba_oracle/auth.py`
- `nba_oracle/security.py`
- `nba_oracle/runtime/meta_scheduler.py`
- `nba_oracle/runtime/jobs.py`
- `nba_oracle/runtime/state.py`
- `nba_oracle/runtime/health.py`
- `nba_oracle/notifications/telegram.py`
- `nba_oracle/notifications/gmail.py`
- `nba_oracle/notifications/formatters.py`
- `nba_oracle/learning/weights.py`
- `nba_oracle/learning/patterns.py`
- `nba_oracle/learning/trainer.py`
- `nba_oracle/learning/review.py`
- `setup_auth.py`

## Manual Inputs Needed Later
- Telegram bot token
- Telegram destination strategy
- Gmail sending configuration
- local API port
- auth bootstrap password
- whether Gmail weekly summary starts immediately

## Acceptance Criteria
Phase 4A is acceptable only if:
- FastAPI runs locally
- auth works
- operator routes are protected
- scheduler jobs can execute the existing flows
- Telegram and Gmail can send working outputs
- learning execution is wired and review-safe
- health and runtime status are exposed through the backend

## Exit Rule
Do not move to Phase 4B until the backend contract is real enough that the frontend can build against it without inventing missing behavior.
