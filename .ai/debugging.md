# Debugging Guide

Where to look first for each class of problem.

---

## API not starting

```bash
# Check logs
docker compose logs api

# Common causes:
# 1. DB connection failed → check DATABASE_URL in .env
# 2. Missing column → run ALTER TABLE (see failure_patterns.md #5)
# 3. Port conflict → check if :8000 is already in use
```

## 422 Unprocessable Entity from API

Pydantic schema mismatch. Check:
1. Request body against `apps/api/app/schemas/` Pydantic models
2. For ingest routes: payload must be `{metrics: [...]}` not `[...]` (see failure_patterns.md #4)
3. `curl -v` the request to see the raw body

## 401 Unauthorized

```bash
# Get a token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@tracemind.ai","password":"demo123"}'

# Use it
curl http://localhost:8000/api/v1/incidents/ \
  -H "Authorization: Bearer <token>"
```

## Analysis returns "Unknown — manual investigation needed"

No rules matched. Debug by checking:
1. `GET /api/v1/incidents/{id}/metrics` — are there any metric points?
2. `GET /api/v1/incidents/{id}/events` — are there any event logs?
3. Check thresholds in `analysis.py`:
   - Rule 1: CPU > 85% AND topic_rate < 5 Hz
   - Rule 2: temp > 75°C AND latency > 100ms
   - Rule 3: events with "crash"/"exit" AND "watchdog"/"timeout"
   - Rule 4: events with "deployment"/"version" AND "regression"/"abort"

## LLM summary not appearing (returns rules text instead)

`ANTHROPIC_API_KEY` is not set or empty. Check:
```bash
# Local
grep ANTHROPIC_API_KEY apps/api/.env

# Render production: check dashboard env vars
```

## Seed fails with UniqueViolationError

DB already seeded. Options:
```sql
-- Nuclear option: wipe and re-seed
TRUNCATE users, workspaces, projects, devices, deployments, incidents,
         event_logs, metric_points, incident_artifacts, annotations CASCADE;
```

## Edge agent not sending data

```bash
# Run with verbose output
./edge-agent --api-url http://localhost:8000 --device-id <uuid> --device-name test-device

# Check API received it
curl http://localhost:8000/api/v1/devices/<device-id>
```

Common issues:
- Wrong `--api-url` (no trailing slash, must include scheme)
- Device UUID mismatch
- API not running

## Frontend shows blank / loading forever

1. Open browser DevTools → Network tab → check API calls
2. `NEXT_PUBLIC_API_URL` is probably `http://localhost:8000` (default) while API is elsewhere
3. Check CORS: `CORS_ORIGINS` in API must include the frontend origin

## Replay bundle download fails (404)

```bash
# Check file exists
ls /path/to/storage/bundles/

# Check API storage_path config
grep STORAGE_PATH apps/api/.env
```

## Graphify graph is stale

```bash
/Users/sagarpatel/.local/bin/uv tool run --from graphifyy graphify update .
```

## claude-mem worker not running

```bash
# Check process
ps aux | grep bun | grep claude-mem

# Restart
PATH="$HOME/.bun/bin:$PATH" npx claude-mem start &

# Health check (note: port is 37701, not 37777)
curl http://127.0.0.1:37701/health
```
