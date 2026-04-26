# Failure Patterns

Confirmed bugs encountered during this build, with exact symptoms and fixes. Read before debugging.

---

## 1. passlib + bcrypt 4.x incompatibility (FIXED)

**Symptom:** `ValueError: password cannot be longer than 72 bytes, truncate manually` on any login attempt, even 4-char passwords.

**Root cause:** passlib's bcrypt wrapper calls internal API changed in bcrypt 4.x. Passlib unmaintained against it.

**Fix:** Removed `passlib[bcrypt]`. Uses `import bcrypt` directly:
```python
bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
```
**Files:** `apps/api/app/security.py`, `apps/api/pyproject.toml`

---

## 2. shadcn v5 `asChild` TypeScript error (FIXED)

**Symptom:** `Property 'asChild' does not exist on type 'ButtonHTMLAttributes<HTMLButtonElement>'` — TypeScript build fails.

**Root cause:** shadcn/ui v5 (base-ui variant) removed the Radix `asChild` prop from Button.

**Fix:**
```tsx
// WRONG
<Button asChild><Link href="/x">text</Link></Button>

// CORRECT
import { buttonVariants } from "@/components/ui/button"
<Link href="/x" className={cn(buttonVariants({ variant: "default" }))}>text</Link>
```
**Files:** Any page with link-styled-as-button — `apps/web/src/app/`

---

## 3. apps/web committed as git submodule (FIXED)

**Symptom:** `git status` shows `apps/web` as `160000` (submodule mode). Files inside not staged.

**Root cause:** `create-next-app` created `.git/` inside `apps/web/`, making git treat it as a submodule.

**Fix:**
```bash
rm -rf apps/web/.git
git rm --cached apps/web
git add apps/web/
```

---

## 4. Edge agent payload format mismatch (FIXED)

**Symptom:** API returns `422 Unprocessable Entity` when agent POSTs metrics.

**Root cause:** Agent was sending flat `[{metric_name, value, ...}]`. API expects `{metrics: [{...}]}` wrapper.

**Fix:** `agents/edge-agent/internal/sender/http.go` wraps payload:
```go
payload := map[string]interface{}{"metrics": metricsArray}
```

---

## 5. Missing DB columns after model change (FIXED)

**Symptom:** `asyncpg.exceptions.UndefinedColumnError: column users.password_hash does not exist`

**Root cause:** `create_all` only creates new tables, not new columns on existing tables. `users` table existed before `password_hash` / `is_active` were added to the model.

**Fix (dev workaround):**
```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255) DEFAULT '';
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
```
**Permanent fix:** Initialize and run Alembic migrations before any schema change on a live DB.

---

## 6. Seed endpoint UniqueViolationError on re-seed (KNOWN)

**Symptom:** `POST /api/v1/seed/demo` returns 500 after first run.

**Root cause:** Seed inserts rows that already exist; not fully idempotent.

**Workaround:**
```sql
TRUNCATE users, workspaces, projects, devices, deployments, incidents,
  event_logs, metric_points, incident_artifacts, annotations CASCADE;
```
Then re-run seed. Safe on dev/staging, never on prod with real data.

---

## 7. Docker not in PATH (KNOWN ENVIRONMENT)

**Symptom:** `command not found: docker` even with Docker Desktop running.

**Fix:** Use full path:
```bash
/Applications/Docker.app/Contents/Resources/bin/docker compose up
```

---

## 8. Port 3000 conflict (docker web vs preview server)

**Symptom:** Claude Code preview server fails: "Port 3000 is required but is in use."

**Root cause:** Docker Compose web service binds host:3000.

**Fix:**
```bash
docker stop tracemind-web-1
# or change docker-compose.yml web port to 3001:3000
```

---

## 9. `postgres://` URL rejected by SQLAlchemy/asyncpg (FIXED)

**Symptom:** `sqlalchemy.exc.ArgumentError: Could not parse rfc1738 URL from string 'postgres://...'`

**Root cause:** Supabase/Render emit `postgres://`. SQLAlchemy+asyncpg requires `postgresql+asyncpg://`.

**Fix:** Already auto-handled by `normalize_postgres_url()` in `app/config.py`. Do not manually edit URLs.

---

## 10. uv not in PATH (KNOWN ENVIRONMENT)

**Symptom:** `command not found: uv`

**Fix:** Full path: `/Users/sagarpatel/.local/bin/uv`

---

## Known risks (not yet hit, but likely)

### R1. Schema change on live Supabase DB
`create_all` will not add columns or modify types. Any model change after first deploy requires manual `ALTER TABLE` or Alembic migration. **High risk once production is live.**

### R2. Render cold start timeouts
First request after 15 min idle takes ~60s. If frontend sets a short API timeout, the first load will fail silently. Frontend should handle loading states generously.

### R3. Supabase pause
Free tier pauses DB after 1 week of inactivity. First request after pause succeeds but with ~30s latency. Consider a health-check ping cron if the app needs to stay responsive.

### R4. Ingest without auth
`/ingest/*` routes accept any caller with a known device_id. If the repo is public and a device_id leaks, anyone can inject telemetry. Add device API tokens before exposing to untrusted networks.
