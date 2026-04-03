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

Phase 3 is now in progress:
- baseline-backed stability review command
- drift assessment against a saved Phase 3 baseline
- timing/freshness review
- strict market-readiness locks for moneylines vs totals/props
- analyst-containment checks and reporting

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
python main.py replay
python main.py review-stability
```

Generated replay and live-slate outputs are written to `reports/`.

## Notes

- The root README is intentionally concise for GitHub.
- The detailed product doctrine, research, and build theory live under `docs/`.
- Sentiment is still intentionally deferred in live mode.
- Supabase is active through the dual storage path.
- Phase 3 is now the active backend phase.
