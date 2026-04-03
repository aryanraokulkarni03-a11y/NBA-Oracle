# Phase 1 Runbook

## Goal
Bring up the Phase 1 validation core and verify that replay, gating, and reporting all work end to end.

## Prerequisite
Python 3.11 or newer must be callable from the shell as `python`.

## Step 1: Verify the interpreter
Run:

```powershell
python --version
```

Expected result:
- a Python 3.11+ version string

If this fails:
- close and reopen the terminal or Codex session
- confirm Python was installed with PATH enabled

## Step 2: Validate the frozen fixture
Run:

```powershell
python main.py validate-fixture
```

Expected result:
- fixture loads successfully
- no snapshot leakage error

## Step 3: Run the test suite
Run:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

Expected result:
- all tests pass

## Step 4: Run the replay
Run:

```powershell
python main.py replay
```

Expected result:
- markdown report written to `reports/phase1_replay_report.md`
- json report written to `reports/phase1_replay_report.json`

## Step 5: Review the report
Check that the report includes:
- BET count
- LEAN count
- SKIP count
- hit rate
- ROI
- CLV
- calibration bins
- skip reasons

## What the current build contains
- frozen snapshot validation
- deterministic Phase 1 predictor
- source freshness and trust scoring
- no-bet and price-discipline gating
- replay metrics and reporting
- sample historical slate fixture
- unit tests for the core validation path

## What Phase 1 does not yet include
- live APIs
- Supabase wiring
- Telegram delivery
- FastAPI service layer
- LLM explanation layer

