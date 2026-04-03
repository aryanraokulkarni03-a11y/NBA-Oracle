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
| Live-mode no-slate handling | Complete | `--live` mode now treats zero-game days as valid empty runs instead of cascading failures. | Safer daily operations | Date-targeted slate support |
| Sentiment deferral | Intentional | Reddit/X live sentiment remains off by design in current live mode. | Keeps Phase 2 stable while core providers mature | Add Reddit-first sentiment later |

## Current Implementation Delta

| Area | Landed | Pending |
|---|---|---|
| Schedule | NBA live scoreboard fetch path | Better date targeting and richer game metadata |
| Odds | The Odds API fetch path and normalization | Stake-aware reference pricing and stronger line shopping |
| Injuries | ESPN parser with graceful degradation | Secondary confirmation source and parser hardening |
| Stats | NBA metrics fetch path | Rest, travel, and broader pregame context |
| Sentiment | Deferred placeholder path | Real Reddit-first live adapter |
| Storage | Local runtime artifact persistence | Supabase tables and database writes |
| CLI | Bundle mode and `--live` mode | Scheduler/operator workflow integration |

## Latest Verified Commands

```powershell
python -m unittest discover -s tests -p "test_*.py"
python main.py build-live-slate
python main.py build-live-slate --live
```

## Current Best Reading Order

1. [project-status-matrix.md](./project-status-matrix.md)
2. [phase-2.md](../runbooks/phase-2.md)
3. [phase-2.md](../plans/implementation/phase-2.md)
4. [master-spec.md](../spec/master-spec.md)
