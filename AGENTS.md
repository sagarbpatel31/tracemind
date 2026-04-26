# TraceMind — AI Agent Context (Codex / OpenAI / Generic)

## Project summary
TraceMind: incident intelligence for ROS2 and edge AI robots. Captures field failures, correlates telemetry, generates replayable bundles with AI root-cause analysis.

**Stack:** FastAPI + SQLAlchemy 2.0 async + Postgres · Next.js 16 + shadcn/ui v5 · Go edge agent · Python ROS2 collector

**Repo:** https://github.com/sagarbpatel31/tracemind

## Context files (read these before making changes)

| File | Contents |
|------|----------|
| `.ai/architecture.md` | Full system topology, all models, all API routes |
| `.ai/handoff.md` | Current state — what's done, what's pending, env vars needed |
| `.ai/decisions.md` | Why key choices were made (bcrypt, no passlib, shadcn v5, etc.) |
| `.ai/failure_patterns.md` | Known bugs with exact fixes — read before debugging |
| `.ai/principles.md` | What to build and what NOT to build |
| `.ai/debugging.md` | Where to look for each class of error |
| `.ai/prompts.md` | LLM prompt templates and token budget guidelines |
| `.ai/next_steps.md` | Ordered backlog — what comes next |

## Hard constraints

### Never do these
- Do not add `passlib` — incompatible with bcrypt 4.x on Python 3.11
- Do not use `<Button asChild>` — shadcn v5 does not have this prop
- Do not hardcode `ANTHROPIC_API_KEY` — it is optional; all LLM calls need a fallback
- Do not modify files outside the task scope on the `add-ai-engineering-system` branch
- Do not build fleet orchestration, teleoperation, OTA, digital twin, or simulation features

### Always do these
- Ingest routes expect `{metrics: [...]}` wrapper — not flat arrays
- `DATABASE_URL` is auto-normalized in `config.py` — do not manually edit Supabase/Render URLs
- New LLM calls: Haiku model, `max_tokens` ceiling, graceful fallback if no API key
- New models: extend `UUIDMixin` and `TimestampMixin` from `apps/api/app/models/base.py`

## API routes quick reference

```
GET  /api/v1/health
POST /api/v1/auth/register         {email, password, name}
POST /api/v1/auth/login            {email, password}
GET  /api/v1/auth/me               Bearer token required

POST /api/v1/devices/register
GET  /api/v1/devices/
GET  /api/v1/devices/{id}
POST /api/v1/devices/heartbeat/{id}
POST /api/v1/devices/deployments

POST /api/v1/incidents/
GET  /api/v1/incidents/
GET  /api/v1/incidents/{id}
GET  /api/v1/incidents/{id}/events
GET  /api/v1/incidents/{id}/metrics
POST /api/v1/incidents/{id}/analyze
POST /api/v1/incidents/{id}/replay-bundle
GET  /api/v1/bundles/{id}          download zip

POST /api/v1/ingest/logs           {logs: [...]}
POST /api/v1/ingest/metrics        {metrics: [...]}
POST /api/v1/ingest/events         {events: [...]}

GET  /api/v1/projects/{id}
GET  /api/v1/projects/{id}/summary

POST /api/v1/seed/demo             seeds demo@tracemind.ai / demo123
```

## Analysis engine (apps/api/app/services/analysis.py)

7 rules, deterministic, confidence-scored. Run via `POST /incidents/{id}/analyze`.

| Rule | Trigger | Confidence |
|------|---------|------------|
| Resource contention | CPU > 85% + topic_rate < 5 Hz | 0.85 |
| Thermal throttling | temp > 75°C + latency > 100ms | 0.80 |
| Version regression | deployment + regression keywords in events | 0.82 |
| Process failure chain | crash + watchdog events | 0.75 |
| Mission abort | abort/e-stop events | evidence only |
| Latency degradation | 2× latency increase, no thermal | evidence only |
| Error spike | > 3 error/fatal logs | evidence only |

After rules: optional Claude Haiku call (`generate_llm_summary()`), max_tokens=80, fallback to rules text.

## Local dev
```bash
cd deploy/docker-compose && docker compose up -d
curl -X POST http://localhost:8000/api/v1/seed/demo
# Dashboard: http://localhost:3000
# API docs:  http://localhost:8000/docs
```
