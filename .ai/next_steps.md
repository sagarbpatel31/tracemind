# Next Steps

Ordered by urgency. Top 4 are production deploy blockers.

---

## 🔴 P0 — Production deploy (blocked on user actions)

### 1. Provision Supabase
- https://supabase.com → New project → name: `tracemind`, region: US East (N. Virginia)
- Settings → Database → Connection string → URI tab
- Copy: `postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres`
- Paste to Claude — the URL normalizer in config.py handles the rest

### 2. Deploy API to Render
- https://render.com → New → Blueprint → connect `sagarbpatel31/tracemind`
- Render auto-detects `apps/api/render.yaml` → proposes `tracemind-api`
- Set env vars: `DATABASE_URL` (Supabase URI), optionally `ANTHROPIC_API_KEY`
- Copy deploy URL: `https://tracemind-api.onrender.com`

### 3. Wire Vercel to live API
```bash
cd apps/web
vercel env add NEXT_PUBLIC_API_URL production
# value: https://tracemind-api.onrender.com
vercel --prod
```

### 4. Seed + smoke test
```bash
curl -X POST https://tracemind-api.onrender.com/api/v1/seed/demo
curl https://tracemind-api.onrender.com/api/v1/health
# → open https://tracemind.vercel.app → login demo@tracemind.ai / demo123
```

---

## 🟠 P1 — Fix real data gaps (code changes needed)

### 5. Edge agent: real system metrics
**File:** `agents/edge-agent/internal/collector/system.go`
Replace simulated CPU/disk/network stubs with actual `/proc` reads (Linux) or `gopsutil` library.
Also: make `project_id` a CLI flag instead of hard-coded string in `sender/http.go`.

### 6. Alembic migrations
**Files:** `apps/api/alembic/` (dir exists, `versions/` is empty)
The current `create_all` on startup is fine for the first deploy but breaks on any schema change once real data exists. Initialize Alembic autogenerate from current models before the first production write.

### 7. Auth on ingest endpoints
**File:** `apps/api/app/routers/ingest.py`
Currently unauthenticated — any caller with a device_id can POST metrics. Add device-level auth token or at minimum rate limiting.

---

## 🟡 P2 — Product completeness

### 8. Populate ros2_snapshot.json in replay bundle
**File:** `apps/api/app/services/replay_bundle.py`
Currently a placeholder dict. Should pull actual ROS2 metadata from EventLog.metadata_json where source=ros2_collector.

### 9. Incident auto-trigger from agent anomaly
Agent detects threshold violation (CPU > 90% for 30s) → `POST /api/v1/incidents/` automatically.
Currently incidents are only created manually or via seed.

### 10. shared-types alignment
**Dir:** `packages/shared-types/src/`
Currently thin. Should export TypeScript interfaces that match `apps/web/src/types/index.ts` to enforce contract between frontend and API response shapes.

---

## 🟢 P3 — Growth features

### 11. Alert notifications on critical incidents
Webhook or email trigger when severity=critical incident is created.

### 12. Multi-workspace user scoping
Currently users can see all workspaces. Enforce workspace membership scoping in list queries.

### 13. Cross-compile edge agent for Jetson
`GOOS=linux GOARCH=arm64 go build` → publish as GitHub Release artifact.

### 14. Incident timeline auto-grouping
Group EventLogs by 10-second windows on the incident detail page for cleaner visual timeline.
