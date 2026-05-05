# Architecture & Implementation Decisions

Decisions visible in the codebase. Read before changing anything they affect.

---

## 1. bcrypt directly — not passlib

**Files:** `apps/api/app/security.py`, `apps/api/pyproject.toml`
**Decision:** `import bcrypt` → `bcrypt.hashpw()` / `bcrypt.checkpw()` directly.
**Why:** passlib calls bcrypt internal API changed in bcrypt 4.x. On Python 3.11 + bcrypt>=4.0, passlib throws `ValueError: password cannot be longer than 72 bytes` on any password. Passlib is unmaintained.
**Rule:** Never add `passlib` back to this project.

---

## 2. Postgres URL auto-normalization

**File:** `apps/api/app/config.py:normalize_postgres_url()`
**Decision:** `@field_validator` rewrites `postgres://` and `postgresql://` → `postgresql+asyncpg://`, strips `?sslmode=require`.
**Why:** Supabase/Render/Heroku all emit `postgres://`. SQLAlchemy+asyncpg requires `postgresql+asyncpg://`. asyncpg uses its own TLS mechanism, rejects `sslmode` in URL params.
**Rule:** Never manually edit cloud provider DB URIs. Paste them directly and the validator handles it.

---

## 3. create_all on startup, not Alembic (temporarily)

**Files:** `apps/api/app/main.py:lifespan()`, `apps/api/alembic/` (dir exists, `versions/` empty)
**Decision:** `Base.metadata.create_all()` on startup.
**Why:** MVP speed. Safe for first deploy — idempotent on existing tables, creates new ones.
**Tradeoff:** Cannot add columns to existing tables. Any schema change on a live DB requires manual `ALTER TABLE`. This is Priority 2 to fix — initialize Alembic before any schema change post-deploy.

---

## 4. Rules-based analysis, LLM synthesis only

**File:** `apps/api/app/services/analysis.py`
**Decision:** 7 deterministic rules run first. Claude Haiku only converts the top rule output to 2-sentence prose.
**Why:** Rules are free, instant, offline-capable, debuggable, and testable. LLM adds readability not reasoning. System fully works without any API key.
**Token constraints:** ~120 input, max_tokens=80, claude-haiku-4-5 (~$0.03/1000 analyses).

---

## 5. shadcn/ui v5 (base-ui) — no asChild

**Files:** `apps/web/src/components/ui/`, all pages with link-as-button
**Decision:** `<Link className={cn(buttonVariants({...}))}>` pattern.
**Why:** shadcn v5 base-ui removed `asChild` Radix prop. `<Button asChild>` causes TypeScript build failure.
**Rule:** Never use `asChild` on Button in this project.

---

## 6. JWT in localStorage (intentional MVP choice)

**File:** `apps/web/src/lib/auth.ts` — keys: `watchpoint_token`, `watchpoint_user`
**Decision:** localStorage-based JWT.
**Why:** Simplest for Next.js app router MVP. No server-side session infrastructure needed.
**Tradeoff:** XSS-extractable. Acceptable for internal tool / demo. Priority 5 to fix post-deploy.

---

## 7. JSONB for evolving data structures

**Files:** `analysis_json` (Incident), `metadata_json` (Deployment, EventLog, MetricPoint), `labels_json` (MetricPoint)
**Decision:** Postgres JSONB for fields still stabilizing.
**Why:** Avoids premature schema lock-in. Analysis output format, metric labels, deployment metadata will evolve. Normalize into columns when shape is stable.

---

## 8. Ingest endpoints unauthenticated (intentional MVP choice)

**File:** `apps/api/app/routers/ingest.py`
**Decision:** No auth on `/ingest/*` routes.
**Why:** Edge agents need simple HTTP POST without token management. Device ID acts as implicit identifier for MVP.
**Tradeoff:** Any caller with a valid device UUID can inject data. Priority 3 to fix — add device-scoped API tokens.

---

## 9. Production: Render + Supabase free tier

**Rejected:** Railway ($5 credit then $1/mo minimum — not truly free), Koyeb (less familiar).
**Chosen:** Render (free web service) + Supabase (free Postgres).
**Tradeoffs:** Render ~60s cold start after 15 min idle. Supabase pauses after 1 week inactivity (~30s resume).

---

## 10. Edge agent collector stubs (intentional MVP shortcut)

**File:** `agents/edge-agent/internal/collector/system.go`
**Decision:** CPU, disk, network are simulated. Memory uses real Go runtime stats.
**Comment in code:** *"This is a cross-platform stub that returns simulated values."*
**Risk:** Simulated values trigger rules engine false positives on real hardware. Priority 4 to fix.

---

## 11. No auth on ingest + hard-coded project_id in agent

**File:** `agents/edge-agent/internal/sender/http.go`
**Decision:** `project_id` hard-coded as `11111111-1111-1111-1111-111111111111` — matches seed data.
**Why:** Demo simplicity. Works with the seeded project out of the box.
**Fix needed:** Make `--project-id` a CLI flag alongside `--device-id`.
