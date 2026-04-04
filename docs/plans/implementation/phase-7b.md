# NBA Oracle Phase 7B Implementation Plan

## Purpose
Phase 7B is the deeper intelligence-upgrade pass.

Once 7A improves what the operator can see, 7B improves how the model actually forms judgment.

This is the phase that makes NBA Oracle materially smarter for pregame NBA moneyline decisioning.

## Goal
Upgrade NBA Oracle from a disciplined rules-plus-model workflow into a stronger probability-and-timing system.

Phase 7B should improve:
1. market-aware probability formation
2. injury and lineup interpretation
3. timing and line-movement judgment
4. uncertainty-aware bet gating
5. segmented evaluation and smarter learning features

## In Scope
- market-as-prior probability design
- stronger team-strength features for pregame moneylines
- injury impact modeling beyond simple flag counts
- lineup/context-aware team strength adjustments
- timing and line-movement intelligence
- uncertainty-aware bet gating
- segmented calibration and evaluation
- stronger learning-review feature inputs
- doc and runbook updates for the upgraded intelligence path

## Out of Scope
- live in-game betting
- autonomous bet placement
- direct Stake integration
- new dashboard page creation
- totals/props modeling

## Problems This Solves

### Problem 1: Probability formation is still too blunt
The current system is disciplined, but it still leaves value on the table in efficient moneyline markets.

### Problem 2: Injury intelligence is still too coarse
It needs to move beyond simple counts and broad trust adjustments into expected impact.

### Problem 3: Timing edge is under-modeled
Pregame value often depends on whether the number is early, stale, or already gone.

### Problem 4: Betting confidence still needs stronger separation from win confidence
A likely winner can still be a bad bet.

### Problem 5: Learning can use better features
The review-only learning loop needs stronger segment-aware inputs.

## Workstreams

### Workstream 1: Market-As-Prior Architecture
- market-implied probability as the starting prior
- model adjustments layered on top
- explicit probability decomposition

### Workstream 2: Team Strength and Lineup Context
- stronger baseline team-strength features
- lineup-aware context where available
- better favorite vs underdog behavior

### Workstream 3: Injury Impact Modeling
- key-player weighting
- expected minutes loss
- replacement quality
- team-side net effect

### Workstream 4: Timing and Line-Movement Intelligence
- opening/reference/best/close comparison
- time-to-tip
- movement magnitude and direction
- stale-edge detection

### Workstream 5: Uncertainty-Aware Bet Gating
- uncertainty score or confidence band
- stricter no-bet behavior in noisy contexts
- less overconfidence on weak favorites

### Workstream 6: Segmented Calibration and Evaluation
- heavy favorites
- moderate favorites
- near coin-flips
- underdogs

### Workstream 7: Learning-Layer Feature Upgrade
- stronger review-only candidate inputs
- better pattern mining
- stronger retraining discipline

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
2. improved team-strength feature set
3. injury impact feature layer
4. timing/line-movement feature layer
5. uncertainty-aware gating behavior
6. segmented calibration and evaluation outputs
7. upgraded learning-review feature inputs
8. test updates and validation checkpoints
9. doc and runbook updates

## Delivered In The Current Scope
- market-aware prior blending now anchors decisions instead of relying on consensus alone
- injury provider now emits impact-oriented metadata, not just broad flag counts
- stats provider now emits stronger team-strength context including defense and team-strength summaries
- predictor now decomposes calls into market prior, source adjustment, timing adjustment, and uncertainty
- decision gating is now uncertainty-aware and segment-aware with slightly more lenient promotion than Phase 7B planning originally assumed
- learning pattern mining now recognizes market segments and uncertainty buckets
- learning weight derivation now tracks timing, uncertainty, source adjustment, and market-prior movement
- replay and live reports now surface the new intelligence fields
- replay acceptance still passes after the upgrade

## Current Verification
1. `python -m unittest discover -s tests -p "test_*.py"` passes
2. `npm run build` passes
3. default replay still reports `Phase 1 readiness: true`
4. Phase 7B regression coverage now exists for:
   - market prior and uncertainty fields
   - high-uncertainty downgrade behavior
   - injury impact metadata
   - segmented learning outputs

## Acceptance Criteria
1. Probability logic is more market-aware and less naive.
2. Injury handling moves beyond broad flag counting.
3. Timing and line movement materially influence decision quality.
4. `BET`, `LEAN`, and `SKIP` become more selective for the right reasons.
5. Evaluation improves in meaningful moneyline buckets.
6. The learning layer gains stronger review features without becoming auto-promotional.
7. Replayability, reporting, and operator trust remain intact.

## Exit Rule
Phase 7B is complete for the current scope when:
1. the intelligence layer is measurably stronger at pregame moneyline decisioning
2. the system still behaves honestly under uncertainty
3. stronger features improve model judgment without breaking the discipline layer
4. the docs clearly explain how the upgraded intelligence now works
