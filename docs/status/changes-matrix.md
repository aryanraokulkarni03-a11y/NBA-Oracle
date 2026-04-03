# NBA Oracle Changes Matrix

## Purpose
Use this file as the quick changelog reference:
- what changed recently
- why it mattered
- what it unblocked
- what is still pending after that change

Pair it with [project-status-matrix.md](./project-status-matrix.md):
- `project-status-matrix.md` = where the project stands now
- `changes-matrix.md` = how we got here

## Change Timeline

| Checkpoint | Status | Main Outcome | What It Unblocked | What Still Remains |
|---|---|---|---|---|
| Repo structure cleanup | Complete | Specs, plans, runbooks, research, and code were separated cleanly under `docs/` and `nba_oracle/`. | Easier implementation planning and status tracking | Keep docs synced as phases land |
| GitHub-facing root README | Complete | Root README became concise and repo-friendly while the full doctrine moved into the master spec. | Clear public repo structure | Keep public README short and current |
| Phase 1 validation core | Complete | Replay engine, deterministic predictor, no-bet logic, reporting, and tests were built. | Honest replay and gated betting logic | More historical depth later |
| Phase 1.1 hardening | Complete | Calibration acceptance checks, richer report output, and stronger replay readiness were added. | Trustworthy Phase 1 closeout | Real historical replay expansion later |
| Status matrix created | Complete | Fast operational checkpoint file was added. | Easier phase-by-phase review | Keep updated after each checkpoint |
| Phase 2 implementation plan | Complete | Signal-quality layer was turned into a concrete backend build plan. | Safe Phase 2 execution | Continue converting plan into code |
| Phase 2 scaffold | Complete | Provider interfaces, assembly layer, local repository, sample bundle, and tests landed. | Live-style execution without real providers | Real upstream wiring |
| Manual setup path | Complete | Supabase, The Odds API, `nba_api`, and ESPN decisions were locked in. | Real provider implementation path | Supabase still needs code wiring |
| Phase 2 live provider wiring | In progress | Real schedule, odds, stats, and injury fetch paths now exist with bundle fallback. | Live mode through the CLI | Provider hardening and richer data coverage |
| Phase 2.1 hardening | In progress | `.env` config, dual storage code path, Supabase schema, and reference-line reporting landed. | Honest storage and setup workflow | Apply schema and verify remote writes |
| Live-mode no-slate handling | Complete | `--live` mode now treats zero-game days as valid empty runs instead of cascading failures. | Safer daily operations | Date-targeted slate support |
| Phase 3 implementation plan | Complete | Stability-layer work is now captured as a concrete build plan. | Safe Phase 3 execution | Continue converting the plan into code |
| Phase 3 execution start | In progress | Saved-baseline review flow, drift checks, timing checks, market locks, and analyst-containment reporting landed. | Operator stability review without spreadsheet work | Retraining workflow and richer graded evidence |
| Phase 3.1 hardening plan | Complete | A one-shot closeout plan now targets the remaining Phase 3 gaps directly. | Precise Phase 3 bug-fix and hardening pass | Execute the Phase 3.1 code changes |
| Phase 3.1 execution | Complete in code | Baseline refresh rules, ROI/CLV/calibration drift, timing-event logs, evidence-backed market locks, analyst disagreement logging, model-review bookkeeping, and Supabase schema draft landed. | A much more trustworthy Phase 3 review workflow | Apply the Phase 3 schema and gather more graded live evidence |
| Outcome grading workflow | Complete in code | A dedicated `grade-outcomes` command now fetches official final results, backfills `actual_winner` into stored live runs, emits reports, and persists grading artifacts. | Real outcome accumulation for Phase 3 drift and retraining evidence | Apply the outcome-grade schema remotely and keep running it after games finish |
| Phase 4 restructuring | Complete | The final product pass is now split into 4A operating core, 4B dashboard, and 4C final integration hardening. | Cleaner execution order with less frontend rework and safer final integration | Execute 4A first, then 4B, then 4C |
| Phase 4A operating core execution | In progress | FastAPI app, auth bootstrap, protected backend routes, scheduler/meta-scheduler, Telegram/Gmail delivery services, learning execution, and Phase 4A runtime persistence are now in code. | A real backend contract for the future dashboard and operator workflow | Live notification tests, auth bootstrap verification, and final 4A hardening |
| Phase 4A.1 hardening | Complete in code | Rate limiting is enforced, learning thresholds are aligned, the scheduler uses a real two-hour target window, Telegram command-style handling exists, and runtime bootstrap is explicit. | Safer 4A closeout and more reproducible setup | Final manual re-verification, then move toward Phase 4B |
| Phase 4B final planning pass | Complete | The dashboard plan now targets the real 4A API contract, defines the exact pages and operator flows, and adds explicit frontend truth rules for degraded, skip, and insufficient-data states. | Safe UI execution without inventing backend behavior | Execute the React/Vite dashboard build in one pass |
| Phase 4B dashboard execution start | In progress | The dashboard folder, app shell, auth flow, page set, inline operator controls, and shared Stripe-leaning dark UI system are now built and compile through Vite. | Real browser-facing operator workflow on top of 4A | Browser verification and final 4B polish before 4C |
| Phase 4C final planning pass | Complete | The final phase is now rewritten as a real integration and hardening closeout around startup, restart, scheduler truth, dashboard/API refresh consistency, delivery verification, recovery, hosted deployment, and final acceptance. | A clean final execution target to finish the product without inventing new major surfaces | Execute the final integration pass end to end |
| Sentiment deferral | Intentional | Reddit/X live sentiment remains off by design in current live mode. | Keeps Phase 2 stable while core providers mature | Add Reddit-first sentiment later |

