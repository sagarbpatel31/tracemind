# TraceMind — Claude Code Context

## What this is
Incident intelligence platform for ROS2 and edge AI robots. FastAPI backend + Next.js frontend + Go/Python edge agents. Monorepo.

## Start here
- `.ai/architecture.md` — system topology, data flow, all models and routes
- `.ai/handoff.md` — current state, what's done, what's pending
- `.ai/failure_patterns.md` — known bugs and fixes (read before debugging anything)
- `.ai/decisions.md` — why key tech choices were made

## Critical rules (do not violate)

1. **shadcn v5 has no `asChild`** — use `<Link className={cn(buttonVariants({...}))}>` instead of `<Button asChild>`
2. **Use `bcrypt` directly** — never add `passlib`; it breaks on bcrypt 4.x / Python 3.11
3. **Postgres URL is auto-normalized** — `config.py` rewrites `postgres://` to `postgresql+asyncpg://`; don't manually fix URLs
4. **Ingest payload format** — agents POST `{metrics: [...]}` not `[...]` flat array
5. **LLM is optional** — every AI call has a fallback; never make `ANTHROPIC_API_KEY` required
6. **No production code on `add-ai-engineering-system` branch** — context layer only

## Repo layout
```
apps/api/          FastAPI + SQLAlchemy async + Postgres
apps/web/          Next.js 16 + shadcn/ui v5
agents/edge-agent/ Go — system metrics collector
agents/ros2-collector/ Python — ROS2 topic/node collector
packages/sample-data/  Seed fixtures + loader script
deploy/docker-compose/ Local dev stack
.ai/               AI engineering context (architecture, decisions, debugging, etc.)
```

## Local dev
```bash
cd deploy/docker-compose && docker compose up -d
curl -X POST http://localhost:8000/api/v1/seed/demo
# login: demo@tracemind.ai / demo123
```

## Tool paths (macOS arm64)
```
uv:      /Users/sagarpatel/.local/bin/uv
graphify: /Users/sagarpatel/.local/bin/uv tool run --from graphifyy graphify
bun:     /Users/sagarpatel/.bun/bin/bun
docker:  /Applications/Docker.app/Contents/Resources/bin/docker
```

---

## graphify

This project has a graphify knowledge graph at `graphify-out/`.

Rules:
- Before answering architecture or codebase questions, read `graphify-out/GRAPH_REPORT.md` for god nodes and community structure
- For cross-module "how does X relate to Y" questions, prefer `graphify query "<question>"` over grep
- After modifying code files, run `graphify update .` to keep the graph current (AST-only, no API cost)
