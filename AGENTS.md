# Watchpoint — AI Agent Bootstrap

## ⚠️ READ BEFORE CODING

All AI agents (Codex, Claude, Gemini, Cursor, Copilot) MUST read these files before writing any code:

```
1. .ai/architecture.md      — full system topology, all models, all API routes
2. .ai/current_task.md      — what is done, what is in progress, what is pending
3. .ai/next_steps.md        — prioritized engineering backlog
4. .ai/failure_patterns.md  — confirmed bugs with exact symptoms and fixes
```

Agent-specific rules:
```
agents/claude.md   — Claude Code rules, tool paths, commit style
agents/codex.md    — Codex constraints, stack facts, pattern reference
```

---

## Project

Watchpoint — incident intelligence for ROS2 and edge AI robots.
Repo: github.com/sagarbpatel31/watchpoint (public)
Frontend: https://watchpoint.vercel.app

---

## Repository layout

```
apps/api/              FastAPI backend (Python 3.11, SQLAlchemy 2.0 async, asyncpg)
apps/web/              Next.js 16 frontend (TypeScript, Tailwind, shadcn/ui v5)
agents/edge-agent/     Go — system metrics collector for edge devices
agents/ros2-collector/ Python — ROS2 topic/node monitor
agents/claude.md       Claude-specific usage rules
agents/codex.md        Codex-specific usage rules
packages/sample-data/  Seed script + JSON fixtures
deploy/docker-compose/ docker-compose.yml — postgres + api + web
.ai/                   AI engineering context (9 files — read before coding)
```

---

## Absolute constraints (apply to all agents)

### Never do these
- `from passlib.context import CryptContext` — passlib incompatible with bcrypt 4.x
- `<Button asChild>` — shadcn v5 does not have this prop
- Ingest payload as flat array `[{...}]` — must be `{metrics: [{...}]}`
- LLM call without fallback — `ANTHROPIC_API_KEY` is optional
- Hardcode any secret or API key

### Always do these
- Read `.ai/architecture.md` before touching any module
- Read `.ai/failure_patterns.md` before debugging
- New DB column on existing table → provide `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` SQL
- New model → extend `UUIDMixin` and `TimestampMixin` from `app/models/base.py`
- New LLM call → `model="claude-haiku-4-5"`, explicit `max_tokens`, fallback path

---

## API quick reference

All routes prefixed `/api/v1`:

```
GET  /health
POST /auth/register    {email, password, name}
POST /auth/login       {email, password} → {access_token, token_type}
GET  /auth/me          Bearer required

POST /devices/register
GET  /devices/         ?project_id=
GET  /devices/{id}
POST /devices/heartbeat/{id}
POST /devices/deployments

POST /incidents/
GET  /incidents/       ?project_id, device_id, status, limit, offset
GET  /incidents/{id}
GET  /incidents/{id}/events    ?limit=500
GET  /incidents/{id}/metrics   ?limit=5000
POST /incidents/{id}/analyze
POST /incidents/{id}/replay-bundle
GET  /bundles/{id}     download ZIP

POST /ingest/logs      {logs: [...]}
POST /ingest/metrics   {metrics: [...]}
POST /ingest/events    {events: [...]}

GET  /projects/{id}
GET  /projects/{id}/summary

POST /seed/demo        creates demo@watchpoint.ai / demo123 + 3 devices + 3 incidents
```

---

## Analysis engine summary

`apps/api/app/services/analysis.py` — 7 rules, confidence-scored, then optional Haiku summary:

| Rule | Trigger | Confidence |
|------|---------|------------|
| Resource contention | cpu_percent > 85 AND topic_rate_hz < 5 | 0.85 |
| Version regression | deployment + regression keywords in events | 0.82 |
| Thermal throttling | temp > 75°C AND inference_latency_ms > 100 | 0.80 |
| Process failure chain | crash events AND watchdog events | 0.75 |
| Mission abort | abort/e-stop events | evidence only |
| Latency degradation | 2× latency increase, no thermal | evidence only |
| Error spike | error/fatal logs > 3 | evidence only |

Fallback if no rules match: `"Unknown — manual investigation needed"` (confidence 0.3)

---

## Local dev quick start

```bash
cd deploy/docker-compose && docker compose up -d
curl -X POST http://localhost:8000/api/v1/seed/demo
# api: http://localhost:8000/docs
# web: http://localhost:3000  (demo@watchpoint.ai / demo123)
```
