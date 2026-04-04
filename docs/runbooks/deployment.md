# NBA Oracle Deployment Runbook

## Purpose
Use this runbook to deploy NBA Oracle in the final no-billing hosted shape:

- `Vercel` for the dashboard
- `Cloudflare Tunnel` for public access to the local FastAPI backend
- local backend/runtime on your machine
- `Supabase` for persistence

Local startup remains the real runtime path. Cloudflare Tunnel exposes it publicly so the hosted dashboard can reach it.

## Hosted Target

### Dashboard
- Host: `Vercel`
- Working directory: `dashboard/`
- Build command: `npm.cmd run build`
- Output directory: `dist`
- Required frontend env:
  - `VITE_API_BASE_URL=https://your-cloudflare-tunnel-host`

### Backend
- Host: local machine
- Runtime: `Python`
- Start command:

```powershell
python main.py serve-api --host 127.0.0.1 --port 8000
```

- Required backend env:
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `ODDS_API_KEY`
  - `ORACLE_PASSWORD_HASH`
  - `ORACLE_SECRET_KEY`
  - `TELEGRAM_BOT_TOKEN`
  - `TELEGRAM_CHAT_ID`
  - `GMAIL_SENDER`
  - `GMAIL_APP_PASSWORD`
  - `GMAIL_RECIPIENT`
  - `ORACLE_ALLOWED_ORIGINS`
  - `ORACLE_PUBLIC_API_BASE_URL`
  - `ORACLE_DEPLOYMENT_TARGET=vercel-cloudflare-supabase`

### Public Tunnel
- Host: `Cloudflare Tunnel`
- Purpose: expose the local backend to the public Vercel dashboard over HTTPS

## Repo Artifacts

- Vercel SPA rewrite config: [vercel.json](/C:/Users/HP/OneDrive/Documents/NBA/dashboard/vercel.json)
- Frontend env template: [dashboard/.env.example](/C:/Users/HP/OneDrive/Documents/NBA/dashboard/.env.example)

## Local Runtime Startup

From the repo root:

```powershell
python main.py bootstrap-runtime
python main.py startup-sanity
python main.py serve-api
```

Phase 6 hosted launcher:

```powershell
.\start_hosted_stack.bat
```

This opens:
- one API terminal
- one Cloudflare tunnel terminal

Phase 6 recurring scheduler setup:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\register_nba_oracle_scheduler.ps1 -IntervalMinutes 30
```

From `dashboard/` for local fallback UI:

```powershell
npm.cmd install
npm.cmd run dev
```

## Pre-Deploy Checklist

1. Apply:
   - [phase2_schema.sql](/C:/Users/HP/OneDrive/Documents/NBA/supabase/phase2_schema.sql)
   - [phase3_schema.sql](/C:/Users/HP/OneDrive/Documents/NBA/supabase/phase3_schema.sql)
   - [phase3_2_schema.sql](/C:/Users/HP/OneDrive/Documents/NBA/supabase/phase3_2_schema.sql)
   - [phase4a_schema.sql](/C:/Users/HP/OneDrive/Documents/NBA/supabase/phase4a_schema.sql)
2. Run:

```powershell
python -m unittest discover -s tests -p "test_*.py"
python main.py startup-sanity
python main.py build-live-slate
python main.py review-stability --force-refresh-baseline
python main.py review-learning
cd dashboard
npm.cmd run build
```

## Cloudflare Tunnel Shape

Target backend:
- `http://127.0.0.1:8000`

After the tunnel is created, use its public HTTPS hostname for:
- `ORACLE_PUBLIC_API_BASE_URL`
- `ORACLE_ALLOWED_ORIGINS`
- Vercel `VITE_API_BASE_URL`

## Post-Deploy Checks

1. Confirm local backend health:
   - `GET /api/health`
2. Confirm Cloudflare Tunnel reaches the backend.
3. Confirm dashboard loads from Vercel and can reach the tunneled backend.
4. Confirm login works.
5. Confirm one operator action completes and the dashboard refreshes.
6. Confirm:
   - Telegram test delivery
   - Gmail test delivery
7. Confirm the next scheduler cadence records a runtime job.
8. Confirm the Phase 6 scheduler log updates:
   - [phase6_scheduler_task.log](/C:/Users/HP/OneDrive/Documents/NBA/data/runtime_state/phase6_scheduler_task.log)

## Local Auto-Start Fallback

Recommended local fallback policy:
- backend auto-start on `login`
- dashboard stays `manual`

If the tunnel is down, keep using:

```powershell
cd C:\Users\HP\OneDrive\Documents\NBA
python main.py serve-api
```

and use the dashboard locally:

```powershell
cd C:\Users\HP\OneDrive\Documents\NBA\dashboard
npm.cmd run dev
```

## Phase 6 Daily Ops Note

Once the scheduler task is registered:
- data collection and review can continue even if the hosted dashboard is not open
- the hosted dashboard still requires the backend and tunnel when you want browser access
