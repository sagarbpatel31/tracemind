# Current Task

## Active branch: `add-ai-engineering-system`

Adding AI engineering context layer to the repo. No production code changes on this branch.

**Scope:**
- `.ai/` — 9 context files for AI agent handoff
- `agents/claude.md` + `agents/codex.md` — per-agent usage rules
- `CLAUDE.md` — Claude Code session bootstrap with read-first enforcement
- `AGENTS.md` — Codex/generic agent bootstrap with read-first enforcement

**Status:** In progress (this file is being written as part of the work).

---

## What is complete on `main`

| Feature | Status | File(s) |
|---------|--------|---------|
| FastAPI backend (7 routers, 9 models) | ✅ | apps/api/app/ |
| JWT auth (register/login/me) | ✅ | app/routers/auth.py, app/security.py |
| Incident CRUD + analysis + replay bundle | ✅ | app/routers/incidents.py, app/services/ |
| Device registration + heartbeat + deployments | ✅ | app/routers/devices.py |
| Telemetry ingest (logs/metrics/events) | ✅ | app/routers/ingest.py |
| Rules-based analysis engine (7 rules) | ✅ | app/services/analysis.py |
| Claude Haiku LLM summarization | ✅ | app/services/analysis.py:generate_llm_summary() |
| Replay bundle (zip) | ✅ | app/services/replay_bundle.py |
| Seed endpoint + demo data | ✅ | app/routers/seed.py |
| Go edge agent | ✅ (stubs) | agents/edge-agent/ |
| Python ROS2 collector | ✅ (sim mode) | agents/ros2-collector/ |
| Next.js frontend (dashboard, incidents, login) | ✅ | apps/web/src/ |
| Docker Compose local dev | ✅ | deploy/docker-compose/ |
| Render IaC (render.yaml) | ✅ | apps/api/render.yaml |
| Vercel frontend deployed | ✅ | https://tracemind.vercel.app |
| Production Dockerfile | ✅ | apps/api/Dockerfile |
| Public GitHub repo | ✅ | github.com/sagarbpatel31/tracemind |
| caveman dev tooling | ✅ | .agents/skills/ |
| graphify knowledge graph | ✅ | graphify-out/ (git-ignored) |
| claude-mem session memory | ✅ | worker on 127.0.0.1:37701 |

---

## What is NOT done (production blockers)

| Task | Blocker | Who |
|------|---------|-----|
| Supabase DB provisioned | Needs account signup + project creation | User |
| Render API deployed | Needs account signup + Blueprint import | User |
| `NEXT_PUBLIC_API_URL` set in Vercel | Needs Render URL first | Claude after user |
| Production DB seeded | Needs Render URL first | Claude after user |

## What is NOT done (code quality)

| Issue | Location | Priority |
|-------|----------|---------|
| Edge agent collector stubs (simulated CPU/disk/net) | agents/edge-agent/internal/collector/system.go | Medium |
| Hard-coded project_id in edge agent | agents/edge-agent/internal/sender/http.go | Medium |
| ros2_snapshot.json is placeholder in replay bundle | app/services/replay_bundle.py | Low |
| alembic/versions/ is empty — no real migrations | apps/api/alembic/ | High (before prod schema changes) |
| No auth on ingest endpoints | app/routers/ingest.py | Medium |
| JWT in localStorage (not httpOnly cookie) | apps/web/src/lib/auth.ts | Low (MVP acceptable) |
| No test suite | anywhere | Medium |
