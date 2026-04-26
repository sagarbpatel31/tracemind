# Current Task

## Branch: `add-ai-engineering-system`

Adding an AI engineering context layer — `.ai/`, `CLAUDE.md`, `AGENTS.md` — to preserve work state, improve handoff between Claude/Codex sessions, and reduce repeated codebase re-reading.

**No production code is being modified on this branch.**

## What's staged / in-progress

The following were committed on `main` before this branch:

- ✅ `anthropic>=0.40.0` added to pyproject.toml
- ✅ `generate_llm_summary()` in analysis.py — Claude Haiku, max_tokens=80, graceful fallback
- ✅ `anthropic_api_key` in config.py
- ✅ `ANTHROPIC_API_KEY` in render.yaml (sync: false)
- ✅ caveman installed (6 skills: /caveman, /caveman-commit, /caveman-review, /caveman-compress, /caveman-help, /compress)
- ✅ graphify installed — 263 nodes, 479 edges, 36 communities, git hooks active
- ✅ claude-mem installed — worker running on 127.0.0.1:37701

## Uncommitted on this branch (before this task)

Staged but not yet committed:
- `.agents/skills/caveman*/` — caveman skill files
- `.kiro/skills/caveman*/` — kiro symlinks
- `skills-lock.json`
- `CLAUDE.md` (graphify section)
- `.gitignore` update (graphify-out/ ignored)

These will be committed as part of the AI engineering layer commit on this branch.

## Pending (not started, separate from this branch)

1. **Render + Supabase deployment** — user must sign up, provide DB URI + deploy URL
2. **Vercel env var** — `NEXT_PUBLIC_API_URL` needs Render URL
3. **Seed production DB** — `curl -X POST https://tracemind-api.onrender.com/api/v1/seed/demo`
4. **Edge agent real metrics** — replace CPU/disk/network stubs in `collector/system.go`
5. **Auto-trigger incidents** from agent anomaly detection
