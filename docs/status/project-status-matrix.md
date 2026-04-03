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
| Live provider integrations | Done | Real schedule, odds, injuries, and stats fetch paths exist with bundle fallback and live verification. |
| Supabase persistence | Done | Dual local-plus-Supabase storage is active and verified in live runs. |
| Scheduler and orchestration | Not started | No meta-scheduler or analysis pipeline runner exists yet. |
| LLM analyst layer | Not started | No live analyst-only explanation layer exists yet. |
| Telegram and notifications | Not started | No bot or Gmail delivery flow is built yet. |
| Dashboard and auth | Planned | Phase 4B now defines the dashboard/auth surface, but no code exists yet. |
| Learning engine | Planned | Phase 4A now defines the first full learning-loop execution path, but no code exists yet. |
| Deployment hardening | Planned | Phase 4A and 4C now define the runtime/deployment story, but no code exists yet. |

## Current Checkpoint

| Question | Answer |
|---|---|
| Where are we now? | Phase 3.1 code is in place, and the new closeout loop is accumulating official graded outcomes into stored live runs so drift can mature beyond `insufficient_outcomes`. |
| What is production-ready today? | Phase 1 replay/validation plus Phase 2 live provider execution, dual persistence, and live prediction assembly with graceful degradation. |
| What is the biggest unfinished backend item? | Phase 4A operating core: API, auth, scheduler/runtime, delivery channels, and learning execution. |
| Can the app run live inputs today? | Yes, through `python main.py build-live-slate --live`, with bundle fallback still available. |
| Can it place real bets end-to-end today? | No. Delivery, persistent storage, scheduler runtime, and final operating flows are still missing. |
| What manual closeout is still required? | Apply [phase3_2_schema.sql](../../supabase/phase3_2_schema.sql) in Supabase to persist outcome-grade history remotely, then keep running `grade-outcomes` after games finish. |

## Build Matrix

| Spec Area | Current Status | Implemented Assets | Remaining Work |
|---|---|---|---|
| Philosophy, research, and operating doctrine | Done | [master-spec.md](../spec/master-spec.md), [prediction-systems-and-public-sentiment-signals.md](../research/prediction-systems-and-public-sentiment-signals.md), [problems-plan.md](../plans/problems-plan.md), [ftw-plan.md](../plans/ftw-plan.md) | Keep updated as phases land |
| Batch 1 money-viability theory | Done | Reflected in docs and Phase 1 implementation | Continue validating with real data later |
| Batch 2 stability theory | In progress | Captured in master spec and now partially executed through the Phase 3 stability review flow | Continue implementing drift follow-through and retraining review workflows |
| Frozen snapshot contract | Done | [snapshots.py](../../nba_oracle/snapshots.py), [phase1_sample_slate.json](../../data/fixtures/phase1_sample_slate.json) | Extend to live providers later |
| Point-in-time replay engine | Done | [replay.py](../../nba_oracle/replay.py), [cli.py](../../nba_oracle/cli.py) | Broaden historical coverage and real data ingestion |
| Deterministic predictor | Done | [predictor.py](../../nba_oracle/predictor.py), [market.py](../../nba_oracle/market.py), [models.py](../../nba_oracle/models.py) | Replace or augment with production-grade scoring later |
| Hard no-bet gate | Done | [predictor.py](../../nba_oracle/predictor.py) | Tune with real replay history |
| Source freshness and trust scoring | Done | [source_scoring.py](../../nba_oracle/source_scoring.py), report outputs | Attach to real adapters later |
| Market discipline and price checks | Done | [predictor.py](../../nba_oracle/predictor.py), [reporting.py](../../nba_oracle/reporting.py) | Add real line-shopping sources |
| Calibration assessment | Done | [replay.py](../../nba_oracle/replay.py), [reporting.py](../../nba_oracle/reporting.py) | Upgrade from fixture-driven to historical-data-driven |
| Phase 1 runbook | Done | [phase-1.md](../runbooks/phase-1.md) | Expand as tooling grows |
| Test coverage for validation core | Done | [test_phase1.py](../../tests/test_phase1.py) | Add integration tests once providers exist |
| Schedule ingestion | Done | [schedule.py](../../nba_oracle/providers/schedule.py), [build_live_slate.py](../../nba_oracle/runs/build_live_slate.py) use the NBA live scoreboard and fall back to the odds-derived upcoming slate when the official feed is stale | Add stronger date-targeted schedule metadata later |
| Odds ingestion | Done | [odds.py](../../nba_oracle/providers/odds.py) calls The Odds API and normalizes market consensus with bundle fallback | Improve line-shopping depth later |
| Injury/news ingestion | Done | [injuries.py](../../nba_oracle/providers/injuries.py) pulls ESPN injuries and degrades safely | Improve parser robustness later |
| Stats ingestion | Done | [stats.py](../../nba_oracle/providers/stats.py) calls NBA estimated metrics with bundle fallback | Add richer pregame context later |
| Sentiment ingestion | Done for Phase 2 scope | [sentiment.py](../../nba_oracle/providers/sentiment.py) remains intentionally optional and safely deferred in live mode | Add real Reddit integration in a later phase |
| Context builder | Done | [live_snapshot_builder.py](../../nba_oracle/assembly/live_snapshot_builder.py) merges real or bundle providers with placeholder fallback for degraded non-market sources | Expand context richness later |
| Stability review layer | In progress | [baseline.py](../../nba_oracle/stability/baseline.py), [drift.py](../../nba_oracle/stability/drift.py), [timing.py](../../nba_oracle/stability/timing.py), [readiness.py](../../nba_oracle/stability/readiness.py), [reporting.py](../../nba_oracle/stability/reporting.py), [review_stability.py](../../nba_oracle/runs/review_stability.py), [catalog.py](../../nba_oracle/models_registry/catalog.py), [persistence.py](../../nba_oracle/stability/persistence.py) | Continue accumulating graded evidence through the new outcome-grading workflow |
| Outcome accumulation | Done for local workflow | [grade_outcomes.py](../../nba_oracle/runs/grade_outcomes.py), [fetcher.py](../../nba_oracle/outcomes/fetcher.py), [persistence.py](../../nba_oracle/outcomes/persistence.py), [reporting.py](../../nba_oracle/outcomes/reporting.py) | Apply remote outcome schema and keep running it after games finish |
| LLM analyst engine | Not started | None | Add analyst-only explanation layer |
| Telegram delivery | Not started | None | Build bot, formatting, and commands |
| Gmail notifications | Not started | None | Build schedule confirmation notifier |
| Supabase schema and client wiring | Done | [repository.py](../../nba_oracle/storage/repository.py), [phase2_schema.sql](../../supabase/phase2_schema.sql) | Expand schema in later phases as needed |
| Pick logging and results tracking | Done for Phase 2 scope | [repository.py](../../nba_oracle/storage/repository.py) stores locally and remotely, and live verification has succeeded | Extend result tracking in later phases |
| Dashboard backend and frontend | Not started | Spec only | Build FastAPI + UI |
| Auth and security layer | Not started | Spec only | Build login, hashing, and route protection |
| Learning engine and pattern miner | Not started | Spec only | Build learner and feedback loop |
| Scheduler and deployment flow | Not started | Spec only | Build APScheduler/meta-scheduler runtime |

