# NBA Oracle Problems Plan

## Purpose
This file tracks the top blockers that keep the current model from being a consistent money-making system.

## Batch 1 Summary
This batch focuses on the five blockers that decide whether the model can survive real betting:
- frozen backtesting
- calibration honesty
- no-bet discipline
- source freshness and trust
- market discipline and price control

## Batch 2 Summary
This batch focuses on the next five blockers that decide whether the model can stay stable and honest after Batch 1:
- timing advantage
- drift control
- price-first behavior
- market scope control
- LLM containment

## Top 5 Problems

### 1. No proven point-in-time backtest
- The README describes a smart system, but it does not yet prove the system using only data that would have been known before tip-off.
- Without this, the model can look better than it really is because of hindsight leakage.
- This is the biggest credibility gap.
- Fixed when the model can replay historical slates from frozen snapshots and produce reproducible, leakage-free results.
- The pass-1 problem is really a timing problem: if the model can see the answer after tip-off, it is not measuring edge.
- This blocker is worse around injury/news-driven slates because market correction happens fast.

### 2. Calibration is described, not enforced
- The README says calibration matters more than accuracy, but there is no concrete calibration gate yet.
- A pick can have a high confidence label without the probabilities actually being trustworthy.
- If calibration is off, Kelly sizing and confidence bands become dangerous.
- Fixed when confidence bins line up with observed win rates closely enough to trust the probability output.
- The blocker is not just "confidence is wrong"; it is "confidence is not yet an enforceable decision rule."
- The model cannot scale money intelligently until the probabilities are honest.

### 3. No hard no-bet engine
- The model philosophy says skip often, but there is no formal skip threshold yet.
- Without a strict no-bet gate, the system will still overtrade weak edges.
- This is one of the fastest ways to lose money even with decent analysis.
- Fixed when the default outcome for weak edges is skip, not action.
- This is a selectivity problem: the model needs to say no more often than it says yes.
- The no-bet path should be treated as a first-class output, not a failure.

### 4. Source freshness and trust are not operationalized
- The README lists odds, injuries, Reddit/X, and stats, but it does not yet score them by freshness, trust, or reliability.
- Stale injury news or delayed social signals can contaminate the pick.
- The system needs explicit source quality weights.
- Fixed when stale or low-trust data is automatically downweighted or ignored.
- This is a source hierarchy problem: official, verified, and fresh information should matter more than noisy, delayed, or brittle sources.

### 5. Market discipline is not complete
- The README mentions closing-line value and Stake pricing, but it does not yet fully enforce line shopping, price comparison, bankroll sizing, or exposure limits.
- A good read at a bad price is still a bad bet.
- Without price discipline, edge gets eaten by vig and bad numbers.
- Fixed when the model consistently chooses the best available number and respects bankroll/exposure limits.
- This is a price problem and a risk problem at the same time: the model must know when the number is good enough to act on.
- The model must be able to pass when Stake is no longer the best number available.

## Secondary Problems
- The LLM is still too close to the final decision path.
- The model does not yet separate moneylines, totals, and props by readiness.
- Learning loops are described, but not yet proven stable.
- Social sentiment is still vulnerable to being overweighted if the gates are weak.
- The model does not yet explicitly reward fresh late-breaking information over stale pregame context.
- The model does not yet monitor live performance decay against its backtest baseline, so drift can hide in plain sight.
- The model is trying to cover too many market types before the easier ones are proven stable.
- The LLM still risks becoming a decision maker instead of a communication layer.

## Top 5 Problems for Batch 2

### 6. Timing advantage is not fully operationalized
- The README mentions timing edges, but it does not yet define a strong trigger for how fresh news changes a pick.
- The model needs to reward late information more explicitly than stale pregame context.
- This is a reaction-speed problem: the system has to know when the news arrived, not just what the news said.

### 7. Drift control is not yet a first-class gate
- The README describes retraining discipline, but it does not yet make drift detection a strong operational decision rule.
- Live decay can hide behind a good backtest if the system does not compare them constantly.
- The model needs a way to detect when its live edge is fading even if the last replay looked strong.

### 8. Price-first behavior can still be improved
- The model compares Stake to the best number, but pass-8 style discipline needs to become a permanent rule, not a one-time check.
- A wrong line should be a downgrade even when the directional read is good.
- Price discipline must be enforced every slate, because EV can leak quietly through repeated bad numbers.