## Current Implementation Delta

| Area | Landed | Pending |
|---|---|---|
| Schedule | NBA live scoreboard fetch path | Better date targeting and richer game metadata |
| Odds | The Odds API fetch path and normalization | Stake-aware reference pricing and stronger line shopping |
| Injuries | ESPN parser with graceful degradation | Secondary confirmation source and parser hardening |
| Stats | NBA metrics fetch path | Rest, travel, and broader pregame context |
| Sentiment | Deferred placeholder path | Real Reddit-first live adapter |
| Storage | Local runtime persistence plus verified dual Supabase path, with Phase 3.1 dual-storage code ready and outcome-grade dual persistence implemented | Apply the outcome-grade schema remotely |
| CLI | Bundle mode, `--live` mode, enhanced `review-stability`, `grade-outcomes`, `review-learning`, `serve-api`, `run-scheduler-once`, `bootstrap-auth`, and delivery test commands | Hosted deployment and final 4C polish |
| Dashboard | React/Vite scaffold, top-nav shell, authenticated pages, operator action cards, and shared CSS system | Final browser verification, Vercel deployment, UI/API sync hardening, and 4C integration |

## Latest Verified Commands

```powershell
python -m unittest discover -s tests -p "test_*.py"
python main.py bootstrap-runtime
python main.py build-live-slate
python main.py build-live-slate --live
python main.py review-stability
python main.py review-stability --force-refresh-baseline
python main.py grade-outcomes
python main.py run-scheduler-once
python main.py serve-api
```

## Current Best Reading Order

1. [project-status-matrix.md](./project-status-matrix.md)
2. [phase-3.md](../plans/implementation/phase-3.md)
3. [phase-3-1.md](../plans/implementation/phase-3-1.md)
4. [phase-4.md](../plans/implementation/phase-4.md)
5. [phase-4a.md](../plans/implementation/phase-4a.md)
6. [phase-4a.md](../runbooks/phase-4a.md)
7. [phase-4b.md](../plans/implementation/phase-4b.md)
8. [phase-4b.md](../runbooks/phase-4b.md)
9. [phase-4c.md](../plans/implementation/phase-4c.md)
10. [phase-3.md](../runbooks/phase-3.md)
11. [master-spec.md](../spec/master-spec.md)
