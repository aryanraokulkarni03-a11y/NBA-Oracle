# 🏀 NBA Oracle — AI-Powered Betting Intelligence System

> **Status:** Concept / In Design  
> **Bet Mode:** Analysis & Pick Generation (Manual Placement on Stake)  
> **Primary Market:** Moneyline (Win/Loss)  
> **Platform Target:** Stake.com  
> **Trigger:** Dynamic cron — auto-schedules 2 hrs before first tip-off (IST) each day  
> **Notifications:** Gmail (12 AM IST confirmation) + Telegram (Pick Cards at runtime)  
> **API Budget:** Free tier only  
> **Deployment:** Local laptop (auto-start on boot via Task Scheduler / systemd)  
> **Telegram:** Interactive bot with commands (/picks, /stats, /result, /history)

---

## 🧠 The Philosophy — Edge Over Luck

The world's best sports bettors don't win because they're lucky. They win because they **consistently know something the market doesn't** — or they know it *faster*. That's the only edge that compounds over time.

NBA Oracle is built on this principle. It is not a coin-flip randomizer dressed up with AI. It is a **systematic research engine** that processes more variables per game than any human analyst could in 2 hours — and synthesizes them into a single, reasoned, high-conviction pick.

> *If the pick can't be explained with data, it doesn't get made.*

**NBA Oracle** runs automatically every day before games tip off. It ingests four intelligence layers, builds a structured analytical context, reasons through it with a frontier LLM, and delivers pick cards directly to your Telegram — so the only thing left for you is to decide whether to pull the trigger on Stake.

| Signal Layer | What It Reads |
|---|---|
| 📈 Live Odds & Lines | Real-time odds shifts, line movement, public vs. sharp money flow |
| 🏥 Injury & News Feeds | Official NBA reports, beat reporters, last-minute scratches |
| 💬 Reddit / Twitter Sentiment | r/nba, team subs, sharp bettor accounts on X, public narrative |
| 📊 Deep Stats & Context | 15+ advanced metrics per team — not just wins, but *why* they win |

The system synthesizes all four layers through an LLM reasoning engine and outputs a **structured Pick Card** with confidence score, signal breakdown, and a clear reasoning chain.

---

## 🔍 Prediction Research Notes

This project is built around the same ingredients used by public NBA prediction systems:

- **Core inputs**: team strength, pace, efficiency, injuries, rest, travel, matchup style, and betting-market odds.
- **Prediction math**: implied probability from odds, vig removal, expected value, calibration, and weighted feature scoring.
- **Model types**: simple heuristics, statistical models like logistic regression and Elo-style ratings, and heavier ML models for interaction effects.
- **Social signals**: Reddit and X are useful for injury/news acceleration and sentiment, but they should stay secondary to stats and market prices.
- **Public research sources**: NBA.com/stats, Basketball-Reference, Dunks & Threes, Cleaning the Glass, Action Network, RotoWire, Lines.com, ScoresAndOdds, and Inpredictable-style win probability models.

### Math Layer

The prediction engine should think in probabilities, not vibes:

1. Convert sportsbook odds into implied probability.
2. Remove vig to estimate a fair baseline line.
3. Compare the model’s probability to the fair line to measure edge.
4. Use calibration checks so confidence scores stay honest over time.
5. Treat expected value as the final gate before a pick becomes active.

### Social Signal Layer

Reddit and X should be treated as fast-moving context streams:

- **Best use**: late injury news, beat-writer updates, lineup changes, and public sentiment shifts.
- **Worst use**: copying picks, chasing hype, or relying on fan confidence as a prediction engine.
- **High-value communities**: `r/sportsbetting`, `r/sportsbook`, `r/nbabetting`, `r/nba`, `r/DFS_Sports`, plus team-specific subreddits for injury and rotation chatter.
- **High-value sites**: Action Network for odds/projections, RotoWire for picks and injury context, Lines.com and ScoresAndOdds for consensus lines, Dunks & Threes for advanced ratings, and Cleaning the Glass for deeper team profile work.

### Practical Rule

If the stats, odds, and injury context all point the same way, the social layer should confirm the idea. If only social chatter points one way, that should usually be a skip, not a pick.

---

## Reality Check

This project is viable as a **decision-support and edge-finding system**. It is not viable as a guarantee of profits just because it is automated.

What the research says in plain English:

- NBA betting markets are often efficient, especially by closing time.
- Social sentiment can contain useful information, but it is noisy and usually secondary to stats, injuries, and market price.
- Prediction quality should be judged by calibration and closing-line value, not just by raw win rate.
- The LLM should explain and synthesize signals, but it should not be the only thing making the final bet decision.

What the README should add to make this project real:

- **Backtesting engine**: replay historical games using only information that was available before tip-off.
- **Calibration layer**: check whether 60 percent picks actually win close to 60 percent over time.
- **Closing-line tracker**: compare model output against the market close to measure real edge.
- **Source reliability scoring**: rank odds feeds, injury news, Reddit, and X by trust and freshness.
- **No-bet gate**: skip games when edge is too small, data is stale, or signals conflict.
- **Risk engine**: add bankroll sizing, max daily exposure, and stop-loss rules.
- **Human override**: keep a manual check for late scratches, weird line movement, or broken data feeds.

Best design rule:

The model should be split into two roles:

- **Analyst**: the LLM summarizes evidence, explains the edge, and produces the report.
- **Predictor**: the structured scoring layer turns signals into probabilities and decides whether a bet is active.

---

## Batch 1 Doctrine

This first batch is the real-money viability layer. It answers one question: can the model stay honest, selective, price-aware, and reproducible enough to survive real betting?

### The five pillars

1. **Frozen truth**
   - Every replay must use only information available before tip-off.
   - If hindsight leaks in, the edge is fake.

2. **Probability honesty**
   - Confidence must behave like a real probability, not a decorative score.
   - Calibration outranks raw accuracy.

3. **Skip discipline**
   - Weak edges should become `SKIP`, not forced bets.
   - Refusing bad spots is a feature.

4. **Signal hierarchy and price discipline**
   - Fresh official injury news and market movement outrank stale chatter.
   - Stake must be compared to the best available line before any bet is active.

5. **Scope control and separation of roles**
   - Moneylines come first, then totals, then props.
   - The LLM explains, but the calibrated predictor decides.

### Batch 1 outcome

If these five pillars hold, the system becomes a selective betting engine rather than a noisy prediction machine.

---

## Batch 2 Doctrine

Batch 2 hardens the remaining decision-risk layer. If Batch 1 proves the model can be honest, Batch 2 proves it can stay stable, narrow, and readable without letting the prose layer or market expansion take over.

### The five pillars

1. **Timing advantage**
   - Fresh injury and lineup information should change the decision faster than stale pregame context.

2. **Drift control**
   - Live performance must be compared against the validated baseline so retraining is justified, not emotional.

3. **Price-first behavior**
   - Stake should be compared to the best available line every time, with line shopping built into the recommendation flow.

4. **Market scope control**
   - Moneylines, totals, and props should mature in that order, not all at once.

5. **LLM containment**
   - The LLM explains the pick, but the calibrated predictor and market filters decide it.

### Batch 2 outcome

If these five pillars hold, the system becomes a stable operating framework instead of a model that drifts, expands too early, or talks itself into bad bets.

---

## Batch Summary

- **Batch 1** proved the model can be frozen, calibrated, selective, source-aware, and price-aware.
- **Batch 2** keeps the model stable by enforcing timing, drift control, scope control, and LLM containment.
- Together, the batches define the minimum viable theory for a real-money NBA betting system.

### Full batch picture

- **Batch 1** is about whether the model can make honest betting decisions.
- **Batch 2** is about whether those honest decisions stay stable, narrow, and readable over time.
- The two batches together form the core theory of a real-money NBA betting system.

## Data Acquisition Strategy

Yes, this system is scrape-heavy in places. The way to make that viable is to treat scraping as a fallback layer, not the whole foundation.

### Source hierarchy

1. **Official APIs first**: use them whenever they exist and are stable.
2. **Public structured feeds second**: RSS, endpoints, and readable pages with predictable markup.
3. **Targeted scrapers last**: use them only for sources that do not offer a clean API.

### How to keep scraping from becoming fragile

