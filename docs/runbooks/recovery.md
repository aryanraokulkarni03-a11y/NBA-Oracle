# NBA Oracle Recovery Runbook

## Purpose
Use this runbook when the product is up but one part of the operating loop is no longer truthful or healthy.

The recovery order is:

1. confirm health
2. isolate the failing surface
3. use the smallest safe fallback
4. re-run the affected job
5. confirm the dashboard, API, and delivery surfaces agree again

## Health First

Run from the repo root:

```powershell
python main.py startup-sanity
python main.py run-scheduler-once
python main.py serve-api
```

Then check:
- `GET /api/health`
- dashboard Overview
- latest runtime job history

## Provider Failure

Symptoms:
- provider degraded or failed in `/api/providers/health`
- live slate has weak or empty input

Recovery:
1. Run:

```powershell
python main.py build-live-slate --live
```

2. If live inputs are still unstable, use bundle fallback:

```powershell
python main.py build-live-slate
```

3. Confirm provider truth stays visible in:
- dashboard Providers
- dashboard Overview
- Telegram/Gmail digests if sent

## Supabase Failure

Symptoms:
- writes missing remotely
- health looks fine locally but remote history is stale

Recovery:
1. Confirm:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
2. Re-run:

```powershell
python main.py startup-sanity
python main.py build-live-slate --live
python main.py grade-outcomes
python main.py review-stability --force-refresh-baseline
```

3. If remote still fails, continue local operation and keep the failure visible until the remote path is restored.

## Delivery Failure

Symptoms:
- Telegram or Gmail test fails
- notification event history shows failed deliveries

Recovery:
1. Run:

```powershell
python main.py notify-telegram-test
python main.py notify-gmail-test
```

2. If Telegram fails:
   - confirm bot token
   - confirm chat id
3. If Gmail fails:
   - confirm sender
   - confirm app password
   - confirm recipient
4. Keep `telegram-primary` as the default failure policy and use Gmail as the backup/history channel.

## Auth or Session Failure

Symptoms:
- login fails
- protected routes return `401`
- dashboard drops back to login

Recovery:
1. Re-bootstrap auth if needed:

```powershell
python main.py bootstrap-auth
```

2. Restart the API:

```powershell
python main.py serve-api
```

3. Log in again from the dashboard.

## Dashboard/API Connectivity Failure

Symptoms:
- dashboard loads but data panels fail
- Vercel frontend cannot reach hosted backend

Recovery:
1. Confirm backend health at `/api/health`
2. Confirm CORS origins are correct in `ORACLE_ALLOWED_ORIGINS`
3. Confirm frontend API target:
   - `VITE_API_BASE_URL` on hosted frontend
4. Rebuild the dashboard if needed:

```powershell
cd C:\Users\HP\OneDrive\Documents\NBA\dashboard
npm.cmd run build
```

## Runtime Loop Recovery

Use this order if the operating loop has drifted:

```powershell
python main.py build-live-slate --live
python main.py grade-outcomes
python main.py review-stability --force-refresh-baseline
python main.py review-learning
python main.py run-scheduler-once
```

Then confirm:
- dashboard Overview
- dashboard Providers
- dashboard Stability
- dashboard Learning
- `/api/health`

## Fallback Truth Rule

If hosted deployment is unavailable:
- keep using the local backend
- keep using the local dashboard manually
- do not hide degraded or fallback state
- do not call the system healthy again until the same truth is visible in API, UI, and delivery
