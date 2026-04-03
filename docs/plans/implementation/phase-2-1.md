# NBA Oracle Phase 2.1 Hardening Pass

## Purpose
Phase 2.1 closes the gaps discovered during the first Phase 2 audit so the project can leave the signal-quality layer cleanly.

This pass exists to make Phase 2:
- storage-real instead of local-only
- provider-honest instead of mislabeled
- setup-reproducible instead of shell-fragile
- ready to hand off into Phase 3 without carrying avoidable debt

## Hardening Goals

1. Remove misleading `Stake` language where no true Stake-specific feed exists yet.
2. Wire dual local-plus-Supabase storage in code.
3. Add a real Supabase schema bootstrap artifact.
4. Make environment loading deterministic through a repo `.env` file.
5. Bring the package manifest in line with the real backend surface.
6. Tighten provider normalization fields to better match the Phase 2 plan.

## What Phase 2.1 Lands

- `.env`-driven runtime config with `.env.example`
- Supabase-ready repository layer with local fallback
- Supabase schema SQL for Phase 2 run storage
- reference-book terminology in reports
- richer market metadata in live predictions
- richer injury metadata in normalized records
- dependency manifest updates for the current backend stack

## Manual Bootstrap Required

Phase 2.1 still requires two manual setup steps:

1. Copy `.env.example` to `.env` and fill in the real values.
2. Run `supabase/phase2_schema.sql` in the Supabase SQL editor.

## Exit Rule

Do not call Phase 2 complete until:
- `.env` is populated locally
- the Supabase schema file has been applied
- a live or bundle-backed Phase 2 run can persist both locally and to Supabase without breaking the Phase 1 scoring path