- **Prefer source adapters** over direct one-off scraping logic so each source can be swapped independently.
- **Normalize every source** into the same internal schema before it reaches the model.
- **Cache aggressively** so temporary site failures do not break a full daily run.
- **Add retries and backoff** for rate-limited or flaky sources.
- **Score freshness and reliability** so stale or partial data gets downweighted instead of treated as truth.
- **Keep fallbacks per layer** so if X breaks, Reddit and official injury feeds still work.
- **Log source health** so you can see when a source is degrading before the output quality drops.

### Practical scraper policy

- Odds: use an odds API or equivalent structured source first.
- Injuries/news: use official reports and beat-writer feeds first, then public scrapes.
- Reddit: use API access where possible; otherwise keep the scrape narrow and purpose-built.
- X/Twitter: treat as optional and brittle, with a clear fallback path if it fails.
- Stats: prefer official stats endpoints and well-known structured libraries over broad web scraping.

### Design rule

Scraping should help the system **collect signals**, not become the system's single point of failure.

### Source Matrix

| Source | Preferred Collection | Reliability | Fallback |
|---|---|---|---|
| NBA schedule / game data | `nba_api` or official NBA endpoints | High | Cached schedule snapshot |
| Odds / lines | Odds API or structured odds feed | High | Cached opening line + last known line |
| Injuries / status | Official injury reports, team reports, beat writers | High | Secondary news feed or skip the source |
| Reddit sentiment | Reddit API or narrow subreddit scrape | Medium | Skip sentiment layer for that run |
| X / Twitter sentiment | Curated feed or scrape of public posts | Medium-Low | Reddit-only sentiment |
| Advanced stats | `nba_api`, Basketball-Reference, trusted stats sites | High | Previous season or prior snapshot |
| Line movement / consensus | Odds aggregator / consensus page | Medium | Recompute from last stored odds |
| Dashboard / history | Supabase | High | Local cache if offline |

### Reliability scoring

Not every source should influence the model equally. Each source should get a freshness and trust score, then the model should use those scores to weight or downweight the signal before prediction.

---

## Bet Selection Philosophy

NBA Oracle is not trying to predict every game. It is trying to find the few games where the edge is worth acting on.

### Core idea

- Most games should be skipped.
- A smaller set of games should be marked as lean or watchlist.
- Only the clearest edges should become active bets.
- Bet size should scale with edge and confidence, not with excitement.

### How the system should think

1. **Is there a real edge?** If not, skip.
2. **Is the edge still there after vig and market movement?** If not, skip.
3. **Is the data fresh enough to trust?** If not, skip.
4. **Do multiple strong signals agree?** If not, keep the bet small or skip.
5. **Does the expected value justify the risk?** If not, skip.

### Practical betting tiers

- **SKIP**: weak edge, stale data, noisy signals, or no clear value.
- **LEAN**: some edge exists, but not enough to go hard.
- **BET**: edge is real, signals align, and the model has high confidence.
- **STRONG BET**: rare spot with strong alignment, sharp confirmation, and clear value.

### Risk rule

Even when the model likes a spot, the system should never assume it is free money. The point is to maximize expected value over time, not to force action on every slate.

---

## Accuracy vs Profitability

Because the bets are placed on **Stake.com**, the system should optimize for **profitability after price**, not just for picking winners.

### What to measure

- **Prediction accuracy**: how often the pick wins.
- **Calibration**: whether the confidence score matches reality over time.
- **Closing-line value**: whether the model is beating the market price before tip-off.
- **Expected value**: whether the bet is worth taking at the current Stake price.
- **Skip rate**: whether the model is disciplined enough to pass weak spots.

### What matters most

1. **Expected value**
2. **Calibration**
3. **Closing-line value**
4. **Prediction accuracy**
5. **Raw volume**

### Practical rule for Stake

The system should only generate an active bet when the model believes the current Stake line is still mispriced after all available signals are applied. If the edge is small or stale, the right answer is to skip, even if the winner seems obvious.

---

## Maximizing Correctness

The best way to improve correctness is not to force more picks. It is to make the system more selective, more calibrated, and more honest about when it does not have an edge.

### Ranked priorities

1. **Hard no-bet filter**
   - Default to skip unless the edge clears a real threshold.
   - Most games should never become bets.

2. **Closing-line value**
   - Treat beating the close as a primary signal that the model is finding real edge.
   - If the model cannot beat the market consistently, the system is not ready.

3. **Backtesting with pre-tip-off data only**
   - Replay historical slates using only information available at decision time.
   - This prevents hindsight from inflating model quality.

4. **Calibration tracking**
   - Check whether 70 percent picks really win near 70 percent over time.
   - Confidence scores should be honest, not just optimistic.

5. **Source freshness scoring**
   - Downweight stale injury, odds, or sentiment data.
   - Time-sensitive sources should matter more when they are fresh.

6. **Official injury and market movement weighting**
   - Prioritize injury reports, lineup changes, and line movement over Reddit/X chatter.
   - Social signals should support, not override, primary sources.

7. **Line shopping**
   - Compare multiple books before deciding a Stake line is worth taking.
   - A good pick at a bad price can still be a bad bet.

8. **Market focus**
   - Start with moneylines, then totals, then props.
   - Favor the most modelable markets first.

9. **Information timing edges**
   - Look for late scratches, delayed updates, and stale lines.
   - Timing can matter as much as the underlying stat edge.

### Correctness target

The goal is not 100 percent hit rate. The goal is a small number of strong, well-timed, well-priced bets with positive expected value and strong calibration.

---

## How We Get Better Than 55%

Moving from a coin-flip-ish system to a real edge is not about adding more noise. It is about tightening the whole pipeline around selectivity, timing, and truthfulness.

### Highest-impact upgrades

1. **Backtest with real pre-tip-off snapshots**
   - Rebuild every historical pick using only data that would have been known at the time.
   - This is the only way to know whether the edge is real or just hindsight.

2. **Add a hard no-bet gate**
   - Default to skip unless the model has a real edge after vig and movement.
   - Fewer bets is a feature, not a failure.

3. **Make calibration the primary model gate**
   - A `70%` pick should really behave close to `70%` over time.
   - Calibration should matter more than raw accuracy when selecting the model.

4. **Track closing-line value from day one**
   - If the model beats the close, it is probably finding real information edge.
   - If it cannot, the system is not yet beating the market.

5. **Prioritize information timing edges**
   - Late scratches, lineup shifts, and delayed reports can create real edge.
   - The system should act fast only when the data is fresh enough.

6. **Score source freshness and trust**
   - Not every injury note, odds update, or social post should count equally.
   - Time-sensitive sources should be weighted higher when they are recent and reliable.

7. **Weight market movement and official injury reports above chatter**
   - Reddit and X are useful for context, not for overriding primary signals.
   - The market and official reports should anchor the decision.

8. **Shop prices across books**
   - Use the best available line, not just Stake’s number in isolation.
   - A good model at a bad price can still be a bad bet.

9. **Start with the most modelable markets**
   - Moneylines first, then totals, then props.
   - Complex markets should come later, after the core engine is proven.

10. **Separate predictor from analyst**
   - The predictor should be a calibrated scoring engine.
   - The LLM should explain and summarize, not invent the bet.

### Core loop

Collect fresh data -> score edge -> compare to market -> skip unless value is real -> store result -> backtest and recalibrate.

### End state

The target is not perfect prediction. The target is a small number of strong, timed, well-priced bets with positive expected value, real calibration, and a consistently healthy no-bet rate.

### Pass 1: Point-in-time backtesting

This is the first real proof layer. The model should only be judged on what it knew **before tip-off**, not on hindsight.

#### What must be frozen

- Odds at decision time
- Injury statuses at decision time
- Team and player stats available at decision time
- Line movement up to that timestamp
- Social/news signals that were actually visible before the prediction was made

#### What the replay must show

- Outcome by pick
- Expected value at the time of decision
- Closing-line value
- Hit rate
- Skip rate
- Calibration by probability bin

#### Why this matters

- NBA betting markets often correct early injury and news edges by the close, so a model that cannot replay point-in-time data is vulnerable to hindsight bias.
- The best public NBA models use time-aware updates, depth-chart context, and rolling adjustments rather than static “season average” logic.
- If a model cannot survive frozen replay, it is not yet a betting model; it is only a story.

#### Pass 1 acceptance rule

