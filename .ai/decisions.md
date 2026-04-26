# Technical Decisions

Key decisions made during the build — why, what was rejected, what the tradeoffs are.

---

## Auth: bcrypt directly, not passlib

**Decision:** `import bcrypt` + `bcrypt.hashpw/checkpw` directly in `security.py`

**Rejected:** `passlib[bcrypt]` (was the first implementation)

**Why:** passlib is incompatible with `bcrypt>=4.x` on Python 3.11. Throws `ValueError: password cannot be longer than 72 bytes` even on short passwords. bcrypt 4.x changed internal API that passlib depends on and passlib hasn't kept up.

**File:** `apps/api/app/security.py`

---

## Postgres URL normalization via field_validator

**Decision:** `@field_validator("database_url")` auto-rewrites any `postgres://` or `postgresql://` URL to `postgresql+asyncpg://` and strips `?sslmode=require`

**Why:** Supabase, Render, and Heroku all expose `postgres://` URLs. SQLAlchemy with asyncpg requires `postgresql+asyncpg://`. asyncpg also doesn't accept `sslmode` as a URL param (uses its own TLS mechanism). Without this, every cloud deploy breaks silently.

**File:** `apps/api/app/config.py`

---

## No passlib, no Alembic (for now)

**Decision:** No DB migrations — `Base.metadata.create_all()` on startup

**Why:** MVP speed. `create_all` is idempotent for new tables. For schema changes during dev, columns were added via raw `ALTER TABLE` SQL.

**Tradeoff:** Not suitable for production schema evolution once real data exists. Alembic is the next step (see next_steps.md).

---

## Rules-based analysis first, LLM second

**Decision:** 7 deterministic rules run first; LLM only synthesizes their output into a 2-sentence summary

**Why:** Rules are free, instant, deterministic, and debuggable. LLM adds narrative polish but not reasoning. Analysis still works (rules text fallback) if `ANTHROPIC_API_KEY` is not set.

**Cost:** claude-haiku-4-5, max_tokens=80, ~$0.03/1000 analyses

**Files:** `apps/api/app/services/analysis.py`

---

## Haiku not Sonnet for incident summarization

**Decision:** `claude-haiku-4-5` for `generate_llm_summary()`

**Why:** 2-sentence synthesis from structured rules output. Haiku is ~25× cheaper than Sonnet; the task doesn't require deep reasoning, just clean prose from structured input.

---

## shadcn/ui v5 (base-ui) — no `asChild` prop

**Decision:** Use `<Link className={cn(buttonVariants({...}))}>` pattern instead of `<Button asChild><Link>...</Link></Button>`

**Why:** shadcn v5 (base-ui variant) doesn't export `asChild` prop on Button. TypeScript build fails. Pattern is to spread `buttonVariants()` CSS onto the Link directly.

**File:** Any page with a link styled as a button (dashboard, incidents, login)

---

## Production: Vercel + Render + Supabase (all free)

**Decision:** Vercel (Next.js), Render (FastAPI Docker), Supabase (Postgres)

**Rejected:**
- Railway — presented as free but requires $5 credit then $1/mo; no true free tier for 24/7 service
- Koyeb — considered; ~5s cold start vs Render's ~60s, but less brand familiarity
- Fly.io — more config complexity for MVP

**Tradeoffs:**
- Render free tier: ~60s cold start on first request after 15 min idle
- Supabase free tier: DB pauses after 1 week inactivity (resumes on next request, ~30s)

---

## Git history: no force-push for path leak

**Decision:** When `.claude/launch.json` was found to contain `/Users/sagarpatel/` paths, we untracked it going forward rather than rewriting history.

**Why:** Force-push destroys linear history, breaks clones, for negligible security benefit (username already public via GitHub handle).

---

## JWT in localStorage (not httpOnly cookie)

**Decision:** Token stored in `localStorage` via `apps/web/src/lib/auth.ts`

**Why:** Simplest for MVP Next.js app router. No server-side session needed.

**Tradeoff:** Vulnerable to XSS. Acceptable for an early-stage internal tool; swap to httpOnly cookies before handling real customer data.

---

## Monorepo layout

```
apps/api/     FastAPI backend
apps/web/     Next.js frontend
agents/       Edge agents (Go + Python)
packages/     Shared utilities / sample data
deploy/       Docker Compose
```

**Why:** All in one repo for MVP velocity. Single `git push` deploys everything. Render detects `apps/api/render.yaml` for the API service.
