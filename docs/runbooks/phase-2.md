# Phase 2 Runbook

## Goal
Bring up the Phase 2 signal-quality layer and verify that live-style provider inputs can be assembled, scored, and stored without breaking the Phase 1 validation core.

## What Phase 2 currently includes
- provider adapter scaffold
- live-slate assembly layer
- local durable storage for run artifacts
- sample live-style provider bundle
- CLI command for live-style slate building
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

## Step 3: Review the report
Check that the report includes:
- provider health table
- decision output per game
- Stake vs best vs close line comparison
- stored artifact paths

## Current manual blockers for full Phase 2

These are not needed for the local scaffold, but they are needed before Phase 2 can be considered complete:
- Supabase URL and key strategy
- real odds provider credentials
- real injury/news source confirmation
- real Reddit API configuration if we move past fixture-backed sentiment

## Recommended next manual setup order

1. Supabase project creation
2. Odds provider credentials
3. Primary injury/news source confirmation
4. Reddit credentials if needed

## Notes

- The current Phase 2 path is intentionally local-first and storage-safe.
- The Phase 1 predictor remains the scoring engine.
- Real providers should be swapped in behind the current adapter contracts, not by rewriting the predictor.
