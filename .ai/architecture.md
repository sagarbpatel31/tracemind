# TraceMind — Architecture

## What this is
Incident intelligence platform for ROS2 and edge AI robots. Captures field failures, correlates telemetry, generates replayable bundles with AI root-cause analysis. "Sentry for robots."

## System topology

```
Edge devices (Jetson/Linux)
  ├── agents/edge-agent/          Go  — system metrics (CPU, mem, disk) → POST /ingest/metrics
  └── agents/ros2-collector/      Python — ROS2 topic rates, node counts → POST /ingest/metrics + /ingest/logs

apps/api/                         FastAPI + SQLAlchemy 2.0 async + asyncpg + Postgres
  ├── /ingest/*                   Receives batched telemetry from agents
  ├── /incidents/*                CRUD + analysis trigger + replay bundle
  ├── /devices/*                  Registration, heartbeat, deployments
  ├── /auth/*                     JWT register/login
  └── /seed/demo                  Seeds 3 devices, 3 incidents, demo user

apps/web/                         Next.js 16 + shadcn/ui v5 (base-ui)
  ├── /dashboard                  Project overview — device grid, incident table
  ├── /incidents/[id]             Incident detail — timeline, metrics, analysis, replay bundle
  └── /login                      JWT auth (localStorage)

Postgres (Supabase in prod)       Single DB — all models in one schema, no migrations (create_all on startup)
Storage (filesystem)              /storage/bundles/ — replay zip files
```

## Data flow

```
1. Agent collects → POST /api/v1/ingest/metrics  (batch: {metrics: [...]})
2. API writes MetricPoint / EventLog rows
3. Incident created (manually or auto-trigger — auto not yet built)
4. POST /incidents/{id}/analyze  →  7 rules engine  →  optional Claude Haiku summary
5. POST /incidents/{id}/replay-bundle  →  zip: metadata + events + metrics + deployment + analysis
6. GET  /api/v1/bundles/{id}  →  download zip
```

## Key models (apps/api/app/models/)

| Model | Table | Purpose |
|-------|-------|---------|
| User | users | Auth — email, password_hash, is_active |
| Workspace | workspaces | Top-level org unit |
| Project | projects | Groups devices + incidents |
| Device | devices | Edge hardware — model, OS, agent version, status |
| Deployment | deployments | Software version pushed to device |
| Incident | incidents | Core entity — severity, status, analysis_json (JSONB), root_cause_summary |
| EventLog | event_logs | Log lines — level, source, message, metadata_json (JSONB) |
| MetricPoint | metric_points | Time-series — metric_name, value, unit, labels_json (JSONB) |
| IncidentArtifact | incident_artifacts | File references (replay bundles) |
| Annotation | annotations | Human notes on incidents |

All models: UUID PK, timezone-aware timestamps via `TimestampMixin`.

## Enums

- Severity: critical / high / medium / low
- IncidentStatus: open / investigating / resolved
- DeviceStatus: online / offline / unknown
- LogLevel: debug / info / warn / error / fatal
- ArtifactType: log_bundle / metrics_bundle / replay_bundle / ros2_snapshot

## Production stack

| Layer | Service | Plan | Notes |
|-------|---------|------|-------|
| Frontend | Vercel | Free | https://tracemind.vercel.app |
| API | Render | Free | ~1 min cold start, `$PORT` env respected |
| Database | Supabase | Free | 500MB, pauses after 1 week inactivity |

## Local dev

```bash
cd deploy/docker-compose
docker compose up          # postgres:5432, api:8000, web:3000
curl -X POST localhost:8000/api/v1/seed/demo
```

## Known limitations

- No DB migrations — uses `create_all` on startup (safe for dev, fine for MVP)
- Edge agent collector stubs CPU/disk/network with simulated values (only memory is real)
- Hard-coded project ID `11111111-...` in edge-agent config
- No incident auto-trigger from agent — incidents created manually or via seed
- Replay bundle `ros2_snapshot.json` is a placeholder (not populated)
- JWT stored in localStorage (not httpOnly cookie)
