# NBA Oracle Phase 4B Final One-Shot Implementation Plan

## Purpose
Phase 4B is the complete dashboard and operator interaction layer.

This is the frontend completion pass that turns the existing Phase 4A backend into a usable product surface:
- authenticated dashboard
- truthful live-slate view
- history and performance surfaces
- stability and learning visibility
- provider and runtime monitoring
- operator actions from the UI

The goal is not to invent new backend behavior. The goal is to expose the real Phase 1-4A system clearly, honestly, and safely.

## Source of Truth
This plan is derived from:
- [master-spec.md](../../spec/master-spec.md)
- [project-status-matrix.md](../../status/project-status-matrix.md)
- [changes-matrix.md](../../status/changes-matrix.md)
- [phase-4.md](./phase-4.md)
- [phase-4a.md](./phase-4a.md)

It is explicitly aligned to the current backend contract already implemented in:
- [app.py](../../../nba_oracle/api/app.py)
- [auth.py](../../../nba_oracle/api/routes/auth.py)
- [health.py](../../../nba_oracle/api/routes/health.py)
- [today.py](../../../nba_oracle/api/routes/today.py)
- [picks.py](../../../nba_oracle/api/routes/picks.py)
- [stability.py](../../../nba_oracle/api/routes/stability.py)
- [learning.py](../../../nba_oracle/api/routes/learning.py)
- [providers.py](../../../nba_oracle/api/routes/providers.py)
- [operator.py](../../../nba_oracle/api/routes/operator.py)

## Phase 4B Goal
Build the complete local dashboard and operator control surface that can answer this question:

> Can the user log in, understand the current system state, inspect the live slate, review history and model health, and trigger operator workflows without touching the terminal?

## Phase 4B Must Respect These Truths

1. The predictor remains the final betting authority.
2. The frontend must display `BET`, `LEAN`, and `SKIP` honestly.
3. Degraded providers, fallback paths, and insufficient-data states must stay visible.
4. The frontend must only use backend APIs and never read local files directly.
5. The frontend must not create fake certainty where the backend reports degraded, deferred, or insufficient evidence.
6. The UI should feel deliberate and trustworthy, not flashy for its own sake.

## In Scope
- React + Vite dashboard
- frontend auth flow against `/api/auth/login`
- token persistence and protected routes
- app shell and layout system
- today dashboard
- history and performance views
- stability and learning views
- provider and runtime health view
- operator action controls backed by real Phase 4A routes
- clear loading, error, empty, degraded, and expired-session states

## Out of Scope
- backend scheduler/runtime logic changes
- Telegram/Gmail transport internals
- real LLM analyst layer
- final cross-surface integration hardening
- deployment/public hosting polish

## What Phase 4B Must Prove

1. The dashboard is truthful to backend state.
2. Auth works end to end in the browser.
3. The user can understand live picks, skips, provider health, outcomes, stability, and learning from the UI alone.
4. Operator actions can be triggered safely without hiding their consequences.
5. Empty and insufficient-data states still feel intentional and readable.

## Frontend Architecture

### Stack
- React
- Vite
- TypeScript
- React Router
- lightweight state via React context + route loaders or query hooks
- CSS variables with a deliberate dashboard visual system

### Design Direction
- dark, high-contrast, operator-grade interface
- not generic SaaS, not neon gimmickry
- strong typography hierarchy
- monospace for:
  - odds
  - EV
  - edge
  - timestamps
  - counts
  - statuses
- color should communicate state:
  - neutral for informational
  - amber for degraded
  - green for healthy
  - red only for failure or lockout
- `SKIP` must be visually visible but not styled as failure

### App Shell
Build:
- authenticated layout
- left navigation or top navigation that works on desktop and mobile
- header with:
  - backend status
  - last refresh
  - auth/session status
  - quick operator actions entry point
- global toast/notice system
- global loading and session-expired handling

## Backend Contract To Target

### Auth
- `POST /api/auth/login`

Expected usage:
- submit password
- receive bearer token
- persist session locally
- handle lockout, rate-limit, and invalid-credentials errors honestly

### Read Routes
- `GET /api/health`
- `GET /api/today`
- `GET /api/picks/history`
- `GET /api/stability/latest`
- `GET /api/learning/status`
- `GET /api/providers/health`

### Operator Routes
- `POST /api/operator/run-live-slate`
- `POST /api/operator/run-scheduler-once`
- `POST /api/operator/grade-outcomes`
- `POST /api/operator/review-stability`
- `POST /api/operator/run-learning-review`

## Required Pages

### 1. `/login`
Purpose:
- authenticate the operator

Must show:
- password form
- invalid-credentials state
- locked/too-many-attempts state
- submit/loading state

Must do:
- store token after login
- redirect into the app
- handle expired or missing session cleanly

### 2. `/`
Purpose:
- primary operator dashboard

Must show:
- latest live run ID
- decision time
- prediction counts by `BET`, `LEAN`, `SKIP`
- provider summary
- first-tipoff / live-slate context if available
- latest outcome grading summary
- latest stability summary
- latest learning summary

Must include:
- quick cards for:
  - health
  - live slate
  - outcomes
  - stability
  - learning
  - provider degradation

### 3. `/today`
Purpose:
- full live-slate inspection

Must show:
- latest predictions from `/api/today`
- card/table hybrid for games
- selected team
- decision
- EV
- edge
- reasons
- market/reference pricing fields if present
- source quality and provider context where available

Rules:
- `SKIP` rows stay visible
- degraded-source rows are visibly flagged
- empty slate state is intentional, not broken-looking

### 4. `/performance`
Purpose:
- run history and operator performance surface

