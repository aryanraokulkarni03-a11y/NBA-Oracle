# Phase 2 Runbook

## Goal
Bring up the Phase 2 signal-quality layer and verify that live-style provider inputs can be assembled, scored, and stored without breaking the Phase 1 validation core.

## What Phase 2 currently includes
- real provider adapters for schedule, odds, injuries, and stats
- live-slate assembly layer
- dual local-plus-Supabase storage path in code
- sample live-style provider bundle
- CLI command for bundle and live-slate building
- tests for the Phase 2 local execution path
- odds-derived schedule fallback when the official live scoreboard returns only stale or finished games

## Step 0: Create `.env`

Copy [.env.example](../../.env.example) to `.env` and fill in:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `ODDS_API_KEY`
- `ORACLE_STORAGE_MODE=dual`

## Step 0.1: Bootstrap Supabase schema

Open the Supabase SQL editor and run:
- [phase2_schema.sql](../../supabase/phase2_schema.sql)

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
- if `.env` and schema are ready, remote writes can also be attempted through the dual storage path

## Step 3: Build the real live slate

```powershell
python main.py build-live-slate --live
```

Expected result:
- the run completes even if there are no games on the slate
- provider artifacts are written under `data/runtime/<run_id>/`
- sentiment remains optional and degraded by default
- if there are valid pregame games available, snapshots and predictions are produced
- if Supabase is ready, the storage path should include remote markers instead of local-only artifacts

## Step 3.1: Phase 2 completion check

To close Phase 2, run the live slate command during a real pregame window and confirm:
- `Snapshot count > 0`
- `Prediction count > 0`
- no `supabase_error:...` markers appear in the stored artifact section
- the schedule provider can still proceed if the official scoreboard is stale, by using the odds-derived fallback

## Step 4: Review the report
Check that the report includes:
- provider health table
- decision output per game
- reference vs best vs close line comparison
- stored artifact paths

## Current manual blockers for full Phase 2

These are the remaining manual pieces for a full Phase 2.1 closeout:
- create `.env` from `.env.example`
- run the Supabase schema SQL
- keep `ODDS_API_KEY` present locally
- add Reddit credentials only when we move past deferred sentiment

## Recommended next manual setup order

1. Create `.env`
2. Apply `phase2_schema.sql`
3. Verify bundle mode
4. Verify live mode
5. Add Reddit credentials only when we enable live sentiment

## Notes

- The current Phase 2 path is intentionally local-first and storage-safe.
- The Phase 1 predictor remains the scoring engine.
- Real providers now sit behind the current adapter contracts, and bundle mode remains the safe fallback.
- The current live schedule path only targets the current-day slate and will naturally return zero snapshots on a no-game day.
- Reports now use `reference line` language instead of implying a true Stake-native price feed.
- When the official live scoreboard only returns stale or finished games, the schedule layer now falls back to the upcoming slate exposed by the odds provider.
