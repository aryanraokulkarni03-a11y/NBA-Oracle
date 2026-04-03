# NBA Oracle Phase 4 Restructure

## Purpose
Phase 4 is being split into three execution parts so the project can finish cleanly:
- backend and operating core first
- frontend and user interaction second
- full integration and hardening third

This is the right structure because the frontend should not guess at contracts that the runtime, auth, delivery, and learning layers have not finalized yet.

## Why The Split Is Better

### 1. Backend-first reduces rework
If the dashboard is built before the API, runtime, auth, and delivery contracts are stable, the UI will need unnecessary rewrites later.

### 2. Frontend becomes cleaner
Once the API and operator flows are real, the dashboard can be built against truth instead of assumptions.

### 3. Integration deserves its own pass
The final bugs in a system like this usually live in the seams:
- scheduler to prediction
- prediction to storage
- storage to UI
- UI to operator actions
- delivery to grading
- grading to stability
- stability to learning

That wiring work is important enough to be its own phase.

## Phase 4 Structure

### Phase 4A: Operating Core
This is the non-frontend product shell.

It includes:
- FastAPI app and route contract
- auth and security
- scheduler/meta-scheduler runtime
- Telegram delivery
- Gmail notifications
- learning engine execution path
- operator commands and health/status APIs
- backend deployment/startup hardening

Primary plan:
- [phase-4a.md](./phase-4a.md)

### Phase 4B: Dashboard and User Interaction
This is the full authenticated frontend and user-facing control surface.

It includes:
- React/Vite dashboard
- login flow
- today/performance/learning/trends pages
- operator interaction flows
- frontend integration with the Phase 4A APIs

Primary plan:
- [phase-4b.md](./phase-4b.md)

### Phase 4C: Final Wiring and Production Hardening
This is the end-to-end integration and closeout pass.

It includes:
- full API/UI/runtime/delivery integration
- run-state truthfulness across every surface
- deployment hardening
- failure recovery
- final runbooks and operator workflow verification
- complete-system acceptance testing

Primary plan:
- [phase-4c.md](./phase-4c.md)

## Recommended Execution Order

1. **Phase 4A first**
   Build the operating core and lock the API/runtime contracts.

2. **Phase 4B second**
   Build the dashboard on top of those contracts.

3. **Phase 4C last**
   Wire everything together and harden the full system.

## Shared Rules Across 4A, 4B, and 4C

1. Keep the predictor as the final betting authority.
2. Never let UI or delivery bypass the trust gates from Phases 1 to 3.
3. Keep `SKIP`, degraded providers, and warnings visible everywhere.
4. Preserve auditability in local and Supabase-backed records.
5. Keep the system manual-bet only.

## Final Exit Rule
Do not call the project complete until all three are true:
- Phase 4A is working end to end
- Phase 4B is usable and truthful
- Phase 4C proves the entire operating loop is stable under real use
