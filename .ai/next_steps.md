# Next Steps

Ordered by priority. Top 3 are blockers for a working production demo.

## 🔴 Immediate — production deployment

### 1. Provision Supabase
- https://supabase.com → New project → name: `tracemind`, region: US East
- Settings → Database → Connection string → URI
- Copy `postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres`

### 2. Deploy API to Render
- https://render.com → New → Blueprint → connect `sagarbpatel31/tracemind`
- Render auto-detects `apps/api/render.yaml`
- Set env vars: `DATABASE_URL` (Supabase URI), optionally `ANTHROPIC_API_KEY`
- Copy deploy URL: `https://tracemind-api.onrender.com`

### 3. Seed + wire Vercel
```bash
curl -X POST https://tracemind-api.onrender.com/api/v1/seed/demo
cd apps/web && vercel env add NEXT_PUBLIC_API_URL production
# value: https://tracemind-api.onrender.com
vercel --prod
```

### 4. Smoke test
```bash
curl https://tracemind-api.onrender.com/api/v1/health
# login, list incidents, trigger analyze, download replay bundle
```

---

## 🟡 Near-term — agent + data quality

### 5. Fix edge agent collector stubs
- `agents/edge-agent/internal/collector/system.go` — replace simulated CPU/disk/network with real `/proc` reads (Linux) or `gopsutil`
- Add `project_id` as config flag (currently hard-coded as `11111111-...`)

### 6. Auto-trigger incidents from agent anomaly
- Threshold rule in edge-agent: if CPU > 90% for 30s, POST `/incidents/` automatically
- Or: server-side cron that scans recent MetricPoints for threshold violations

### 7. ROS2 snapshot in replay bundle
- `apps/api/app/services/replay_bundle.py` — populate `ros2_snapshot.json` with real node/topic data from EventLog metadata

---

## 🟢 Growth — product surface

### 8. Incident auto-timeline
- Group EventLogs by time window into visual timeline on `/incidents/[id]`

### 9. Alert notifications
- Webhook or email on severity=critical incident creation

### 10. Multi-workspace auth
- Currently all devices/incidents share implicit workspace; enforce workspace scoping per user

### 11. Alembic migrations
- Replace `create_all` on startup with proper Alembic migration chain for production schema evolution

### 12. Edge agent binary release
- Cross-compile Go agent for `linux/arm64` (Jetson), publish GitHub release artifact
