# Phase 2 Runbook

## Goal
Bring up the Phase 2 signal-quality layer and verify that live-style provider inputs can be assembled, scored, and stored without breaking the Phase 1 validation core.

## What Phase 2 currently includes
- real provider adapters for schedule, odds, injuries, and stats
- live-slate assembly layer
- local durable storage for run artifacts
- sample live-style provider bundle
- CLI command for bundle and live-slate building
- tests for the Phase 2 local execution path

## Step 1: Run the full test suite

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

Expected result:
- all tests pass

## Step 2: Build the sample live slate

```powershell
python main.py build-live-slate
```

Expected result:
- markdown report written to `reports/phase2_live_slate_report.md`
- json report written to `reports/phase2_live_slate_report.json`
- provider artifacts, snapshots, and predictions written under `data/runtime/<run_id>/`

## Step 3: Build the real live slate

```powershell
python main.py build-live-slate --live
```

Expected result:
- the run completes even if there are no games on the slate
- provider artifacts are written under `data/runtime/<run_id>/`
- sentiment remains optional and degraded by default
- if there are valid pregame games available, snapshots and predictions are produced
## Step 4: Review the report
Check that the report includes:
- provider health table
- decision output per game
- Stake vs best vs close line comparison
- stored artifact paths

## Current manual blockers for full Phase 2

These are not needed for the bundle scaffold, but they matter for live-mode completeness:
- Supabase URL and key strategy
- `ODDS_API_KEY`
- primary injury/news source confirmation
- real Reddit API configuration if we move past deferred sentiment

## Recommended next manual setup order

1. Save `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`
2. Save `ODDS_API_KEY`
3. Confirm `ESPN + nba_api-aligned NBA endpoints` as the Phase 2 source stack
4. Add Reddit credentials only when we enable live sentiment

## Notes

- The current Phase 2 path is intentionally local-first and storage-safe.
- The Phase 1 predictor remains the scoring engine.
- Real providers now sit behind the current adapter contracts, and bundle mode remains the safe fallback.
- The current live schedule path only targets the current-day slate and will naturally return zero snapshots on a no-game day.
