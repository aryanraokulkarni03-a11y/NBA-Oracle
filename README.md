# NBA Oracle

NBA Oracle is a Python-first NBA betting intelligence project focused on building a selective, auditable decision system before trusting any live betting workflow.

## Current Status

Phase 1 is complete locally:
- frozen snapshot validation
- deterministic replay engine
- `BET`, `LEAN`, and `SKIP` decision flow
- calibration, source-quality, and market-discipline reporting
- test coverage for the validation core

Phase 2 has started:
- real live-provider wiring for schedule, odds, stats, and injuries
- live-slate assembly path with no-slate-day handling
- local durable storage for provider outputs, snapshots, and predictions
- bundle and `--live` execution modes through the Phase 1 predictor

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
- Phase 1 runbook: [docs/runbooks/phase-1.md](docs/runbooks/phase-1.md)
- Phase 2 runbook: [docs/runbooks/phase-2.md](docs/runbooks/phase-2.md)
- Problems tracker: [docs/plans/problems-plan.md](docs/plans/problems-plan.md)
- FTW solutions plan: [docs/plans/ftw-plan.md](docs/plans/ftw-plan.md)
- Research report: [docs/research/prediction-systems-and-public-sentiment-signals.md](docs/research/prediction-systems-and-public-sentiment-signals.md)

## Quick Start

```powershell
python main.py validate-fixture
python -m unittest discover -s tests -p "test_*.py"
python main.py replay
```

Generated replay and live-slate outputs are written to `reports/`.

## Notes

- The root README is intentionally concise for GitHub.
- The detailed product doctrine, research, and build theory live under `docs/`.
- Sentiment is still intentionally deferred in live mode.
- Supabase wiring and delivery systems are planned for later phases.
