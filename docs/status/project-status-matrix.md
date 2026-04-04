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
| Scheduler and orchestration | Done | Meta-scheduler, runtime job runner, startup sanity, and hosted/local operating checks now exist and have been verified through the dashboard and CLI. |
| LLM analyst layer | Not started | No live analyst-only explanation layer exists yet. |
| Telegram and notifications | Done | Telegram and Gmail service code, digests, command-style handling, test sends, and notification history surfacing are wired and verified. |
| Dashboard and auth | Done | Auth bootstrap, protected API routes, the React/Vite dashboard, and hosted Vercel connectivity are all verified. |
| Learning engine | Done for current scope | Learning review execution and persistence exist and behave honestly when evidence is insufficient. |
| Deployment hardening | Done for chosen deployment shape | Startup sanity, recovery docs, Vercel frontend hosting, Cloudflare Tunnel backend exposure, and Supabase persistence are all verified. |

## Current Checkpoint

| Question | Answer |
|---|---|
| Where are we now? | The full project is now operating end to end with a recommended free daily workflow of local dashboard + local backend + recurring scheduler, while Vercel + Cloudflare Tunnel + Supabase remains the optional hosted-access path. |
| What is production-ready today? | Phase 1 replay/validation, Phase 2 live provider execution and dual persistence, Phase 3 review/outcome workflows, and the full Phase 4 operating/dashboard stack. |
| What is the biggest unfinished product item? | The main remaining product thread is now Phase 7B: the deeper intelligence-upgrade pass after the completed 7A forecast-visibility work. |
| Can the app run live inputs today? | Yes, through `python main.py build-live-slate --live`, with bundle fallback still available. |
| Can it place real bets end-to-end today? | No. It remains a selective analysis and operator workflow system, not an auto-betting system. |
| What manual closeout is still required? | No Phase 6 setup gap remains for the current scope. Daily operation is now local-dashboard-first, with hosted Vercel access kept as an optional quick-tunnel path. |

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
| Stability review layer | Done for current scope | [baseline.py](../../nba_oracle/stability/baseline.py), [drift.py](../../nba_oracle/stability/drift.py), [timing.py](../../nba_oracle/stability/timing.py), [readiness.py](../../nba_oracle/stability/readiness.py), [reporting.py](../../nba_oracle/stability/reporting.py), [review_stability.py](../../nba_oracle/runs/review_stability.py), [catalog.py](../../nba_oracle/models_registry/catalog.py), [persistence.py](../../nba_oracle/stability/persistence.py) | Continue accumulating graded evidence through the outcome-grading workflow |
| Outcome accumulation | Done for local workflow | [grade_outcomes.py](../../nba_oracle/runs/grade_outcomes.py), [fetcher.py](../../nba_oracle/outcomes/fetcher.py), [persistence.py](../../nba_oracle/outcomes/persistence.py), [reporting.py](../../nba_oracle/outcomes/reporting.py) | Apply remote outcome schema and keep running it after games finish |
| LLM analyst engine | Not started | None | Add analyst-only explanation layer |
| Telegram delivery | Done for current scope | [telegram.py](../../nba_oracle/notifications/telegram.py), [formatters.py](../../nba_oracle/notifications/formatters.py), [cli.py](../../nba_oracle/cli.py) | Add richer command depth later only if the operator workflow grows |
| Gmail notifications | Done for current scope | [gmail.py](../../nba_oracle/notifications/gmail.py), [formatters.py](../../nba_oracle/notifications/formatters.py), [cli.py](../../nba_oracle/cli.py) | Add richer summary formatting later only if the operator workflow grows |
| Supabase schema and client wiring | Done | [repository.py](../../nba_oracle/storage/repository.py), [phase2_schema.sql](../../supabase/phase2_schema.sql) | Expand schema in later phases as needed |
| Pick logging and results tracking | Done for Phase 2 scope | [repository.py](../../nba_oracle/storage/repository.py) stores locally and remotely, and live verification has succeeded | Extend result tracking in later phases |
| Dashboard backend and frontend | Done | Phase 4A backend APIs, auth, and operator routes are real, the React/Vite dashboard is hosted on Vercel, and 4C hosted/API refresh support is verified | Keep UI polish synced with backend truth later |
| Auth and security layer | Done for current scope | [app.py](../../nba_oracle/api/app.py), [dependencies.py](../../nba_oracle/api/dependencies.py), [auth.py](../../nba_oracle/auth.py), [security.py](../../nba_oracle/security.py), [setup_auth.py](../../setup_auth.py) include hosted CORS support and verified login flow | Add richer session management later only if needed |
| Learning engine and pattern miner | Done for current scope | [trainer.py](../../nba_oracle/learning/trainer.py), [weights.py](../../nba_oracle/learning/weights.py), [patterns.py](../../nba_oracle/learning/patterns.py), [review.py](../../nba_oracle/learning/review.py) | Accumulate more graded evidence and harden promotion workflow |
| Scheduler and deployment flow | Done for current scope | [meta_scheduler.py](../../nba_oracle/runtime/meta_scheduler.py), [jobs.py](../../nba_oracle/runtime/jobs.py), [state.py](../../nba_oracle/runtime/state.py), [cli.py](../../nba_oracle/cli.py), [startup.py](../../nba_oracle/runtime/startup.py), [vercel.json](../../dashboard/vercel.json) | Keep the local backend and local dashboard stable for free daily use; use the tunnel only when hosted access is specifically needed |