Pass 1 is only done when the historical replay can be repeated on the same inputs and produces the same recommendation path, same skip path, and same evaluation metrics.

### Pass 2: Calibration-first gate

After frozen replay works, the next question is whether the model’s probabilities are honest enough to trust.

#### What calibration means here

- A `70%` pick should win close to `70%` of the time over enough samples.
- A `60%` pick should behave like a `60%` pick, not a `45%` or `85%` pick.
- Confidence should be usable for bet selection and sizing, not just for display.

#### What must be measured

- Reliability curves
- Probability bins
- Brier-style error behavior
- Confidence versus actual hit rate
- Whether calibration outperforms raw accuracy as a model-selection rule

#### Why this matters

- Public sports-betting research has shown that calibration-based model selection can outperform accuracy-based selection on ROI.
- Reliability diagrams are only useful if they are treated as a real decision tool, not a pretty chart.
- A model with prettier accuracy numbers but bad probability truth will still fail in the betting market.

#### Pass 2 acceptance rule

Pass 2 is only done when the model can produce stable probability bins whose observed hit rates are close enough to the predicted bins to support live betting decisions and size selection.

### Pass 3: Hard no-bet engine

Once the probabilities are honest, the next question is whether the system has the discipline to refuse weak edges.

#### What the no-bet engine does

- Blocks low-edge recommendations by default
- Forces the model to justify why a bet is active instead of skipped
- Keeps weak lines, stale news, and conflicting signals out of the final card
- Treats `SKIP` as a valid high-quality output

#### What must be measured

- Skip rate
- Reason-for-skip distribution
- Edge threshold hit rate
- How often the model wanted to bet but the gate refused

#### Why this matters

- Overtrading is one of the quickest ways to destroy a betting model’s edge.
- A selective system can look less active while actually being more profitable.
- The best public betting systems are usually strong at saying no, not just at saying yes.

#### Pass 3 acceptance rule

Pass 3 is only done when weak-edge games are routed to `SKIP` by default and the skip decision is logged in a way that can be audited later.

### Pass 4: Source freshness and trust

After the model can skip weak spots, the next question is which sources deserve trust at the moment of decision.

#### What source trust means here

- Official injury reports should outrank fan sentiment and noisy reposts.
- Market movement should outrank speculative chatter when the line is already reacting.
- Social apps can be useful for speed, but only when the underlying signal is confirmed or at least corroborated.

#### What must be measured

- Source freshness
- Source trust
- Source failure rate
- Agreement between source classes
- How much the pick changes when a source updates

#### Why this matters

- Reddit and X can surface fast injury chatter, but the official report is still the anchor when the decision is final.
- Social feeds can be useful for timing, but they are not the truth layer.
- If the system cannot score source quality, it will overreact to stale or brittle data.

#### Pass 4 acceptance rule

Pass 4 is only done when every source can be scored by freshness and trust, and stale sources are automatically downweighted before the prediction step.

### Pass 5: Market discipline

After the system can judge source quality, it has to judge the price itself.

#### What market discipline means here

- Stake should be compared to the best available line, not treated as the only line.
- A good prediction at a bad number is still a bad bet.
- The model should care about closing-line value, not just opening confidence.

#### What must be measured

- Best available price versus Stake
- Opening line versus closing line
- Closing-line value by bet type
- Exposure per slate
- Whether the selected price remains good after line movement

#### Why this matters

- NBA totals have historically shown early-season inefficiencies, but the market still tends to learn and move toward better prices.
- Line movement can reflect informed money, so the model should treat market movement as part of the analysis, not background noise.
- If the model does not shop for price, it can lose edge even when the read is correct.

#### Pass 5 acceptance rule

Pass 5 is only done when Stake price, best available price, and closing line are all compared before activation, and bankroll or exposure limits keep one slate from dominating the account.

### Pass 6: Timing edges

After source trust and market discipline, the model should reward information that arrives at the right time.

#### What timing edge means here

- Fresh injury news should move the decision faster than old season averages.
- Late lineup changes should matter more than stale social narrative.
- A useful signal can be less about what it says and more about when it arrived.

#### What must be measured

- Update lag between source arrival and model reaction
- Whether late injury news changes the recommendation
- Whether line movement was captured before the market fully adjusted
- Timing score by source class

#### Why this matters

- NBA injury chatter often reaches social feeds and beat writers before the final public picture settles.
- r/nba and related community threads show that fans heavily track injury timing and late status changes.
- If the model reacts too slowly, it misses the best price and the edge disappears.

#### Pass 6 acceptance rule

Pass 6 is only done when the model can visibly reward fresh pre-tip-off information over older or noisier inputs and can show that timing changed the recommendation at the right moment.

### Pass 7: Model drift and retraining discipline

After timing works, the model has to stay honest as the data environment changes.

#### What drift means here

- The market changes, even if the README does not.
- A model that was calibrated last month can become less reliable this month.
- Overfitting can make a backtest look strong while live performance slowly weakens.

#### What must be measured

- Performance decay over time
- Calibration drift over time
- CLV decay by month or season slice
- Whether new data really improves the model
- When retraining helps versus when it just adds noise

#### Why this matters

- Public research on drifting predictive systems shows that data distribution shifts can break confidence alignment even when the model still looks plausible.
- Sports markets also show behavioral effects and time-varying structure, so the model should expect regime change instead of assuming stationarity.
- If the model retrains too often, it can chase noise; if it retrains too rarely, it can become stale.

#### Pass 7 acceptance rule

Pass 7 is only done when the model can detect performance decay, explain whether it is real drift or noise, and retrain only when the improvement is worth the added complexity.

### Pass 8: Price discipline and line shopping

After the model can track drift, it has to prove that the number itself is good enough to bet.

#### What price discipline means here

- Stake should be compared to the best available market price before any active bet is created.
- The model should treat a bad number as a bad bet, even if the prediction is directionally correct.
- Closing-line value should be a standing quality check, not a postgame curiosity.

#### What must be measured

- Stake price versus best available price
- Opening line versus closing line
- Whether the chosen line was ever actually the best available number
- Exposure by slate and by market
- When a bet should be downgraded because the price is no longer good

#### Why this matters

- Betting-market research shows that if you select the best odds across bookmakers, some markets become meaningfully more efficient to bet.
- Informed trading makes prices move, so the model has to care about price movement, not just direction.
- A model that ignores line shopping can lose EV even when the read is correct.

#### Pass 8 acceptance rule

Pass 8 is only done when the model always compares Stake to the best available number, refuses worse prices when necessary, and respects bankroll or exposure limits while doing so.

### Pass 9: Market scope control

After the model can manage prices, it has to manage complexity.

#### What market scope control means here

- Moneylines should be proven before totals are expanded.
- Totals should be proven before props are considered.
- Each market type should have its own readiness threshold.

#### What must be measured

- Market-specific ROI
- Market-specific calibration
- Market-specific CLV
- Market-specific skip rate
- Whether one market type is polluting another

#### Why this matters

- Some betting markets are more modelable than others, so starting narrow reduces noise.
- NBA totals have different signal structure from moneylines, and props are even more sensitive to minute and usage assumptions.
- If the model expands too early, it can look sophisticated while actually becoming less reliable.

#### Pass 9 acceptance rule

Pass 9 is only done when moneylines, totals, and props are handled as separate readiness stages and the model does not expand into a harder market until the easier one is stable.

### Pass 10: LLM as analyst, not final decider

Once market scope is controlled, the last safeguard is to keep the LLM in the right role.

#### What the LLM should do

- Explain the edge in natural language
- Summarize the structured evidence
- Turn the pick into a readable card
- Highlight risks, uncertainty, and alternative interpretations

#### What the LLM should not do

- Override the no-bet gate
- Override the market-price filter
- Invent confidence that the scoring system does not support
- Replace the calibrated predictor

#### What must be measured

- Whether the LLM explanation matches the structured inputs
- Whether the LLM ever contradicts the scoring engine
- Whether the final decision can be reproduced without the prose layer

#### Why this matters

- FiveThirtyEight-style NBA prediction systems are driven by structured ratings, depth charts, pace, and simulation logic; explanation is secondary to the actual forecast machinery.
- A betting system with a persuasive explanation but a weak decision engine is still a losing system.
- The analyst layer should make the output usable, not make the bet.

#### Pass 10 acceptance rule

