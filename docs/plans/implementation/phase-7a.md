# NBA Oracle Phase 7A Implementation Plan

## Purpose
Phase 7A is the forecast-visibility and performance-truth pass.

Phase 7A exists to improve what the operator can see and act on without changing the core model logic first.

It answers two practical questions:
- how do we make the slate view more useful before games start and even for the next day?
- how do we show predicted-vs-actual truth inside the existing dashboard instead of leaving it buried in backend artifacts?

## Goal
Make NBA Oracle more useful for daily operator planning by:
1. surfacing upcoming and next-day pregame opportunities more clearly
2. keeping completed games from dominating the actionable Today workflow
3. showing predicted-vs-actual truth and accuracy inside the existing Performance page

## In Scope
- next-day pregame prediction support
- actionable-slate filtering/ordering for Today
- cleaner separation between future-look planning and already-completed games
- Performance-page predicted-vs-actual result display
- accuracy summaries derived from graded outcomes
- BET / LEAN / SKIP outcome visibility where meaningful
- supporting API and type updates
- doc updates for the new operator workflow

## Out of Scope
- deeper model redesign
- market-prior architecture
- injury-impact redesign
- timing/uncertainty logic changes
- new dashboard page creation

## Problems This Solves

### Problem 1: Today is too tied to the latest stored run
The operator needs:
- upcoming actionable games
- next-day planning visibility

The current latest-run snapshot is too narrow for that workflow.

### Problem 2: Completed games are not the right main focus on Today
Completed games still matter historically, but they should not crowd out the operator's pregame decision surface.

### Problem 3: Prediction truth is not visible enough in the dashboard
The backend already stores:
- selected team
- actual winner
- graded win/loss truth

But the dashboard still does not surface that clearly enough inside Performance.

## Workstreams

### Workstream 1: Forward-Looking Today Logic
- support next-day pregame prediction visibility
- make Today prioritize not-yet-completed games
- distinguish current actionable slate from future-look planning

### Workstream 2: Performance Truth Upgrade
- add predicted side vs actual winner
- add won/lost visibility
- add graded-decision summaries
- add simple accuracy metrics where evidence exists

### Workstream 3: Operator Copy and Truth Rules
- explain what is upcoming vs completed
- explain what accuracy means and does not mean
- avoid pretending thin evidence is stronger than it is

## Recommended Implementation Areas
- `nba_oracle/api/routes/today.py`
- `nba_oracle/api/routes/picks.py`
- `nba_oracle/runs/build_live_slate.py`
- `dashboard/src/pages/Today.tsx`
- `dashboard/src/pages/Performance.tsx`
- `dashboard/src/lib/types.ts`
- `dashboard/src/lib/format.ts`
- `tests/`

## Concrete Deliverables
1. next-day pregame prediction support
2. cleaner actionable Today logic
3. predicted-vs-actual table or section in Performance
4. accuracy summary blocks in Performance
5. supporting API/type updates
6. doc updates for the new operator-facing workflow

## Acceptance Criteria
1. Today is more useful for upcoming and next-day planning than it is today.
2. Completed games no longer dominate the operator's main pregame view.
3. Performance shows predicted-vs-actual truth clearly.
4. Accuracy summaries exist without inventing confidence beyond graded evidence.
5. No new dashboard page is required.

## Exit Rule
Do not call Phase 7A complete until:
1. Today better supports forward-looking operator use
2. Performance clearly shows predicted-vs-actual truth
3. the dashboard remains honest about evidence depth
