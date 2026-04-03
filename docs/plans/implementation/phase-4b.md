# NBA Oracle Phase 4B Implementation Plan

## Purpose
Phase 4B is the dashboard and user interaction layer.

This phase builds the operator-facing product shell on top of the Phase 4A backend contract.

## Source of Truth
This plan is derived from:
- [master-spec.md](../../spec/master-spec.md)
- [project-status-matrix.md](../../status/project-status-matrix.md)
- [changes-matrix.md](../../status/changes-matrix.md)
- [phase-4.md](./phase-4.md)
- [phase-4a.md](./phase-4a.md)

## Phase 4B Goal
Build the full local dashboard and operator interaction layer that can answer this question:

> Can the user log in, inspect today’s slate, review history, monitor system health, and understand learning/stability state from a clean frontend without touching the terminal?

## In Scope
- React/Vite dashboard
- login page
- authenticated route handling
- today page
- performance page
- learning page
- trends page
- operator actions that call Phase 4A APIs

## Out of Scope
- backend scheduler/runtime logic
- Telegram/Gmail internals
- full final end-to-end production hardening

## What Phase 4B Must Prove

1. The dashboard is truthful to backend state.
2. Auth works end to end in the UI.
3. The user can understand picks, skips, history, stability, and learning at a glance.
4. Operator actions are exposed without hiding risk, degraded state, or missing evidence.

## Required Pages

### `/login`
- password entry
- auth error state
- lockout/error messaging

### `/`
- today’s live slate
- pick cards
- provider health
- runtime status
- first-tipoff countdown

### `/performance`
- pick history
- win/loss trends
- confidence/outcome relationship
- filters and expanded pick detail

### `/learning`
- current weights
- pattern cards
- learning-cycle status
- next review state

### `/trends`
- market movement summaries
- provider-source trends
- injury/sentiment/trend support surfaces

## UI Rules

1. Preserve the spec’s dark, deliberate, data-terminal feel.
2. Use monospace for numbers and betting metrics where appropriate.
3. Keep degraded state visible.
4. Never hide `SKIP`.
5. Keep mobile-safe layouts for operator use, even if desktop is primary.

## Frontend Contract Requirements

The frontend should consume backend routes for:
- auth/session
- today’s slate
- picks/history
- stability summary
- learning summary
- provider health
- operator actions

The frontend must not read local files directly.

## Recommended Files

- `dashboard/package.json`
- `dashboard/vite.config.*`
- `dashboard/src/main.*`
- `dashboard/src/App.*`
- `dashboard/src/pages/Login.*`
- `dashboard/src/pages/Today.*`
- `dashboard/src/pages/Performance.*`
- `dashboard/src/pages/Learning.*`
- `dashboard/src/pages/Trends.*`
- `dashboard/src/components/*`
- `dashboard/src/lib/api.*`
- `dashboard/src/lib/auth.*`

## Manual Inputs Needed Later
- preferred frontend port
- whether the dashboard should auto-open after backend startup
- whether operator actions need confirmation modals by default

## Acceptance Criteria
Phase 4B is acceptable only if:
- login works
- core pages render against real backend data
- operator actions can be triggered from the UI
- history/stability/learning surfaces are readable and useful
- UI reflects degraded states and `SKIP` behavior honestly

## Exit Rule
Do not move to Phase 4C until the dashboard is usable enough that the remaining work is mostly integration, polishing, and hardening rather than major missing features.