## Phase Status

| Phase | Status | Meaning |
|---|---|---|
| Phase 1: Validation Core | Complete | The model can replay frozen slates, gate decisions, and produce audit reports. |
| Phase 1.1: Hardening | Complete | Calibration gate, source audit output, and status reporting are in place. |
| Phase 2: Signal Quality Layer | Complete | Real provider paths, bundle fallback, dual storage code path, live execution mode, and Phase 2.2 schedule fallback are built and verified on a real pregame run. |
| Phase 3: Stability Layer | Complete for current scope | Baseline refresh rules, ROI/CLV/calibration drift review, timing-event logs, market-readiness evidence, analyst disagreement logging, model-review bookkeeping, and official outcome grading are live; graded evidence depth still needs to mature. |
| Phase 4: Output / Operating Layer | Complete for chosen deployment shape | Phase 4A operating core, Phase 4B dashboard, and Phase 4C hosted/deployment closeout are now wired and verified against Vercel + Cloudflare Tunnel + Supabase. |
| Phase 5: Interpretation and Guidance | Complete for current scope | Human-readable reason translation, metric explanations, provider/bookmaker naming cleanup, the in-product guide page, page-level operator guidance, and advanced-only technical details are now in the dashboard. |
| Phase 6: Operations Automation | Complete for current scope | Hosted launcher scripts, recurring scheduler helper scripts, operator workflow runbook, tunnel/runtime recovery guidance, evidence-loop hardening, and the verified Windows scheduler task are now in place; local dashboard mode is the recommended free daily workflow. |
| Phase 7A: Forecast Visibility | Complete for current scope | Today now prioritizes actionable upcoming games, exposes a next-up lookahead section, and Performance now surfaces predicted-vs-actual truth with graded accuracy summaries. |
| Phase 7B: Intelligence Upgrade | Planned | Market-as-prior modeling, richer team-strength and injury intelligence, timing-aware pregame judgment, uncertainty-aware gating, and segmented moneyline evaluation are the deeper model-quality pass after 7A. |

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
| Phase 4A operating core | Complete | Auth bootstrap, protected API routes, scheduler/meta-scheduler, Telegram/Gmail services, Telegram command-style handling, explicit runtime bootstrap, learning review execution, and Phase 4A runtime persistence are landed and verified. |
| Phase 4B final plan | Complete | The dashboard pass is now rewritten against the actual 4A route contract, page-by-page frontend truth rules, and explicit operator flows. |
| Phase 4B dashboard execution | Complete | The dashboard folder, app shell, authenticated pages, shared UI system, operator action panels, and hosted Vercel deployment are working. |
| Phase 4C final one-shot plan | Complete | The last remaining pass is now rewritten around the real unfinished seams: startup, scheduler truth, dashboard/API refresh consistency, delivery verification, recovery, hosted deployment, and end-to-end closeout. |
| Phase 4C execution start | Complete | Startup sanity, hosted API/CORS support, notification history in health, deployment artifacts, recovery runbooks, dashboard-wide runtime refresh, and hosted verification are landed. |
| Phase 5 planning | Complete | The next pass now targets human-readable reason translation, metric explanations, provider/bookmaker naming cleanup, and a first-class guide page. |
| Phase 5 execution closeout | Complete | Shared translation helpers, inline metric explanations, provider/bookmaker naming cleanup, the Guide route/page, Today and Providers interpretation panels, and advanced-only raw card details are now in code and building successfully. |
| Phase 6 execution closeout | Complete | Hosted launcher scripts, recurring scheduler helper scripts, startup sanity checks, verified Windows task scheduling, and local-dashboard-first operator guidance are now landed. |
| Phase 7 split planning | Complete | Phase 7 is now split into 7A forecast visibility and 7B intelligence upgrade so operator-surface improvements can land before deeper model changes. |
| Phase 7A forecast visibility execution | Complete | Today now shows actionable upcoming games plus a next-up lookahead, and Performance now includes predicted-vs-actual truth with overall, BET, and LEAN accuracy summaries. |
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
- Outcome grading now retries/falls back safely when the primary official NBA endpoint is slow, and synthetic runtime runs no longer inflate live `pending_unfinished` summaries.
- `python main.py startup-sanity` now reports on the Phase 6 hosted launcher, scheduler runner script, and scheduler task registration state.
- `python main.py run-scheduler-once` now executes due runtime jobs successfully.
- The free daily local dashboard workflow on `http://localhost:3000` is now the recommended operating path.
- `python main.py serve-api` boots the Phase 4A FastAPI server successfully.
- `npm.cmd run build` now compiles the Phase 4B dashboard successfully.
- The final Phase 5 polish build now compiles successfully with clearer Today, Providers, and review-surface guidance.
- The Phase 7A forecast-visibility pass now compiles successfully with actionable Today sections and predicted-versus-actual truth inside Performance.
- Phase 4C now closes against `Vercel + Cloudflare Tunnel + Supabase` as the deployment target.
- `python main.py startup-sanity` now succeeds and reports hosted/local readiness.
- Hosted Vercel frontend, public Cloudflare health endpoint, and dashboard operator actions have now been manually verified.
- Supabase RLS has been enabled on all Oracle public tables, and schema files now enforce that by default.
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
| Phase 4B dashboard | [App.tsx](../../dashboard/src/App.tsx), [AppShell.tsx](../../dashboard/src/components/AppShell.tsx), [Dashboard.tsx](../../dashboard/src/pages/Dashboard.tsx), [Today.tsx](../../dashboard/src/pages/Today.tsx), [Operations.tsx](../../dashboard/src/pages/Operations.tsx), [index.css](../../dashboard/src/styles/index.css) |
| Phase 4C startup and deployment | [startup.py](../../nba_oracle/runtime/startup.py), [deployment.md](../runbooks/deployment.md), [recovery.md](../runbooks/recovery.md), [phase-4.md](../runbooks/phase-4.md), [vercel.json](../../dashboard/vercel.json) |
| Phase 6 operator tooling | [start_hosted_stack.bat](../../start_hosted_stack.bat), [start_nba_oracle_backend.ps1](../../scripts/start_nba_oracle_backend.ps1), [start_nba_oracle_tunnel.ps1](../../scripts/start_nba_oracle_tunnel.ps1), [run_nba_oracle_scheduler.ps1](../../scripts/run_nba_oracle_scheduler.ps1), [register_nba_oracle_scheduler.ps1](../../scripts/register_nba_oracle_scheduler.ps1), [phase-6.md](../runbooks/phase-6.md) |
| Phase 7A forecast visibility | [today.py](../../nba_oracle/api/routes/today.py), [picks.py](../../nba_oracle/api/routes/picks.py), [prediction_views.py](../../nba_oracle/runtime/prediction_views.py), [Today.tsx](../../dashboard/src/pages/Today.tsx), [Performance.tsx](../../dashboard/src/pages/Performance.tsx) |
| Phase 3.1 remote schema | [phase3_schema.sql](../../supabase/phase3_schema.sql) |
| Outcome remote schema | [phase3_2_schema.sql](../../supabase/phase3_2_schema.sql) |
| Phase 4A remote schema | [phase4a_schema.sql](../../supabase/phase4a_schema.sql) |
| Runtime persistence | [repository.py](../../nba_oracle/storage/repository.py) |
| Config and env | [config.py](../../nba_oracle/config.py), [env.py](../../nba_oracle/env.py), [http.py](../../nba_oracle/http.py), [teams.py](../../nba_oracle/teams.py) |
| Manual bootstrap artifacts | [.env.example](../../.env.example), [phase2_schema.sql](../../supabase/phase2_schema.sql) |

## Next Recommended Step

Operate the finished system, keep evidence accumulating, and prepare for Phase 7:
- use the local dashboard workflow as the default free daily path:
  - `python main.py serve-api`
  - `cd dashboard && npm.cmd run dev`
  - open `http://localhost:3000`
- use the hosted Vercel + Cloudflare Tunnel path only when you specifically want remote browser access
- run `python main.py build-live-slate --live` on slate days
- run `python main.py run-scheduler-once` after games finish, or `python main.py grade-outcomes` directly when you want a focused grading pass
- run `python main.py review-stability` and `python main.py review-learning` as evidence grows
- use [phase-6.md](../plans/implementation/phase-6.md) as the current runtime-automation source of truth
- use [phase-7a.md](../plans/implementation/phase-7a.md) as the forecast-visibility closeout record
- use [phase-7b.md](../plans/implementation/phase-7b.md) as the deeper intelligence-upgrade source of truth
- keep the Phase 1 replay flow intact as the acceptance gate for every future provider or model change