## Phase Status

| Phase | Status | Meaning |
|---|---|---|
| Phase 1: Validation Core | Complete | The model can replay frozen slates, gate decisions, and produce audit reports. |
| Phase 1.1: Hardening | Complete | Calibration gate, source audit output, and status reporting are in place. |
| Phase 2: Signal Quality Layer | Complete | Real provider paths, bundle fallback, dual storage code path, live execution mode, and Phase 2.2 schedule fallback are built and verified on a real pregame run. |
| Phase 3: Stability Layer | In progress | Baseline refresh rules, ROI/CLV/calibration drift review, timing-event logs, market-readiness evidence, analyst disagreement logging, model-review bookkeeping, and official outcome grading are live; graded evidence depth still needs to mature. |
| Phase 4: Output / Operating Layer | Planned | The final product pass is now split into 4A operating core, 4B dashboard, and 4C integration hardening. |

## Recent Changes Summary

| Change Area | Status | What Landed |
|---|---|---|
| Phase 1 validation core | Complete | Replay engine, no-bet logic, calibration reporting, and audit reports are fully working. |
| Phase 1.1 hardening | Complete | Calibration acceptance logic, richer report outputs, and stronger replay readiness checks are in place. |
| Phase 2 scaffold | Complete | Provider contracts, live-slate assembly, local runtime storage, sample bundle, and tests landed. |
| Phase 2 live provider wiring | Complete | Real schedule, odds, stats, and ESPN injury fetch paths now exist behind the provider interfaces. |
| Phase 2 live execution mode | Complete | `--live` mode now runs against upstreams, handles no-slate days, and has produced a real non-zero pregame slate. |
| Phase 2.1 hardening | Complete | Dual storage wiring, `.env` support, schema bootstrap, and honest market labels landed. |
| Phase 2.2 closeout path | Complete | Official schedule now falls back to odds-derived upcoming games when the live scoreboard is stale, and the fallback has produced real predictions. |
| Phase 3 stability review | In progress | `review-stability` now creates or refreshes a saved baseline, reviews recent live runs, emits markdown/JSON health reports, writes a model-review registry, and can record analyst disagreements. |
| Phase 3.1 hardening pass | Complete in code | ROI/CLV/calibration drift, baseline refresh discipline, timing-event logging, evidence-backed market locks, analyst disagreement logging, and review bookkeeping landed. |
| Outcome grading workflow | Complete in code | `grade-outcomes` now fetches official NBA finals, backfills `actual_winner`, writes grading reports, and stores run-level outcome artifacts. |
| Phase 4 restructuring | Complete | The final product pass is now split into 4A, 4B, and 4C so backend/runtime, frontend, and integration can be executed in the right order. |
| Sentiment | Deferred | Still intentionally optional and not live-enabled yet. |
| Supabase | Complete for current scope | Credentials are loaded from `.env`, dual persistence is active, and live runs are storing successfully. |

