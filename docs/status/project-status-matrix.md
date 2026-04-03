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
| Scheduler and orchestration | In progress | A first meta-scheduler and runtime job runner now exist through the CLI. |
| LLM analyst layer | Not started | No live analyst-only explanation layer exists yet. |
| Telegram and notifications | In progress | Telegram and Gmail service code, digests, and command-style handling now exist. |
| Dashboard and auth | In progress | Phase 4A has auth bootstrap and protected API routes; dashboard UI is still unbuilt. |
| Learning engine | In progress | Phase 4A learning review execution and persistence now exist. |
| Deployment hardening | In progress | API serve command, scheduler-once path, and explicit runtime bootstrap now exist; production hardening is still ahead. |

## Current Checkpoint

| Question | Answer |
|---|---|
| Where are we now? | Phase 4A is in progress, with the operating core now partially built on top of the completed Phase 1-3 backend. |
| What is production-ready today? | Phase 1 replay/validation, Phase 2 live provider execution and dual persistence, plus early Phase 4A API/scheduler/auth scaffolding. |
| What is the biggest unfinished backend item? | Finishing and hardening the full Phase 4A operating core so it can become the stable backend contract for the dashboard. |
| Can the app run live inputs today? | Yes, through `python main.py build-live-slate --live`, with bundle fallback still available. |
| Can it place real bets end-to-end today? | No. Delivery, persistent storage, scheduler runtime, and final operating flows are still missing. |
| What manual closeout is still required? | Apply [phase4a_schema.sql](../../supabase/phase4a_schema.sql), bootstrap auth, and run live Telegram/Gmail delivery tests. |

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
| Telegram delivery | In progress | [telegram.py](../../nba_oracle/notifications/telegram.py), [formatters.py](../../nba_oracle/notifications/formatters.py), [cli.py](../../nba_oracle/cli.py) | Run live delivery tests and add richer command handling |
| Gmail notifications | In progress | [gmail.py](../../nba_oracle/notifications/gmail.py), [formatters.py](../../nba_oracle/notifications/formatters.py), [cli.py](../../nba_oracle/cli.py) | Run live delivery tests and add richer summary formatting |
| Supabase schema and client wiring | Done | [repository.py](../../nba_oracle/storage/repository.py), [phase2_schema.sql](../../supabase/phase2_schema.sql) | Expand schema in later phases as needed |
| Pick logging and results tracking | Done for Phase 2 scope | [repository.py](../../nba_oracle/storage/repository.py) stores locally and remotely, and live verification has succeeded | Extend result tracking in later phases |
| Dashboard backend and frontend | Not started | Spec only | Build FastAPI + UI |
| Auth and security layer | In progress | [app.py](../../nba_oracle/api/app.py), [dependencies.py](../../nba_oracle/api/dependencies.py), [auth.py](../../nba_oracle/auth.py), [security.py](../../nba_oracle/security.py), [setup_auth.py](../../setup_auth.py) | Add final session hardening and operator auth workflows |
| Learning engine and pattern miner | In progress | [trainer.py](../../nba_oracle/learning/trainer.py), [weights.py](../../nba_oracle/learning/weights.py), [patterns.py](../../nba_oracle/learning/patterns.py), [review.py](../../nba_oracle/learning/review.py) | Accumulate more graded evidence and harden promotion workflow |
| Scheduler and deployment flow | In progress | [meta_scheduler.py](../../nba_oracle/runtime/meta_scheduler.py), [jobs.py](../../nba_oracle/runtime/jobs.py), [state.py](../../nba_oracle/runtime/state.py), [cli.py](../../nba_oracle/cli.py) | Add production cadence hardening and auto-start setup |

## Phase Status

| Phase | Status | Meaning |
|---|---|---|
| Phase 1: Validation Core | Complete | The model can replay frozen slates, gate decisions, and produce audit reports. |
| Phase 1.1: Hardening | Complete | Calibration gate, source audit output, and status reporting are in place. |
| Phase 2: Signal Quality Layer | Complete | Real provider paths, bundle fallback, dual storage code path, live execution mode, and Phase 2.2 schedule fallback are built and verified on a real pregame run. |
| Phase 3: Stability Layer | In progress | Baseline refresh rules, ROI/CLV/calibration drift review, timing-event logs, market-readiness evidence, analyst disagreement logging, model-review bookkeeping, and official outcome grading are live; graded evidence depth still needs to mature. |
| Phase 4: Output / Operating Layer | In progress | Phase 4A operating-core code is underway; 4B and 4C still remain. |

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
| Phase 4A operating core | In progress | Auth bootstrap, protected API routes, scheduler/meta-scheduler, Telegram/Gmail services, Telegram command-style handling, explicit runtime bootstrap, learning review execution, and Phase 4A runtime persistence have landed in code. |
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
- `python main.py run-scheduler-once` now executes due runtime jobs successfully.
- `python main.py serve-api` boots the Phase 4A FastAPI server successfully.
- GitHub and local `main` are in sync.

