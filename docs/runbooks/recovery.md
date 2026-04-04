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
- `schtasks /Query /TN "NBA Oracle Scheduler" /V /FO LIST`
- [phase6_scheduler_task.log](/C:/Users/HP/OneDrive/Documents/NBA/data/runtime_state/phase6_scheduler_task.log)

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
- Vercel frontend cannot reach the tunneled backend

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

4. If hosted startup was interrupted, relaunch:

```powershell
cd C:\Users\HP\OneDrive\Documents\NBA
.\start_hosted_stack.bat
```

## Scheduler Automation Failure

Symptoms:
- new runtime jobs stop appearing
- postgame grading does not happen unless you run commands manually
- scheduler task history looks stale

Recovery:
1. Verify the task exists:

```powershell
schtasks /Query /TN "NBA Oracle Scheduler" /V /FO LIST
```

2. If missing, re-register it:

```powershell
cd C:\Users\HP\OneDrive\Documents\NBA
powershell.exe -ExecutionPolicy Bypass -File .\scripts\register_nba_oracle_scheduler.ps1 -IntervalMinutes 30
```

3. Inspect:
- [phase6_scheduler_task.log](/C:/Users/HP/OneDrive/Documents/NBA/data/runtime_state/phase6_scheduler_task.log)

4. Run the bridge manually once:

```powershell
python main.py run-scheduler-once
```

## Outcome Grading Failure

Symptoms:
- finished games remain ungraded
- `Missing official outcomes` is non-zero
- stability or learning stays stale because grading did not land

Recovery:
1. Run:

```powershell
python main.py grade-outcomes
```

2. If needed, follow with:

```powershell
python main.py review-stability
python main.py review-learning
```

3. Remember:
- the grading path now retries slow official fetches
- it falls back safely when the primary endpoint stalls
- it ignores synthetic runtime artifacts in live summaries

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

If Cloudflare Tunnel or hosted frontend access is unavailable:
- keep using the local backend
- keep using the local dashboard manually
- do not hide degraded or fallback state
- do not call the system healthy again until the same truth is visible in API, UI, and delivery
