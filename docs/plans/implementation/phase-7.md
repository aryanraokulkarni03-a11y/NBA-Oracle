# NBA Oracle Phase 7 Implementation Plan

## Purpose
Phase 7 is the intelligence-upgrade pass.

Phases 1 through 5 built:
- replay validation
- live provider ingestion
- stability and grading workflows
- operating/dashboard infrastructure
- product clarity and operator guidance

That means NBA Oracle now works as an honest pregame moneyline workflow.

Phase 7 exists to answer the next serious question:

> How do we make the model materially smarter for daily NBA moneyline betting without turning the system into an overfit, overcomplicated black box?

The goal is not to add random complexity.

The goal is to improve:
- probability quality
- price sensitivity
- injury and lineup interpretation
- timing discipline
- uncertainty handling

## Source of Truth
This plan is derived from:
- [master-spec.md](../../spec/master-spec.md)
- [prediction-systems-and-public-sentiment-signals.md](../../research/prediction-systems-and-public-sentiment-signals.md)
- [project-status-matrix.md](../../status/project-status-matrix.md)
- [changes-matrix.md](../../status/changes-matrix.md)
- [phase-3.md](./phase-3.md)
- [phase-3-1.md](./phase-3-1.md)
- [phase-5.md](./phase-5.md)

It is grounded in the current shipped decision path:
- [predictor.py](../../../nba_oracle/predictor.py)
- [market.py](../../../nba_oracle/market.py)
- [source_scoring.py](../../../nba_oracle/source_scoring.py)
- [live_snapshot_builder.py](../../../nba_oracle/assembly/live_snapshot_builder.py)
- [schedule.py](../../../nba_oracle/providers/schedule.py)
- [odds.py](../../../nba_oracle/providers/odds.py)
- [injuries.py](../../../nba_oracle/providers/injuries.py)
- [stats.py](../../../nba_oracle/providers/stats.py)
- [trainer.py](../../../nba_oracle/learning/trainer.py)
- [patterns.py](../../../nba_oracle/learning/patterns.py)

## Phase 7 Goal
Upgrade NBA Oracle from a disciplined rules-plus-model pregame workflow into a stronger probability-and-timing system for daily NBA moneyline betting.

Phase 7 should make the system better at:
1. starting from a strong market prior
2. translating injuries and lineup context into real probability movement
3. recognizing when the edge is early, stale, or gone
4. separating model confidence from betting confidence
5. learning from graded outcomes without becoming reckless

## What Phase 7 Must Respect

1. NBA Oracle remains a pregame decision system, not a live in-game betting engine.
2. The system must stay honest about uncertainty.
3. New intelligence should improve decision quality, not just add more features.
4. The market remains a strong information source and should be treated as a prior, not ignored.
5. Every upgrade must preserve replayability, auditability, and the current no-bet discipline.

## In Scope
- market-as-prior probability design
- stronger team-strength features for pregame moneylines
- injury impact modeling beyond simple flag counts
- lineup/context-aware team strength adjustments
- timing and line-movement intelligence
- uncertainty-aware bet gating
- decision-quality upgrades for `BET`, `LEAN`, and `SKIP`
- calibration by meaningful moneyline buckets
- improved learning features for review-only candidate generation
- doc and runbook updates for the upgraded intelligence path

## Out of Scope
- live in-game win probability updates
- autonomous bet placement
- direct Stake integration
- new frontend redesign work
- totals/props modeling
- replacing the whole architecture with an opaque LLM-only system

## The Problems Phase 7 Is Solving

### Problem 1: The current system is disciplined, but still too blunt in how it forms probability
Right now the model has:
- pregame team context
- odds-derived market context
- injuries
- team metrics
- source quality gates

That is good enough to be honest.

It is not yet strong enough to fully capitalize on NBA moneyline edges where the market is already efficient.

### Problem 2: Injury intelligence is still too coarse
The system knows when injuries matter, but it is still too close to:
- flag counts
- basic summaries
- broad trust adjustments

It needs to understand:
- who is missing
- how much that player matters
- how lineups and team strength shift when key players are absent

### Problem 3: Timing edge is under-modeled
Pregame moneyline value often depends on:
- when the market moved
- whether the current number is stale
- whether the edge is already gone

The current system tracks timing operationally, but not deeply enough as predictive intelligence.

