# Architecture & Implementation Decisions

Decisions visible in the codebase, with rationale and tradeoffs.

---

## 1. bcrypt directly — not passlib

**Location:** `apps/api/app/security.py`, `apps/api/pyproject.toml`

**Decision:** `import bcrypt` → `bcrypt.hashpw()` / `bcrypt.checkpw()` directly.

**Rejected:** `passlib[bcrypt]`

**Why:** passlib's bcrypt wrapper calls internal API that changed in bcrypt 4.x. On Python 3.11 with bcrypt>=4.0, passlib throws `ValueError: password cannot be longer than 72 bytes` on any password regardless of length. Passlib is unmaintained against this.

**Rule:** Never add `passlib` back to this project.

---

## 2. Postgres URL auto-normalization

**Location:** `apps/api/app/config.py:normalize_postgres_url()`

**Decision:** `@field_validator` auto-rewrites `postgres://` → `postgresql+asyncpg://` and strips `?sslmode=require`.

**Why:** Supabase, Render, and Heroku all emit `postgres://` URIs. SQLAlchemy+asyncpg requires `postgresql+asyncpg://`. asyncpg uses its own TLS mechanism and rejects `sslmode` in URL params.

**Implication:** Paste any cloud provider's URI directly — it just works.

---

## 3. create_all on startup, not Alembic (for now)

**Location:** `apps/api/app/main.py:lifespan()`, `apps/api/alembic/` (dir exists, versions/ empty)

**Decision:** `Base.metadata.create_all(bind=engine)` on lifespan startup.

**Why:** MVP speed. `create_all` is idempotent for new tables. New columns were added with raw `ALTER TABLE` SQL during dev.

**Tradeoff:** Cannot evolve schema on a live database safely. `alembic/` directory exists and is set up but has no migration files. Must add Alembic before any schema change on a populated production DB.

---

## 4. Rules-based analysis first, LLM synthesis second

**Location:** `apps/api/app/services/analysis.py`

**Decision:** 7 deterministic heuristic rules run first. Claude Haiku only synthesizes the highest-confidence rule output into a 2-sentence prose summary.

**Why:** Rules are free, instant, offline-capable, and deterministic. LLM adds polish not reasoning. System is fully functional without any API key.

**Token constraints:** input ~120 tokens, output capped at `max_tokens=80`, model=claude-haiku-4-5.

---

## 5. shadcn/ui v5 (base-ui) — no asChild

**Location:** `apps/web/src/components/ui/`, all pages

**Decision:** Use `<Link className={cn(buttonVariants({...}))}>` pattern.

**Rejected:** `<Button asChild><Link>` — TypeScript error in v5: `Property 'asChild' does not exist on type 'ButtonHTMLAttributes'`.

**Why:** This project uses the base-ui variant of shadcn v5, which removed the `asChild` Radix prop.

**Rule:** Never use `asChild` on Button. Spread `buttonVariants()` onto the Link directly.

---

## 6. JWT in localStorage (not httpOnly cookie)

**Location:** `apps/web/src/lib/auth.ts` — keys: `tracemind_token`, `tracemind_user`

**Decision:** localStorage-based JWT.

**Why:** Simplest for Next.js app router MVP. No server-side session or cookie handling required.

**Tradeoff:** Vulnerable to XSS token theft. Acceptable for internal tool / MVP. Swap to httpOnly Secure cookie before handling real customer data.

---

## 7. JSONB for evolving data structures

**Location:** `analysis_json` (Incident), `metadata_json` (Deployment, EventLog, MetricPoint), `labels_json` (MetricPoint)

**Decision:** Use Postgres JSONB columns for fields whose schema is still evolving.

**Why:** Avoids premature schema lock-in. Analysis output format, metric labels, and deployment metadata will evolve. Serialize to JSONB until shape stabilizes, then normalize.

---

## 8. No auth on ingest endpoints

**Location:** `apps/api/app/routers/ingest.py`

**Decision:** Ingest routes (`/ingest/logs`, `/ingest/metrics`, `/ingest/events`) accept unauthenticated requests.

**Why:** Edge agents need simple HTTP POST with no token management. Device ID acts as implicit identifier.

**Tradeoff:** Any caller with a valid device_id UUID can inject data. Acceptable for MVP/private deploy. Add device-scoped API tokens before exposing to public internet.

---

## 9. Production: Render + Supabase (free tier)

**Rejected:** Railway (not truly free — $5 credit then $1/mo), Koyeb (less familiar).

**Chosen:** Render free web service + Supabase free Postgres.

**Tradeoffs:**
- Render: ~60s cold start after 15 min idle on free tier
- Supabase: DB pauses after 1 week of no activity (resumes on next request, ~30s)

---

## 10. Edge agent collector stubs

**Location:** `agents/edge-agent/internal/collector/system.go`

**Decision (temporary):** CPU, disk, and network metrics are simulated/estimated. Only memory uses real Go runtime stats.

**Comment in code:** "This is a cross-platform stub that returns simulated values. A production implementation would read from /proc (Linux) or use platform-specific syscalls."

**Action needed:** Replace with real `/proc` reads or `gopsutil` library before deploying to real Jetson devices.