## Active Backend Assets

| Area | Primary Files |
|---|---|
| Validation core | [predictor.py](../../nba_oracle/predictor.py), [replay.py](../../nba_oracle/replay.py), [reporting.py](../../nba_oracle/reporting.py) |
| Live provider layer | [schedule.py](../../nba_oracle/providers/schedule.py), [odds.py](../../nba_oracle/providers/odds.py), [injuries.py](../../nba_oracle/providers/injuries.py), [stats.py](../../nba_oracle/providers/stats.py), [sentiment.py](../../nba_oracle/providers/sentiment.py) |
| Live run orchestration | [build_live_slate.py](../../nba_oracle/runs/build_live_slate.py), [live_snapshot_builder.py](../../nba_oracle/assembly/live_snapshot_builder.py), [cli.py](../../nba_oracle/cli.py) |
| Stability layer | [baseline.py](../../nba_oracle/stability/baseline.py), [drift.py](../../nba_oracle/stability/drift.py), [timing.py](../../nba_oracle/stability/timing.py), [readiness.py](../../nba_oracle/stability/readiness.py), [reporting.py](../../nba_oracle/stability/reporting.py), [review_stability.py](../../nba_oracle/runs/review_stability.py), [catalog.py](../../nba_oracle/models_registry/catalog.py) |
| Outcome grading | [grade_outcomes.py](../../nba_oracle/runs/grade_outcomes.py), [fetcher.py](../../nba_oracle/outcomes/fetcher.py), [persistence.py](../../nba_oracle/outcomes/persistence.py), [reporting.py](../../nba_oracle/outcomes/reporting.py) |
| Phase 4A operating core | [app.py](../../nba_oracle/api/app.py), [dependencies.py](../../nba_oracle/api/dependencies.py), [auth.py](../../nba_oracle/auth.py), [security.py](../../nba_oracle/security.py), [meta_scheduler.py](../../nba_oracle/runtime/meta_scheduler.py), [jobs.py](../../nba_oracle/runtime/jobs.py), [telegram.py](../../nba_oracle/notifications/telegram.py), [gmail.py](../../nba_oracle/notifications/gmail.py), [trainer.py](../../nba_oracle/learning/trainer.py) |
| Phase 3.1 remote schema | [phase3_schema.sql](../../supabase/phase3_schema.sql) |
| Outcome remote schema | [phase3_2_schema.sql](../../supabase/phase3_2_schema.sql) |
| Phase 4A remote schema | [phase4a_schema.sql](../../supabase/phase4a_schema.sql) |
| Runtime persistence | [repository.py](../../nba_oracle/storage/repository.py) |
| Config and env | [config.py](../../nba_oracle/config.py), [env.py](../../nba_oracle/env.py), [http.py](../../nba_oracle/http.py), [teams.py](../../nba_oracle/teams.py) |
| Manual bootstrap artifacts | [.env.example](../../.env.example), [phase2_schema.sql](../../supabase/phase2_schema.sql) |

## Next Recommended Step

Finish and verify Phase 4A, then continue Phase 4 in order:
- apply [phase3_2_schema.sql](../../supabase/phase3_2_schema.sql)
- apply [phase4a_schema.sql](../../supabase/phase4a_schema.sql)
- run `python main.py grade-outcomes` after games finish
- re-run `python main.py review-stability --force-refresh-baseline`
- verify `python main.py serve-api`
- verify delivery with `python main.py notify-telegram-test` and `python main.py notify-gmail-test`
- then [phase-4b.md](../plans/implementation/phase-4b.md)
- finish with [phase-4c.md](../plans/implementation/phase-4c.md)

Keep the Phase 1 replay flow intact as the acceptance gate for every new provider added.
