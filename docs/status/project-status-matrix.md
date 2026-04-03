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
| Live provider integrations | In progress | Provider adapter scaffold and local live-style bundle flow exist. |
| Supabase persistence | Not started | Storage abstraction exists, but Supabase is not wired yet. |
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
| Schedule ingestion | In progress | [schedule.py](../../nba_oracle/providers/schedule.py), [build_live_slate.py](../../nba_oracle/runs/build_live_slate.py) | Replace bundle-backed schedule flow with real provider calls |
| Odds ingestion | In progress | [odds.py](../../nba_oracle/providers/odds.py), [phase2_sample_bundle.json](../../data/live_sources/phase2_sample_bundle.json) | Wire real odds provider and fallback path |
| Injury/news ingestion | In progress | [injuries.py](../../nba_oracle/providers/injuries.py) | Wire official-first provider stack |
| Stats ingestion | In progress | [stats.py](../../nba_oracle/providers/stats.py) | Replace bundle-backed stats flow with structured live adapter |
| Sentiment ingestion | In progress | [sentiment.py](../../nba_oracle/providers/sentiment.py) | Keep optional and add real Reddit integration first |
| Context builder | In progress | [live_snapshot_builder.py](../../nba_oracle/assembly/live_snapshot_builder.py) | Expand from bundle assembly to true provider merge logic |
| LLM analyst engine | Not started | None | Add analyst-only explanation layer |
| Telegram delivery | Not started | None | Build bot, formatting, and commands |
| Gmail notifications | Not started | None | Build schedule confirmation notifier |
| Supabase schema and client wiring | Not started | Spec only in [master-spec.md](../spec/master-spec.md) | Implement DB layer and migrations |
| Pick logging and results tracking | In progress | [repository.py](../../nba_oracle/storage/repository.py) stores local run artifacts | Add permanent database-backed persistence |
| Dashboard backend and frontend | Not started | Spec only | Build FastAPI + UI |
| Auth and security layer | Not started | Spec only | Build login, hashing, and route protection |
| Learning engine and pattern miner | Not started | Spec only | Build learner and feedback loop |
| Scheduler and deployment flow | Not started | Spec only | Build APScheduler/meta-scheduler runtime |

## Phase Status

| Phase | Status | Meaning |
|---|---|---|
| Phase 1: Validation Core | Complete | The model can replay frozen slates, gate decisions, and produce audit reports. |
| Phase 1.1: Hardening | Complete | Calibration gate, source audit output, and status reporting are in place. |
| Phase 2: Signal Quality Layer | In progress | Adapter scaffold, local storage, and live-style execution path are built. |
| Phase 3: Stability Layer | Not started | Drift control, retraining discipline, and market scope hardening are still ahead. |
| Phase 4: Output / Operating Layer | Not started | Delivery, dashboard, auth, and live operations are untouched. |

## Last Verified State

- Fixture validation passes.
- The Phase 1 test suite passes.
- Replay report generation passes.
- Default replay reports `Phase 1 readiness: true`.
- Phase 2 test suite passes.
- `python main.py build-live-slate` succeeds against the sample live bundle.
- GitHub and local `main` are in sync.

## Next Recommended Step

Continue Phase 2 by replacing bundle-backed provider inputs with real providers and wiring permanent storage:
- real schedule adapter
- real odds adapter
- real injury/news adapter
- real stats adapter
- Reddit-first sentiment adapter
- Supabase-backed storage

Keep the Phase 1 replay flow intact as the acceptance gate for every new provider added.
