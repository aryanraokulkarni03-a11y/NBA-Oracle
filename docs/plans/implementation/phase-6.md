# NBA Oracle Phase 6 Implementation Plan

## Purpose
Phase 6 is the operator-convenience and runtime-automation pass.

Phases 1 through 5 built the model, the live data path, the review workflows, the operating dashboard, the hosted access path, and the comprehension layer.

That means NBA Oracle can now function as a real pregame operator system.

But there is still an operating gap:

> The product works, yet it still depends too much on manual startup and manual recurring execution.

Phase 6 exists to make NBA Oracle easier to live with day to day without changing the core model logic.

## Source of Truth
This plan is derived from:
- [master-spec.md](../../spec/master-spec.md)
- [project-status-matrix.md](../../status/project-status-matrix.md)
- [changes-matrix.md](../../status/changes-matrix.md)
- [phase-4c.md](./phase-4c.md)
- [phase-5.md](./phase-5.md)
- [deployment.md](../../runbooks/deployment.md)
- [recovery.md](../../runbooks/recovery.md)

It is grounded in the current runtime path:
- [cli.py](../../../nba_oracle/cli.py)
- [meta_scheduler.py](../../../nba_oracle/runtime/meta_scheduler.py)
- [jobs.py](../../../nba_oracle/runtime/jobs.py)
- [startup.py](../../../nba_oracle/runtime/startup.py)

## Phase 6 Goal
Make the system operationally smoother and more automatic for normal daily use.

Phase 6 should reduce friction in four areas:
1. starting the hosted operating stack
2. keeping the scheduler running on a useful cadence
3. making daily operator workflow explicit and easy to follow
4. handling local-backend-plus-tunnel reality more cleanly

## What Phase 6 Must Respect

1. Phase 6 is not a model redesign.
2. Phase 6 is not a frontend redesign.
3. Phase 6 should improve convenience and automation without hiding operational truth.
4. The hosted deployment shape remains:
   - `Vercel` frontend
   - local backend
   - `Cloudflare Tunnel`
   - `Supabase`
5. The scheduler must run often enough to catch the built-in pregame decision window.

## In Scope
- hosted-mode startup launcher
- recurring scheduler execution on Windows
- runbook updates for daily operation
- clearer documentation of what runs automatically versus manually
- tunnel/runtime reliability guidance
- small helper artifacts for operating the system cleanly

## Out of Scope
- new model features
- direct Stake integration
- autonomous bet placement
- live in-game betting
- new dashboard pages
- replacing the deployment shape

## The Problems Phase 6 Is Solving

### Problem 1: Hosted access currently takes two manual terminals
Today, normal hosted usage requires:
- backend terminal
- Cloudflare tunnel terminal

That is workable, but more manual than it should be.

### Problem 2: Scheduler intelligence exists, but recurring execution does not
The system already knows when jobs are due.

But unless `python main.py run-scheduler-once` is executed repeatedly, nothing new happens:
- no fresh live slate
- no outcome grading
- no stability follow-up
- no learning follow-up

### Problem 3: The app can be mistaken for “running automatically” when it is not
The dashboard can be open while the backend is not truly operating.

We need clearer runtime truth around:
- dashboard open vs backend running
- backend running vs scheduler being called
- stored predictions vs newly graded outcomes

### Problem 4: Tunnel-backed hosted operation is functional but still fragile
Quick tunnel URLs can change, and the current setup benefits from cleaner operator instructions and helper tooling.

## Workstreams

### Workstream 1: Hosted Startup Launcher
Create a single hosted-mode launcher that:
- starts the backend
- starts Cloudflare Tunnel

Recommended deliverable:
- one `.bat` file for hosted mode only

Deliverables:
- one-click hosted startup path
- reduced terminal friction for normal use

### Workstream 2: Recurring Scheduler Automation
Set up external recurring execution for:

```powershell
python main.py run-scheduler-once
```

Recommended platform:
- Windows Task Scheduler

Recommended cadence:
- every `30` or `60` minutes

Reason:
- the internal scheduler uses a pregame target window around `2` hours before tipoff
- a `4` hour cadence is too sparse to reliably catch that window

Deliverables:
- clear Task Scheduler setup path
- documented cadence recommendation
- operator confidence that the system continues collecting and reviewing even when the dashboard is not open

### Workstream 3: Daily Operator Workflow Cleanup
Document the real daily operating flow:
- what must be started
- what runs automatically once the scheduler is recurring
- what still needs manual intervention
- what happens on no-slate days
- what happens after games finish

Deliverables:
- simpler runbook language
- clearer daily checklist
- explicit distinction between “hosted dashboard visible” and “system actively operating”

### Workstream 4: Tunnel and Runtime Reliability Polish
Clarify and harden the reality of the tunnel-backed deployment:
- quick tunnel URL rotation
- env-update implications when URLs change
- fallback workflow when the tunnel is down
- recommended path toward a cleaner persistent tunnel later if desired

Deliverables:
- stronger tunnel troubleshooting guidance
- less confusion around hosted availability
- cleaner restart/recovery instructions

## Recommended Implementation Areas

- `nba_oracle/cli.py`
- `nba_oracle/runtime/meta_scheduler.py`
- `docs/runbooks/deployment.md`
- `docs/runbooks/recovery.md`
- `docs/runbooks/`
- repo-root helper scripts or batch files

## Concrete Deliverables

1. hosted-mode `.bat` launcher
2. recurring scheduler automation setup for Windows
3. runbook updates for daily operation
4. runbook updates for tunnel/restart behavior
5. explicit docs clarifying what is automatic vs what is manual

## Acceptance Criteria
Phase 6 is acceptable only if:

1. The hosted operating stack can be started with one simple launcher.
2. The scheduler can run on a recurring cadence without manual command entry each time.
3. It is clear that the dashboard being open does not itself mean the intelligence layer is running.
4. The system can keep collecting, grading, and reviewing data even when the operator is not manually opening the dashboard that day.
5. The docs explain the daily operating reality cleanly.

## Final Exit Rule
Do not call Phase 6 complete until:

1. startup friction is materially lower
2. recurring scheduler execution is set up and documented
3. the operator workflow is easier to follow day to day
4. the hosted runtime path feels operational, not improvised
