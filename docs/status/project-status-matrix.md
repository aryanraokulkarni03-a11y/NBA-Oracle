# NBA Oracle Status Matrix

## Purpose
This file is the quickest way to answer two questions:
- What from the master spec is already built?
- What is still theoretical, partial, or not started?

Use this as the operational checkpoint before starting a new phase.

## Overall Snapshot

| Area | Status | Notes |
|---|---|---|
| Product doctrine and master spec | Done | The long-form theory and architecture are documented. |
| Research and model hardening docs | Done | Research, blockers, and FTW plans are in place. |
| Phase 1 validation core | Done | Replay engine, gates, reporting, and tests are built. |
| Live provider integrations | Not started | No live odds, schedule, injury, stats, or sentiment providers are wired. |
| Supabase persistence | Not started | Storage is specified, not implemented. |
| Scheduler and orchestration | Not started | No meta-scheduler or analysis pipeline runner exists yet. |
| LLM analyst layer | Not started | No live analyst-only explanation layer exists yet. |
| Telegram and notifications | Not started | No bot or Gmail delivery flow is built yet. |
| Dashboard and auth | Not started | No FastAPI dashboard backend or frontend exists yet. |
| Learning engine | Not started | No learner, pattern miner, or retraining loop exists yet. |
| Deployment hardening | Not started | No boot-time service or long-running local runtime exists yet. |

## Build Matrix

| Spec Area | Current Status | Implemented Assets | Remaining Work |
|---|---|---|---|
| Philosophy, research, and operating doctrine | Done | [master-spec.md](../spec/master-spec.md), [prediction-systems-and-public-sentiment-signals.md](../research/prediction-systems-and-public-sentiment-signals.md), [problems-plan.md](../plans/problems-plan.md), [ftw-plan.md](../plans/ftw-plan.md) | Keep updated as phases land |
| Batch 1 money-viability theory | Done | Reflected in docs and Phase 1 implementation | Continue validating with real data later |
| Batch 2 stability theory | Done as spec | Captured in master spec and plan docs | Not implemented yet |
| Frozen snapshot contract | Done | [snapshots.py](../../nba_oracle/snapshots.py), [phase1_sample_slate.json](../../data/fixtures/phase1_sample_slate.json) | Extend to live providers later |
| Point-in-time replay engine | Done | [replay.py](../../nba_oracle/replay.py), [cli.py](../../nba_oracle/cli.py) | Broaden historical coverage and real data ingestion |
| Deterministic predictor | Done | [predictor.py](../../nba_oracle/predictor.py), [market.py](../../nba_oracle/market.py), [models.py](../../nba_oracle/models.py) | Replace or augment with production-grade scoring later |
| Hard no-bet gate | Done | [predictor.py](../../nba_oracle/predictor.py) | Tune with real replay history |
| Source freshness and trust scoring | Done | [source_scoring.py](../../nba_oracle/source_scoring.py), report outputs | Attach to real adapters later |
| Market discipline and price checks | Done | [predictor.py](../../nba_oracle/predictor.py), [reporting.py](../../nba_oracle/reporting.py) | Add real line-shopping sources |
| Calibration assessment | Done | [replay.py](../../nba_oracle/replay.py), [reporting.py](../../nba_oracle/reporting.py) | Upgrade from fixture-driven to historical-data-driven |
| Phase 1 runbook | Done | [phase-1.md](../runbooks/phase-1.md) | Expand as tooling grows |
| Test coverage for validation core | Done | [test_phase1.py](../../tests/test_phase1.py) | Add integration tests once providers exist |
| Schedule ingestion | Not started | None | Build real schedule provider adapter |
| Odds ingestion | Not started | None | Build odds provider adapter(s) |
| Injury/news ingestion | Not started | None | Build official + fallback adapters |
| Stats ingestion | Not started | None | Build structured stats adapter |
| Sentiment ingestion | Not started | None | Build Reddit/X adapters with fallbacks |
| Context builder | Not started | None | Build matchup assembly layer |
| LLM analyst engine | Not started | None | Add analyst-only explanation layer |
| Telegram delivery | Not started | None | Build bot, formatting, and commands |
| Gmail notifications | Not started | None | Build schedule confirmation notifier |
| Supabase schema and client wiring | Not started | Spec only in [master-spec.md](../spec/master-spec.md) | Implement DB layer and migrations |
| Pick logging and results tracking | Not started | Spec only | Implement storage flows |
| Dashboard backend and frontend | Not started | Spec only | Build FastAPI + UI |
| Auth and security layer | Not started | Spec only | Build login, hashing, and route protection |
| Learning engine and pattern miner | Not started | Spec only | Build learner and feedback loop |
| Scheduler and deployment flow | Not started | Spec only | Build APScheduler/meta-scheduler runtime |

## Phase Status

| Phase | Status | Meaning |
|---|---|---|
| Phase 1: Validation Core | Complete | The model can replay frozen slates, gate decisions, and produce audit reports. |
| Phase 1.1: Hardening | Complete | Calibration gate, source audit output, and status reporting are in place. |
| Phase 2: Signal Quality Layer | Not started | Real providers and permanent storage are the next build target. |
| Phase 3: Stability Layer | Not started | Drift control, retraining discipline, and market scope hardening are still ahead. |
| Phase 4: Output / Operating Layer | Not started | Delivery, dashboard, auth, and live operations are untouched. |

## Last Verified State

- Fixture validation passes.
- The Phase 1 test suite passes.
- Replay report generation passes.
- Default replay reports `Phase 1 readiness: true`.
- GitHub and local `main` are in sync.

## Next Recommended Step

Start Phase 2 by building permanent provider adapters and storage behind the existing validation core:
- schedule adapter
- odds adapter
- injury/news adapter
- stats adapter
- storage layer

Keep the Phase 1 replay flow intact as the acceptance gate for every new provider added.

