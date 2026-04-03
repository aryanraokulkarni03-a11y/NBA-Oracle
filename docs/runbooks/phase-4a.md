# Phase 4A Runbook

## Purpose
Phase 4A turns NBA Oracle into a real operating backend.

Use this runbook to:
- bootstrap the project-local runtime package cache
- bootstrap auth
- run the API
- run the scheduler once
- send Telegram and Gmail test notifications
- execute the learning review from the backend layer

## One-Time Manual Setup

1. Fill `.env` with:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `ODDS_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `GMAIL_SENDER`
   - `GMAIL_APP_PASSWORD`
   - `GMAIL_RECIPIENT`
2. Apply [phase4a_schema.sql](../../supabase/phase4a_schema.sql) in Supabase SQL Editor.
3. Bootstrap the project-local runtime dependency cache:

```powershell
python main.py bootstrap-runtime
```

4. Bootstrap auth:

```powershell
python main.py bootstrap-auth
```

## Core Commands

Run from the repo root:

```powershell
python -m unittest discover -s tests -p "test_*.py"
python main.py bootstrap-runtime
python main.py run-scheduler-once
python main.py review-learning
python main.py serve-api
```

## Delivery Verification

Telegram:

```powershell
python main.py notify-telegram-test
```

Gmail:

```powershell
python main.py notify-gmail-test
```

## API Verification

Boot the API:

```powershell
python main.py serve-api
```

Then check:
- `GET /api/health`
- `POST /api/auth/login`
- `GET /api/today`
- `GET /api/picks/history`
- `GET /api/stability/latest`
- `GET /api/learning/status`
- `GET /api/providers/health`
- `POST /api/operator/run-live-slate`
- `POST /api/operator/grade-outcomes`
- `POST /api/operator/review-stability`
- `POST /api/operator/run-learning-review`
- `POST /api/operator/run-scheduler-once`

## Scheduler Verification

Run once:

```powershell
python main.py run-scheduler-once
```

Healthy output usually means:
- no crash
- at least a readable decision list
- due jobs execute and record runtime job history

## Runtime Logging And Recovery

Runtime state and recovery artifacts live under:
- `data/runtime_state/`
- `data/auth/`
- `data/learning/`

If a Phase 4A command fails:
1. re-run `python main.py bootstrap-runtime`
2. check `python main.py review-stability`
3. check `python main.py grade-outcomes`
4. restart the API with `python main.py serve-api`

## Startup Guidance

Recommended startup order:

```powershell
python main.py bootstrap-runtime
python main.py bootstrap-auth
python main.py serve-api
```

For operator-only runtime checks without the API:

```powershell
python main.py run-scheduler-once
python main.py review-learning
```

## Learning Verification

Run:

```powershell
python main.py review-learning
```

Outputs:
- `reports/phase4_learning_report.md`
- `reports/phase4_learning_report.json`

## Exit Rule

Do not move to Phase 4B until:
- auth is bootstrapped
- API boots locally
- protected routes work
- scheduler runs safely
- Telegram and Gmail tests both succeed
- Phase 4A schema is applied remotely
