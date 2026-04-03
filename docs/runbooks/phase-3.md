# Phase 3 Runbook

## Purpose
Phase 3 reviews model stability after live runs have already been stored.

Use this runbook to answer:
- is the live model behaving like its validated baseline?
- are freshness and timing still healthy?
- are non-moneyline markets still locked?
- is predictor authority still intact?

## Command

Run from the repo root:

```powershell
python main.py review-stability
```

Optional flags:

```powershell
python main.py review-stability --limit 10
python main.py review-stability --runtime-dir data/runtime
python main.py review-stability --replay-report reports/phase1_replay_report.json
python main.py review-stability --force-refresh-baseline
python main.py review-stability --analyst-payload data/stability/analyst_payload.json
python main.py review-stability --candidate-model-version phase3-candidate-v1
```

## Outputs

Phase 3 writes:
- [reports/phase3_stability_report.md](../../reports/phase3_stability_report.md)
- [reports/phase3_stability_report.json](../../reports/phase3_stability_report.json)
- [data/stability/phase3_baseline.json](../../data/stability/phase3_baseline.json)
- [data/stability/phase3_model_registry.json](../../data/stability/phase3_model_registry.json)

## What The Command Does

1. Creates the baseline file if one does not already exist.
2. Automatically refreshes the saved baseline when replay/config/model metadata is incompatible or when `--force-refresh-baseline` is used.
3. Reviews recent live runs from `data/runtime/live-*`.
4. Ignores incomplete runtime folders safely.
5. Computes:
   - drift status
   - timing status
   - market readiness
   - analyst containment
6. Records model-review workflow state in the local registry.
7. Writes markdown and JSON reports for operator review.

## How To Read The Output

### Drift status
- `stable` means recent live behavior is still within the configured thresholds.
- `warning` means behavior moved enough to deserve review.
- `retrain_review` means drift is real and the graded sample is finally large enough to justify retraining review.
- `insufficient_data` means there are not enough actionable live runs yet.
- `insufficient_outcomes` means live runs exist, but graded outcome depth is still too thin for full ROI/CLV/calibration judgment.

### Timing status
- `healthy` means source freshness and market age are still within acceptable bounds.
- `watch` means timing quality slipped and should be monitored.
- `degraded` means stale signals are showing up too often.

### Market readiness
- `moneyline` should remain active.
- `totals` and `props` should remain locked in strict Phase 3 mode.

### Analyst containment
- `contained` is the desired state.
- anything weaker means predictor authority needs attention before Phase 4.

## Supabase Closeout

Phase 3.1 introduces new remote tables for:
- baselines
- reviews
- timing events
- analyst logs
- model review records

Apply [phase3_schema.sql](../../supabase/phase3_schema.sql) in Supabase SQL Editor to complete the dual-storage path for Phase 3.1.

## Good Phase 3 Output

Healthy Phase 3 output usually looks like:
- no crash
- readable markdown report
- baseline file present
- drift either `stable` or `insufficient_data`
- timing `healthy` or at worst `watch`
- moneylines active
- totals and props locked
- analyst containment `contained`

## Escalation Rules

Do not move to Phase 4 just because this command runs.

Escalate for review if:
- drift becomes `warning` or `retrain_review`
- timing becomes `degraded`
- totals or props unlock unexpectedly
- analyst containment is no longer `contained`

## Verification

At minimum, verify:

```powershell
python -m unittest discover -s tests -p "test_*.py"
python main.py review-stability
python main.py review-stability --force-refresh-baseline
```
