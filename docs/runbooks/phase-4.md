# NBA Oracle Phase 4 Closeout Runbook

## Purpose
Use this runbook to verify the finished product loop across:

- backend runtime
- dashboard
- delivery
- grading
- stability
- learning
- hosted deployment shape

## Final Verification Order

From the repo root:

```powershell
python -m unittest discover -s tests -p "test_*.py"
python main.py bootstrap-runtime
python main.py startup-sanity
python main.py build-live-slate --live
python main.py grade-outcomes
python main.py review-stability --force-refresh-baseline
python main.py review-learning
python main.py run-scheduler-once
python main.py notify-telegram-test
python main.py notify-gmail-test
```

## API Verification

Run:

```powershell
python main.py serve-api
```

Then verify:
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

## Dashboard Verification

From `dashboard/`:

```powershell
npm.cmd run build
npm.cmd run dev
```

Verify in the browser:
1. Login works
2. Overview reflects:
   - deployment target
   - startup status
   - latest notifications
3. Providers reflects degraded and failed sources honestly
4. Stability reflects insufficient data honestly
5. Learning reflects candidate-only review honestly
6. Operator actions refresh other pages without stale state
7. `429` and `401` states are understandable

## Hosted Verification

Deployment target:
- `Vercel` for frontend
- `Cloudflare Tunnel` for public access to the local backend/runtime
- `Supabase` for persistence

Verify:
1. hosted frontend loads
2. hosted frontend can reach the tunneled backend
3. backend health is live
4. one operator action works from the hosted UI
5. scheduler cadence records a runtime job
6. Telegram and Gmail tests still succeed

## Exit Rule

Do not call the product complete unless:
- startup sanity is at least warning-only
- dashboard and API agree on state
- delivery history matches runtime truth
- hosted deployment is documented and verifiable
- recovery steps are written and usable
