# NBA Oracle Phase 4C Final One-Shot Implementation Plan

## Purpose
Phase 4C is the final wiring, operating hardening, and closeout pass.

This is where the already-built backend and frontend stop being separate successes and become one coherent product that can run, recover, and stay truthful under real use.

The final question is:

> Can NBA Oracle run the full daily loop, expose the same truth across CLI, API, UI, Telegram, Gmail, storage, grading, stability, and learning, and recover cleanly when something goes wrong?

If the answer is not yes, the project is not finished.

## Source of Truth
This plan is derived from:
- [master-spec.md](../../spec/master-spec.md)
- [project-status-matrix.md](../../status/project-status-matrix.md)
- [changes-matrix.md](../../status/changes-matrix.md)
- [phase-4.md](./phase-4.md)
- [phase-4a.md](./phase-4a.md)
- [phase-4b.md](./phase-4b.md)

It is explicitly grounded in the code already shipped through:
- [app.py](../../../nba_oracle/api/app.py)
- [meta_scheduler.py](../../../nba_oracle/runtime/meta_scheduler.py)
- [jobs.py](../../../nba_oracle/runtime/jobs.py)
- [state.py](../../../nba_oracle/runtime/state.py)
- [repository.py](../../../nba_oracle/storage/repository.py)
- [grade_outcomes.py](../../../nba_oracle/runs/grade_outcomes.py)
- [review_stability.py](../../../nba_oracle/runs/review_stability.py)
- [trainer.py](../../../nba_oracle/learning/trainer.py)
- [App.tsx](../../../dashboard/src/App.tsx)
- [AppShell.tsx](../../../dashboard/src/components/AppShell.tsx)
- [Operations.tsx](../../../dashboard/src/pages/Operations.tsx)

## Phase 4C Goal
Prove the entire product works as one system:

> scheduler -> live slate -> storage -> grading -> stability -> learning -> API -> UI -> delivery

No layer is allowed to lie about state, lag behind the others invisibly, or require terminal babysitting for normal operation.

## What Phase 4C Must Respect

1. The predictor remains the final betting authority.
2. `BET`, `LEAN`, `SKIP`, degraded state, fallback usage, and insufficient-data states remain visible across every surface.
3. The operator should not need the terminal for normal daily use once startup is done.
4. Telegram, Gmail, API, and UI must agree on the same underlying run state.
5. The system stays manual-bet only.

## In Scope
- end-to-end API/UI/runtime/delivery wiring
- startup and restart hardening
- local automation and boot-time operating flow
- hosted deployment target selection and operating shape
- auth/session hardening across backend and dashboard
- structured runbooks and recovery workflow
- final acceptance verification across real commands and real UI paths

## Out of Scope
- new betting markets
- autonomous bet placement
- new analyst/LLM explanation layer

## What Phase 4C Must Prove

1. The scheduler can drive the product without manual babysitting.
2. UI, API, Telegram, Gmail, and stored reports all reflect the same truth.
3. Grading, stability, and learning are part of one operating loop, not isolated commands.
4. Startup and restart are deterministic.
5. Failures are visible, understandable, and recoverable.
6. The operator can run the product normally from the dashboard plus delivery surfaces.

## Deployment Direction
Phase 4C will close against this deployment target:

- `Vercel` for the dashboard frontend
- `Cloudflare Tunnel` for secure public access to the local FastAPI backend and runtime
- local backend/runtime on the operator machine
- `Supabase` for persistent storage

This is the preferred no-billing shape because:
- the dashboard benefits from Vercel's frontend workflow and preview model
- the backend and runtime can remain local without forcing paid infrastructure
- Cloudflare Tunnel provides a more stable free public bridge than disposable tunnels
- Supabase is already the persistence system of record

Local operation is no longer a fallback-only afterthought. It is part of the intended operating model, with Cloudflare Tunnel making the local backend reachable by the hosted frontend.

## Real Remaining Gaps To Close

This phase is not about inventing major new features. It is about closing the seams that still remain:

- browser-level verification and final truth checks across all dashboard pages
- final delivery verification for Telegram and Gmail under the same live state the dashboard sees
- startup and auto-start behavior that can survive restarts
- schema/bootstrap sanity checks at startup
- run-state consistency across runtime logs, reports, API payloads, and UI
- clear recovery steps when providers, storage, delivery, or auth fail
- hosted deployment verification for the chosen Vercel plus Cloudflare Tunnel shape
- final acceptance suite and closeout docs

## Workstreams

