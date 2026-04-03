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
| Live provider integrations | In progress | Real schedule, odds, injuries, and stats fetch paths exist with bundle fallback and no-slate handling. |
| Supabase persistence | In progress | Dual local-plus-Supabase storage exists in code, pending schema bootstrap. |
| Scheduler and orchestration | Not started | No meta-scheduler or analysis pipeline runner exists yet. |
| LLM analyst layer | Not started | No live analyst-only explanation layer exists yet. |
| Telegram and notifications | Not started | No bot or Gmail delivery flow is built yet. |
| Dashboard and auth | Not started | No FastAPI dashboard backend or frontend exists yet. |
| Learning engine | Not started | No learner, pattern miner, or retraining loop exists yet. |
| Deployment hardening | Not started | No boot-time service or long-running local runtime exists yet. |

## Current Checkpoint

| Question | Answer |
|---|---|
| Where are we now? | Late Phase 2, with real live-provider wiring in place but no permanent database wiring yet. |
| What is production-ready today? | Phase 1 replay/validation and Phase 2 local-plus-live provider execution with graceful degradation. |
| What is the biggest unfinished backend item? | Supabase-backed persistence and stronger provider hardening. |
| Can the app run live inputs today? | Yes, through `python main.py build-live-slate --live`, with bundle fallback still available. |
| Can it place real bets end-to-end today? | No. Delivery, persistent storage, scheduler runtime, and final operating flows are still missing. |
| What manual bootstrap is still required? | Create `.env` from `.env.example` and apply `supabase/phase2_schema.sql`. |

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
| Schedule ingestion | In progress | [schedule.py](../../nba_oracle/providers/schedule.py), [build_live_slate.py](../../nba_oracle/runs/build_live_slate.py) call the NBA live scoreboard endpoint with bundle fallback | Add date-targeted live fetch options and stronger schedule metadata |
| Odds ingestion | In progress | [odds.py](../../nba_oracle/providers/odds.py) calls The Odds API and normalizes market consensus with bundle fallback | Add bookmaker selection tuning and true Stake/line-shop support |
| Injury/news ingestion | In progress | [injuries.py](../../nba_oracle/providers/injuries.py) pulls ESPN injuries and degrades safely | Improve parser robustness and add secondary confirmation source |
| Stats ingestion | In progress | [stats.py](../../nba_oracle/providers/stats.py) calls NBA estimated metrics with bundle fallback | Add richer pregame context and rest/travel features |
| Sentiment ingestion | In progress | [sentiment.py](../../nba_oracle/providers/sentiment.py) is intentionally deferred in live mode | Add real Reddit integration first |
| Context builder | In progress | [live_snapshot_builder.py](../../nba_oracle/assembly/live_snapshot_builder.py) merges real or bundle providers with placeholder fallback for degraded non-market sources | Expand context richness and stricter critical-source rules |
| LLM analyst engine | Not started | None | Add analyst-only explanation layer |
| Telegram delivery | Not started | None | Build bot, formatting, and commands |
| Gmail notifications | Not started | None | Build schedule confirmation notifier |
| Supabase schema and client wiring | In progress | [repository.py](../../nba_oracle/storage/repository.py), [phase2_schema.sql](../../supabase/phase2_schema.sql) | Apply schema and verify remote writes end to end |
| Pick logging and results tracking | In progress | [repository.py](../../nba_oracle/storage/repository.py) stores locally and can write remotely | Verify Supabase inserts with real credentials and schema |
| Dashboard backend and frontend | Not started | Spec only | Build FastAPI + UI |
| Auth and security layer | Not started | Spec only | Build login, hashing, and route protection |
| Learning engine and pattern miner | Not started | Spec only | Build learner and feedback loop |
| Scheduler and deployment flow | Not started | Spec only | Build APScheduler/meta-scheduler runtime |

## Phase Status

| Phase | Status | Meaning |
|---|---|---|
| Phase 1: Validation Core | Complete | The model can replay frozen slates, gate decisions, and produce audit reports. |
| Phase 1.1: Hardening | Complete | Calibration gate, source audit output, and status reporting are in place. |
| Phase 2: Signal Quality Layer | In progress | Real provider paths, bundle fallback, dual storage code path, and live execution mode are built. |
| Phase 3: Stability Layer | Not started | Drift control, retraining discipline, and market scope hardening are still ahead. |
| Phase 4: Output / Operating Layer | Not started | Delivery, dashboard, auth, and live operations are untouched. |

## Recent Changes Summary

| Change Area | Status | What Landed |
|---|---|---|
| Phase 1 validation core | Complete | Replay engine, no-bet logic, calibration reporting, and audit reports are fully working. |
| Phase 1.1 hardening | Complete | Calibration acceptance logic, richer report outputs, and stronger replay readiness checks are in place. |
| Phase 2 scaffold | Complete | Provider contracts, live-slate assembly, local runtime storage, sample bundle, and tests landed. |
| Phase 2 live provider wiring | In progress | Real schedule, odds, stats, and ESPN injury fetch paths now exist behind the provider interfaces. |
| Phase 2 live execution mode | In progress | `--live` mode runs against upstreams and handles no-slate days without cascading failure. |
| Phase 2.1 hardening | In progress | Dual storage wiring, `.env` support, schema bootstrap, and honest market labels landed. |
| Sentiment | Deferred | Still intentionally optional and not live-enabled yet. |
| Supabase | In progress | Credentials can now be read from `.env`, and the storage layer is dual-ready. |

## Last Verified State

- Fixture validation passes.
- The Phase 1 test suite passes.
- Replay report generation passes.
- Default replay reports `Phase 1 readiness: true`.
- Phase 2 test suite passes.
- `python main.py build-live-slate` succeeds against the sample live bundle.
- `python main.py build-live-slate --live` completes and handles a no-slate day without cascading provider failure.
- Phase 2.1 dual-storage code path and reference-line reporting are covered by tests.
- GitHub and local `main` are in sync.

## Active Backend Assets

| Area | Primary Files |
|---|---|
| Validation core | [predictor.py](../../nba_oracle/predictor.py), [replay.py](../../nba_oracle/replay.py), [reporting.py](../../nba_oracle/reporting.py) |
| Live provider layer | [schedule.py](../../nba_oracle/providers/schedule.py), [odds.py](../../nba_oracle/providers/odds.py), [injuries.py](../../nba_oracle/providers/injuries.py), [stats.py](../../nba_oracle/providers/stats.py), [sentiment.py](../../nba_oracle/providers/sentiment.py) |
| Live run orchestration | [build_live_slate.py](../../nba_oracle/runs/build_live_slate.py), [live_snapshot_builder.py](../../nba_oracle/assembly/live_snapshot_builder.py), [cli.py](../../nba_oracle/cli.py) |
| Runtime persistence | [repository.py](../../nba_oracle/storage/repository.py) |
| Config and env | [config.py](../../nba_oracle/config.py), [env.py](../../nba_oracle/env.py), [http.py](../../nba_oracle/http.py), [teams.py](../../nba_oracle/teams.py) |
| Manual bootstrap artifacts | [.env.example](../../.env.example), [phase2_schema.sql](../../supabase/phase2_schema.sql) |

## Next Recommended Step

Continue Phase 2 by hardening the new live providers and wiring permanent storage:
- strengthen schedule targeting beyond the current-day scoreboard
- improve ESPN parser resilience and add a secondary injury confirmation path
- add bookmaker selection strategy and a true Stake-specific price source if one becomes available
- add Reddit-first live sentiment when ready
- apply the Supabase schema and validate dual storage in a real run

Keep the Phase 1 replay flow intact as the acceptance gate for every new provider added.
