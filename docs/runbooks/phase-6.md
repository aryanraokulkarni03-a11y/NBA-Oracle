# NBA Oracle Phase 6 Runbook

## Purpose
Use this runbook to operate NBA Oracle after the Phase 6 convenience and automation layer landed.

Phase 6 is about four practical things:
- making the free daily workflow easy to start and keep stable
- keeping the scheduler recurring without typing commands each time
- making the daily operator workflow obvious
- keeping the evidence loop trustworthy after games finish

## Recommended Daily Mode

The recommended free daily operating mode is:
- local backend
- local dashboard
- recurring scheduler task in the background

Use this as the default daily path:
- backend API on `http://127.0.0.1:8000`
- dashboard UI on `http://localhost:3000`

Use hosted access only when you specifically want remote browser access.

Why:
- the local dashboard is stable and fully free
- quick `trycloudflare.com` tunnels can rotate and break the hosted Vercel path until env values are updated

## One-Time Setup

### 1. Register the recurring scheduler task
Run from the repo root:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\register_nba_oracle_scheduler.ps1 -IntervalMinutes 30
```

Then verify:

```powershell
schtasks /Query /TN "NBA Oracle Scheduler" /V /FO LIST
```

This task runs:

```powershell
python main.py run-scheduler-once
```

through the wrapper script:
- [run_nba_oracle_scheduler.ps1](/C:/Users/HP/OneDrive/Documents/NBA/scripts/run_nba_oracle_scheduler.ps1)

### 2. Confirm startup sanity
Run:

```powershell
python main.py startup-sanity
```

The Phase 6-specific checks should become healthy for:
- hosted launcher
- scheduler runner script
- scheduler task

## Local Dashboard Startup

Normal free daily usage starts with two local terminals.

### Terminal 1: backend

```powershell
cd C:\Users\HP\OneDrive\Documents\NBA
python main.py serve-api
```

### Terminal 2: dashboard

```powershell
cd C:\Users\HP\OneDrive\Documents\NBA\dashboard
npm.cmd run dev
```

Then open:
- `http://localhost:3000`

This path does not need:
- Cloudflare Tunnel
- Vercel env changes

## Hosted Startup

Hosted usage now starts from:
- [start_hosted_stack.bat](/C:/Users/HP/OneDrive/Documents/NBA/start_hosted_stack.bat)

You can:
- double-click it in Explorer
- or run it from PowerShell:

```powershell
.\start_hosted_stack.bat
```

What it does:
- opens one visible PowerShell terminal for the backend
- opens one visible PowerShell terminal for the Cloudflare tunnel

What it does not do:
- it does not open the dashboard browser for you
- it does not replace the scheduler task

After it starts, use the hosted dashboard:
- [nba-oracle-lilac.vercel.app](https://nba-oracle-lilac.vercel.app)

Important:
- this hosted path is optional
- quick tunnel URLs can rotate
- if the tunnel URL changes, the hosted Vercel env must be updated before the browser path works again

## Daily Operator Workflow

### If you want the local dashboard
1. Run the backend terminal.
2. Run the dashboard terminal.
3. Open `http://localhost:3000`.

This is the preferred free daily path.

### If you want the hosted dashboard live
1. Run:

```powershell
.\start_hosted_stack.bat
```

2. Open the hosted dashboard.

This requires:
- backend terminal alive
- tunnel terminal alive
- Vercel pointing at the current tunnel URL

### If you only want the system collecting and reviewing data
You do not need the hosted dashboard open.

The scheduler task is the important part.

As long as the machine is on and the task is registered, the recurring scheduler can:
- collect due live runs
- grade finished outcomes
- trigger stability review follow-up
- trigger learning review follow-up when eligible

### On slate days
- keep the scheduler task active
- optionally run `python main.py build-live-slate --live` manually if you want an immediate pregame refresh outside the normal scheduler cadence

### After games finish
Preferred path:

```powershell
python main.py run-scheduler-once
```

Focused fallback path:

```powershell
python main.py grade-outcomes
```

Use the focused grading path when:
- you want to check outcome ingestion immediately
- you want to debug grading specifically
- you do not need the whole scheduler decision pass

## Runtime Truth Rules

Keep these distinctions clear:

- dashboard open != backend running
- backend running != tunnel available
- tunnel available != scheduler recurring
- predictions stored != outcomes graded

The system is only fully operating when:
- backend is available for the dashboard mode you are using
- the scheduler task is recurring
- the evidence loop is successfully grading outcomes after games finish

## Logs and Verification

Scheduled task output is written to:
- [phase6_scheduler_task.log](/C:/Users/HP/OneDrive/Documents/NBA/data/runtime_state/phase6_scheduler_task.log)

Useful checks:

```powershell
python main.py startup-sanity
python main.py run-scheduler-once
python main.py grade-outcomes
```

Useful task check:

```powershell
schtasks /Query /TN "NBA Oracle Scheduler" /V /FO LIST
```

## Recovery Shortcuts

### Hosted dashboard cannot load data
1. restart:
   - backend terminal
   - tunnel terminal
2. confirm:
   - `python main.py startup-sanity`
   - `GET /api/health`
3. if the tunnel URL changed:
   - update the hosted API base env
   - redeploy the hosted frontend

### Local dashboard cannot load data
1. confirm backend is running on `http://127.0.0.1:8000`
2. confirm the dashboard dev server is running on `http://localhost:3000`
3. run:

```powershell
python main.py startup-sanity
```

### Scheduler seems idle
1. verify the task exists:

```powershell
schtasks /Query /TN "NBA Oracle Scheduler" /V /FO LIST
```

2. inspect:
- [phase6_scheduler_task.log](/C:/Users/HP/OneDrive/Documents/NBA/data/runtime_state/phase6_scheduler_task.log)

3. run the bridge manually once:

```powershell
python main.py run-scheduler-once
```

### Outcome grading looks wrong
1. run:

```powershell
python main.py grade-outcomes
```

2. confirm:
- `Pending unfinished`
- `Missing official outcomes`

The grading path now:
- retries slow official fetches
- falls back safely
- ignores synthetic runtime artifacts in live summaries