### 9. Market scope control needs stronger readiness boundaries
- Moneylines, totals, and props are still described as stages, but they need even cleaner maturity boundaries.
- The system should not expand into harder markets before simpler ones are stable.
- Different market types can be profitable or unprofitable for different reasons, so the model needs to respect their separate learning curves.

### 10. LLM containment is still too soft
- The README says the LLM is an analyst, but the prose layer still risks carrying too much authority.
- The predictor must remain the only final decision engine.
- The system needs a hard separation between explanation and decision so the model cannot talk itself into a weak bet.

## What This File Is For
Each problem above must be solved one-by-one, then moved into `ftw-plan.md` as a concrete fix path.

## Evidence Notes
- NBA betting research shows that opening injuries can create edges, but closing lines often absorb that information by tip-off, so the model must care about timing and CLV more than raw confidence.
- Calibration research shows that a better-calibrated betting model can outperform a more accurate but poorly calibrated one on ROI, so accuracy alone is not enough.
- Market-comparison research shows that price differences across books matter, so line shopping is part of the edge, not a side task.
- Line-movement studies show that informed money can improve closing prices, which means market movement itself is a signal the system should learn from.
- The model is most exposed when it treats social chatter like primary signal instead of confirmation.
- A system without a skip gate tends to overtrade, which is one of the fastest ways to turn a smart-looking model into a losing one.

## Research Anchors
- `Calibration > accuracy`: calibration-driven model selection had materially better ROI than accuracy-driven selection in the cited NBA betting study.
- `Opening != closing`: early lines can be mispriced, but market action often corrects those mispricings before game time.
- `Line movement matters`: closing lines can be more informative than opening lines when informed traders are active.
- `Social is secondary`: Reddit and X are useful for timing and context, but not as a primary predictor over odds, injuries, and stats.
- `Frozen replay is mandatory`: the model must be tested only on source snapshots that existed before the decision timestamp.
- `Probability honesty`: a betting model is only as good as its probability estimates, because staking and edge both depend on them.
- `Skip is signal`: a good model can improve by refusing more bad spots, not by forcing more picks.
- `Source hierarchy`: official injury reports and live market movement should outrank social chatter when the decision is final.
- `Price discipline`: the best number matters as much as the pick itself, because EV lives or dies on price.
- `Timing edge`: the value of a signal depends on whether it arrived before the market fully adjusted.
- `Reaction speed`: the model must use the timestamp of information, not just its content.
- `Drift awareness`: a model can decay quietly even if yesterday’s backtest looked strong.
- `Live decay`: the model must watch current performance against the validated baseline, not just the last training result.
- `Best available line`: the model should shop the number because EV can vanish on a bad price.
- `Permanent price discipline`: line shopping has to happen every time, not only when the model feels uncertain.
- `Market readiness`: moneylines, totals, and props should not be treated as equally mature targets.
- `Scope hardening`: harder markets should stay closed until the easier ones prove stable and profitable.
- `LLM as analyst`: the prose layer should explain the model, not replace it.
- `Decision authority`: the predictor should always outrank prose, no matter how persuasive the explanation is.
- `Timing edge`: fresh late information should move the pick before stale context does.
- `Drift control`: live decay must be checked against the validated baseline, or the model can quietly worsen.
- `LLM containment`: the explanation layer can narrate the pick, but it cannot own it.

## Missing Stack Pieces
- Frozen snapshot layer
- Market comparator
- Probability engine with calibration gate
- No-bet engine
- Source scorer
- Timing engine
- LLM analyst separation

## Per-Problem Acceptance

### Backtest problem
- Fixed when the replay uses frozen decision-time snapshots and the report shows ROI, hit rate, and CLV with no leakage.

### Calibration problem
- Fixed when probability bins are honest enough that the model’s confidence can be trusted for gating and sizing.

### No-bet problem
- Fixed when weak-edge games resolve to skip by default and skip rate is visible in reporting.

### Source quality problem
- Fixed when every source has a freshness/trust score and stale feeds are automatically downweighted.

### Market discipline problem
- Fixed when Stake price, line shopping, and exposure controls are enforced before any bet becomes active.
