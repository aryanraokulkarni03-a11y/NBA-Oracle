# NBA Oracle Deployment Runbook

## Purpose
Use this runbook to deploy NBA Oracle in the final hosted shape:

- `Vercel` for the dashboard
- `Render` for the FastAPI backend and scheduler cadence
- `Supabase` for persistence

Local startup remains the fallback path for development and emergency recovery.

## Hosted Target

### Dashboard
- Host: `Vercel`
- Working directory: `dashboard/`
- Build command: `npm.cmd run build`
- Output directory: `dist`
- Required frontend env:
  - `VITE_API_BASE_URL=https://your-render-api-host`

### Backend
- Host: `Render`
- Runtime: `Python`
- Build command: `pip install .`
- Start command:

```powershell
python main.py serve-api --host 0.0.0.0 --port $PORT
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
  - `ORACLE_DEPLOYMENT_TARGET=vercel-render-supabase`

### Scheduler
- Host: `Render Cron`
- Command:

```powershell
python main.py run-scheduler-once
```

- Recommended cadence:
  - every `30` minutes

## Repo Artifacts

- Render blueprint: [render.yaml](/C:/Users/HP/OneDrive/Documents/NBA/render.yaml)
- Vercel SPA rewrite config: [vercel.json](/C:/Users/HP/OneDrive/Documents/NBA/dashboard/vercel.json)
- Frontend env template: [dashboard/.env.example](/C:/Users/HP/OneDrive/Documents/NBA/dashboard/.env.example)

## Local Fallback Startup

From the repo root:

```powershell
python main.py bootstrap-runtime
python main.py startup-sanity
python main.py serve-api
```

From `dashboard/`:

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

## Post-Deploy Checks

1. Confirm backend health:
   - `GET /api/health`
2. Confirm login works:
   - `POST /api/auth/login`
3. Confirm dashboard loads and can reach the hosted backend.
4. Confirm one operator action completes and the dashboard refreshes.
5. Confirm:
   - Telegram test delivery
   - Gmail test delivery
6. Confirm the next scheduler cadence records a runtime job.

## Local Auto-Start Fallback

Recommended local fallback policy:
- backend auto-start on `login`
- dashboard stays `manual`

If hosted deployment is unavailable, use Windows Task Scheduler to run:

```powershell
cd C:\Users\HP\OneDrive\Documents\NBA
python main.py serve-api
```

and keep the dashboard manual:

```powershell
cd C:\Users\HP\OneDrive\Documents\NBA\dashboard
npm.cmd run dev
```
