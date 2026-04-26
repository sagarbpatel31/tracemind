# Next Steps

Priority order is fixed. Do not skip or reorder.

---

## 🔴 Priority 1 — End-to-end production deploy

Nothing else matters until the app works for real users. All code is ready.

### Step A: Provision Supabase (user action, ~5 min)
1. https://supabase.com → sign up → New project
2. Name: `tracemind`, region: **US East (N. Virginia)**, strong password
3. Settings → Database → Connection string → URI tab
4. Copy URI: `postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres`
5. Paste to Claude — `config.py` normalizes automatically

### Step B: Deploy API to Render (user action, ~5 min)
1. https://render.com → sign up → New → Blueprint
2. Connect `sagarbpatel31/tracemind` — Render auto-detects `apps/api/render.yaml`
3. Set env vars: `DATABASE_URL` (Supabase URI), optionally `ANTHROPIC_API_KEY`
4. Click Apply → wait for build (~3–5 min)
5. Copy deploy URL: `https://tracemind-api.onrender.com`

### Step C: Wire Vercel + seed + smoke test (Claude handles after URLs provided)
```bash
# Set API URL in Vercel
cd apps/web
vercel env add NEXT_PUBLIC_API_URL production  # value: https://tracemind-api.onrender.com
vercel --prod

# Seed production DB
curl -X POST https://tracemind-api.onrender.com/api/v1/seed/demo

# Smoke test
curl https://tracemind-api.onrender.com/api/v1/health
# → open https://tracemind.vercel.app → login demo@tracemind.ai / demo123
```

**Blocker:** Steps A and B require user signups. Everything after is automated.

---

## 🟠 Priority 2 — Alembic migrations

**Do this before any schema change on a populated production DB.**

`apps/api/alembic/` exists but `versions/` is empty — there are no migration files.
Currently `create_all` on startup is the only mechanism. Safe once, breaks on any column change.

```bash
cd apps/api
pip install alembic  # already in pyproject.toml if present
alembic revision --autogenerate -m "initial schema from models"
alembic upgrade head
```

**Files to touch:** `apps/api/alembic/env.py` (wire async engine), `apps/api/alembic/versions/` (generated).
No model changes required. Run immediately after first successful production deploy.

---

## 🟠 Priority 3 — Secure ingest endpoints

**File:** `apps/api/app/routers/ingest.py`

Current state: `/ingest/logs`, `/ingest/metrics`, `/ingest/events` are unauthenticated.
Any caller with a device_id UUID can inject telemetry data.

Minimal fix: add a device API token (UUID generated at registration, stored hashed, sent in `X-Device-Token` header).

Do not use JWT for agents — token management on embedded devices is fragile.
Keep the change backward-compatible with existing agents by checking for token presence first.

---

## 🟡 Priority 4 — Real edge agent metrics

**File:** `agents/edge-agent/internal/collector/system.go`

Current state: CPU, disk, and network metrics are simulated stubs. Only memory is real.
Comment in code: *"A production implementation would read from /proc (Linux) or use platform-specific syscalls."*

Options:
- Add `github.com/shirou/gopsutil/v3` — cross-platform, reads `/proc` on Linux, works on Jetson
- Or implement `/proc/stat` reads directly for zero-dependency

Also: make `project_id` a CLI flag instead of hard-coded `11111111-...` in `sender/http.go`.

**Important:** Do not deploy to real Jetson hardware until this is done — simulated values will trigger false analysis matches.

---

## 🟡 Priority 5 — Auth/token storage improvements

**File:** `apps/web/src/lib/auth.ts`

Current state: JWT stored in `localStorage` — extractable by any XSS payload.

Fix: Switch to `httpOnly; Secure; SameSite=Strict` cookies.
Requires: Next.js API route as token relay (client → Next.js server → FastAPI), or middleware-based cookie handling.

This is a meaningful security improvement but low urgency for an MVP with no sensitive customer data.
Do not do this before Priority 1–4 are complete.

---

## Backlog (no priority yet)

- Populate `ros2_snapshot.json` in replay bundle (currently placeholder)
- `packages/shared-types/` alignment with frontend types
- Incident auto-trigger from agent anomaly detection
- Multi-workspace user scoping
- Alert notifications on critical incidents
- Cross-compile Go agent for `linux/arm64` (Jetson)
- Incident timeline auto-grouping by time window
