# Changelog

All notable changes to Watchpoint are documented here.
Format: [Conventional Commits](https://www.conventionalcommits.org/).

---

## [Unreleased] — Week 1 (2026-05-01)

### Added
- `agents/model-collector/` — new Python package for AI inference capture
  - `RingBuffer`: thread-safe fixed-size deque, O(1) append + snapshot
  - `CollectorConfig`: all tunables, reads from environment variables
  - `writer.py`: flush frames to `{flush_path}/{incident_id}/run_{ts}.msgpack` (msgpack + numpy serialization)
  - `Collector`: central coordinator — ring buffer, flush interface
  - `adapters/pytorch_adapter.py`: `register_forward_hook` based capture; records layer name, input/output shapes, mean/std, top-1 confidence, input hash, timestamp_ns
  - `sender.py`: HTTP flush to `/ingest/model-runs` + `/ingest/inferences`
  - `scripts/demo_hook.py`: ResNet-18 hook demo — 5 forward passes, flush to disk
  - 16 tests, all passing
- `apps/api/alembic/` — Alembic migration infrastructure initialized
  - `alembic.ini`, `env.py` (async engine), `script.py.mako`
  - `0001_initial.py`: DDL for all 10 existing tables
  - `0002_ai_layer.py`: DDL for `model_runs`, `inferences`, `decisions`, `ood_signals`
- `apps/api/app/models/ai_layer.py` — `ModelRun`, `Inference`, `Decision`, `OODSignal` SQLAlchemy models
- `apps/api/app/routers/ai_ingest.py` — unauthenticated AI layer ingest endpoints:
  - `POST /api/v1/ingest/model-runs`
  - `POST /api/v1/ingest/inferences` (batch)
  - `POST /api/v1/ingest/decisions` (batch)
- `apps/api/app/schemas/ai_layer.py` — Pydantic v2 schemas for all AI layer endpoints
- `Makefile` — root-level `make dev`, `make test`, `make lint`, `make seed`, `make clean`
- `CHANGELOG.md` — this file

### Changed
- **Renamed TraceMind → Watchpoint** across all source, configs, docs, and `.ai/` context files (35 files)
- `CLAUDE.md` — replaced with full engineering spec; added Session rules section
- `apps/api/pyproject.toml` — package name `watchpoint-api`
- `apps/api/app/main.py` — API title + bundle path prefix
- `apps/api/app/services/replay_bundle.py` — ZIP prefix `watchpoint-replay-`
- `apps/api/app/config.py` — default DB URL + JWT secret key prefix
- `apps/api/app/routers/seed.py` — demo email `demo@watchpoint.ai`, workspace slug `watchpoint-demo`
- `agents/edge-agent/go.mod` — module path `github.com/watchpoint/edge-agent`
- `deploy/docker-compose/docker-compose.yml` — Postgres user/db `watchpoint`
- `apps/web/src/lib/auth.ts` — localStorage keys `watchpoint_token` / `watchpoint_user`
- `apps/web/src/app/layout.tsx` — page title updated
- Git remote updated to `https://github.com/sagarbpatel31/watchpoint.git`

---

## [0.1.0] — MVP (2026-04-25)

### Added
- FastAPI backend: JWT auth, devices, incidents, ingest, 7-rule RCA engine, Claude Haiku LLM summary, replay ZIP bundles
- Next.js 16 frontend: dashboard, login, incident detail, device detail
- Go edge agent: system metrics collector (CPU/disk/net stubs), cross-compile Linux/ARM
- Python ROS2 collector: topic rates, node health, simulation mode
- Docker Compose local dev stack
- 3 demo scenarios: CPU contention, thermal throttling, version regression
- `.ai/` context layer: 9 engineering reference files
