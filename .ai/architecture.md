# Architecture

## Identity
TraceMind — incident intelligence for ROS2 and edge AI robots.
"Sentry for robots": captures field failures, correlates telemetry, generates replayable bundles with AI root-cause analysis.

---

## Monorepo layout

```
apps/api/                   FastAPI backend (Python 3.11)
apps/web/                   Next.js 16 frontend (TypeScript)
agents/edge-agent/          Go system metrics collector
agents/ros2-collector/      Python ROS2 topic/node monitor
packages/sample-data/       Seed script + JSON fixtures
packages/shared-types/      Shared TypeScript types (src/ — currently thin)
deploy/docker-compose/      Local dev stack
docs/                       Empty
```

---

## Data flow

```
Edge devices (Jetson / Linux / sim)
  agents/edge-agent        → POST /api/v1/ingest/metrics  (batch: {metrics:[...]})
  agents/ros2-collector    → POST /api/v1/ingest/metrics + /ingest/logs

apps/api (FastAPI + Postgres)
  /ingest/*                → writes MetricPoint / EventLog rows
  /incidents/{id}/analyze  → runs 7 rules engine → optional Claude Haiku summary
  /incidents/{id}/replay-bundle → zips metadata+events+metrics+deployment+analysis

apps/web (Next.js)
  /dashboard               → devices + incidents overview
  /incidents/[id]          → full incident case file
  /login                   → JWT auth
```

---

## Backend: apps/api

**Framework:** FastAPI 0.115+ with async SQLAlchemy 2.0 + asyncpg driver

**Entry:** `app/main.py`
- Lifespan: `Base.metadata.create_all()` on startup (no Alembic migrations active; `alembic/` dir exists but `versions/` is empty)
- CORS: origins from `settings.cors_origins` (comma-split)
- All routes prefixed `/api/v1`

**Routes mounted:**
```
/api/v1/health          health.router
/api/v1/auth/*          auth.router
/api/v1/devices/*       devices.router
/api/v1/incidents/*     incidents.router
/api/v1/ingest/*        ingest.router
/api/v1/projects/*      projects.router
/api/v1/seed/*          seed.router
GET /api/v1/bundles/{incident_id}   download zip (in main.py directly)
```

**Full route table:**

| Method | Path | Handler | Notes |
|--------|------|---------|-------|
| GET | /health | health_check | returns {status, version} |
| POST | /auth/register | register | email+password+name → JWT |
| POST | /auth/login | login | email+password → JWT |
| GET | /auth/me | get_me | Bearer required |
| POST | /devices/register | register_device | DeviceRegister → DeviceResponse |
| GET | /devices/ | list_devices | ?project_id= |
| GET | /devices/{id} | get_device | |
| POST | /devices/heartbeat/{id} | device_heartbeat | sets status=online, last_seen_at |
| POST | /devices/deployments | create_deployment | version + metadata_json |
| POST | /incidents/ | create_incident | IncidentCreate |
| GET | /incidents/ | list_incidents | ?project_id, device_id, status, limit, offset |
| GET | /incidents/{id} | get_incident | detail + event/metric counts |
| GET | /incidents/{id}/events | get_incident_events | ?limit=500 |
| GET | /incidents/{id}/metrics | get_incident_metrics | ?limit=5000 |
| POST | /incidents/{id}/analyze | analyze_incident_endpoint | triggers rules + LLM |
| POST | /incidents/{id}/replay-bundle | create_replay_bundle | generates zip |
| GET | /projects/{id} | get_project | |
| GET | /projects/{id}/summary | get_project_summary | {total_devices, online_devices, total_incidents} |
| POST | /ingest/logs | ingest_logs | {logs:[...]} |
| POST | /ingest/metrics | ingest_metrics | {metrics:[...]} |
| POST | /ingest/events | ingest_events | {events:[...]} |
| POST | /seed/demo | seed_demo_data | creates demo workspace, project, 3 devices, 3 incidents |
| GET | /bundles/{incident_id} | download_bundle | FileResponse from storage/bundles/ |

**Database models:**

| Model | Table | Key fields |
|-------|-------|-----------|
| User | users | id(UUID PK), email(unique), name, password_hash, is_active |
| Workspace | workspaces | id, name, slug(unique), owner_id(FK→users) |
| Project | projects | id, name, slug, workspace_id(FK→workspaces) |
| Device | devices | id, project_id(FK), device_name, hardware_model, os_version, agent_version, status(enum), last_seen_at, registered_at |
| Deployment | deployments | id, device_id(FK), version, deployed_at, metadata_json(JSONB) |
| Incident | incidents | id, project_id(FK), device_id(FK), deployment_id(FK nullable), title, severity(enum), status(enum), trigger_type, root_cause_summary(Text), analysis_json(JSONB), started_at, resolved_at(nullable) |
| IncidentArtifact | incident_artifacts | id, incident_id(FK), artifact_type(enum), file_path, size_bytes |
| EventLog | event_logs | id, device_id(FK,idx), incident_id(FK,idx,nullable), timestamp(idx), level(enum), source, message(Text), metadata_json(JSONB) |
| MetricPoint | metric_points | id, device_id(FK,idx), incident_id(FK,idx,nullable), timestamp(idx), metric_name(idx), value(float), unit, labels_json(JSONB) |
| Annotation | annotations | id, incident_id(FK), user_id(FK nullable), content(Text), annotation_type |

