# NBA Oracle Phase 6 Final One-Shot Implementation Plan

## Purpose
Phase 6 is the final operator-convenience and runtime-automation pass.

Phases 1 through 5 built the model, the live data path, the review workflows, the operating dashboard, the hosted access path, and the comprehension layer.

That means NBA Oracle can already function as a real pregame operator system.

What still remains is an operations gap:

> The product works, but it still depends too much on manual startup and manual recurring execution for normal day-to-day use.

Phase 6 exists to close that gap in one coherent pass without changing the core model logic.

## What Changed Since The First Phase 6 Draft
The original Phase 6 plan focused on convenience and automation at a high level.

Since then, two important realities became clearer through real usage and audit work:
- the daily evidence loop matters just as much as startup convenience
- runtime truth must stay explicit, especially around what is automatic, what is manual, and what is merely visible in the dashboard

Recent validated changes that now shape this final plan:
- official outcome fetching now retries and falls back safely when the primary NBA endpoint stalls
- synthetic runtime runs are now filtered out of live grading summaries
- the real postgame bridge today is `python main.py run-scheduler-once`

So this final Phase 6 plan is not just about launching the stack more easily. It is about making the full operating loop livable, repeatable, and trustworthy.

## Source of Truth
This plan is derived from:
- [master-spec.md](../../spec/master-spec.md)
- [project-status-matrix.md](../../status/project-status-matrix.md)
- [changes-matrix.md](../../status/changes-matrix.md)
- [phase-4c.md](./phase-4c.md)
- [phase-5.md](./phase-5.md)
- [phase-7.md](./phase-7.md)
- [deployment.md](../../runbooks/deployment.md)
- [recovery.md](../../runbooks/recovery.md)

It is grounded in the current runtime path:
- [cli.py](../../../nba_oracle/cli.py)
- [meta_scheduler.py](../../../nba_oracle/runtime/meta_scheduler.py)
- [jobs.py](../../../nba_oracle/runtime/jobs.py)
- [startup.py](../../../nba_oracle/runtime/startup.py)
- [grade_outcomes.py](../../../nba_oracle/runs/grade_outcomes.py)
- [fetcher.py](../../../nba_oracle/outcomes/fetcher.py)

## Fixed Reality Phase 6 Must Respect

1. Phase 6 is not a model redesign.
2. Phase 6 is not a frontend redesign.
3. Phase 6 must improve convenience without hiding operational truth.
4. The deployment shape remains:
   - local dashboard as the recommended free daily workflow
   - optional `Vercel` frontend for hosted access
   - local backend
   - optional `Cloudflare Tunnel`
   - `Supabase`
5. The scheduler must run often enough to catch the built-in pregame decision window.
6. The evidence loop must remain honest about what is graded, what is pending, and what is synthetic.
7. Dashboard visibility is not the same as backend operation.
8. Backend operation is not the same as recurring scheduler execution.

## Phase 6 Goal
Make NBA Oracle operationally smoother and more automatic for normal daily use.

This pass should reduce friction in five areas:
1. starting the real daily operating stack with less friction
2. keeping the scheduler running on a useful cadence
3. making the daily operator workflow explicit and easy to follow
4. handling local-backend-plus-optional-tunnel reality more cleanly
5. keeping the postgame evidence loop trustworthy and low-friction

## In Scope
- local dashboard daily workflow guidance
- hosted-mode startup launcher
- recurring scheduler execution on Windows
- runbook updates for daily operation
- clearer documentation of what runs automatically versus manually
- tunnel/runtime reliability guidance
- evidence-loop reliability hardening as part of the operating story
- small helper artifacts for operating the system cleanly

## Out of Scope
- new model features
- direct Stake integration
- autonomous bet placement
- live in-game betting
- new dashboard pages
- replacing the deployment shape
- Phase 7 intelligence changes

## Problems This Final Plan Solves

### Problem 1: The free daily workflow was not explicit enough
Normal free usage is more stable through:
- one backend terminal
- one local dashboard terminal

Hosted access is still functional, but quick tunnels make it a weaker default daily workflow.

### Problem 2: The scheduler exists, but recurring execution still does not
The system already knows when jobs are due.

But unless `python main.py run-scheduler-once` is executed repeatedly, nothing new happens:
- no fresh live slate
- no outcome grading
- no stability follow-up
- no learning follow-up

### Problem 3: The operator truth can still be misunderstood
There are four different runtime states that must not be conflated:
- dashboard open
- backend running
- tunnel available
- scheduler recurring

Phase 6 needs to make those distinctions explicit.

### Problem 4: Tunnel-backed hosted operation is workable, but still brittle
Quick tunnel URLs can rotate, and recovery depends on the operator knowing:
- what changed
- which env values matter
- what must be restarted

### Problem 5: The postgame evidence loop must stay operationally trustworthy
The system is only as good as its ability to:
- fetch official finals reliably
- backfill real outcomes into stored predictions
- avoid letting synthetic runtime artifacts distort live summaries

That means the grading path belongs inside the Phase 6 operating story, not as an isolated backend detail.

## Final One-Shot Execution Order
Phase 6 should be executed in this order and treated as one pass:

1. lock the free-first daily workflow into the docs
2. create the hosted startup launcher
3. add recurring scheduler automation
4. tighten runtime and tunnel recovery guidance
5. rewrite the daily operator workflow around the real system behavior
6. verify the full loop:
   - startup
   - scheduler cadence
   - live-slate timing
   - postgame grading
   - stability follow-up
   - learning follow-up

Do not split this phase into scattered convenience changes. It should land as one operational closeout.

## Workstreams

### Workstream 1: Free-First Workflow Clarification
Document and standardize:
- backend on `http://127.0.0.1:8000`
- dashboard on `http://localhost:3000`
- scheduler task in the background

Expected outcome:
- the operator treats local dashboard mode as the normal free daily path

### Workstream 2: Hosted Startup Launcher
Create a single hosted-mode launcher that:
- starts the backend
- starts Cloudflare Tunnel

Required deliverable:
- one `.bat` file for hosted mode only

Expected outcome:
- hosted usage becomes one simple launch action instead of two separate terminal rituals

### Workstream 3: Recurring Scheduler Automation
Set up external recurring execution for:

```powershell
python main.py run-scheduler-once
```

Required platform:
- Windows Task Scheduler

Recommended cadence:
- every `30` minutes

Acceptable fallback cadence:
- every `60` minutes

Reason:
- the internal scheduler is built around a pregame target window roughly `2` hours before tipoff
- a `4` hour cadence is too sparse to catch that window reliably

Expected outcome:
- the system keeps collecting, grading, reviewing, and feeding the evidence loop even when the operator does not manually open the dashboard that day

### Workstream 4: Daily Operator Workflow Rewrite
Document the real day-to-day operator flow:
- what must be started
- what remains running
- what becomes automatic once scheduler recurrence exists
- what still remains manual
- what happens on no-slate days
- what happens after games finish

The workflow must explicitly separate:
- visible dashboard state
- runtime state
- evidence state

Expected outcome:
- a new operator can understand how to use NBA Oracle day to day without guessing

### Workstream 5: Tunnel and Runtime Recovery Polish
Clarify and harden the reality of the tunnel-backed deployment:
- quick tunnel URL rotation
- env-update implications when URLs change
- fallback workflow when the tunnel is down
- exact restart order for backend and tunnel
- guidance for hosted dashboard availability checks

Expected outcome:
- fewer operator mistakes during hosted access failures
- less confusion about when the app is actually reachable

### Workstream 6: Evidence-Loop Operational Hardening
Treat the daily grading and review loop as an operations feature, not just a backend command.

Required expectations:
- official outcome fetches degrade safely instead of failing the whole loop when the primary endpoint is slow
- synthetic runtime runs do not pollute live grading summaries
- postgame operator guidance prefers `python main.py run-scheduler-once`
- direct `python main.py grade-outcomes` remains documented as the focused fallback path

Expected outcome:
- the daily evidence loop is operationally reliable enough to support future Phase 7 intelligence work

## Required Deliverables

1. one documented free-first local workflow
2. one hosted-mode `.bat` launcher
3. one documented Windows Task Scheduler setup path for recurring scheduler execution
4. updated deployment and recovery runbooks
5. updated daily operator workflow documentation
6. explicit docs clarifying:
   - dashboard open vs backend running
   - backend running vs scheduler recurring
   - predictions stored vs outcomes graded
7. verified evidence-loop hardening included in the Phase 6 operating story

## Implementation Areas

- `nba_oracle/cli.py`
- `nba_oracle/runtime/meta_scheduler.py`
- `docs/runbooks/deployment.md`
- `docs/runbooks/recovery.md`
- `docs/runbooks/`
- repo-root helper scripts or batch files

Already-landed supporting files that Phase 6 must account for:
- [grade_outcomes.py](../../../nba_oracle/runs/grade_outcomes.py)
- [fetcher.py](../../../nba_oracle/outcomes/fetcher.py)

## Manual Operator Truth During Phase 6
Until recurring automation is fully set up, the real bridge remains:

- pregame:
  - run the live-slate workflow when needed
- postgame:
  - run `python main.py run-scheduler-once`
- focused grading fallback:
  - run `python main.py grade-outcomes`

This must remain explicit in the docs until Workstream 2 is actually implemented and verified.

## Acceptance Criteria
Phase 6 is acceptable only if:

1. The free local dashboard workflow is explicit and easy to follow.
2. The hosted operating stack can be started with one simple launcher.
3. The scheduler can run on a recurring cadence without manual command entry each time.
4. It is clear that the dashboard being open does not itself mean the intelligence layer is running.
5. It is clear that backend uptime alone does not guarantee scheduler execution.
6. The system can keep collecting, grading, and reviewing data even when the operator is not manually opening the dashboard that day.
7. The docs explain the daily operating reality cleanly.
8. Outcome grading remains reliable enough for daily use even when the primary official endpoint is slow.
9. Synthetic runtime artifacts do not pollute live grading summaries.

## Final Exit Rule
Do not call Phase 6 complete until:

1. startup friction is materially lower
2. recurring scheduler execution is actually set up and documented
3. the local free daily workflow is the documented default
4. the operator workflow is easier to follow day to day
5. the hosted runtime path feels operational instead of improvised when used
6. the evidence loop is operationally trustworthy for daily postgame use
7. the repo docs match the real operator workflow exactly