Pass 10 is only done when the LLM can explain the pick without changing the decision, and the calibrated scoring system remains the only final authority.

### Pass 11: Timing advantage

Batch 2 starts by asking whether fresh information can change the pick before the market fully adjusts.

#### What timing advantage means here

- Late injury news should move the model faster than stale pregame context.
- A source that arrives closer to tip-off can matter more than an older source with the same content.
- The model should react to timing, not just to content.

#### What must be measured

- Source publication time versus model reaction time
- Whether late injury or lineup news changes the recommendation
- Whether the recommendation changed before the market closed the gap
- Timing score by source type and market type

#### Why this matters

- Injury and availability updates are often where real NBA betting edge lives.
- Social and beat-writer sources can surface changes early, but only if the model is fast enough to use them.
- If the model reacts too late, the edge has already been priced out.

#### Pass 11 acceptance rule

Pass 11 is only done when fresh pre-tip-off information can visibly change the decision earlier than stale context and the timing score can show that the model actually captured that edge.

### Pass 12: Drift control

Once the model can react quickly, it has to stay calibrated as the environment changes.

#### What drift control means here

- Live performance should be checked against the last validated baseline.
- A model that looked good last month can quietly worsen this month.
- Retraining should happen because drift was detected, not because the model feels old.

#### What must be measured

- ROI drift
- Calibration drift
- CLV drift
- Skip quality drift
- Whether retraining actually improves the next window

#### Why this matters

- Time-series and probabilistic forecast research shows that concept drift can break calibration even when predictions still look plausible.
- Recentness-biased and adaptive-window methods exist because static training eventually fails on non-stationary data.
- If the model retrains too often, it chases noise; if it retrains too rarely, it becomes stale.

#### Pass 12 acceptance rule

Pass 12 is only done when the system can detect drift, explain whether it is meaningful, and retrain only when the new baseline is better than the old one.

### Pass 13: Price discipline permanence

After drift is controlled, price discipline has to become permanent instead of occasional.

#### What price discipline permanence means here

- Stake should always be compared to the best available market number.
- A bet can be directionally right and still be EV-negative if the price is bad.
- Exposure and bankroll limits should apply every slate, not only when the model feels uncertain.

#### What must be measured

- Best available price versus Stake on every active recommendation
- Opening, current, and closing line behavior
- Whether the model would have benefited from skipping because of price
- Exposure concentration by slate, market, and team

#### Why this matters

- Sports betting market efficiency research shows that selecting the best available odds across bookmakers can reveal different efficiency levels and better forecasting opportunities.
- Price movements also carry information when informed traders are active, so the model should treat the number as a live signal, not a static label.
- A model that only cares about direction can still bleed money through bad pricing.

#### Pass 13 acceptance rule

Pass 13 is only done when the system consistently shops the number, respects exposure limits, and can show that price discipline is built into every recommendation rather than added afterward.

### Pass 14: Market scope control hardening

After price discipline is permanent, market scope has to stay narrow until each layer proves stable.

#### What scope hardening means here

- Moneylines are the first market because they are the most direct expression of team strength.
- Totals come next because they need pace, efficiency, and context to be stable.
- Props come last because they depend heavily on minutes, usage, and role assumptions.

#### What must be measured

- Market-specific ROI
- Market-specific calibration
- Market-specific CLV
- Market-specific skip rate
- Cross-market contamination

#### Why this matters

- Public sports-betting research shows that some market segments behave differently than others, and some become efficient only when information is fully incorporated.
- Totals can be biased early in a season, but that does not mean the same edge exists for moneylines or props.
- If the model expands too early, it can become more complex without becoming more profitable.

#### Pass 14 acceptance rule

Pass 14 is only done when each market type has its own maturity threshold and the model refuses to expand into harder markets before the simpler ones are clearly stable.

### Pass 15: LLM containment hardening

After scope control is stable, the final Batch 2 safeguard is to keep the LLM permanently in analyst mode.

#### What containment means here

- The LLM should describe the pick, not decide it.
- The predictor and market filters remain the final authority.
- A persuasive explanation cannot promote a weak bet into an active one.

#### What must be measured

- Whether the LLM explanation matches the structured output
- Whether the LLM ever contradicts the predictor
- Whether the final decision is reproducible without the prose layer

#### Why this matters

- The model is strongest when the predictor is deterministic and the LLM is interpretive.
- A betting system that lets prose carry decision authority can talk itself into weak spots.
- The analyst layer should make the output human-friendly, not decision-driven.

#### Pass 15 acceptance rule

Pass 15 is only done when the LLM can explain the recommendation without changing it, and the predictor remains the final authority even when the prose is compelling.

---

## What Is Capping The Ceiling

The current model is still capped by five things:

1. **No point-in-time backtest**
   - The README describes the system, but it does not yet prove the edge on historical snapshots only.

2. **Calibration is not enforced**
   - The model says calibration matters, but it does not yet use calibration as a hard gate.

3. **No formal no-bet engine**
   - The philosophy says skip often, but the system does not yet enforce that discipline in code.

4. **Source freshness and trust are not operationalized**
   - Odds, injuries, social sentiment, and stats need explicit source quality scoring.

5. **Market discipline is incomplete**
   - Stake pricing, line shopping, bankroll sizing, and exposure controls still need to be built into the process.

Detailed versions of these blockers and their fixes live in [`problems-plan.md`](../plans/problems-plan.md) and [`ftw-plan.md`](../plans/ftw-plan.md).

### What the research says about the ceiling

- NBA injury edges can exist at open, but they often get priced out by close, so the model must care about timing and line movement more than static confidence.
- Calibration is more important than raw accuracy for sports betting ROI, which is why probability quality has to outrank winner-chasing.
- Some bookmakers and exchanges provide measurably different probability forecasts, which means line shopping can improve the price of the bet before any model edge is applied.
- Early-season totals in the NBA have shown exploitable inefficiency in the literature, while sides tend to be closer to efficient.
- Informed trading is visible through line movement, so the model should learn from price paths instead of treating them as background noise.

---

## Iteration Rule

This project should be hardened in repeated passes, not one giant rewrite.

### The loop

1. Identify the current blocker.
2. Research the blocker from public sources.
3. Write the blocker in `problems-plan.md`.
4. Write the fix path in `ftw-plan.md`.
5. Scrutinize the fix as a predictor, backend developer, and game-time decision maker.
6. Push the best version of the fix back into this README.
7. Re-check the next blocker.

### The first 10 passes

- Pass 1: prove the edge with point-in-time backtesting.
- Pass 2: make calibration the real model gate.
- Pass 3: enforce a hard no-bet threshold.
- Pass 4: anchor on closing-line value and Stake price.
- Pass 5: score source trust and freshness.
- Pass 6: prioritize late timing edges.
- Pass 7: reduce model drift and overfitting.
- Pass 8: add price discipline and line shopping.
- Pass 9: constrain market scope to the most modelable bets first.
- Pass 10: keep the LLM as analyst, not final decider.

### Pass gates

- **Pass 1 gate**: backtest results must come from frozen pre-tip-off snapshots only, with no leakage.
- **Pass 2 gate**: confidence bins must match observed hit rates closely enough to trust the score.
- **Pass 3 gate**: the model must skip weak spots by default and only activate on real edge.
- **Pass 4 gate**: the model must show positive closing-line value against Stake or the market.
- **Pass 5 gate**: stale, brittle, or low-trust sources must be downweighted automatically.
- **Pass 6 gate**: fresh injury and lineup news must move the model before stale sentiment does.
- **Pass 7 gate**: model performance must hold up across time, not just on one historical slice.
- **Pass 8 gate**: Stake must not be treated as the final truth if a better price exists elsewhere.
- **Pass 9 gate**: moneylines must be stable before totals or props are added.
- **Pass 10 gate**: the LLM must never be the final decider when the scoring model says skip.

Do not advance to the next pass until the current gate is satisfied.

### Pass outputs

