# NBA Oracle Phase 3 Implementation Plan

## Purpose
Phase 3 is the stability layer. Its job is to make the live model durable enough to trust over time after Phase 2 proved that real upstream data can be ingested, normalized, scored, and stored.

This phase exists because a live model that works today can still drift, overreact, expand too early, or let the explanation layer quietly overrule the decision engine. Phase 3 is where the system learns to stay narrow, measurable, and stable.

## Source of Truth
This plan is derived from:
- [master-spec.md](../../spec/master-spec.md)
- [project-status-matrix.md](../../status/project-status-matrix.md)
- [changes-matrix.md](../../status/changes-matrix.md)
- [problems-plan.md](../problems-plan.md)
- [ftw-plan.md](../ftw-plan.md)
- [phase-1.md](./phase-1.md)
- [phase-2.md](./phase-2.md)
- [phase-2-1.md](./phase-2-1.md)

## Phase 3 Goal
Build the first stability layer that can answer this question:

> Can the live model detect when it is drifting, react to fresh information at the right speed, avoid expanding into immature markets, and preserve predictor authority without weakening the replay-based trust rules?

If the answer is not yes, the system should not move toward user-facing delivery, automated scheduling, or a broader betting surface.

## Phase 3 Scope

### In scope
- Drift monitoring against the validated baseline
- Retraining discipline and model promotion rules
- Timing-priority rules for fresh late-breaking information
- Market readiness and scope control
- LLM containment and decision-authority enforcement
- Stability reporting and health review outputs
- Controlled execution paths for stability review

### Out of scope
- Telegram bot delivery
- Gmail notifications
- Dashboard UI
- Auth
- Full self-learning automation
- Full scheduler/runtime deployment
- Autonomous bet placement

## What Phase 3 Must Prove

1. Live performance can be compared to a stable historical baseline, not just judged by short-term vibes.
2. The system can detect meaningful drift in ROI, CLV, calibration, and skip quality.
3. Fresh late information can change a decision faster than stale context.
4. Market expansion is controlled by readiness gates instead of ambition.
5. The predictor remains the final decision authority even when an LLM explanation layer is introduced later.
6. Stability evidence can be reviewed from clean reports without tracing code by hand.

## Phase 3 Design Rules

1. Keep the Phase 1 replay gate as the final trust anchor.
2. Prefer explicit thresholds over fuzzy “looks off” logic.
3. Treat retraining as a controlled promotion event, not an automatic reflex.
4. Keep moneylines as the only active market unless readiness rules explicitly unlock more.
5. Let explanation layers narrate the decision, but never own it.
6. Record every stability downgrade, retrain trigger, and market lock with enough evidence to audit later.

## Implementation Steps

### Step 1: Define the baseline contract
- Capture a stable baseline from validated replay and recent live runs.
- The baseline should include:
  - calibration metrics
  - ROI
  - CLV
  - skip rate
  - active-bet rate
  - provider health expectations
- Store baseline metadata separately from live run output so comparisons stay explicit.

### Step 2: Build drift monitoring
- Add a drift monitor that compares rolling live performance against the baseline.
- Measure:
  - ROI drift
  - CLV drift
  - calibration drift
  - skip-quality drift
  - provider degradation frequency
- Distinguish “random bad stretch” from “persistent model decay.”

### Step 3: Build retraining discipline
- Define a model review and promotion path.
- Require:
  - enough new observations
  - a drift trigger or explicit operator review
  - replay proof on the candidate model before promotion
- Keep a registry of:
  - current model version
  - candidate version
  - baseline metrics
  - promotion reason
  - rollback reason if needed

### Step 4: Build timing-priority rules
- Add a timing engine that re-scores when late-breaking information arrives.
- Prioritize:
  - verified injury changes
  - lineup/availability changes
  - fast market movement
- Require the system to record:
  - what changed
  - when it changed
  - whether the pick changed
  - whether the market had already moved

### Step 5: Build market scope control
- Introduce market readiness flags.
- Keep:
  - moneylines as active
  - totals as locked by default
  - props as locked by default
- Define unlock rules using:
  - sample size
  - calibration stability
  - CLV stability
  - skip discipline
- The model must not silently expand its market surface.

### Step 6: Build LLM containment
- Define a strict contract for any future analyst layer.
- The LLM may:
  - summarize
  - explain
  - format rationale
- The LLM may not:
  - alter probabilities
  - activate a skipped bet
  - downgrade or upgrade market readiness
  - override the predictor
- Log any disagreement between predictor output and explanation output.

### Step 7: Build Phase 3 reporting
- Add a stability report that shows:
  - baseline vs current live metrics
  - drift flags
  - retrain recommendation state
  - timing-trigger events
  - market readiness status
  - predictor-vs-analyst authority status
- The report should make it obvious whether the model is stable enough to operate.

### Step 8: Build the Phase 3 review path
- Add a controlled command or workflow that:
  - reviews recent live runs
  - compares them to the baseline
  - emits drift and readiness findings
  - does not promote a new model automatically
- This remains an operator review flow, not an autonomous optimization loop.

## Recommended Module Additions

### New package areas
- `nba_oracle/stability/`
- `nba_oracle/models_registry/`

### Likely first files
- `stability/baseline.py`
- `stability/drift.py`
- `stability/timing.py`
- `stability/readiness.py`
- `stability/reporting.py`
- `models_registry/catalog.py`
- `runs/review_stability.py`

## Manual Inputs Needed Later

These should be asked for during implementation, not guessed:
- rolling window size for drift review
- minimum sample size before retraining is considered
- how conservative market unlocking should be
- whether analyst-layer logging should begin in Phase 3 or Phase 4

## Acceptance Criteria
Phase 3 is acceptable only if all of the following are true:
- A measurable baseline exists for live-vs-replay comparison.
- Drift can be detected without manual spreadsheet work.
- Retraining is gated by evidence, not mood.
- Timing-trigger events can be observed and audited.
- Moneylines remain the only active market unless readiness rules explicitly unlock more.
- Predictor authority is preserved even if explanation scaffolding is introduced.
- Stability review output is readable enough to judge system health quickly.

## Risks
- Drift thresholds can be too sensitive and create false alarms.
- Retraining can become noisy if sample sizes are too small.
- Timing logic can overreact to rumor-quality information.
- Market unlocking can happen too early if readiness rules are weak.
- LLM containment can be undermined if explanation output leaks into the decision path.

## Phase 3 Deliverables
- Baseline specification
- Drift-monitoring specification
- Retraining and promotion specification
- Timing-engine specification
- Market-readiness specification
- LLM-containment specification
- Phase 3 stability report template
- Phase 3 review workflow

## Phase 3 Exit Rule
Do not move to the next phase until the system can show, on recent live operation and validated replay evidence, that it:
- detects meaningful drift,
- preserves a controlled retraining path,
- reacts correctly to fresh information,
- stays within approved market scope,
- and keeps the predictor as the only decision authority.

## Why This Phase Comes Next
Phase 2 proved the system can ingest the world and produce live predictions.

Phase 3 is where the system proves it can stay sane after that. Without it, the model can still decay, overexpand, or let soft logic creep into hard betting decisions.
