# NBA Oracle Phase 4C Implementation Plan

## Purpose
Phase 4C is the final wiring and production hardening pass.

This is where the already-built backend and frontend become one coherent operating system.

## Source of Truth
This plan is derived from:
- [master-spec.md](../../spec/master-spec.md)
- [project-status-matrix.md](../../status/project-status-matrix.md)
- [changes-matrix.md](../../status/changes-matrix.md)
- [phase-4.md](./phase-4.md)
- [phase-4a.md](./phase-4a.md)
- [phase-4b.md](./phase-4b.md)

## Phase 4C Goal
Prove the entire product works as one system:

> scheduler -> live slate -> storage -> grading -> stability -> learning -> API -> UI -> delivery

If any of those seams are unreliable, the project is not finished.

## In Scope
- end-to-end integration
- API/UI contract hardening
- delivery/runtime truthfulness checks
- auth/session hardening
- deployment/startup hardening
- failure recovery and operator runbooks
- final acceptance verification

## Out of Scope
- new major product surfaces
- new betting markets
- autonomous bet placement

## What Phase 4C Must Prove

1. The scheduler can drive the product without terminal babysitting.
2. UI, API, Telegram, and Gmail all reflect the same truth.
3. Outcome grading, stability review, and learning updates are part of the same operating loop.
4. Failures are visible and recoverable.
5. The project can restart and continue without silent corruption or lost state.

## Major Workstreams

### Workstream 1: End-to-End Wiring
Verify and tighten:
- scheduler -> backend commands
- backend commands -> persistence
- persistence -> API
- API -> UI
- persistence/API -> Telegram/Gmail
- grading -> stability
- stability -> learning review

### Workstream 2: Operator Flows
Verify core operator flows:
- login
- inspect today’s slate
- review provider degradation
- inspect history
- review stability
- inspect learning state
- trigger operator actions safely

### Workstream 3: Recovery and Logging
Build/verify:
- structured runtime logs
- startup state checks
- schema/bootstrap checks
- failure banners/alerts
- manual recovery runbooks

### Workstream 4: Deployment Hardening
Finalize:
- local startup instructions
- Task Scheduler automation
- environment checks
- backup/recovery notes
- operator boot-time sanity checklist

### Workstream 5: Final Acceptance Suite
Run and document:
- full backend tests
- key end-to-end smoke flows
- real live run
- grading pass
- stability review pass
- learning-cycle verification if enough evidence exists

## Recommended Deliverables

- `docs/runbooks/phase-4.md`
- `docs/runbooks/deployment.md`
- `docs/runbooks/recovery.md`
- final operator checklist
- end-to-end verification notes
- final status matrix update

## Manual Inputs Needed Later
- preferred boot-time automation behavior
- whether desktop auto-launch of dashboard/backend is desired
- whether failure notifications should go to Telegram, Gmail, or both by default

## Acceptance Criteria
Phase 4C is acceptable only if:
- all major product surfaces agree on system state
- the scheduler can drive the daily flow
- runtime failures are visible and recoverable
- the operator can use the system without terminal dependence for normal operation
- the system remains faithful to the trust rules from Phases 1 to 3

## Final Exit Rule
Do not call NBA Oracle complete until Phase 4A, 4B, and 4C have all passed their acceptance criteria and the end-to-end loop has been exercised successfully on real data.