- **Pass 1 output**: a replay report with ROI, hit rate, CLV, and leakage checks by market type.
- **Pass 2 output**: calibration curves, reliability checks, and acceptance thresholds per probability bin.
- **Pass 3 output**: a visible skip rate, a no-bet reason log, and the final activation threshold.
- **Pass 4 output**: a market comparison report showing Stake price versus best available line and closing price.
- **Pass 5 output**: source trust weights, freshness scores, and source failure flags per feed.
- **Pass 6 output**: a timing score that shows which picks changed because of fresh injury or lineup news.
- **Pass 7 output**: drift monitoring and retrain triggers by month and by market.
- **Pass 8 output**: a line-shopping table across books with the selected price highlighted.
- **Pass 9 output**: market readiness flags for moneylines, totals, and props with promotion rules.
- **Pass 10 output**: an LLM explanation layer that cannot override the scoring engine or no-bet gate.

---

## What The Best Version Would Do

If this system were being built by the best free AI betting researcher, it would not try to bet everything. It would try to be the cleanest possible edge-finder.

### What it would prioritize

1. **Extreme selectivity**
   - Bet only when the edge is actually there.
   - Most games should end in `SKIP`, not `BET`.

2. **Probability quality over winner-chasing**
   - Predictive output should be calibrated probabilities, not just a winner label.
   - A well-calibrated `60%` beat is more useful than a noisy `70%` claim.

3. **Market-first thinking**
   - Stake’s line is the thing being attacked.
   - The system should ask whether the market is wrong, not just whether a team is good.

4. **Timing advantage**
   - The best version would be strongest when information is newest.
   - Late injury updates, rotation changes, and line movement are the most valuable windows.

5. **Strong abstention**
   - The model must be comfortable saying no.
   - A good no-bet is better than a forced weak bet.

6. **Source hierarchy**
   - Official injury reports, market movement, and verified stats anchor the pick.
   - Reddit and X are context layers, not final authority.

7. **Price discipline**
   - Compare Stake against other books before acting.
   - If the number is bad, the bet is bad even if the team looks right.

8. **Closed-loop learning**
   - Every pick, skip, and outcome should feed back into calibration and thresholds.
   - The system should get more selective after every cycle.

### What the strongest predictor stack would look like

- **Frozen snapshot layer**: stores every pre-tip-off input so replay is honest.
- **Market comparator**: compares Stake against the best available price and the close.
- **Probability engine**: turns features into calibrated win probabilities.
- **No-bet gate**: blocks weak edges before they become recommendations.
- **Timing engine**: rewards fresh injury, rotation, and line movement signals.
- **Source scorer**: downweights stale or brittle feeds before prediction.
- **LLM analyst**: explains the result in plain language without deciding the bet.

### What it would avoid

- Chasing every “obvious” favorite.
- Trusting social sentiment more than market movement.
- Treating scraping volume as the same thing as edge.
- Letting the LLM invent confidence.
- Confusing a good prediction with a good bet.

### The free-AI version of success

The best free version would be a model that is:
- selective,
- calibrated,
- price-aware,
- fast on new information,
- and willing to skip the majority of slates.

That is the path that gives the system the best chance of turning useful information into real betting edge.

---

## What This System Is Supposed To Be

NBA Oracle is a **research-first betting intelligence system**. Its job is to turn messy public information into a disciplined pregame decision, not to pretend it has magical certainty.

### The core promise

- Pull in the strongest available public signals before tip-off.
- Convert those signals into a probability, not a gut feeling.
- Compare the model probability against the market price.
- Only surface bets when the edge is real enough to matter.
- Log everything so the system can be audited and improved later.

### The operating model

1. **Collect**: odds, injuries, stats, travel, rest, and sentiment.
2. **Structure**: normalize those inputs into one matchup context.
3. **Score**: estimate win probability and expected value.
4. **Explain**: generate a readable pick card with the why behind it.
5. **Store**: save the pick, inputs, confidence, and outcome history in Supabase.
6. **Learn**: compare predictions against results and adjust weights over time.

### What the system is not

- It is not a guarantee of profit.
- It is not a copy-paste picks bot.
- It is not a pure LLM guessing engine.
- It is not meant to bet every game.
- It is not useful if it cannot say “skip.”

### What success looks like

- The model stays calibrated over time.
- Pick decisions beat the closing line often enough to justify risk.
- The no-bet rate stays healthy instead of forcing action on weak edges.
- The reasoning stays explainable enough that a human can audit it quickly.
- The system becomes better from feedback instead of drifting into noise.

### Reference checkpoint

For a fast view of what is already implemented versus what is still only specified, use [project-status-matrix.md](../status/project-status-matrix.md).

### Design principles

- **Edge over volume**: fewer, better bets beat more action.
- **Signal hierarchy**: market price and injuries matter more than chatter.
- **Explainability first**: every active pick needs a clear reason.
- **Auditability**: every recommendation should be traceable later.
- **No-bet discipline**: skipping is a feature, not a failure.

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────┐
│              LAYER 0 — META SCHEDULER                    │
│         Fixed cron fires at 12:00 AM IST daily           │
│  → Fetches today's NBA schedule via nba_api              │
│  → Finds first tip-off time, calculates T - 2hrs (IST)   │
│  → Sends Gmail: "Analysis will run at [TIME] IST today"  │
│  → Registers dynamic one-shot job via APScheduler        │
└────────────────────────────┬─────────────────────────────┘
                             │  fires at T - 2hrs
┌────────────────────────────▼─────────────────────────────┐
│              LAYER 1 — SCOPE RESOLVER                    │
│   Pulls only today's games + teams playing today         │
│   (No wasted analysis on rest-day teams)                 │
└────────────────────────────┬─────────────────────────────┘
                             │  per matchup
┌────────────────────────────▼─────────────────────────────┐
│              LAYER 2 — PARALLEL DATA INGESTION           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  📈 Odds Scraper     → The-Odds-API (free tier)     │ │
│  │  🏥 Injury Feed      → nba_api + ESPN (unofficial)  │ │
│  │  💬 Sentiment        → PRAW (Reddit) + Nitter/X     │ │
│  │  📊 Stats Puller     → nba_api + BRef scrape        │ │
│  └─────────────────────────────────────────────────────┘ │
└────────────────────────────┬─────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────┐
│              LAYER 3 — CONTEXT BUILDER                   │
│   Assembles all signals into a structured prompt block   │
│   per matchup, fed into LLM reasoning engine             │
└────────────────────────────┬─────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────┐
│              LAYER 4 — LLM REASONING ENGINE              │
│            (Claude Sonnet via Anthropic API)             │
│   - Analyzes all 4 signal layers per game                │
│   - Assigns confidence score                             │
│   - Identifies edge / value in the line                  │
│   - Flags LOW CONVICTION picks (< 65%) as SKIP           │
└────────────────────────────┬─────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────┐
│              LAYER 5 — OUTPUT & DELIVERY                 │
│  → Pick Cards pushed to Telegram bot (per game)         │
│  → Full digest summary (all games) sent to Telegram      │
│  → Supabase logs pick + confidence for accuracy tracking   │
└──────────────────────────────────────────────────────────┘
```

---

## 📡 Deep Analytics — The 15+ Signal Variables

This is what separates NBA Oracle from a basic "who's favored" checker. The stats puller collects **15+ contextual variables per team per game**, grouped into 5 categories:

### 1. 🏃 Pace & Style Matchup
| Variable | Why It Matters |
|---|---|
| Pace (possessions per 48) | Fast-paced teams score more but also give up more — affects total & ML |
| Offensive / Defensive Rating | Points per 100 possessions — the truest efficiency measure |
| 3-Point Attempt Rate | High 3PA teams are variance-heavy — risky ML bets |
| Turnover % | Turnover-prone teams collapse under pressure |
| Rebounding differential | Second-chance points can swing close games |

### 2. 😴 Rest & Travel (The Hidden Edge)
| Variable | Why It Matters |
|---|---|
| Days of rest (each team) | 0 days = back-to-back, massive fatigue multiplier |
| Back-to-back indicator | Teams on B2Bs cover at ~44% — well below 50% |
| Cross-country travel | LA → Boston red-eye = invisible disadvantage |
| Games in last 7 days | Cumulative fatigue over a grueling stretch |
| Home/Away split (current season) | Some teams are dramatically better at home |

### 3. 📈 Recent Form (Last 10 Games)
| Variable | Why It Matters |
|---|---|
| Win/Loss record (L10) | Rolling momentum — not season-long averages |
| Net rating trend (L10) | Are they getting better or declining? |
| Point differential (L10) | Margin of victory/loss reveals true competitiveness |
| Clutch record (games within 5pts, L5min) | Who wins when it matters? |
| Scoring variance | Consistent teams are safer ML bets than streaky ones |

### 4. 🔁 Head-to-Head Context
| Variable | Why It Matters |
|---|---|
| H2H record (current season) | Some matchups are stylistic mismatches |
| H2H average margin | Is this historically a blowout or a nailbiter? |
| Home team H2H edge | Courts matter more against specific opponents |

### 5. 🏥 Injury Impact Scoring
Not all injuries are equal. The system scores injury impact by:
- **Player's usage rate** (high usage = high impact)
- **Position scarcity** (losing your only true PG vs. a backup wing)
- **Recency** (day-of scratch vs. already-known absence)
- **Replacement quality** (starter-level backup vs. G-League call-up)

Each injury is scored 0–10 and factored into the team's adjusted projected strength.

---

## 🤖 Telegram Bot Commands

The bot runs 24/7 on your laptop and accepts commands at any time:

| Command | Action |
|---|---|
| `/picks` | Today's pick cards (all games) |
| `/picks [team]` | Pick card for a specific game, e.g. `/picks lakers` |
| `/result WIN` or `/result LOSS` | Log outcome for the most recent pick |
| `/result [game_id] WIN` | Log outcome for a specific game |
| `/stats` | Your all-time pick record (win rate, ROI, avg confidence) |
| `/stats week` | This week's performance |
| `/history` | Last 10 picks with outcomes |
| `/schedule` | Today's NBA schedule + tip-off times (IST) |
| `/signal [team]` | Raw signal breakdown for a team without a full pick card |
| `/help` | Command list |

> All commands work in a private Telegram chat with your bot. No group chats, no public access.

---

## 💻 Deployment — Running on Your Laptop

### Auto-start on boot

**Windows (Task Scheduler):**
```
Trigger: At log on
Action:  python C:\nba-oracle\meta_scheduler.py
```

**macOS / Linux (systemd or launchd):**
```bash
# Linux systemd service
[Unit]
Description=NBA Oracle Meta Scheduler

