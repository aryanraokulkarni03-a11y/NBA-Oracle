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
```

## Outputs

Phase 3 writes:
- [reports/phase3_stability_report.md](../../reports/phase3_stability_report.md)
- [reports/phase3_stability_report.json](../../reports/phase3_stability_report.json)
- [data/stability/phase3_baseline.json](../../data/stability/phase3_baseline.json)

## What The Command Does

1. Creates the baseline file if one does not already exist.
2. Reuses the saved baseline on later runs so drift is measured against a stable anchor.
3. Reviews recent live runs from `data/runtime/live-*`.
4. Ignores incomplete runtime folders safely.
5. Computes:
   - drift status
   - timing status
   - market readiness
   - analyst containment
6. Writes markdown and JSON reports for operator review.

## How To Read The Output

### Drift status
- `stable` means recent live behavior is still within the configured thresholds.
- `warning` means behavior moved enough to deserve review.
- `retrain_review` means drift is real and the graded sample is finally large enough to justify retraining review.
- `insufficient_data` means there are not enough actionable live runs yet.

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
```
