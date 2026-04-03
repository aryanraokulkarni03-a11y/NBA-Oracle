# NBA Oracle Phase 5 Implementation Plan

## Purpose
Phase 5 is the interpretation, clarity, and operator-confidence pass.

Phases 1 through 4 built the model, data flow, storage, operating layer, dashboard, and hosted deployment path.

That means the product now works.

But working is not the same as being easy to understand.

Phase 5 exists to solve the last serious product gap:

> Can an operator look at the dashboard, understand what the system is saying, understand why it is saying it, and place or skip a manual bet without needing internal repo knowledge?

If the answer is no, the product is still too technical for normal use.

## Source of Truth
This plan is derived from:
- [master-spec.md](../../spec/master-spec.md)
- [project-status-matrix.md](../../status/project-status-matrix.md)
- [changes-matrix.md](../../status/changes-matrix.md)
- [phase-4b.md](./phase-4b.md)
- [phase-4c.md](./phase-4c.md)

It is grounded in the current shipped surfaces:
- [Dashboard.tsx](../../../dashboard/src/pages/Dashboard.tsx)
- [Today.tsx](../../../dashboard/src/pages/Today.tsx)
- [Performance.tsx](../../../dashboard/src/pages/Performance.tsx)
- [Providers.tsx](../../../dashboard/src/pages/Providers.tsx)
- [Operations.tsx](../../../dashboard/src/pages/Operations.tsx)
- [PredictionCard.tsx](../../../dashboard/src/components/PredictionCard.tsx)
- [ProviderList.tsx](../../../dashboard/src/components/ProviderList.tsx)
- [format.ts](../../../dashboard/src/lib/format.ts)
- [predictor.py](../../../nba_oracle/predictor.py)
- [reporting.py](../../../nba_oracle/reporting.py)

## Phase 5 Goal
Turn NBA Oracle from a technically correct operator dashboard into an actually understandable product.

The operator should be able to answer these questions directly from the UI:

1. What is the system recommending?
2. Why is it recommending that?
3. Why is a likely winner still a `SKIP` sometimes?
4. What do `EV`, `Edge`, `Reference`, `Best`, `Model`, and `Market time` mean?
5. What does `degraded` mean?
6. What do `insufficient_data`, `fallback`, and raw reason/status labels actually imply?
7. How should a human use the dashboard to decide whether to place a manual bet?

## What Phase 5 Must Respect

1. The product must remain honest.
2. The UI must not invent certainty where the backend is uncertain.
3. Machine-readable values can remain in the backend, but they must not leak into the primary user-facing copy unchanged.
4. A guide page must explain the dashboard without dumbing down the system.
5. Phase 5 should improve understanding, not weaken the trust discipline built in earlier phases.

## In Scope
- human-readable translation of machine reason codes
- human-readable translation of provider/source labels
- metric explanations for EV, Edge, Reference, Best, Model, and market timing
- bookmaker display-name normalization
- dashboard glossary and explanation layer
- operator guide/help page inside the dashboard
- tooltip, helper-copy, or inline explanation design for important metrics and statuses
- product-copy cleanup across dashboard pages
- clarification of degraded/fallback/insufficient-data states

## Out of Scope
- new betting markets
- new providers
- autonomous bet placement
- replacing the prediction model
- redesigning the entire dashboard shell from scratch

## The Problems Phase 5 Is Solving

### Problem 1: Raw internal labels are leaking into the UI
Examples include:
- `edge_too_small`
- `negative_expected_value`
- raw bookmaker ids like `betmgm`
- low-context provider identifiers like `nba_schedule_with_odds_fallback`

These are useful for backend truth and debugging, but too raw for final operator-facing product language.

### Problem 2: Critical betting concepts are visible but not taught
Examples:
- `EV`
- `Edge`
- `Reference`
- `Best`
- `Model`
- `Market time`

These metrics are meaningful only if the operator knows how to interpret them.

### Problem 3: The app explains state, but not usage
The operator can see:
- today’s slate
- provider health
- stability
- learning
- operations

But there is still no first-class in-product explanation of:
- how to read the dashboard
- how to manually use it for betting decisions
- how to interpret `BET`, `LEAN`, `SKIP`
- when to trust the system less because of degraded inputs

