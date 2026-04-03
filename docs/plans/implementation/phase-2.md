# NBA Oracle Phase 2 Implementation Plan

## Purpose
Phase 2 is the signal quality layer. Its job is to connect the Phase 1 validation core to real-world inputs and permanent storage without weakening the replay and gating discipline that Phase 1 established.

This phase exists because the current system can validate predictions on frozen data, but it still cannot ingest live schedule, odds, injury, stats, and sentiment inputs or persist live analysis history.

## Source of Truth
This plan is derived from:
- [master-spec.md](../../spec/master-spec.md)
- [project-status-matrix.md](../../status/project-status-matrix.md)
- [problems-plan.md](../problems-plan.md)
- [ftw-plan.md](../ftw-plan.md)
- [phase-1.md](./phase-1.md)

## Phase 2 Goal
Build the first permanent live-data layer that can answer this question:

> Can the system ingest real pregame inputs through stable adapters, normalize them into Phase 1-compatible snapshots, store them durably, and produce live-style prediction inputs without breaking the validation rules?

If the answer is not yes, the system should not move toward delivery, LLM explanation, or live betting workflows.

## Phase 2 Scope

### In scope
- Provider adapter architecture
- Real schedule ingestion
- Real odds ingestion
- Real injury/news ingestion
- Real stats ingestion
- Optional sentiment ingestion with fallback behavior
- Snapshot normalization compatible with the Phase 1 predictor
- Permanent storage wiring for snapshots and predictions
- Provider health, freshness, and fallback handling
- Local execution path for building one live-style slate snapshot

### Out of scope
- Telegram bot delivery
- Gmail notifications
- Dashboard UI
- Auth
- Learning engine automation
- Full scheduler runtime
- LLM explanation generation

## What Phase 2 Must Prove

1. Real providers can be called through stable adapter interfaces.
2. Every provider output can be normalized into the same snapshot shape the validation core expects.
3. Snapshot timing and source metadata are preserved for every live input.
4. Missing or degraded providers do not crash the full slate build.
5. Permanent storage can persist raw snapshots, normalized records, and prediction outputs.
6. A live-style slate can be built and passed through the Phase 1 scorer and reports.

## Phase 2 Design Rules

1. Keep the Phase 1 predictor unchanged as much as possible.
2. Build adapters around the predictor, not predictor logic around adapters.
3. Prefer official or structured sources first, scraper fallbacks second.
4. Treat sentiment as optional and degradable, not mandatory.
5. Persist both raw provider output and normalized output when practical.
6. Keep every live input timestamped so replay compatibility is preserved.

## Implementation Steps

### Step 1: Define the provider adapter contract
- Create a common interface for all providers.
- Every adapter should expose:
  - provider name
  - source kind
  - fetch method
  - normalization method
  - health/failure metadata
- Every adapter output must include:
  - `source_time`
  - `source_version`
  - trust metadata
  - raw payload reference or raw payload body

### Step 2: Build the schedule adapter
- Add a schedule provider for today's NBA slate.
- Normalize games into a common schedule shape with:
  - game id
  - teams
  - tip-off time
  - decision-time candidate
- Treat schedule ingestion as the root object for the rest of the live slate.

### Step 3: Build the odds adapter
- Add a primary odds provider adapter.
- Normalize:
  - current line
  - best available line if available
  - opening line if available
  - market timestamp
- Preserve provider freshness and fallback state.

### Step 4: Build the injury/news adapter
- Add an official-first injury/news adapter layer.
- Normalize:
  - player status
  - team impact summary
  - source confirmation level
  - update timestamp
- Make this adapter capable of returning partial data without killing the pipeline.

### Step 5: Build the stats adapter
- Add a structured stats adapter that can return the core pregame team context needed for scoring.
- Normalize:
  - form metrics
  - efficiency context
  - rest/travel indicators when available
- Keep the initial stats scope narrow and high-signal.

### Step 6: Build the optional sentiment adapter
- Add Reddit/X sentiment adapters behind a clearly optional interface.
- If sentiment fails, the live slate should still build successfully.
- Normalize sentiment as a support signal only.

### Step 7: Build the live snapshot assembler
- Merge schedule, odds, injuries, stats, and optional sentiment into one normalized game snapshot.
- Match the Phase 1 snapshot format as closely as possible.
- Ensure every game snapshot remains point-in-time safe and replay-compatible.

### Step 8: Build the storage layer
- Add permanent storage wiring for:
  - raw provider fetches
  - normalized snapshots
  - prediction outputs
  - run metadata
- Keep the schema Phase 1-compatible so replay and audit stay possible.
- Store enough information to support later Supabase-backed history, reporting, and learning.

### Step 9: Build provider health and fallback handling
- Record provider success/failure per run.
- Track freshness and degraded mode by provider.
- Allow the slate build to continue when one optional provider fails.
- Block prediction activation only when a critical provider fails badly enough.

### Step 10: Build the Phase 2 execution path
- Add one command that:
  - fetches the current slate
  - assembles live-style snapshots
  - runs them through the Phase 1 predictor
  - persists the outputs
  - generates a report for review
- This should still be a controlled operator workflow, not a fully automated betting workflow.

## Recommended Module Additions

### New package areas
- `nba_oracle/providers/`
- `nba_oracle/storage/`
- `nba_oracle/assembly/`
- `nba_oracle/runs/`

### Likely first files
- `providers/base.py`
- `providers/schedule.py`
- `providers/odds.py`
- `providers/injuries.py`
- `providers/stats.py`
- `providers/sentiment.py`
- `assembly/live_snapshot_builder.py`
- `storage/repository.py`
- `runs/build_live_slate.py`

## Manual Inputs Needed Later

These should be asked for during implementation, not guessed:
- Supabase project URL
- Supabase service or anon key strategy
- Primary odds provider choice
- Primary injury/news provider choice
- Whether Phase 2 storage should start in Supabase immediately or use a dual local-plus-Supabase mode

## Acceptance Criteria
Phase 2 is acceptable only if all of the following are true:
- A real current slate can be fetched and normalized.
- Provider outputs preserve source timing and version metadata.
- The live snapshot builder produces Phase 1-compatible records.
- The system can continue in degraded mode when optional sources fail.
- Critical provider failures are visible and auditable.
- Normalized snapshots and predictions are stored durably.
- A live-style run can pass through the existing predictor and reporting flow.

## Risks
- Provider contracts can drift if upstream sources change.
- Too much provider-specific logic can leak into the core predictor.
- Sentiment integration can create fragility if treated as mandatory.
- Storage can become noisy if raw and normalized payloads are not separated clearly.
- Live data freshness can look healthy while specific fields are stale.

## Phase 2 Deliverables
- Provider adapter specification
- Live schedule adapter
- Live odds adapter
- Live injury/news adapter
- Live stats adapter
- Optional sentiment adapter with fallback behavior
- Snapshot assembly layer
- Storage repository layer
- Phase 2 live-slate command
- Phase 2 run report template

## Phase 2 Exit Rule
Do not move to the next phase until the system can build a real pregame slate from live sources, persist the evidence trail, and pass the resulting normalized snapshots through the Phase 1 validation core without breaking replay compatibility.

## Why This Phase Comes Next
Phase 1 proved the decision engine can be audited in a controlled environment.

Phase 2 is where the system stops being a lab-only model and starts becoming a real operating backend. It does not yet need to talk to users, but it must be able to ingest the world faithfully.

