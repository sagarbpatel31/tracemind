# Failure Patterns

Bugs hit during build, how they manifested, and how they were fixed. Read before debugging.

---

## 1. passlib + bcrypt 4.x incompatibility

**Symptom:** `ValueError: password cannot be longer than 72 bytes, truncate manually` on ANY login attempt, even 6-char passwords.

**Root cause:** passlib's bcrypt wrapper calls an internal bcrypt API that changed in bcrypt 4.x. Passlib hasn't been updated.

**Fix:** Remove `passlib[bcrypt]` from deps. Import `bcrypt` directly. Use `bcrypt.hashpw` / `bcrypt.checkpw`.

**Files:** `apps/api/app/security.py`, `apps/api/pyproject.toml`

---

## 2. shadcn Button `asChild` TypeScript error

**Symptom:** `Property 'asChild' does not exist on type 'ButtonHTMLAttributes<...>'` — build fails.

**Root cause:** This project uses shadcn/ui v5 (base-ui variant). v5 does NOT have `asChild` prop on Button.

**Fix:** Replace `<Button asChild><Link href="...">text</Link></Button>` with:
```tsx
import { buttonVariants } from "@/components/ui/button"
import { cn } from "@/lib/utils"
<Link href="..." className={cn(buttonVariants({ variant: "default" }))}>text</Link>
```

**Files:** Any page using `<Button asChild>` — check `apps/web/src/app/`

---

## 3. `apps/web` committed as git submodule

**Symptom:** `git status` shows `apps/web` as `160000` mode (submodule). `git add apps/web/` doesn't stage files inside it.

**Root cause:** `create-next-app` initializes a `.git` directory inside `apps/web/`, which git treats as a submodule.

**Fix:**
```bash
rm -rf apps/web/.git
git rm --cached apps/web
git add apps/web/
```

---

## 4. Edge agent payload format mismatch

**Symptom:** API returns 422 Unprocessable Entity when edge agent POSTs metrics.

**Root cause:** Edge agent was sending flat `[{metric_name, value, ...}]` array. API ingest route expects `{metrics: [{...}, ...]}` batch wrapper object.

**Fix:** Update `agents/edge-agent/internal/sender/http.go` to wrap payload:
```go
payload := map[string]interface{}{"metrics": metricsArray}
```

---

## 5. Missing DB columns after auth was added

**Symptom:** `asyncpg.exceptions.UndefinedColumnError: column users.password_hash does not exist`

**Root cause:** `create_all` only creates new tables; it doesn't add columns to existing tables. The `users` table was created before `password_hash` and `is_active` were added to the model.

**Fix (dev — no migrations):**
```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255) DEFAULT '';
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
```

**Permanent fix:** Alembic migrations (see next_steps.md #11).

---

## 6. Seed endpoint fails on re-seed (unique constraint)

**Symptom:** `POST /api/v1/seed/demo` returns 500 after first run. `asyncpg.exceptions.UniqueViolationError` on device_name or email.

**Root cause:** Seed is not idempotent — it tries to INSERT rows that already exist.

**Workaround:** The seed endpoint uses `INSERT ... ON CONFLICT DO NOTHING` for most rows. If it still fails: truncate or drop the relevant tables and re-run.

**Note:** On fresh Supabase DB (first deploy), seed runs cleanly.

---

## 7. Docker daemon not in PATH

**Symptom:** `command not found: docker` even though Docker Desktop is running.

**Root cause:** Shell PATH doesn't include Docker Desktop's binary directory in some terminals.

**Fix:** Use full path: `/Applications/Docker.app/Contents/Resources/bin/docker`

---

## 8. Port 3000 conflict between Docker web container and preview server

**Symptom:** Preview server (Claude Code) fails to start: "Port 3000 is required but is in use."

**Root cause:** Docker Compose web service bound to host port 3000.

**Fix:** Stop Docker web container before starting preview:
```bash
docker stop tracemind-web-1
```
Or change Docker Compose web port mapping to `3001:3000`.

---

## 9. `postgres://` URL rejected by SQLAlchemy/asyncpg

**Symptom:** `sqlalchemy.exc.ArgumentError: Could not parse rfc1738 URL from string 'postgres://...'`

**Root cause:** Supabase/Render/Heroku expose `postgres://` scheme. SQLAlchemy requires `postgresql+asyncpg://`.

**Fix:** Already handled automatically in `config.py` via `normalize_postgres_url()`. No manual fix needed if using `settings.database_url`.

---

## 10. `uv` not in PATH on macOS (arm64)

**Symptom:** `command not found: uv` when trying to install graphify.

**Root cause:** uv installs to `~/.local/bin` which may not be in the shell PATH during programmatic execution.

**Fix:** Use full path: `/Users/sagarpatel/.local/bin/uv`
