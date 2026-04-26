# Handoff

Concise state summary for switching between Claude Code and Codex, or resuming after a context break.
Last updated: 2026-04-25.

---

## Project identity

- **Name:** TraceMind — incident intelligence for ROS2 and edge AI robots
- **Tagline:** "Sentry for robots"
- **Repo:** https://github.com/sagarbpatel31/tracemind (public)
- **Frontend:** https://tracemind.vercel.app (deployed, not yet wired to prod API)

---

## Current branch state

| Branch | Status |
|--------|--------|
| `main` | 8 commits — full MVP code + LLM integration + public release prep |
| `add-ai-engineering-system` | In progress — AI context layer only, no production code changes |

---

## What's fully working

- FastAPI backend: auth, devices, incidents, ingest, analysis (7 rules + Haiku), replay bundles, seed
- Next.js frontend: dashboard, incident detail, login
- Go edge agent: registers + sends metrics (collector stubs — simulated values)
- Python ROS2 collector: simulation mode works
- Docker Compose local dev: `docker compose up` → api:8000, web:3000, postgres:5432
- Vercel deploy: frontend live (but NEXT_PUBLIC_API_URL still points to localhost)

## What's NOT working yet

| Blocker | Action needed | By |
|---------|-------------|-----|
| No live production API | Sign up Render + Blueprint import + set DATABASE_URL | User then Claude |
| No production DB | Sign up Supabase + create project + paste URI | User then Claude |
| Vercel points to localhost | Set NEXT_PUBLIC_API_URL after Render URL known | Claude |
| No production seed | Run seed curl after deploy | Claude |

---

## Demo credentials (seeded DB)

```
email:    demo@tracemind.ai
password: demo123
```

---

## Required env vars for production

| Var | Source | Where |
|-----|--------|-------|
| `DATABASE_URL` | Supabase → Settings → DB → URI | Render dashboard |
| `JWT_SECRET_KEY` | Auto-generated | render.yaml: `generateValue: true` |
| `ANTHROPIC_API_KEY` | console.anthropic.com | Render dashboard (optional) |
| `NEXT_PUBLIC_API_URL` | Render deploy URL | Vercel env vars |

---

## Local dev quick start

```bash
cd /Users/sagarpatel/Documents/Tracemind/deploy/docker-compose
/Applications/Docker.app/Contents/Resources/bin/docker compose up -d
curl -X POST http://localhost:8000/api/v1/seed/demo
open http://localhost:3000   # login: demo@tracemind.ai / demo123
open http://localhost:8000/docs  # Swagger UI
```

---

## Critical rules (do not break)

1. **No passlib** — use `import bcrypt` directly
2. **No `asChild` on Button** — use `buttonVariants()` spread on Link
3. **Ingest format** — `{metrics:[...]}` not `[...]` flat array
4. **All LLM calls have fallback** — never require `ANTHROPIC_API_KEY`
5. **Postgres URL** — auto-normalized in config.py, never manually edit cloud URIs

---

## Tool paths (macOS arm64, this machine)

```bash
uv:       /Users/sagarpatel/.local/bin/uv
graphify: /Users/sagarpatel/.local/bin/uv tool run --from graphifyy graphify
bun:      /Users/sagarpatel/.bun/bin/bun
docker:   /Applications/Docker.app/Contents/Resources/bin/docker
```

---

## Key file map

```
apps/api/app/main.py          FastAPI app, lifespan, routers
apps/api/app/config.py        All settings + URL normalization
apps/api/app/security.py      JWT + bcrypt auth
apps/api/app/services/analysis.py    7 rules + Haiku LLM summary
apps/api/app/services/replay_bundle.py  ZIP bundle generation
apps/web/src/lib/api-client.ts  Typed HTTP client with JWT injection
apps/web/src/lib/auth.ts        Token storage + auth helpers
apps/web/src/types/index.ts     All TypeScript interfaces
agents/edge-agent/internal/collector/system.go   Metric collection (STUBS)
agents/edge-agent/internal/sender/http.go        API sender (hard-coded project_id)
```