## Last Verified State

- Fixture validation passes.
- The Phase 1 test suite passes.
- Replay report generation passes.
- Default replay reports `Phase 1 readiness: true`.
- Phase 2 test suite passes.
- `python main.py build-live-slate` succeeds against the sample live bundle.
- `python main.py build-live-slate --live` completes and handles a no-slate day without cascading provider failure.
- Phase 2.1 dual-storage code path and reference-line reporting are covered by tests.
- Phase 2.2 schedule fallback is covered by tests.
- `python main.py build-live-slate --live` has now produced `Snapshot count: 9`, `Prediction count: 9`, and no `supabase_error:...` markers.
- `python main.py review-stability --force-refresh-baseline` now succeeds and writes baseline-backed Phase 3.1 health reports.
- `python main.py grade-outcomes` now succeeds and writes Phase 3 outcome-grading reports.
- GitHub and local `main` are in sync.

## Active Backend Assets

| Area | Primary Files |
|---|---|
| Validation core | [predictor.py](../../nba_oracle/predictor.py), [replay.py](../../nba_oracle/replay.py), [reporting.py](../../nba_oracle/reporting.py) |
| Live provider layer | [schedule.py](../../nba_oracle/providers/schedule.py), [odds.py](../../nba_oracle/providers/odds.py), [injuries.py](../../nba_oracle/providers/injuries.py), [stats.py](../../nba_oracle/providers/stats.py), [sentiment.py](../../nba_oracle/providers/sentiment.py) |
| Live run orchestration | [build_live_slate.py](../../nba_oracle/runs/build_live_slate.py), [live_snapshot_builder.py](../../nba_oracle/assembly/live_snapshot_builder.py), [cli.py](../../nba_oracle/cli.py) |
| Stability layer | [baseline.py](../../nba_oracle/stability/baseline.py), [drift.py](../../nba_oracle/stability/drift.py), [timing.py](../../nba_oracle/stability/timing.py), [readiness.py](../../nba_oracle/stability/readiness.py), [reporting.py](../../nba_oracle/stability/reporting.py), [review_stability.py](../../nba_oracle/runs/review_stability.py), [catalog.py](../../nba_oracle/models_registry/catalog.py) |
| Outcome grading | [grade_outcomes.py](../../nba_oracle/runs/grade_outcomes.py), [fetcher.py](../../nba_oracle/outcomes/fetcher.py), [persistence.py](../../nba_oracle/outcomes/persistence.py), [reporting.py](../../nba_oracle/outcomes/reporting.py) |
| Phase 3.1 remote schema | [phase3_schema.sql](../../supabase/phase3_schema.sql) |
| Outcome remote schema | [phase3_2_schema.sql](../../supabase/phase3_2_schema.sql) |
| Runtime persistence | [repository.py](../../nba_oracle/storage/repository.py) |
| Config and env | [config.py](../../nba_oracle/config.py), [env.py](../../nba_oracle/env.py), [http.py](../../nba_oracle/http.py), [teams.py](../../nba_oracle/teams.py) |
| Manual bootstrap artifacts | [.env.example](../../.env.example), [phase2_schema.sql](../../supabase/phase2_schema.sql) |

## Next Recommended Step

Close the remaining Phase 3 evidence loop, then execute Phase 4 in order:
- apply [phase3_2_schema.sql](../../supabase/phase3_2_schema.sql)
- run `python main.py grade-outcomes` after games finish
- re-run `python main.py review-stability --force-refresh-baseline`
- start with [phase-4a.md](../plans/implementation/phase-4a.md)
- then [phase-4b.md](../plans/implementation/phase-4b.md)
- finish with [phase-4c.md](../plans/implementation/phase-4c.md)

Keep the Phase 1 replay flow intact as the acceptance gate for every new provider added.
