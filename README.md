# NBA Oracle

NBA Oracle is a Python-first NBA betting intelligence project focused on building a selective, auditable decision system before trusting any live betting workflow.

## Current Status

Phase 1 is complete locally:
- frozen snapshot validation
- deterministic replay engine
- `BET`, `LEAN`, and `SKIP` decision flow
- calibration, source-quality, and market-discipline reporting
- test coverage for the validation core

Phase 2 is complete:
- real live-provider wiring for schedule, odds, stats, and injuries
- live-slate assembly path with no-slate-day handling
- dual local-plus-Supabase storage path in code
- bundle and `--live` execution modes through the Phase 1 predictor
- Phase 2.2 schedule fallback derives the upcoming slate from odds when the official live scoreboard is stale
- real live verification has produced non-zero snapshots and predictions with no `supabase_error:...`

Phase 3 is complete for the current system scope and now operating in evidence-accumulation mode:
- baseline-backed stability review command
- automatic baseline refresh on incompatible replay/config/model metadata
- ROI, CLV, and calibration-aware drift assessment
- timing/freshness review with event logs
- evidence-backed market-readiness locks for moneylines vs totals/props
- analyst-containment checks, disagreement logging, and model-review bookkeeping
- official outcome-grading command that backfills finished winners into stored live predictions

Phase 4A is complete:
- FastAPI operating-core app and protected route layer
- auth bootstrap command plus token-based operator access
- scheduler/meta-scheduler run path
- Telegram and Gmail delivery services
- explicit project-local runtime bootstrap path
- learning-review execution path
- runtime job, notification, and learning-review persistence

Phase 4B is complete:
- React/Vite dashboard scaffold
- authenticated top-nav operator shell
- overview, today, performance, stability, learning, providers, and operations pages
- inline operator action panels backed by real Phase 4A routes
- production build path through `dashboard/`
- hosted frontend path on `Vercel`

Phase 4C is complete for the chosen deployment shape:
- startup sanity command
- CORS + hosted API base support for `Vercel + Cloudflare Tunnel`
- runtime truth now includes startup checks and notification history
- deployment and recovery runbooks
- Cloudflare Tunnel deployment path and Vercel SPA rewrite config
- dashboard-wide refresh after operator actions
- hosted verification through `Vercel + Cloudflare Tunnel + Supabase`

## Repo Structure

```text
nba-oracle/
|-- nba_oracle/                 # Backend package
|-- data/fixtures/              # Frozen replay fixtures
|-- tests/                      # Validation-core tests
|-- docs/
|   |-- spec/                   # Master system spec
|   |-- research/               # Research notes and external findings
|   |-- plans/                  # Problem tracking and implementation plans
|   |   `-- implementation/     # Phase-by-phase implementation plans
|   `-- runbooks/               # Execution and verification runbooks
|-- main.py                     # CLI entrypoint
|-- pyproject.toml              # Project metadata
`-- config.py                   # Root config re-export
```

## Key Docs

- Full master spec: [docs/spec/master-spec.md](docs/spec/master-spec.md)
- Project status matrix: [docs/status/project-status-matrix.md](docs/status/project-status-matrix.md)
- Changes matrix: [docs/status/changes-matrix.md](docs/status/changes-matrix.md)
- Phase 1 implementation plan: [docs/plans/implementation/phase-1.md](docs/plans/implementation/phase-1.md)
- Phase 2 implementation plan: [docs/plans/implementation/phase-2.md](docs/plans/implementation/phase-2.md)
- Phase 2.1 hardening pass: [docs/plans/implementation/phase-2-1.md](docs/plans/implementation/phase-2-1.md)
- Phase 3 implementation plan: [docs/plans/implementation/phase-3.md](docs/plans/implementation/phase-3.md)
- Phase 3 runbook: [docs/runbooks/phase-3.md](docs/runbooks/phase-3.md)
- Phase 3.1 hardening plan: [docs/plans/implementation/phase-3-1.md](docs/plans/implementation/phase-3-1.md)
- Phase 4 restructure: [docs/plans/implementation/phase-4.md](docs/plans/implementation/phase-4.md)
- Phase 4A operating core plan: [docs/plans/implementation/phase-4a.md](docs/plans/implementation/phase-4a.md)
- Phase 4A runbook: [docs/runbooks/phase-4a.md](docs/runbooks/phase-4a.md)
- Phase 4B dashboard plan: [docs/plans/implementation/phase-4b.md](docs/plans/implementation/phase-4b.md)
- Phase 4B runbook: [docs/runbooks/phase-4b.md](docs/runbooks/phase-4b.md)
- Phase 4C integration plan: [docs/plans/implementation/phase-4c.md](docs/plans/implementation/phase-4c.md)
- Deployment runbook: [docs/runbooks/deployment.md](docs/runbooks/deployment.md)
- Recovery runbook: [docs/runbooks/recovery.md](docs/runbooks/recovery.md)
- Phase 4 closeout runbook: [docs/runbooks/phase-4.md](docs/runbooks/phase-4.md)
- Supabase Phase 4A schema: [supabase/phase4a_schema.sql](supabase/phase4a_schema.sql)
- Supabase Phase 3 schema: [supabase/phase3_schema.sql](supabase/phase3_schema.sql)
- Phase 3 outcome-grading schema: [supabase/phase3_2_schema.sql](supabase/phase3_2_schema.sql)
- Phase 1 runbook: [docs/runbooks/phase-1.md](docs/runbooks/phase-1.md)
- Phase 2 runbook: [docs/runbooks/phase-2.md](docs/runbooks/phase-2.md)
- Supabase Phase 2 schema: [supabase/phase2_schema.sql](supabase/phase2_schema.sql)
- Problems tracker: [docs/plans/problems-plan.md](docs/plans/problems-plan.md)
- FTW solutions plan: [docs/plans/ftw-plan.md](docs/plans/ftw-plan.md)
- Research report: [docs/research/prediction-systems-and-public-sentiment-signals.md](docs/research/prediction-systems-and-public-sentiment-signals.md)

## Quick Start

```powershell
python main.py validate-fixture
python -m unittest discover -s tests -p "test_*.py"
python main.py bootstrap-runtime
python main.py startup-sanity
python main.py replay
python main.py review-stability
python main.py review-stability --force-refresh-baseline
python main.py grade-outcomes
python main.py run-scheduler-once
python main.py review-learning
cd dashboard
npm.cmd run build
```

Generated replay and live-slate outputs are written to `reports/`.

## Notes

- The root README is intentionally concise for GitHub.
- The detailed product doctrine, research, and build theory live under `docs/`.
- Sentiment is still intentionally deferred in live mode.
- Supabase is active through the dual storage path.
- Apply `supabase/phase3_schema.sql` to complete Phase 3.1 remote persistence.
- Apply `supabase/phase3_2_schema.sql` to persist outcome-grade history remotely.
- Apply `supabase/phase4a_schema.sql` to persist Phase 4A runtime jobs, notification events, and learning reviews remotely.
- Phase 4B now has a working dashboard scaffold and build path on top of the Phase 4A backend contract.
- Phase 4 remains split into 4A, 4B, and 4C for cleaner execution.
- The preferred final deployment shape is `Vercel` for the dashboard, `Cloudflare Tunnel` for public access to the local backend/runtime, and `Supabase` for persistence.
- Phase 4C now adds startup sanity, deployment artifacts, recovery runbooks, and hosted API support.
- Supabase schema files now enable RLS by default for all Oracle tables in `public`.
- Phase 5 is planned as the interpretation and operator-confidence pass for human-readable explanations, metric education, and the in-product guide page.
