# NBA Oracle FTW Plan

## Purpose
This file captures the strongest practical fixes for the blockers in `problems plan.md`.

## Batch 1 Summary
This batch turns the five blockers into the core money-making doctrine:
- replay only frozen pre-tip-off data
- trust calibrated probabilities, not raw confidence
- skip weak edges by default
- score sources by freshness and trust
- shop prices and respect bankroll discipline

## Batch 2 Summary
This batch turns the next five blockers into the stability doctrine:
- make fresh information move the decision first
- detect and respect model drift
- keep price discipline as a permanent rule
- control market scope by readiness
- keep the LLM in analyst-only mode

## Solution 1: Point-in-time backtesting
- Build a replay engine that reconstructs each slate using only pre-tip-off data.
- Freeze snapshots for odds, injuries, stats, and sentiment at decision time.
- Run every historical pick through the exact same selection logic the live model would use.
- Measure ROI, hit rate, calibration, and closing-line value from those runs.

## Solution 2: Calibration-first model gate
- Use calibration as the primary model-selection criterion, not raw accuracy.
- Add probability bins and reliability curves to the evaluation loop.
- Reject models whose confidence does not match real outcomes.
- Treat a well-calibrated 58-60 percent model as more valuable than a noisy higher-accuracy model.

## Solution 3: Hard no-bet engine
- Add a strict threshold that prevents weak edges from becoming bets.
- Require agreement across edge, freshness, and market price before activating a pick.
- Make `SKIP` the default output when uncertainty or price conflict is high.
- Log every skip so the model can learn whether it is being too conservative.

## Solution 4: Source trust and freshness scoring
- Assign every source a trust score and a freshness score.
- Prefer official injury reports, official stats, and line movement over social chatter.
- Downweight stale Reddit/X signals unless they are confirmed by better sources.
- Route every source through an adapter layer so the model sees normalized inputs.

## Solution 5: Price and bankroll discipline
- Compare Stake against other books before triggering an active bet.
- Add line-shopping logic so the best available number is used.
- Separate moneyline, totals, and props into different readiness levels.
- Add bankroll sizing rules and max-exposure limits so one bad slate does not wipe the edge.

## What “FTW” Means Here
FTW means the model is:
- selective,
- calibrated,
- price-aware,
- fast on fresh information,
- and disciplined enough to skip most games.

## Strong Predictor Stack
- Frozen snapshot layer for every pre-tip-off input.
- Market comparator for Stake versus the best available line and the close.
- Probability engine that outputs calibrated win probabilities.
- No-bet gate that blocks weak edges before recommendation.
- Timing engine that rewards fresh injury, rotation, and line movement signals.
- Source scorer that downweights stale or brittle feeds.
- LLM analyst that explains the edge without deciding the bet.

## Batch 2 Additions
- Timing trigger that reacts to fresh injury, lineup, and line movement changes.
- Drift monitor that compares live performance against the validated backtest baseline.
- Permanent line-shopping rule that downgrades or skips bad prices.
- Readiness gate that keeps moneylines, totals, and props in separate maturity stages.
- LLM containment rule that lets the prose layer explain, but never decide.

## Pass 11: Timing advantage

### Pass 11 details
- Measure the lag between source publication and model reaction.
- Re-score the pick when late injury or lineup news arrives.
- Give fresh pre-tip-off information more weight than stale context with the same content.
- Track whether the model caught the edge before the market closed it.
- Keep timing as a permanent value signal, not an exception.

### Pass 11 success condition
- The model changes direction or confidence quickly enough that fresh news still matters when it arrives.
- The timing score shows the system is reacting before the value disappears.

## Pass 12: Drift control

### Pass 12 details
- Compare live ROI, calibration, CLV, and skip quality against the last validated baseline.
- Detect whether the model is decaying or simply experiencing short-term variance.
- Retrain only when drift is persistent and the new baseline is clearly better.
- Keep a record of the reason for each retrain so later audits can explain the change.
- Prefer stable improvement over frequent model churn.

### Pass 12 success condition
- The model can prove that it knows when it is getting worse and can respond without overfitting to random noise.

## Pass 13: Price discipline permanence

### Pass 13 details
- Compare Stake against the best available line on every active recommendation.
- Treat a bad number as a reason to downgrade or skip, even when the read is correct.
- Enforce exposure limits on every slate, not only during high-confidence days.
- Track price leakage over time to see whether repeated bad numbers are eating EV.
- Make line shopping a permanent part of the recommendation flow.