[Service]
ExecStart=/usr/bin/python3 /home/user/nba-oracle/meta_scheduler.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Laptop Sleep Handling
The main risk with laptop deployment is **sleep/hibernate interrupting cron**. Mitigations:
- Use `wakepy` Python library to prevent sleep during active analysis window
- Meta-scheduler sets a **no-sleep lock** from 11:55 PM IST to 12:10 AM IST (during cron window)
- Analysis pipeline sets a **no-sleep lock** for its full runtime (~30 min)
- If script detects it woke up late (missed trigger), it sends a Gmail alert: *"NBA Oracle: Missed trigger. Run analysis manually."*

### Keeping It Alive
```
meta_scheduler.py runs as a background process (nohup / pythonw on Windows)
Telegram bot runs in a separate thread within the same process
APScheduler manages all timed jobs in-process
```

---

## ⏰ Scheduling Deep Dive

This is the trickiest part of the system. NBA tip-offs vary every day, so a static `cron` job can't directly fire "2 hours before first game." Here's the two-layer approach:

### Layer A — The Fixed Cron (12 AM IST)
```
# crontab entry
0 18 * * * /usr/bin/python3 /path/to/meta_scheduler.py  # 18:00 UTC = 12:00 AM IST (UTC+5:30)
```
This job runs every night at midnight IST. It:
1. Calls `nba_api` to get today's game schedule
2. Extracts the **earliest tip-off time** and converts to IST
3. Calculates `trigger_time = first_tip_off_IST - 2 hours`
4. Sends a Gmail: *"NBA Oracle analysis scheduled for [trigger_time] IST"*
5. Uses **APScheduler** to register a one-shot job at `trigger_time`

### Layer B — The Dynamic One-Shot (APScheduler)
```python
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler(timezone="Asia/Kolkata")
scheduler.add_job(run_analysis, 'date', run_date=trigger_time)
scheduler.start()
```
This fires `run_analysis()` exactly 2 hours before tip-off, which kicks off the full pipeline.

### Edge Cases Handled
| Scenario | Behavior |
|---|---|
| No games today | Meta-scheduler detects empty schedule, sends Gmail: "No games today. Oracle resting." |
| All games after midnight IST | Trigger time calculated correctly across midnight boundary |
| API rate limit hit | Exponential backoff + fallback to cached odds |
| Script crash | Systemd watchdog restarts process; Gmail alert sent on failure |

---

## 📤 Output Format — The Pick Card

Every analysis run produces a structured **Pick Card**:

```
╔══════════════════════════════════════════════╗
║  🏀 NBA ORACLE — PICK CARD                  ║
║  Game: Lakers vs. Celtics                   ║
║  Tip-off: April 3, 2026 | 7:30 PM ET        ╠══════════════════════════════════════════════╣
║  📌 PICK: Boston Celtics ML                 ║
║  💰 Stake Odds: -145                        ║
║  🎯 Confidence: 74%                         ║
╠══════════════════════════════════════════════╣
║  SIGNAL BREAKDOWN                           ║
║  ─────────────────────────────────────────  ║
║  Odds Movement:  Line moved from -130→-145  ║
║                  (sharp money on Celtics)    ║
║  Injury Impact:  LeBron questionable (knee)  ║
║                  AD listed as probable       ║
║  Sentiment:      r/nba bullish on Celtics,   ║
║                  Jalen Brown trending +ve    ║
║  Stats Edge:     Celtics 8-2 ATS vs. LA,    ║
║                  +6.2 net rating last 10     ║
╠══════════════════════════════════════════════╣
║  🤖 AI REASONING SUMMARY                   ║
║  "Sharp line movement toward Boston,         ║
║   compounded by LeBron injury uncertainty    ║
║   and Celtics' dominant recent form.         ║
║   Value exists at current price."            ║
╚══════════════════════════════════════════════╝
```

---

## 🔧 Tech Stack

| Layer | Tool | Cost |
|---|---|---|
| Language | Python 3.11+ | Free |
| Fixed Scheduler | Linux cron | Free |
| Dynamic Scheduler | APScheduler | Free |
| NBA Schedule & Stats | `nba_api` Python library | Free |
| Odds Data | The-Odds-API (500 req/month free tier) | Free |
| Injury Feed | ESPN unofficial API + `nba_api` | Free |
| Reddit Sentiment | PRAW (Reddit API) | Free |
| Twitter/X Sentiment | Nitter RSS scrape (no API key needed) | Free |
| Historical Stats | `nba_api` + Basketball Reference scrape | Free |
| LLM Engine | Anthropic Claude API (claude-sonnet-4-5) | ~₹1–2/day |
| Learning Engine | `scikit-learn` (LogisticRegression) | Free |
| Pattern Miner | `mlxtend` (association rules) | Free |
| Dashboard Backend | FastAPI | Free |
| Dashboard Frontend | React 18 + Vite + Recharts + TailwindCSS | Free |
| Telegram Output | `python-telegram-bot` library | Free |
| Storage | Supabase (Postgres) | Free tier available |

> **LLM cost note:** Full day analysis (8–12 games) uses ~50–80K tokens. At Claude Sonnet pricing, that's roughly **₹1–2 per day**. Practically free.

> **Twitter/X note:** Official API is paywalled. Nitter instances scrape public tweets — free but brittle. Fallback: Reddit-only sentiment if Nitter breaks.

---

## 📁 Project Structure

