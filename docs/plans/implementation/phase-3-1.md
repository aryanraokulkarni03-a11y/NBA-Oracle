# NBA Oracle Phase 3.1 Implementation Plan

## Purpose
Phase 3.1 is the hardening pass for Phase 3.

Phase 3 established the first real stability-review workflow, but it did not finish the full contract defined in the master spec and the original Phase 3 plan. Phase 3.1 exists to close those gaps in one focused pass before the project moves any closer to delivery, UI work, or automated runtime behavior.

This pass is not about adding a new product surface. It is about making the existing stability layer trustworthy enough to rely on.

## Source of Truth
This plan is derived from:
- [master-spec.md](../../spec/master-spec.md)
- [project-status-matrix.md](../../status/project-status-matrix.md)
- [changes-matrix.md](../../status/changes-matrix.md)
- [phase-3.md](./phase-3.md)
- the current Phase 3 implementation in:
  - [baseline.py](../../../nba_oracle/stability/baseline.py)
  - [drift.py](../../../nba_oracle/stability/drift.py)
  - [timing.py](../../../nba_oracle/stability/timing.py)
  - [readiness.py](../../../nba_oracle/stability/readiness.py)
  - [reporting.py](../../../nba_oracle/stability/reporting.py)
  - [review_stability.py](../../../nba_oracle/runs/review_stability.py)
  - [catalog.py](../../../nba_oracle/models_registry/catalog.py)

## Why Phase 3.1 Exists
The current Phase 3 implementation is good enough to review recent live behavior, but not good enough to call complete.

The main misses are:
- drift does not yet include ROI, CLV, or calibration
- retraining discipline is only a recommendation flag, not a real controlled workflow
- timing review is aggregate-only and does not log concrete decision-change events
- market readiness is still policy-locked instead of evidence-driven
- analyst containment is declared, but disagreement logging is not implemented
- the saved baseline can silently go stale
- one status doc still frames the project as “ready to move into Phase 3” even though Phase 3 is already active

Phase 3.1 should fix those gaps as one coherent closeout pass.

## Phase 3.1 Goal
Make the Phase 3 stability layer complete enough to answer this question honestly:

> Can the system compare live behavior to a trustworthy baseline, detect meaningful degradation with the right metrics, log timing and authority events explicitly, and enforce a real evidence-based review path before any model promotion or market expansion happens?

If the answer is not yes, the project should not move to Phase 4.

## In Scope
- ROI, CLV, and calibration-aware drift review
- baseline freshness and baseline refresh rules
- retraining review workflow and model promotion bookkeeping
- timing-event logging and decision-change audit trail
- evidence-based market readiness evaluation
- analyst disagreement logging contract
- status/doc cleanup so the repo tells the truth about current state

## Out of Scope
- dashboard UI
- Telegram or Gmail delivery
- actual LLM explanation generation
- autonomous retraining
- autonomous market unlocking
- scheduler/runtime deployment

## Problem List To Close

### Problem 1: Drift metrics are incomplete
Current drift only checks:
- active-bet rate
- skip rate
- source quality
- edge
- provider degradation

Phase 3.1 must add:
- ROI drift
- CLV drift
- calibration drift
- clearer separation between:
  - insufficient sample
  - soft warning
  - real retraining review trigger

### Problem 2: Baseline reuse can become stale
The current saved baseline is reused indefinitely once it exists.

Phase 3.1 must add:
- baseline metadata versioning
- baseline refresh triggers
- explicit reasons for refresh, such as:
  - model version change
  - threshold/config change
  - replay report change
  - explicit operator refresh request

### Problem 3: Retraining discipline is not operationalized
Current logic only sets `retraining_recommended`.

Phase 3.1 must add:
- model registry records, not just a static dict
- candidate model metadata
- promotion reason
- rollback reason
- replay gate requirement before promotion
- manual review status markers such as:
  - `no_review`
  - `review_open`
  - `candidate_waiting_for_replay`
  - `eligible_for_promotion`
  - `rolled_back`

### Problem 4: Timing review is too shallow
Current timing is aggregate-only.

Phase 3.1 must add timing-event tracking that records:
- what changed
- source kind
- source timestamp
- decision timestamp
- whether the predictor output changed
- whether the market had already moved
- whether the event strengthened, weakened, or canceled a bet

### Problem 5: Market readiness is not evidence-based yet
Current readiness keeps moneylines active and everything else locked, but it does not evaluate the actual unlock rules described in the Phase 3 plan.

Phase 3.1 must add readiness evidence for each market family:
- graded sample count
- calibration stability
- CLV stability
- skip-discipline health
- operator review requirement before unlock

Even if totals and props remain locked after this pass, the reason must be evidence-backed, not just policy-backed.

### Problem 6: Analyst containment is not fully auditable
Current logic declares containment but does not log disagreements.

Phase 3.1 must add:
- analyst-contract schema
- predictor output snapshot
- optional analyst output snapshot
- disagreement log entries when both exist
- explicit rule that the predictor wins every conflict

### Problem 7: Docs still contain stale state language
The status docs should no longer say the project is merely “ready to move into Phase 3.”

