# NBA Oracle Phase 4B Runbook

## Purpose
Use this runbook to start, verify, and rebuild the Phase 4B dashboard against the real Phase 4A backend.

## Prerequisites
- Phase 4A backend is configured
- auth has been bootstrapped
- backend can run through `python main.py serve-api`
- dashboard dependencies are installed in `dashboard/`

## First-Time Setup

From:

`C:\Users\HP\OneDrive\Documents\NBA\dashboard`

Run:

```powershell
npm.cmd install
```

## Start The Backend

From:

`C:\Users\HP\OneDrive\Documents\NBA`

Run:

```powershell
python main.py serve-api
```

The API should be available at:

- `http://127.0.0.1:8000`

## Start The Dashboard

Open a second terminal.

From:

`C:\Users\HP\OneDrive\Documents\NBA\dashboard`

Run:

```powershell
npm.cmd run dev
```

The dashboard should be available at:

- `http://127.0.0.1:3000`

Vite proxies `/api/*` requests to the backend running on `127.0.0.1:8000`.

## Build Verification

From:

`C:\Users\HP\OneDrive\Documents\NBA\dashboard`

Run:

```powershell
npm.cmd run build
```

Expected result:
- production build completes successfully
- output is written to `dashboard/dist/`

## Manual Verification Checklist

1. Open the dashboard in the browser.
2. Log in with the dashboard password created during Phase 4A auth bootstrap.
3. Confirm the top navigation renders:
   - Overview
   - Today
   - Performance
   - Stability
   - Learning
   - Providers
   - Operations
4. Confirm `/today` renders the current live run truthfully, including `SKIP`.
5. Confirm `/providers` shows degraded and failed sources when present.
6. Confirm `/stability` shows `insufficient_data` honestly when evidence is immature.
7. Confirm `/learning` shows `candidate_model_version = none` honestly when no candidate exists.
8. Confirm `/operations` actions require explicit confirmation before running.
9. Trigger one safe operator action and confirm the returned payload appears in the UI.

## Expected Truth Rules
- `SKIP` is visible
- degraded providers are visible
- fallback usage is visible through provider error/status fields
- insufficient data is not treated as failure
- the UI does not read local files directly

## Recovery

If the dashboard cannot reach the backend:
1. make sure `python main.py serve-api` is running
2. confirm `http://127.0.0.1:8000/api/health` responds
3. restart `npm.cmd run dev`

If the dashboard build fails:
1. rerun `npm.cmd install`
2. rerun `npm.cmd run build`
3. fix any TypeScript or API-shape mismatch before continuing