### Pass 13 success condition
- The model behaves like price discipline is part of the bet itself, not a separate cleanup step.

## Pass 14: Market scope control hardening

### Pass 14 details
- Keep moneylines as the first stable market.
- Open totals only after moneylines show stable ROI, CLV, and calibration.
- Add props only after totals prove stable and the minutes/usage assumptions are trustworthy.
- Track market-specific performance separately so weak markets do not contaminate strong ones.
- Block market expansion unless the readiness threshold is met.

### Pass 14 success condition
- The model expands into harder markets only after the simpler market is demonstrably stable and profitable enough to justify the extra complexity.

## Pass 15: LLM containment hardening

### Pass 15 details
- Keep the LLM in an explanation-only role.
- Prevent any prose output from changing the recommendation.
- Make the predictor and market filters the final authority.
- Log contradictions between the LLM and the predictor for audit purposes.
- Require that the same recommendation can be recovered without the prose layer.

### Pass 15 success condition
- The LLM can make the output readable and useful, but it cannot rescue a weak bet or overrule a skip.

## Pass Outputs We Want
- **Replay report** from the backtester with ROI, hit rate, and CLV.
- **Calibration report** with probability bins and reject thresholds.
- **Skip dashboard** that shows the model is willing to pass weak spots.
- **Source score report** with freshness/trust weights per feed.
- **Market comparison table** for Stake versus other books.
- **Market readiness flags** for moneylines, totals, and props.
- **LLM explanation layer** that is readable but cannot overrule the scoring engine.

## Implementation Order
1. Backtesting
2. Calibration gates
3. No-bet engine
4. Source scoring
5. Market and bankroll discipline

## 10-Pass Hardening Loop

### Pass 1: Prove the edge
- Build the point-in-time backtester.
- Verify the model can survive hindsight-free replay.
- Freeze odds, injuries, stats, and sentiment at the exact decision timestamp.
- Success means the replay uses only frozen inputs and produces stable, reproducible outputs.
- Deliverable: a historical slate report with leakage checks and CLV.

#### Pass 1 details
- Tag each source snapshot with `decision_time`, `source_time`, and `source_version`.
- Freeze the source state before the prediction step starts.
- Replay the exact same prediction path on a historical slate.
- Compare expected value, closing-line value, hit rate, and skip rate.
- Reject any replay that uses post-tip-off information.
- Keep moneylines, totals, and future market types separated in the replay report.

### Pass 2: Make probabilities honest
- Add calibration curves and model-selection gates.
- Reject noisy confidence output.
- Use probability bins and reliability curves to catch overconfidence.
- Success means predicted bins line up with observed win rates well enough to trust the score.
- Deliverable: calibration curves and probability-bin tables.

#### Pass 2 details
- Create probability bins such as 0-10, 10-20, 20-30, and so on.
- Compare predicted probability against realized hit rate inside each bin.
- Mark any model as unsafe if it looks accurate but is badly calibrated.
- Use calibration as a selection gate for live activation and bet sizing.
- Keep the reporting focused on whether probability can be trusted, not just whether picks won.

### Pass 3: Force selectivity
- Require a no-bet threshold before any active recommendation.
- Track skip behavior as a key quality signal.
- Make skip volume visible in reporting so the model can be judged on discipline.
- Success means weak-edge games default to skip instead of being forced into action.
- Deliverable: explicit skip reasons and skip-rate reporting.

#### Pass 3 details
- Define a numeric edge threshold, not a vague confidence label.
- Make the threshold sensitive to vig-adjusted EV and market movement.
- Return explicit skip reasons when the gate fails.
- Log skip reasons for later model analysis.
- Treat skip as a valid model output that protects bankroll and preserves edge.
- Use the skip log to understand whether the model is too aggressive or too conservative.

### Pass 4: Anchor on the market
- Compare model value against the closing line and Stake price.
- Refuse bets that lose edge after movement.
- Treat closing-line value as evidence of real information, not a cosmetic stat.
- Success means the model can show consistent positive closing-line value when it does bet.
- Deliverable: model-vs-Stake-vs-close comparison report.

