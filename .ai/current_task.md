# Current Task

## Active branch: `add-ai-engineering-system`

Rebuilding the `.ai/` context layer from a verified codebase inspection.
**No production source code is modified on this branch.**

---

## Immediate next action (after this branch merges)

**Priority 1: Production deploy** — user must sign up for Supabase and Render, then paste two URLs.
See `.ai/next_steps.md` for the exact steps. All code is ready; this is purely a platform provisioning task.

---

## Build status

### ✅ Complete and working

| Feature | Files |
|---------|-------|
| FastAPI backend — 7 routers, 9 models | `apps/api/app/` |
| JWT auth (register, login, /me) | `app/routers/auth.py`, `app/security.py` |
| Incident CRUD + analysis (7 rules) | `app/routers/incidents.py`, `app/services/analysis.py` |
| Claude Haiku LLM summarization | `app/services/analysis.py:generate_llm_summary()` |
| Replay bundle (ZIP export) | `app/services/replay_bundle.py` |
| Device registration + heartbeat + deployments | `app/routers/devices.py` |
| Telemetry ingest (logs/metrics/events) | `app/routers/ingest.py` |
| Seed endpoint + demo data | `app/routers/seed.py` |
| Go edge agent (collector stubs) | `agents/edge-agent/` |
| Python ROS2 collector (simulation mode) | `agents/ros2-collector/` |
| Next.js frontend (dashboard, incidents, login) | `apps/web/src/` |
| Docker Compose local dev stack | `deploy/docker-compose/` |
| Render IaC | `apps/api/render.yaml` |
| Vercel frontend deployed | https://watchpoint.vercel.app |
| GitHub repo public | https://github.com/sagarbpatel31/watchpoint |
| Graphify knowledge graph | `graphify-out/` (git-ignored, rebuilds on commit) |
| claude-mem session memory | worker on `127.0.0.1:37701` |
| caveman dev tooling | `.agents/skills/` |

### 🔴 Blocked (Priority 1 — deploy)

| Task | Blocker |
|------|---------|
| Supabase DB provisioned | User must sign up and create project |
| Render API deployed | User must sign up and Blueprint-import the repo |
| `NEXT_PUBLIC_API_URL` set in Vercel | Needs Render URL |
| Production DB seeded | Needs Render URL |

### 🟠 Not started (Priority 2–5, ordered)

| Task | Priority | File(s) |
|------|----------|---------|
| Alembic migrations initialized | P2 | `apps/api/alembic/versions/` |
| Ingest endpoint auth | P3 | `app/routers/ingest.py` |
| Real edge agent metrics | P4 | `agents/edge-agent/internal/collector/system.go` |
| Configurable project_id in edge agent | P4 | `agents/edge-agent/internal/sender/http.go` |
| httpOnly cookie auth | P5 | `apps/web/src/lib/auth.ts` |

---

## Known issues in current code

| Issue | Location | Impact |
|-------|----------|--------|
| Collector stubs (CPU/disk/net simulated) | `collector/system.go` | False analysis triggers on real hardware |
| Hard-coded project_id `11111111-...` | `sender/http.go` | All agents report to same project |
| `ros2_snapshot.json` is placeholder | `replay_bundle.py` | Replay bundle incomplete |
| `alembic/versions/` empty | `apps/api/alembic/` | Schema changes on live DB = manual ALTER TABLE |
| No ingest auth | `ingest.py` | Anyone with device_id can inject data |
| JWT in localStorage | `apps/web/src/lib/auth.ts` | XSS-extractable token |