Phase 3.1 must clean up:
- current checkpoint language
- next-step recommendations
- status wording around what is really done vs still missing

## Implementation Steps

### Step 1: Harden the baseline contract
- Extend the saved baseline format with:
  - model version
  - config fingerprint
  - replay report fingerprint
  - baseline schema version
  - creation reason
- Add logic that decides whether to:
  - reuse baseline
  - refresh baseline
  - refuse comparison because the baseline is incompatible

### Step 2: Add richer drift metrics
- Extend drift inputs to include:
  - ROI
  - CLV
  - calibration gap
  - active-bet rate
  - skip rate
  - provider degradation
- Keep sample-size-aware behavior so the system does not overreact to tiny live windows
- Make the report separate:
  - observed metrics
  - thresholds
  - trigger state
  - why retraining is or is not allowed yet

### Step 3: Build a real retraining review path
- Add a model-registry store under `nba_oracle/models_registry/`
- Track:
  - active model
  - candidate model
  - review status
  - promotion reason
  - rollback reason
- Add a CLI or review artifact path that does not promote automatically, but does create the review record

### Step 4: Build timing-event logging
- Introduce a timing-events file or persisted artifact per review window
- Capture:
  - source change events
  - market move events
  - decision changes
  - event ordering
- Make timing status depend on both:
  - freshness metrics
  - event-handling behavior

### Step 5: Build evidence-backed market readiness
- Keep moneylines active
- Keep totals and props locked unless evidence qualifies them
- For every locked market, report:
  - why it is still locked
  - what evidence is missing
  - what threshold it has not yet met

### Step 6: Build analyst disagreement logging
- Define a lightweight analyst payload model now, even if the full LLM layer still does not exist
- Store:
  - predictor decision snapshot
  - analyst suggestion snapshot
  - disagreement type
  - final authority outcome
- Make disagreement logging optional if no analyst payload exists, but mandatory when one does

### Step 7: Upgrade reporting
- Expand the markdown and JSON stability reports to show:
  - baseline freshness status
  - ROI/CLV/calibration drift
  - retraining review state
  - timing-event summaries
  - market unlock evidence
  - analyst disagreement summary

### Step 8: Clean up docs and status truthfulness
- Update:
  - [README.md](../../../README.md)
  - [project-status-matrix.md](../../status/project-status-matrix.md)
  - [changes-matrix.md](../../status/changes-matrix.md)
- Make Phase 3 wording consistent everywhere
- Clearly separate:
  - what Phase 3 now does
  - what Phase 3.1 fixes
  - what still remains before Phase 4

## Recommended Module Additions

### New or expanded files
- `nba_oracle/stability/baseline.py`
- `nba_oracle/stability/drift.py`
- `nba_oracle/stability/timing.py`
- `nba_oracle/stability/readiness.py`
- `nba_oracle/stability/reporting.py`
- `nba_oracle/models_registry/catalog.py`
- `nba_oracle/models_registry/` review-state files or helpers
- `nba_oracle/runs/review_stability.py`
- `tests/test_phase3.py`
- `tests/test_phase3_1.py` if the new scope becomes large enough

## Manual Inputs Needed
These should be confirmed during implementation, not guessed if the defaults need to change:
- whether baseline refresh should happen automatically on replay/config drift or only with operator approval
- whether retraining review records should be stored locally only or in Supabase too
- whether analyst disagreement logs should start local-only first or be persisted remotely as well

Recommended defaults:
- automatic baseline refresh on incompatible baseline metadata
- local-first retraining review records in Phase 3.1
- local-first analyst disagreement logs in Phase 3.1

## Acceptance Criteria
Phase 3.1 is acceptable only if all of the following are true:
- drift reporting includes ROI, CLV, calibration, skip discipline, and provider health
- the baseline can no longer silently go stale
- retraining review has a real tracked workflow
- timing review produces auditable event records, not only aggregates
- non-moneyline markets remain locked or unlock only with evidence shown in the report
- analyst disagreement logging exists when analyst payloads are present
- docs and status files accurately reflect the true state of the project

## Risks
- adding too much sensitivity to drift metrics can create false alarms
- baseline refresh logic can become noisy if fingerprints are too fragile
- timing-event logging can produce a lot of low-value noise if not filtered
- retraining review can look “real” without enough graded outcomes if thresholds are weak
- market readiness evidence can be misleading if there is not enough sample depth yet

## Deliverables
- Phase 3.1 implementation plan
- upgraded drift engine specification
- baseline refresh specification
- retraining review and promotion bookkeeping specification
- timing-event logging specification
- market-readiness evidence specification
- analyst disagreement logging specification
- upgraded Phase 3 reporting specification
- cleaned status/docs language

## Exit Rule
Do not call Phase 3 complete until the system can show:
- a stable or explicitly refreshed baseline
- drift metrics that include ROI, CLV, and calibration
- a tracked retraining review path
- auditable timing-event output
- evidence-backed market locks
- predictor authority that is enforced and auditable

## Why This Pass Matters
Phase 3 got the project from “live prediction engine” to “first real stability review.”

Phase 3.1 is what turns that into a trustworthy operating layer instead of a smart-looking checkup command.