#### Pass 4 details
- Score each source by freshness, trust, and failure rate.
- Prioritize official injury reports, verified stats, and market movement over social chatter.
- Allow social feeds to influence timing, but not to override the final decision.
- Downweight any source that is stale, inconsistent, or brittle.
- Treat source scoring as a permanent layer of the predictor, not a one-off cleanup step.

### Pass 5: Control source quality
- Add source freshness and trust scoring.
- Downweight stale or brittle inputs.
- Use adapters so each source can be swapped without changing model logic.
- Success means stale or low-trust sources no longer dominate the pick.
- Deliverable: source trust matrix and freshness-weight audit.

#### Pass 5 details
- Compare Stake against the best available market price before activation.
- Track opening line, current line, and closing line for every active bet.
- Add exposure and bankroll caps so one slate cannot dominate account risk.
- Treat bad price as a downgrade even when the prediction is correct.
- Make line shopping part of the core recommendation pipeline, not a manual afterthought.

### Pass 6: Prioritize timing
- Surface late injury and lineup changes faster than static stats.
- Reward information that arrives before the market fully adjusts.
- Give fresh injury and lineup data a higher trust multiplier than older social posts.
- Success means fresh verified news changes the decision earlier than social noise.
- Deliverable: timing score that explains why a pick changed.

#### Pass 6 details
- Measure the lag between source publication and model response.
- Re-evaluate a pick immediately when late injury or lineup news drops.
- Boost the weight of information that arrives shortly before the market moves.
- Reduce the weight of signals that are old by the time the decision is made.
- Use timing as a value signal, not just as a scheduling detail.

### Pass 7: Reduce model drift
- Watch for performance decay over time.
- Retrain only when the data regime changes enough to justify it.
- Compare current performance to the last calibrated baseline before retraining.
- Success means the model does not quietly degrade across months of usage.
- Deliverable: drift chart and retrain trigger logic.

#### Pass 7 details
- Compare live performance against the last validated backtest baseline.
- Track drift in ROI, calibration, CLV, and skip quality by month.
- Retrain only when performance decay is persistent, not when one slate goes badly.
- Separate real regime change from random variance before changing the model.
- Keep a record of why the model was retrained so later analysis can audit the decision.

### Pass 8: Add price discipline
- Shop multiple books and compare numbers.
- Never assume Stake is the best available price.
- Treat a worse price as a reason to downgrade or skip the bet.
- Success means the chosen number is consistently among the best available prices.
- Deliverable: line-shopping table with the chosen line highlighted.

#### Pass 8 details
- Compare Stake to the best available line before any active recommendation.
- Refuse a bet if the selected number is materially worse than the market.
- Track opening, current, and closing prices per bet.
- Use exposure caps to prevent one slate from dominating risk.
- Make line shopping a required step in the decision flow, not an optional human check.

### Pass 9: Constrain market scope
- Finish moneylines first.
- Move to totals only after moneylines prove stable.
- Add props last.
- Do not expand market scope until the previous market shows stable CLV and calibration.
- Success means each market type is unlocked only after the previous one proves stable.
- Deliverable: readiness flags for moneylines, totals, and props.

#### Pass 9 details
- Maintain separate readiness criteria for moneylines, totals, and props.
- Keep market-specific ROI, CLV, calibration, and skip rates separate.
- Prevent weaker market types from polluting stronger ones in the analysis.
- Expand scope only after the simpler market has stable, repeatable results.
- Treat props as a later-stage market because they depend heavily on minutes and usage projection quality.

### Pass 10: Keep the LLM in its lane
- Use the LLM for explanation, synthesis, and reporting.
- Keep the final bet decision inside the calibrated scoring system.
- Do not let the LLM override a no-bet gate or the market-price filter.
- Success means the LLM can justify a pick, but cannot override the decision engine.
- Deliverable: explanation-only output with no decision authority.

### Pass 11: Batch 2 closing logic
- Keep the five Batch 2 pillars linked to the predictor, not the prose.
- Treat timing, drift, price, scope, and LLM containment as stability gates.
- Do not let Batch 2 become a new source of complexity without improving betting quality.
- Success means the model stays narrow, stable, and explainable while the predictor remains authoritative.

#### Pass 10 details
- Restrict the LLM to summarizing structured inputs and producing human-readable rationale.
- Keep the final bet/no-bet decision inside the predictor and market filters.
- Prevent any prose output from changing the underlying recommendation.
- Log LLM output separately so it can be audited against the structured decision.
- If the LLM and predictor disagree, the predictor wins.
