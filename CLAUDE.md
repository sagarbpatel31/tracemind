# TraceMind — Claude Code Bootstrap

## ⚠️ READ BEFORE CODING

You MUST read these files before writing any production code in this session:

```
1. .ai/architecture.md      — system topology, all models, all routes
2. .ai/current_task.md      — what's in progress, what's done, what's blocked
3. .ai/next_steps.md        — ordered engineering backlog
4. .ai/failure_patterns.md  — confirmed bugs with exact fixes (read this before debugging anything)
```

Additional context files (read as needed):
```
.ai/decisions.md      — why key technical choices were made
.ai/principles.md     — engineering rules for this repo
.ai/debugging.md      — per-error-class debugging workflow
.ai/handoff.md        — concise state summary for resuming after context break
.ai/prompts.md        — reusable prompts + product LLM prompt templates
agents/claude.md      — Claude-specific usage rules (hard constraints, tool paths, commit style)
```

---

## Project identity

TraceMind — incident intelligence for ROS2 and edge AI robots.
Repo: https://github.com/sagarbpatel31/tracemind

```
apps/api/              FastAPI + SQLAlchemy 2.0 async + Postgres (Python 3.11)
apps/web/              Next.js 16 + shadcn/ui v5 + TypeScript
agents/edge-agent/     Go — system metrics collector
agents/ros2-collector/ Python — ROS2 topic/node monitor
packages/sample-data/  Seed script + fixtures
deploy/docker-compose/ Local dev stack
.ai/                   AI engineering context (read before coding)
```

---

## Non-negotiable rules (memorize these)

| Rule | Detail |
|------|--------|
| No passlib | Use `import bcrypt` directly — passlib breaks on bcrypt 4.x / Python 3.11 |
| No `asChild` on Button | shadcn v5 doesn't have it — use `buttonVariants()` spread on Link |
| Ingest format | `{metrics:[...]}` not `[...]` — all three agents depend on this |
| LLM fallback required | Every LLM call returns rules text / default if `ANTHROPIC_API_KEY` is empty |
| No hardcoded secrets | JWT key and Anthropic key via env vars only |
| URL normalization | `config.py` handles `postgres://` → `postgresql+asyncpg://` automatically — never manually edit |

---

## Local dev

```bash
cd deploy/docker-compose
/Applications/Docker.app/Contents/Resources/bin/docker compose up -d
curl -X POST http://localhost:8000/api/v1/seed/demo
# open http://localhost:3000  →  demo@tracemind.ai / demo123
# open http://localhost:8000/docs  →  Swagger
```

---

## Tool paths (macOS arm64)

```bash
uv:       /Users/sagarpatel/.local/bin/uv
graphify: /Users/sagarpatel/.local/bin/uv tool run --from graphifyy graphify
bun:      /Users/sagarpatel/.bun/bin/bun
docker:   /Applications/Docker.app/Contents/Resources/bin/docker
```

---

## graphify (knowledge graph)

Before answering architecture questions, query the graph instead of re-reading source files:

```bash
graphify query "how does incident analysis work"
graphify path "analyze_incident" "generate_llm_summary"
graphify explain "MetricPoint"
```

After modifying code: `graphify update .` (AST-only, no API cost, rebuilds in <1s)

Graph report: `graphify-out/GRAPH_REPORT.md` — read for community structure and god nodes.