```
nba-oracle/
├── meta_scheduler.py            # Cron entry point — 12 AM IST
├── main.py                      # Core analysis pipeline
├── config.py                    # API keys, constants, IST timezone
├── confidence_weights.json      # Live signal weights (auto-updated by learner)
│
├── ingestion/
│   ├── schedule_fetcher.py      # nba_api — today's games only
│   ├── odds_scraper.py          # The-Odds-API — live lines + movement
│   ├── injury_feed.py           # ESPN unofficial + nba_api
│   ├── sentiment_scraper.py     # PRAW (Reddit) + Nitter (X)
│   └── stats_puller.py          # nba_api — 15+ variables per team
│
├── processing/
│   ├── scope_resolver.py        # Filter to today's matchups
│   ├── context_builder.py       # Signal → structured LLM prompt
│   └── preprocessor.py          # Cleaning + normalization
│
├── reasoning/
│   ├── llm_engine.py            # Claude API + response parsing
│   ├── confidence_scorer.py     # Weighted scoring + SKIP logic
│   └── prompt_injector.py       # Injects learned patterns into prompt
│
├── learning/
│   ├── weight_optimizer.py      # LogisticRegression on pick history
│   ├── pattern_miner.py         # Rule extraction from winning picks
│   └── learning_cycle.py        # Orchestrates full retraining loop
│
├── output/
│   ├── pick_card.py             # Formats pick cards
│   └── telegram_bot.py          # Bot + /picks /result /stats /history
│
├── notifications/
│   └── gmail_notifier.py        # 12 AM IST schedule confirmation
│
├── storage/
│   └── picks_db.py              # Supabase: picks, patterns, weights history
│
├── dashboard/
│   ├── backend/
│   │   └── api.py               # FastAPI — serves Supabase/Postgres data as REST API
│   └── frontend/
│       ├── src/
│       │   ├── pages/
│       │   │   ├── Today.jsx        # Live pick cards + countdown
│       │   │   ├── Performance.jsx  # Win rate, confidence scatter
│       │   │   ├── Learning.jsx     # Weight evolution, patterns
│       │   │   └── Trends.jsx       # Line movement, sentiment, injuries
│       │   └── components/
│       └── vite.config.js
│
├── prompts/
│   └── analysis_prompt.md       # Master LLM system prompt (editable)
│
└── README.md
```

---

## 🎯 Confidence Scoring — Base Layer (v1)

Before the self-learning engine kicks in (needs 30+ picks), the LLM uses these static weights:

| Signal Factor | Base Weight | Notes |
|---|---|---|
| Odds / line movement | 30% | Sharp money = strongest single signal |
| Injury impact score | 25% | Weighted by usage rate + position scarcity |
| Deep stats edge (L10 form, rest, travel) | 25% | 15-variable context block |
| Sentiment consensus | 20% | Only acts on strong directional consensus |

> **Threshold rule:** Confidence **≥ 65%** = active pick. Below = logged as `⚠️ SKIP`.

---

## 🧬 Self-Learning Engine — Intelligence Through Experience

> *"This is the most important part of the entire system."*

The self-learning engine transforms NBA Oracle from a static analyzer into a **system that gets sharper every single day** — learning from what worked, unlearning what didn't, and adapting its weights to your specific pick history.

### How It Works — The Feedback Loop

```
┌──────────────────────────────────────────────────────────┐
│                    PICK MADE                             │
│  Oracle outputs pick + confidence + raw signal values    │
│  → All 15+ signal values stored to Supabase (picks_log)   │
└────────────────────────┬─────────────────────────────────┘
                         │  (next day)
┌────────────────────────▼─────────────────────────────────┐
│                 OUTCOME LOGGED                           │
│  User logs WIN / LOSS via Telegram: /result WIN          │
│  outcome field updated in picks_log                      │
└────────────────────────┬─────────────────────────────────┘
                         │  (every 30 new picks)
┌────────────────────────▼─────────────────────────────────┐
│              META-LEARNING CYCLE                         │
│                                                          │
│  1. WEIGHT OPTIMIZER                                     │
│     Logistic regression trained on picks_log            │
│     X = [odds_score, injury_score, stats_score,          │
│           sentiment_score, rest_diff, travel_flag, ...]  │
│     y = outcome (1=WIN, 0=LOSS)                          │
│     → Learns which signals actually predict YOUR wins    │
│     → Outputs new signal weights                         │
│                                                          │
│  2. PATTERN MEMORY BUILDER                               │
│     Extracts recurring winning conditions:               │
│     e.g. "When rest_diff ≥ 2 AND sharp line move        │
│           → 78% win rate in your history (n=18)"        │
│     → Stored as named patterns in patterns_db           │
│                                                          │
│  3. PROMPT INJECTOR                                      │
│     Injects top 5 learned patterns into LLM system      │
│     prompt before next analysis run                      │
│     → LLM now reasons WITH your historical edge data    │
│                                                          │
│  4. WEIGHT FILE UPDATER                                  │
│     Overwrites confidence_weights.json with new values   │
│     Confidence scorer uses updated weights next run      │
└────────────────────────┬─────────────────────────────────┘
                         │  (every new pick)
┌────────────────────────▼─────────────────────────────────┐
│              PICKS MADE WITH EVOLVED INTELLIGENCE        │
│  Oracle now knows: which signals YOU win on, which       │
│  patterns in YOUR data repeat, and how to weight them    │
└──────────────────────────────────────────────────────────┘
```

### The Three Learning Layers

**Layer 1 — Weight Optimizer (sklearn LogisticRegression)**
Trains on your pick history. Learns which of the 15+ signals *actually* correlate with your wins — not generic sports betting theory, but *your specific data*. Replaces the hard-coded weights with personalized ones.

```python
# runs every 30 picks
X = picks_df[SIGNAL_COLUMNS]
y = picks_df['outcome']  # 1=WIN, 0=LOSS
model = LogisticRegression().fit(X, y)
new_weights = dict(zip(SIGNAL_COLUMNS, model.coef_[0]))
save_weights(new_weights)  # → confidence_weights.json
```

**Layer 2 — Pattern Memory (Rule Miner)**
Scans pick history for high-win-rate signal combinations using a simple association rule miner. If `rest_diff ≥ 2 AND sharp_line_move = True` has won 78% of the time in your data across 18+ instances — that's a named pattern. Named patterns get injected into the LLM prompt as explicit context.

**Layer 3 — LLM Prompt Evolution**
The system prompt isn't static. Before each analysis run, the Prompt Injector reads the top 5 patterns from `patterns_db` and prepends them:
```
[LEARNED PATTERNS FROM YOUR HISTORY]
Pattern #1: Rest advantage ≥ 2 days + sharp line movement → 78% win rate (n=18)
Pattern #2: Home team + opponent on B2B + net rating diff > 4 → 81% win rate (n=11)
Pattern #3: High injury score on road team + Reddit consensus → 71% win rate (n=22)
...
[END LEARNED PATTERNS]
```
The LLM now reasons with your personal edge data baked in — getting smarter the longer you run it.

### Learning Milestones

| Picks Logged | System Behavior |
|---|---|
| 0–29 | Base weights only. Static analysis. |
| 30+ | Weight Optimizer activates. Weights personalized. |
| 50+ | Pattern Miner activates. Named patterns injected into LLM. |
| 100+ | Full feedback loop. Weights re-optimize every 30 new picks. Patterns evolve. |
| 200+ | High-confidence regime: system flags picks matching 2+ historical winning patterns. |

> At 200+ picks you're running one of the most personalized NBA betting intelligence systems in existence. Not because it's "AI" — because it's *your* AI, trained on *your* outcomes.

---

## 📊 Pick Accuracy Tracker — Supabase / Postgres Schema

Supabase is the source of truth for picks, outcomes, learned patterns, and weight history. The schema below reflects the underlying Postgres tables.

```sql
-- Core picks table
CREATE TABLE picks_log (
    id              INTEGER PRIMARY KEY,
    game_id         TEXT,
    date            TEXT,
    matchup         TEXT,
    pick_team       TEXT,
    odds            REAL,
    confidence      REAL,

    -- Raw signal values (feed into weight optimizer)
    odds_score      REAL,
    injury_score    REAL,
    stats_score     REAL,
    sentiment_score REAL,
    rest_diff       INTEGER,     -- home_rest - away_rest (days)
    travel_flag     INTEGER,     -- 1 if opponent on cross-country trip
    b2b_flag        INTEGER,     -- 1 if opponent on back-to-back
    net_rating_diff REAL,
    h2h_edge        REAL,
    form_score      REAL,        -- L10 composite

    signal_breakdown TEXT,       -- full JSON blob for dashboard
    llm_reasoning   TEXT,        -- raw LLM output

    outcome         TEXT,        -- 'WIN' / 'LOSS' / 'PUSH' / NULL
    logged_at       TEXT
);

-- Learned patterns table
CREATE TABLE patterns_db (
    id              INTEGER PRIMARY KEY,
    pattern_name    TEXT,
    conditions      TEXT,        -- JSON rule definition
    win_rate        REAL,
    sample_size     INTEGER,
    last_updated    TEXT
);

-- Weight history (track how weights evolve over time)
CREATE TABLE weight_history (
    id              INTEGER PRIMARY KEY,
    weights_json    TEXT,
    trained_on_n    INTEGER,     -- number of picks used
    recorded_at     TEXT
);
```