### Problem 4: Probability confidence and betting confidence are still too tightly coupled
A team can be likely to win and still be a bad bet.

That means the system needs to get better at separating:
- win probability quality
- bet-worthiness quality

### Problem 5: Learning exists, but the feature base can be smarter
The review-only learning loop is cautious, which is good.

But it still needs better features and better segment-level evaluation before it can propose meaningfully stronger candidate behavior.

## Workstreams

### Workstream 1: Market-As-Prior Architecture
Move the core logic toward:
- market-implied probability as the starting prior
- model adjustments layered on top of that prior
- explicit measurement of where and why the model departs from the market

Deliverables:
- clearer prior-plus-adjustment decision flow
- explicit probability decomposition
- more stable moneyline behavior in efficient markets

### Workstream 2: Team Strength and Lineup Context
Upgrade pregame team context using richer NBA features such as:
- net rating
- offensive/defensive strength
- pace context
- Four Factors style signals
- lineup-aware context when available

Deliverables:
- stronger baseline team-strength layer
- better favorite-vs-underdog behavior
- clearer matchup context before price comparison

### Workstream 3: Injury Impact Modeling
Translate injuries into expected effect instead of only counts or broad summaries.

Target logic:
- key-player weight
- expected minutes loss
- replacement quality
- team-side net effect

Deliverables:
- injury impact score
- more realistic probability movement from game-day availability changes
- better handling of star absences versus low-impact absences

### Workstream 4: Timing and Line-Movement Intelligence
Model the price path more explicitly:
- reference line
- best line
- opening line
- close when available
- time-to-tip
- line movement magnitude and direction

Deliverables:
- timing-aware decision logic
- stronger stale-edge detection
- better understanding of when a pregame signal should decay into `LEAN` or `SKIP`

### Workstream 5: Uncertainty-Aware Bet Gating
Add a stronger distinction between:
- raw win estimate
- confidence in that estimate
- willingness to recommend action

Deliverables:
- uncertainty score or confidence band
- stricter no-bet behavior in unstable contexts
- less overconfidence on noisy favorites

### Workstream 6: Segmented Calibration and Evaluation
Evaluate the model in betting-relevant buckets instead of only globally.

Suggested buckets:
- heavy favorites
- moderate favorites
- near coin-flips
- underdogs

Deliverables:
- segmented calibration review
- segmented EV/edge behavior checks
- more targeted model hardening

### Workstream 7: Learning-Layer Feature Upgrade
Improve the review-only learning workflow with stronger feature inputs from:
- team-strength deltas
- injury impact deltas
- timing/line movement
- segmented price behavior

Deliverables:
- better candidate-review signal quality
- more useful pattern mining
- stronger future retraining discipline

## Recommended Implementation Areas

- `nba_oracle/predictor.py`
- `nba_oracle/market.py`
- `nba_oracle/source_scoring.py`
- `nba_oracle/providers/injuries.py`
- `nba_oracle/providers/stats.py`
- `nba_oracle/assembly/live_snapshot_builder.py`
- `nba_oracle/learning/trainer.py`
- `nba_oracle/learning/patterns.py`
- `nba_oracle/stability/drift.py`
- `nba_oracle/stability/baseline.py`
- `tests/`

## Concrete Deliverables

1. market-prior probability layer
2. improved team-strength feature set for moneylines
3. injury impact feature layer
4. timing/line-movement feature layer
5. uncertainty-aware gating behavior
6. segmented calibration and evaluation outputs
7. upgraded learning-review feature inputs
8. test updates and validation checkpoints
9. doc and runbook updates explaining the new intelligence path

## Acceptance Criteria
Phase 7 is acceptable only if:

1. The model’s probability logic is more market-aware and less naive.
2. Injury handling moves beyond broad flag counting.
3. Timing and line movement materially influence decision quality.
4. `BET`, `LEAN`, and `SKIP` become more selective for the right reasons, not simply more aggressive.
5. Evaluation improves in meaningful moneyline buckets, not only in global averages.
6. The learning layer gains stronger review features without becoming auto-promotional.
7. Replayability, reporting, and operator trust remain intact.

## Final Exit Rule
Do not call Phase 7 complete until:

1. the intelligence layer is measurably stronger at pregame moneyline decisioning
2. the system still behaves honestly under uncertainty
3. stronger features improve model judgment without breaking the discipline layer
4. the docs clearly explain how the upgraded intelligence now works