Must show:
- recent run history from `/api/picks/history`
- bet/lean/skip counts
- prediction counts
- run IDs and timestamps when available
- drill-down into selected run if available from current payloads

Important note:
- current backend history is run-summary oriented, not fully analytics-rich
- the UI must reflect that honestly instead of fabricating ROI charts not yet supported

### 5. `/stability`
Purpose:
- expose model health and drift status

Must show:
- drift status
- timing status
- market readiness
- analyst containment status if present
- baseline/review identifiers
- insufficient-data state clearly when evidence is still immature

Must support:
- trigger `review-stability`
- show completion result
- show report references or summary payload returned by the route

### 6. `/learning`
Purpose:
- expose learning-cycle readiness and review state

Must show:
- learning review ID
- status
- candidate model version
- graded prediction count
- insufficient-data state

Must support:
- trigger `run-learning-review`
- show result inline

### 7. `/providers`
Purpose:
- operational health page for sources and runtime

Must show:
- provider rows from `/api/providers/health`
- success/degraded/failed state
- source version
- trust
- record count
- fallback error reasons
- degraded and failed counts

Must also show:
- a compact `/api/health` summary:
  - API host/port/timezone
  - Telegram configured
  - Gmail configured
  - latest runtime jobs

### 8. `/operations`
Purpose:
- safe operator controls

Must support:
- run live slate
- run scheduler once
- grade outcomes
- review stability
- run learning review

Rules:
- every action needs an explicit confirmation state
- running actions must lock their button while in flight
- results must be surfaced immediately
- destructive-looking language must be avoided because these are operational jobs, not deletes

## Workstreams

### Workstream 1: Frontend Foundation
Build:
- `dashboard/` app scaffold
- Vite + React + TypeScript setup
- route system
- environment/config handling
- shared API client
- auth storage strategy
- protected-route wrapper
- global error boundary

### Workstream 2: Design System
Build:
- CSS variable palette
- layout primitives
- metric cards
- status pills
- data tables
- empty-state components
- degraded-state banners
- operator action buttons
- form inputs and auth states

### Workstream 3: Data and Session Layer
Build:
- login client
- token persistence
- auth guard
- request wrapper with bearer token
- session-expired interceptor
- typed response models for current backend payloads

### Workstream 4: Dashboard Pages
Build:
- login page
- dashboard overview
- today page
- performance page
- stability page
- learning page
- providers page
- operations page

### Workstream 5: Operator Actions
Build:
- UI actions for:
  - run live slate
  - run scheduler once
  - grade outcomes
  - review stability
  - run learning review
- in-flight state
- success/failure toast or panel
- inline returned payload display

### Workstream 6: Truthfulness and Recovery UX
Build:
- empty-state language
- degraded-source banners
- insufficient-data cards
- auth-expired redirect
- backend-unreachable state
- retry controls

## Recommended File Structure

- `dashboard/package.json`
- `dashboard/tsconfig.json`
- `dashboard/vite.config.ts`
- `dashboard/index.html`
- `dashboard/src/main.tsx`
- `dashboard/src/App.tsx`
- `dashboard/src/styles/`
- `dashboard/src/routes/`
- `dashboard/src/pages/Login.tsx`
- `dashboard/src/pages/Dashboard.tsx`
- `dashboard/src/pages/Today.tsx`
- `dashboard/src/pages/Performance.tsx`
- `dashboard/src/pages/Stability.tsx`
- `dashboard/src/pages/Learning.tsx`
- `dashboard/src/pages/Providers.tsx`
- `dashboard/src/pages/Operations.tsx`
- `dashboard/src/components/`
- `dashboard/src/lib/api.ts`
- `dashboard/src/lib/auth.ts`
- `dashboard/src/lib/types.ts`
- `dashboard/src/lib/format.ts`
- `dashboard/src/hooks/`

## Data Truth Rules By Surface

### Today Page
- show what backend returned
- do not infer missing fields
- if predictions are empty, say no current live predictions are available

### Performance Page
- do not show fake profit graphs unless backend supports them
- run-count, bet/lean/skip distribution, and run summaries are acceptable now

### Stability Page
- treat `insufficient_data` as a first-class status, not as an error

### Learning Page
- treat `candidate_model_version = null` as a valid system state

### Providers Page
- degraded providers are not hidden
- fallback usage must remain visible

## UX Rules

1. Show timestamps in a readable local format and preserve raw IDs where useful.
2. Never collapse `SKIP` out of the primary surface.
3. Never present learning or drift as stronger than the actual evidence.
4. Keep auth/session errors understandable.
5. Keep the interface responsive on laptop and mobile widths.
6. Use confirmation dialogs or inline confirms for operator job triggers.
7. Preserve operator trust over visual cleverness.

## Manual Inputs Needed Later
- whether the dashboard should auto-open after backend startup
- final frontend port confirmation if `3000` changes
- whether operator actions should use modal confirmations or inline confirmations by default

## Acceptance Criteria
Phase 4B is acceptable only if:
- login works end to end against the real backend
- protected routes redirect correctly when unauthenticated or expired
- dashboard overview, today, performance, stability, learning, providers, and operations pages render from real API payloads
- operator actions can be triggered from the UI and show returned results honestly
- degraded state, fallback usage, `SKIP`, and insufficient-data conditions remain visible
- no page depends on reading local files directly
- the UI is readable and stable on both desktop and mobile

## Exit Rule
Do not move to Phase 4C until all three are true:
- the frontend is fully usable against the real Phase 4A contract
- operator workflows can be run from the UI without terminal dependence
- the remaining work is mainly final integration, recovery hardening, and production polish rather than major missing features