---

## 🖥️ Web Dashboard

A locally-hosted React + Vite dashboard. Not a simple stats page — a full **performance intelligence interface**, designed to feel like a personal Bloomberg Terminal for NBA betting.

### Tech
```
Frontend:  React 18 + Vite + Recharts + TailwindCSS + shadcn/ui
Backend:   FastAPI (Python) — serves Supabase/Postgres data as REST API on :8000
Dashboard: localhost:3000
```
The FastAPI server spins up inside `meta_scheduler.py` on startup — dashboard is always live while Oracle is running.

---

## 🎨 Dashboard Design System

Design direction: **data-terminal meets dark luxury.** Directly inspired by CylinderCheck.in's dense functional dark aesthetic and 21st.dev's polished component library — glassmorphism cards, animated counters, sharp micro-interactions.

### Color Palette
```
Background:    #08080F   (near-black, slightly blue-tinted)
Surface:       #10101A   (card fills)
Surface+:      #16162A   (elevated cards, modals)
Border:        #1E1E35   (subtle dividers)
Accent:        #00E5A0   (electric mint-green — NBA court energy)
Accent-dim:    #00E5A020 (accent at 12% opacity for glows/fills)
Text-primary:  #F0F0FF   (near-white, cool tint)
Text-secondary:#8888AA   (muted labels)
Text-dim:      #44445A   (placeholders, inactive states)
WIN:           #22C55E
LOSS:          #EF4444
SKIP:          #F59E0B
```

### Typography
```
Display/Headers:  'Syne'           — geometric, sharp (Google Fonts)
Body/Labels:      'Inter'          — clean and readable
Data/Numbers:     'JetBrains Mono' — ALL stat values, odds, scores, rates
```
Every number renders in `JetBrains Mono` — odds like `-145`, win rates like `74.3%`, confidence `82%`. Gives a Bloomberg Terminal / trading desk feel across the whole dashboard.

### Card Style (21st.dev glass card pattern)
```css
.card {
  background: #10101A;
  border: 1px solid #1E1E35;
  border-radius: 12px;
  box-shadow: 0 0 0 1px rgba(0,229,160,0.04),
              0 8px 32px rgba(0,0,0,0.4);
  transition: border-color 200ms, box-shadow 200ms;
}
.card:hover {
  border-color: #00E5A030;
  box-shadow: 0 0 24px rgba(0,229,160,0.07);
}
.metric-accent {
  color: #00E5A0;
  text-shadow: 0 0 20px rgba(0,229,160,0.4);
}
```

### Pages

**`/login` — Auth Gate**
Full-screen dark canvas with a faint animated dot-grid background (21st.dev shader pattern). Centered card: NBA Oracle wordmark + single password input + "Enter Oracle" CTA. Mint-green border glow on focus. Failed attempt: card shakes, border pulses red.

**`/` — Today's Command Center**
- Top bar: today's date + "N games" badge + live countdown to first tip-off in large monospace
- 2-col pick card grid — each card has: matchup header, Oracle's pick team highlighted with accent border, animated confidence progress ring (CylinderCheck gauge aesthetic), 4 thin horizontal signal bars, WIN/LOSS/PENDING badge
- Cards stagger-animate in on load (21st.dev card reveal)
- Bottom strip: signal heatmap across all today's games

**`/performance` — Pick Intelligence Hub**
- 4 KPI cards top row: All-time Win Rate, Last 7 Days, Avg Confidence, Total Picks — all primary numbers in mint JetBrains Mono
- Recharts AreaChart: rolling win rate, mint gradient fill, 7-day average overlay
- Confidence vs. Outcome scatter: each dot = one pick. X = confidence, Y = win/loss. Clear upward trend = model working.
- shadcn `<Table>`: pick history, sortable, WIN/LOSS/SKIP badges, expandable row reveals full signal breakdown + raw LLM reasoning

**`/learning` — Self-Learning Engine Monitor**
- Multi-line chart: each signal's weight over learning cycles — watch them drift as Oracle learns
- 4 radial arc gauges (CylinderCheck gauge style): current weight per signal as % of total
- Pattern cards grid: each named pattern shows win rate badge, sample size, last triggered, conditions in monospace. High win-rate patterns get a mint glow border.
- Learning progress banner: "Next optimization in 12 picks" with a thin mint progress bar

**`/trends` — Market Intelligence**
- Line movement chart: opening vs. current odds per game, sharp movement annotated
- Sentiment feed: scrollable Reddit + X posts with team tag + sentiment bar
- Injury impact table: recent injuries, impact score bars 0-10 color-coded

### Shared Components (21st.dev sourced)
| Component | Usage |
|---|---|
| Animated counter | Win rate, pick count — counts up on load |
| Progress ring | Confidence score on pick cards |
| Gradient badge | WIN / LOSS / SKIP / LOW CONVICTION |
| Collapsible row | Expand pick history for LLM reasoning |
| Toast | `/result` logged, learning cycle fired |
| Sidebar nav | Icon + label, active = accent left-border |
| Command palette | `Cmd+K` — jump to any page or game |

### 🔐 Authentication & Protection

The dashboard is **password-protected**. Your pick history, learned patterns, signal weights, and betting data stay private — no one on your local network can access them without the password.

**Auth Flow:**
```
Browser hits localhost:3000
└── React checks for valid JWT in localStorage
    ├── No token / expired → redirect to /login
    └── Valid token → render dashboard

/login page
└── User enters password
└── POST /api/auth/login → FastAPI
    └── bcrypt hash comparison
        ├── Match → issue signed JWT (24hr expiry)
        └── No match → 401 + 60s lockout after 5 failed attempts

All /api/* routes
└── FastAPI JWT dependency on every request
    ├── Valid → serve data
    └── Invalid / missing → 401 Unauthorized
```

**Core auth module:**
```python
# backend/auth.py
from passlib.context import CryptContext
from jose import jwt
import os

pwd_context = CryptContext(schemes=["bcrypt"])
SECRET_KEY = os.environ["ORACLE_SECRET_KEY"]  # random, never hardcoded
ALGORITHM  = "HS256"
TOKEN_TTL  = 60 * 24  # 24 hours

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(data: dict) -> str:
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
```

**First-run setup:**
```bash
python setup_auth.py
# Prompts: "Set your dashboard password:"
# → bcrypt hashes it → saved to .env as ORACLE_PASSWORD_HASH
# → generates random ORACLE_SECRET_KEY
# → password never stored in plaintext anywhere
```

**Additional hardening:**
- 5 failed logins → IP locked 60 seconds (in-memory counter)
- All failed attempts logged to `auth_log.txt` with timestamps
- `slowapi` rate limiter on all `/api/*` routes — 60 req/min max
- `.env` listed in `.gitignore` — credentials never accidentally committed

---

## 📬 Notification Flow

```
12:00 AM IST
└── Gmail: "NBA Oracle: 6 games today. Analysis fires at 6:45 AM IST."
└── Gmail: "Dashboard live at localhost:3000"

6:45 AM IST (T-2hrs before first tip-off)
└── Pipeline runs (~25–35 min for full analysis)

~7:15 AM IST (analysis complete)
├── Telegram: Pick Card #1
├── Telegram: Pick Card #2
├── Telegram: ... (all games)
├── Telegram: 📋 Daily Digest (all picks + signal summary)
└── Dashboard /today updated with live pick cards

[Next day]
└── /result WIN|LOSS via Telegram (per game)
└── If 30 new picks logged → auto-trigger learning cycle
└── Monday: Weekly performance digest → Telegram
```

---

## 🔮 Future Enhancements (Backlog)

- [ ] Spread & Player Props signal layers
- [ ] Stake odds direct scrape (read-only)
- [ ] Kelly Criterion bankroll sizing on dashboard
- [ ] Advanced pattern miner (XGBoost feature importance)
- [ ] LLM self-critique: second pass where Oracle challenges its own pick
- [ ] Season-end model export: save your trained weights as a `.pkl` artifact

---

## ⚠️ Disclaimer

This tool is for **personal research and entertainment purposes only**. NBA Oracle does not guarantee wins. Gambling carries financial risk — always bet responsibly and within your means.

---

*README v0.6 — Living document. Updated iteratively.*





