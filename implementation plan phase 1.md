# NBA Oracle Phase 1 Implementation Plan

## Purpose
Phase 1 is the validation core. Its job is to prove that the model can be trusted before any real betting output is treated as actionable.

This phase exists because the README and planning docs agree on one thing: the system is not ready to bet until it can prove frozen replay, honest probabilities, hard skip discipline, source trust, and price discipline.

## Source of Truth
This plan is derived from:
- [README.md](./README.md)
- [problems plan.md](./problems%20plan.md)
- [ftw plan.md](./ftw%20plan.md)

## Phase 1 Goal
Build the smallest possible validation layer that can answer this question:

> Can the model survive a leakage-free replay and produce calibrated, selective, price-aware decisions that are better than random or forced action?

If the answer is not yes, the system should not move toward live betting.

## Phase 1 Scope

### In scope
- Frozen pre-tip-off snapshot handling
- Point-in-time backtest logic
- Calibration evaluation
- No-bet decision gate
- Source freshness and trust scoring
- Basic market and price comparison
- Baseline reporting for review

### Out of scope
- Full dashboard polish
- Learning loop automation
- Multi-market expansion beyond the core moneyline use case
- Prop betting
- Advanced social scraping coverage
- Any live betting automation

## What Phase 1 Must Prove

1. The model only sees information that existed before the decision timestamp.
2. The model can replay historical slates consistently.
3. The model's confidence is roughly honest when compared to actual outcomes.
4. The model says no when the edge is weak or the data is stale.
5. The model can compare its own number to the market and detect bad prices.
6. The model can produce a clean report that shows why a pick was or was not active.

## Implementation Steps

### Step 1: Define the frozen snapshot contract
- Every source must carry:
  - `decision_time`
  - `source_time`
  - `source_version`
- The replay engine must only read snapshots that existed before `decision_time`.
- Any post-tip-off or post-lock information must be rejected.

### Step 2: Define the replay input shape
- Create one normalized pregame record per matchup.
- The record should include:
  - game metadata
  - odds snapshot
  - injury snapshot
  - team stats snapshot
  - sentiment snapshot if available
  - timestamp metadata for every source
- The replay must use the same shape for live-style and historical-style runs.

### Step 3: Define the selection logic for replay
- Use the same theoretical decision rules that the live model would use.
- Keep the logic deterministic enough to audit.
- Return one of three outputs for each game:
  - `BET`
  - `LEAN`
  - `SKIP`

### Step 4: Define the calibration gate
- Group predictions into probability bins.
- Compare predicted probability against observed win rate.
- Reject any model state that is materially miscalibrated.
- Use calibration as a trust gate, not a vanity metric.

### Step 5: Define the no-bet gate
- Require a minimum edge threshold.
- Require freshness and market support before activation.
- Default weak or conflicting spots to `SKIP`.
- Log skip reasons so the system can later audit its own restraint.

### Step 6: Define the price check
- Compare the model's number against the best available number.
- Compare Stake to the broader market if a better reference is available.
- Downgrade or skip bad prices even if the directional read is correct.

### Step 7: Define the first reporting output
- Create a replay report that shows:
  - hit rate
  - ROI
  - CLV
  - calibration by probability bin
  - skip rate
  - active bet count
  - key skip reasons
- The report should make it obvious whether the model is selective or just noisy.

## Acceptance Criteria
Phase 1 is acceptable only if all of the following are true:
- Replay uses frozen pre-tip-off data only.
- Results are reproducible for the same historical slate.
- Calibration is measurable and not obviously broken.
- Skip is a real output, not a hidden failure.
- Price comparison is part of the recommendation flow.
- The replay report is readable enough to review without code tracing.

## Risks
- Hindsight leakage can fake edge if snapshot timing is not strict.
- Calibration can look fine in aggregate while still failing in key bins.
- Skip logic can become too aggressive and kill all useful action.
- Price comparisons can be misleading if the reference market is poor.
- A strong-looking report can still hide bad source quality unless freshness is explicit.

## Phase 1 Deliverables
- Frozen snapshot specification
- Replay specification
- Calibration gate specification
- No-bet gate specification
- Source trust/freshness specification
- Price comparison specification
- Baseline validation report template

## Phase 1 Exit Rule
Do not move to the next phase until the validation core can prove, on frozen historical data, that the system is:
- leakage-free,
- calibrated enough to trust,
- selective enough to skip weak bets,
- and disciplined enough to respect price and source quality.

## Why This Phase Comes First
This phase is the foundation for the whole money-making theory in the README.

If Phase 1 fails, the system is not a betting system yet. It is only a prediction narrative.
