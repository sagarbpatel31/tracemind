# Current Task

Last updated: 2026-05-31.

## Active branch

Current checkout is `main`.

This repo is no longer just the original MVP. The codebase now includes:
- Core incident intelligence backend + frontend
- AI-layer ingest/query endpoints and rules
- A Python `model-collector` package
- Alembic migration files `0001_initial` and `0002_ai_layer`

---

## Current product state

### ✅ Implemented in source

| Feature | Status | Files |
|---------|--------|-------|
| FastAPI backend — auth, devices, incidents, ingest, projects, seed | Implemented | `apps/api/app/routers/` |
| 7 classic incident-analysis rules + optional Haiku summary | Implemented | `apps/api/app/services/analysis.py` |
| Replay bundle ZIP export | Implemented | `apps/api/app/services/replay_bundle.py` |
| Next.js dashboard, login, device, incident, inference views | Implemented | `apps/web/src/app/` |
| AI-layer data model (model runs, inferences, decisions, OOD signals) | Implemented | `apps/api/app/models/ai_layer.py` |
| AI-layer ingest/query endpoints | Implemented | `apps/api/app/routers/ai_ingest.py` |
| AI-layer RCA rules AI-001, AI-002, AI-003 | Implemented | `apps/api/app/rca/ai_rules/` |
| Demo seed data including AI-layer frames | Implemented | `apps/api/app/routers/seed.py` |
| Go edge agent | Implemented, still partly stubbed | `agents/edge-agent/` |
| ROS2 collector | Implemented | `agents/ros2-collector/` |
| Python model-collector package + tests | Implemented | `agents/model-collector/` |
| Alembic setup + migration files | Implemented | `apps/api/alembic/versions/` |
| Render deployment config | Implemented | `apps/api/render.yaml` |

### ✅ Verified during this review

| Check | Result |
|------|--------|
| Frontend lint | Passed via `npm run lint` in `apps/web` |
| API tests exist | Present in `apps/api/tests/` |
| Model-collector tests exist | Present in `agents/model-collector/tests/` |

### ⚠️ Verification gaps found during this review

| Gap | Detail |
|-----|--------|
| Python test envs are stale | Checked-in `.venv` entrypoints still point at the old repo path `.../Documents/Tracemind/...` |
| Offline dependency resolution | Fresh `uv` runs cannot refill missing deps without network access |
| Production deploy not proven | No confirmed live Render API URL or wired Vercel production API base in this review |

---

## Production blocker audit

Priority order remains deployment first, then security/hardening.

### 🔴 P1 — End-to-end production deploy

**Status:** Still blocked on platform provisioning / final wiring, not on missing product code.

Blocking items:
- Supabase project + production `DATABASE_URL` not confirmed in repo/docs
- Render API deployment not confirmed live from this review
- Vercel `NEXT_PUBLIC_API_URL` wiring to production API not confirmed
- `apps/api/render.yaml` currently sets `CORS_ORIGINS` for `https://watchpoint-gray.vercel.app`, so the final production frontend domain must be confirmed and aligned
- Production seed + smoke test not confirmed

### 🟠 P2 — Migration discipline

**Status:** Partially complete.

What is true now:
- Alembic is initialized
- Migration files already exist: `0001_initial`, `0002_ai_layer`

What is still incomplete:
- Runtime still uses `Base.metadata.create_all()` on startup in `apps/api/app/main.py`
- Production process is not yet clearly documented as migration-first

### 🟠 P3 — Secure ingest endpoints

**Status:** Not started in code.

Current blocker:
- `/api/v1/ingest/logs`, `/metrics`, `/events` are still unauthenticated in `apps/api/app/routers/ingest.py`
- AI ingest endpoints in `apps/api/app/routers/ai_ingest.py` are also unauthenticated

### 🟡 P4 — Real edge telemetry

**Status:** Not started in code.

Current blocker:
- `agents/edge-agent/internal/collector/system.go` still simulates CPU/disk/network
- `agents/edge-agent/internal/sender/http.go` still hard-codes demo `project_id`

### 🟡 P5 — Web auth hardening

**Status:** Not started in code.

Current blocker:
- JWT remains in `localStorage` in `apps/web/src/lib/auth.ts`

---

## Known code issues still open

| Issue | Location | Impact |
|-------|----------|--------|
| Runtime still does `create_all` | `apps/api/app/main.py` | Easy to drift from migration-first production discipline |
| Ingest endpoints unauthenticated | `apps/api/app/routers/ingest.py`, `apps/api/app/routers/ai_ingest.py` | Telemetry injection risk |
| Edge agent collector stubs | `agents/edge-agent/internal/collector/system.go` | False positives on real hardware |
| Hard-coded demo project ID | `agents/edge-agent/internal/sender/http.go` | Real deployments all map to seed project |
| `ros2_snapshot.json` placeholder | `apps/api/app/services/replay_bundle.py` | Replay bundle incomplete |
| JWT in `localStorage` | `apps/web/src/lib/auth.ts` | XSS-extractable token |
| Checked-in `.venv` shebangs still reference `Tracemind` path | `apps/api/.venv/`, `agents/model-collector/.venv/` | Local test tooling breaks after repo rename |
