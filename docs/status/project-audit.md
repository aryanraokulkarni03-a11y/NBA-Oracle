# NBA Oracle Project Audit

## Audit Date
2026-04-05

## Purpose
This file is the one-shot audit summary for the current NBA Oracle build.

It answers:
- what is actually complete now
- what remains intentionally deferred or out of scope
- what operational assumptions are still true
- which commits materially shaped the current product

## Executive Verdict
NBA Oracle is complete for the currently planned scope through Phase 7B.

The project has moved from:
- replay-only validation

to:
- live provider ingestion
- persistent storage
- outcome grading
- stability and learning reviews
- operator backend and dashboard
- recurring scheduler automation
- forecast visibility
- upgraded intelligence logic

The current system is a real pregame NBA moneyline decision tool with auditability and evidence accumulation.

It is not:
- a live in-game betting engine
- an auto-betting product
- a fully cloud-hosted always-on service

## Complete Work

### Phase 1
- deterministic replay engine
- snapshot validation
- `BET` / `LEAN` / `SKIP` gating
- calibration and audit reporting

### Phase 2
- real schedule, odds, injuries, and stats providers
- live slate assembly
- no-slate-day handling
- dual local-plus-Supabase persistence
- official schedule fallback from odds

### Phase 3
- baseline-backed stability reviews
- outcome grading from official results
- market-readiness and containment logic
- learning-review evidence path

### Phase 4
- FastAPI operator backend
- auth and protected routes
- dashboard routes and action flows
- Vercel frontend path
- startup sanity and recovery/deployment runbooks

### Phase 5
- plain-language explanations
- guide page
- operator-facing copy and metric interpretation

### Phase 6
- local-first daily workflow
- Windows scheduler automation
- hosted launcher helpers
- grading reliability hardening

### Phase 7A
- actionable Today page
- next-up forecast visibility
- predicted-vs-actual truth in Performance

### Phase 7B
- market-aware prior blending
- richer injury and team-strength features
- timing-aware and uncertainty-aware gating
- segmented learning/reporting behavior

## Intentionally Deferred Or Out Of Scope
- live in-game betting
- autonomous bet placement
- direct Stake integration
- real live Reddit sentiment in production mode
- analyst-only LLM layer
- totals and props modeling

These are not hidden failures. They are explicit scope boundaries.

## Operational Truth
- the recommended free daily workflow is local:
  - backend on `http://127.0.0.1:8000`
  - dashboard on `http://localhost:3000`
  - recurring scheduler task in the background
- Vercel plus quick Cloudflare Tunnel is still optional hosted access only
- quick `trycloudflare.com` tunnels remain brittle because the URL can rotate
- grading, stability, and learning are real, but still depend on evidence accumulation over time

## Remaining Real Risks
1. Hosted access is still operationally weaker than local-first use unless a stable named tunnel or hosted backend exists.
2. Stability and learning honesty still often read as `insufficient_data` until a larger graded sample accumulates.
3. Sentiment and analyst layers remain absent, so the system relies on the structured provider stack only.
4. The intelligence layer is much better after 7B, but long-run edge still depends on real graded history, not just better theory.

## Most Important Commits
- `10df156` `feat: execute phase 4c integration hardening`
- `1b80789` `feat: implement phase 5 clarity layer`
- `466fb6a` `feat: finish phase 5 dashboard polish`
- `bac80b2` `feat: implement phase 6 operations automation`
- `23b60bc` `feat: implement phase 7a forecast visibility`
- `34c2fc2` `feat: implement phase 7b intelligence upgrade`

These are the commits that most clearly turned the repo into the current operator-grade product.

## Recommended Next Direction
No mandatory remediation phase is open right now.

The next work should be a deliberate expansion, not a rescue pass.

Best candidates:
1. persistent hosted access without quick-tunnel fragility
2. real sentiment integration
3. analyst/explanation layer
4. richer postgame performance analytics
5. any future Phase 8 only if it materially improves operator outcomes