### Problem 4: “Encoding issues” are really product-language issues
Most of what currently feels like “encoding” is better described as:
- underspecified text formatting
- snake_case labels
- internal identifiers
- raw values without explanation

Phase 5 should fix that at the UI language layer.

## Workstreams

### Workstream 1: Human-Readable Translation Layer
Create a shared frontend formatting/translation layer for:
- prediction reason codes
- provider names
- bookmaker names
- status identifiers
- fallback and degradation messages

Deliverables:
- centralized display mapping utility
- clean operator-facing copy for today cards and provider panels
- no raw snake_case reasons in primary surfaces unless intentionally shown in an advanced/debug context

### Workstream 2: Metric Interpretation Layer
Add clear explanations for:
- `EV`
- `Edge`
- `Reference`
- `Best`
- `Model`
- `Market time`
- `BET`
- `LEAN`
- `SKIP`

Possible UI forms:
- inline helper text
- compact glossary cards
- hover tooltips
- “what this means” sections on detail cards

Deliverables:
- shared metric glossary content
- cleaner labels and helper text
- high-probability-but-bad-price explanation path

### Workstream 3: Guide Page
Add a first-class dashboard page for operator education.

Recommended route:
- `/guide`

The guide page should explain:
- what NBA Oracle is and is not
- how to read the Overview page
- how to read Today predictions
- how to understand Providers
- how to interpret Stability and Learning
- what degraded sources mean
- how to manually decide whether to place a bet
- why a likely winner can still be a `SKIP`
- what the operator actions do

Deliverables:
- `Guide` page in the top nav
- sectioned product documentation inside the app
- clear examples using the current metric language

### Workstream 4: Product-Copy Cleanup
Sweep the dashboard for:
- machine-ish headers
- repeated technical phrasing
- low-context labels
- inconsistent casing and naming
- overloaded phrases like “reference” without explanation

Deliverables:
- product-clean copy pass across all pages
- clearer alert banners
- cleaner empty states and insufficient-data states

### Workstream 5: Visual Comprehension Polish
Use layout and hierarchy to improve understanding:
- better grouping of reasons vs prices vs probabilities
- better distinction between recommendation and caution
- more obvious metric hierarchy
- more obvious degradation/warning hierarchy

This is not a full redesign.
It is a comprehension-first polish pass.

Deliverables:
- tighter informational grouping
- improved card substructure
- clearer explanatory rhythm in the Today view and Provider view

## Recommended Implementation Areas

- `dashboard/src/lib/format.ts`
- `dashboard/src/lib/`
- `dashboard/src/components/PredictionCard.tsx`
- `dashboard/src/components/ProviderList.tsx`
- `dashboard/src/components/`
- `dashboard/src/pages/Today.tsx`
- `dashboard/src/pages/Providers.tsx`
- `dashboard/src/pages/Dashboard.tsx`
- `dashboard/src/pages/`
- `dashboard/src/styles/index.css`

## Concrete Deliverables

1. Shared label/meaning translation utilities
2. Human-readable reason rendering for prediction cards
3. Human-readable provider and bookmaker display names
4. Metric explanation system for EV/Edge/Reference/Best/Model/Market time
5. New in-dashboard Guide page
6. Nav update to include Guide
7. Product-copy cleanup across overview, today, providers, and operations
8. Final explanation-focused browser verification pass

## Acceptance Criteria
Phase 5 is acceptable only if:

1. A normal operator can understand the key dashboard terms without repo knowledge.
2. Raw reason codes no longer dominate the main prediction surfaces.
3. `EV`, `Edge`, `Reference`, `Best`, `Model`, and `Market time` are explained in-product.
4. `BET`, `LEAN`, and `SKIP` are explained clearly and truthfully.
5. `degraded`, `fallback`, and `insufficient_data` are understandable at a glance.
6. The guide page is useful enough that a new operator could learn the dashboard from it.
7. The UI remains honest and does not flatten cautionary states into marketing language.

## Final Exit Rule
Do not call Phase 5 complete until:

1. The dashboard no longer feels like it is leaking backend internals.
2. The operator can interpret betting-value metrics correctly from the UI alone.
3. The guide page explains how to use the product for manual betting decisions.
4. The product reads like a finished operator tool, not an internal engineering surface.