All models inherit `UUIDMixin` (uuid4 PK) and `TimestampMixin` (created_at, updated_at) from `app/models/base.py`.
All datetimes are timezone-aware (`DateTime(timezone=True)` via type_annotation_map).

**Enums:** Severity(critical/high/medium/low), IncidentStatus(open/investigating/resolved), DeviceStatus(online/offline/unknown), LogLevel(debug/info/warn/error/fatal), ArtifactType(log_bundle/metrics_bundle/replay_bundle/ros2_snapshot)

**Config (`app/config.py`):**

| Setting | Default | Notes |
|---------|---------|-------|
| database_url | postgresql+asyncpg://tracemind:tracemind@localhost:5432/tracemind | auto-normalized |
| cors_origins | http://localhost:3000 | comma-separated |
| storage_path | ./storage | replay bundle root |
| api_version | 0.1.0 | |
| jwt_secret_key | tracemind-dev-secret-change-in-production | override in prod |
| jwt_algorithm | HS256 | |
| jwt_expiration_minutes | 60 | |
| anthropic_api_key | "" | optional — LLM disabled if empty |

`normalize_postgres_url()` validator: rewrites `postgres://` and `postgresql://` → `postgresql+asyncpg://`, strips `?sslmode=require` params.

**Auth (`app/security.py`):** JWT (python-jose, HS256). Passwords: raw `bcrypt` (NOT passlib — incompatible with bcrypt 4.x). `get_current_user` returns None on invalid token (soft); `require_current_user` raises 401.

**Analysis service (`app/services/analysis.py`):**

7 rules run deterministically, then optional Claude Haiku call:

| # | Rule | Trigger | Confidence |
|---|------|---------|------------|
| 1 | Resource contention | cpu_percent > 85 AND topic_rate_hz < 5 | 0.85 |
| 2 | Thermal throttling | temp > 75°C AND inference_latency_ms > 100 | 0.80 |
| 3 | Process failure chain | crash/exit events AND watchdog/timeout events | 0.75 |
| 4 | Version regression | deployment/version keywords AND regression/abort keywords | 0.82 |
| 5 | Mission abort | abort/e-stop/emergency stop events | evidence only |
| 6 | Latency degradation | latency > 50ms AND 2× increase without thermal | evidence only |
| 7 | Error spike | error/fatal logs > 3 | evidence only |

`generate_llm_summary()`: model=claude-haiku-4-5, max_tokens=80, ~120 input tokens, fallback to rules text if no API key.

**Replay bundle service (`app/services/replay_bundle.py`):**
ZIP at `{storage_path}/bundles/tracemind-replay-{incident_id}.zip` containing:
- `metadata.json` — incident + device metadata
- `events.json` — all EventLog entries
- `metrics.json` — all MetricPoint entries
- `deployment.json` — deployment info (if linked)
- `analysis_summary.txt` — root_cause_summary text
- `ros2_snapshot.json` — **placeholder, not populated**

Also creates `IncidentArtifact` row (artifact_type=replay_bundle).

---

## Frontend: apps/web

**Framework:** Next.js 16 (app router) + TypeScript + Tailwind + shadcn/ui v5 (base-ui)

**Important:** shadcn v5 has NO `asChild` prop on Button. Use `<Link className={cn(buttonVariants({...}))}>` pattern.

**Pages:**
- `/` — home/redirect
- `/login` — email+password form, register toggle, demo hint
- `/dashboard` — 4 stat cards, device grid, incident table
- `/devices/[id]` — device detail, metrics, incident history
- `/incidents/[id]` — full incident case file: header, analysis panel, events/metrics tabs, replay bundle button

**Auth:** JWT stored in `localStorage` (keys: `tracemind_token`, `tracemind_user`). `apiFetch()` auto-injects `Authorization: Bearer`. On 401 → clears auth + redirects to /login.

**API base URL:** `NEXT_PUBLIC_API_URL` env var (build-time baked into bundle).

---

## Edge agents

**edge-agent (Go):**
- CLI flags: `--api-url`, `--device-id`, `--device-name`, `--interval`
- Registers device on startup → collection loop (ticker)
- Exposes health on `:8081`
- **Collector stubs:** CPU, disk, network use simulated/placeholder values. Only memory uses real Go runtime stats.
- Hard-coded `project_id = "11111111-1111-1111-1111-111111111111"` in sender

**ros2-collector (Python):**
- Collects: `topic_rate_hz` per topic, `ros2_node_count`, `ros2_topic_count`
- `--simulate` flag for running without live ROS2
- Sends `{metrics:[...]}` and `{logs:[...]}` batches

---

## Production stack

| Layer | Service | Notes |
|-------|---------|-------|
| Frontend | Vercel | https://tracemind.vercel.app — live but NEXT_PUBLIC_API_URL not yet set to prod |
| API | Render (free) | IaC: apps/api/render.yaml — ~60s cold start after idle |
| Database | Supabase (free) | 500MB, pauses after 1 week inactivity |

**Not yet deployed:** Render + Supabase accounts not provisioned.

---

## Local dev

```bash
cd deploy/docker-compose
docker compose up -d
# services: postgres:5432  api:8000  web:3000
curl -X POST http://localhost:8000/api/v1/seed/demo
# demo@tracemind.ai / demo123
open http://localhost:3000
open http://localhost:8000/docs
```

Docker binary: `/Applications/Docker.app/Contents/Resources/bin/docker` (not in PATH by default on this machine).