### Workstream 1: End-to-End Truth Wiring
Tighten and verify:
- scheduler -> backend jobs
- backend jobs -> local and Supabase persistence
- persistence -> API
- API -> dashboard
- persistence/API -> Telegram/Gmail
- outcome grading -> stability review
- stability review -> learning review

Deliverables:
- single-source runtime truth checks
- shared operator-visible run identifiers
- consistent timestamps and status naming across surfaces

### Workstream 2: Dashboard-to-Backend Hardening
Finish the last UI/API seams:
- expired-session handling
- operator action feedback consistency
- no stale page sections after operator-triggered jobs
- dashboard refresh behavior after live-slate, grading, stability, and learning runs
- browser-safe handling of `429`, `401`, and degraded states

Deliverables:
- final dashboard interaction pass
- route-level smoke verification
- hardening notes in the runbook

### Workstream 3: Delivery and Notification Truthfulness
Verify and tighten:
- Telegram test delivery
- Gmail test delivery
- operational digests reflect the same live run shown in the dashboard
- failure alerts reflect real backend failures and not generic noise
- notification history is inspectable and consistent with runtime state

Deliverables:
- final delivery verification notes
- notification troubleshooting section

### Workstream 4: Startup, Restart, and Automation
Build and document the real operating path:
- startup sanity check command
- backend + dashboard launch flow
- local Windows Task Scheduler fallback for backend startup and scheduler cadence
- hosted launch flow for Vercel + Cloudflare Tunnel
- environment validation before runtime begins
- restart/reboot behavior

Deliverables:
- `deployment.md`
- boot-time checklist
- startup automation instructions
- hosted deployment instructions for Vercel frontend and Cloudflare Tunnel backend exposure

### Workstream 5: Recovery and Operator Runbooks
Write the operator-grade recovery layer:
- provider failure recovery
- auth/session recovery
- Supabase failure handling
- dashboard connectivity issues
- delivery failure recovery
- manual fallback command order

Deliverables:
- `recovery.md`
- `phase-4.md` closeout runbook
- operator quick-reference checklist

### Workstream 6: Final Acceptance and Project Closeout
Run and document:
- backend tests
- frontend build verification
- hosted deployment verification
- live slate execution
- dashboard verification pass
- delivery verification
- outcome grading verification
- stability review verification
- learning review verification
- scheduler once verification

If enough graded evidence exists:
- confirm learning review remains candidate-only and honest

Deliverables:
- final verification checklist
- final status matrix update
- final "project complete" closeout only if all gates pass

## Recommended Implementation Areas

- `nba_oracle/runtime/`
- `nba_oracle/api/`
- `nba_oracle/notifications/`
- `nba_oracle/storage/`
- `dashboard/src/`
- `docs/runbooks/phase-4.md`
- `docs/runbooks/deployment.md`
- `docs/runbooks/recovery.md`
- final operator checklist under `docs/runbooks/`

## Concrete 4C Deliverables

1. Final runtime/startup sanity command or equivalent startup checks
2. Deployment runbook for:
   - local backend start
   - local dashboard start
   - Vercel frontend deployment
   - Cloudflare Tunnel backend exposure
   - scheduler cadence
   - restart behavior
3. Recovery runbook for:
   - provider failures
   - auth/session failures
   - Supabase issues
   - notification failures
   - dashboard/API connectivity issues
4. Phase 4 end-to-end operator checklist
5. Status matrix and changes matrix closeout update
6. Verified commands list for the finished product

## Manual Inputs Needed Later
- preferred Windows Task Scheduler behavior for local fallback cadence
- whether local backend should auto-start on login or machine boot
- whether the local dashboard should auto-open after backend startup
- default failure-alert destination if Telegram and Gmail disagree or one is down

## Acceptance Criteria
Phase 4C is acceptable only if:
- scheduler, API, UI, Telegram, Gmail, and stored reports agree on current system state
- operator actions from the dashboard reflect real backend outcomes immediately or through a documented refresh path
- the system can start cleanly from a cold restart
- the hosted deployment target is documented and verifiable
- runtime failures are visible and recoverable through documented procedures
- delivery tests succeed and are traceable in runtime history
- outcome grading, stability review, and learning review all fit into one repeatable operating loop
- the product can be used normally without terminal dependence after startup
- the trust rules from Phases 1 to 3 are still preserved

## Final Exit Rule
Do not call NBA Oracle complete until all of these are true:

1. Phase 4A has passed real operating verification.
2. Phase 4B has passed browser-level verification and operator-flow verification.
3. Phase 4C has proven the full product loop is stable under real use.
4. Recovery runbooks exist and are usable.
5. The final status matrix and changes matrix reflect a finished project truthfully.
