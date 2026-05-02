# Debugging

Systematic approach for each failure class in this codebase.

---

## Start here for any issue

```bash
# 1. Is the API up?
curl http://localhost:8000/api/v1/health
# → {"status":"ok","version":"0.1.0"}

# 2. Check docker services
/Applications/Docker.app/Contents/Resources/bin/docker compose -f deploy/docker-compose/docker-compose.yml ps

# 3. Tail API logs
/Applications/Docker.app/Contents/Resources/bin/docker compose -f deploy/docker-compose/docker-compose.yml logs api -f
```

---

## API not starting

**Check:** `docker compose logs api`

**Common causes:**
1. DB connection failed → verify `DATABASE_URL` in `.env`, check postgres container is healthy
2. Missing column → model added field after `create_all` ran (see failure_patterns.md #5)
3. Port 8000 conflict → `lsof -i :8000`
4. Import error → look for `ModuleNotFoundError` in logs

---

## 422 Unprocessable Entity

Pydantic schema mismatch. Steps:
1. `curl -v` the request to see exact body sent
2. Compare against schema in `apps/api/app/schemas/`
3. **Ingest routes**: body must be `{metrics:[...]}` or `{logs:[...]}` — not a flat array
4. Check required vs optional fields — Pydantic raises 422 on missing required

---

## 401 Unauthorized

```bash
# Get a fresh token
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@watchpoint.ai","password":"demo123"}' | python3 -m json.tool

# Use it (replace <token>)
curl http://localhost:8000/api/v1/incidents/ \
  -H "Authorization: Bearer <token>"
```

If login returns 401: password hash may be empty (see `ALTER TABLE` fix in failure_patterns.md #5).

---

## Analysis returns "Unknown — manual investigation needed"

No rules matched. Debug checklist:
```bash
# Are there metrics attached to this incident?
curl "http://localhost:8000/api/v1/incidents/{id}/metrics" \
  -H "Authorization: Bearer <token>" | python3 -m json.tool | head -40

# Are there events?
curl "http://localhost:8000/api/v1/incidents/{id}/events" \
  -H "Authorization: Bearer <token>" | python3 -m json.tool | head -40
```

Check rule thresholds in `apps/api/app/services/analysis.py`:
- Rule 1: `cpu_percent > 85` AND `topic_rate_hz < 5`
- Rule 2: `gpu_temp_c or cpu_temp_c > 75` AND `inference_latency_ms > 100`
- Rule 3: events with `crash|exit` AND `watchdog|timeout`
- Rule 4: events with `deployment|version|config|v2.|v1.` AND `regression|abort|missed`

---

## LLM summary not appearing (returns rules description text)

`ANTHROPIC_API_KEY` is empty or not set.

```bash
# Check local
grep ANTHROPIC_API_KEY apps/api/.env

# Verify it's loaded in the app
curl http://localhost:8000/api/v1/health  # doesn't expose key, but app would fail to start if config broken
```

The fallback is intentional — returning rules text is correct behavior when key is absent.

---

## Seed fails (UniqueViolationError)

DB already has demo data. Either truncate (dev only):
```sql
-- Connect to postgres
TRUNCATE users, workspaces, projects, devices, deployments, incidents,
  event_logs, metric_points, incident_artifacts, annotations CASCADE;
```
Then: `curl -X POST http://localhost:8000/api/v1/seed/demo`

---

## Edge agent not sending / device not appearing

```bash
# Run agent directly with verbose output
cd agents/edge-agent
go run ./cmd/agent \
  --api-url http://localhost:8000 \
  --device-id <uuid> \
  --device-name debug-device \
  --interval 5s

# Check device registered
curl http://localhost:8000/api/v1/devices/ | python3 -m json.tool
```

Common causes:
- Wrong `--api-url` (no trailing slash; must include `http://`)
- Device UUID not a valid UUID4 format
- API container not reachable from host (check docker network)

---

## Frontend blank / loading forever

1. Open DevTools → Network → find failing API call
2. `NEXT_PUBLIC_API_URL` is probably `http://localhost:8000` while API is on a different host
3. Check CORS: API `CORS_ORIGINS` must include the exact frontend origin (no trailing slash)
4. If 401 on dashboard: localStorage token expired → go to `/login`

---

## Replay bundle 404

```bash
# Check bundle file exists
ls apps/api/storage/bundles/

# Check storage_path config
grep STORAGE_PATH apps/api/.env

# Check IncidentArtifact was created
curl "http://localhost:8000/api/v1/incidents/{id}" \
  -H "Authorization: Bearer <token>" | python3 -m json.tool | grep artifact
```

---

## Graphify graph stale

```bash
/Users/sagarpatel/.local/bin/uv tool run --from graphifyy graphify update .
```

---

## claude-mem worker down

```bash
# Check if running
ps aux | grep worker-service | grep -v grep

# Restart (bun must be in PATH)
PATH="$HOME/.bun/bin:$PATH" npx claude-mem start &

# Health check (port is 37701, not 37777)
curl http://127.0.0.1:37701/health
```
