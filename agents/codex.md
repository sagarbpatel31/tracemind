# Codex Usage Rules — Watchpoint

These rules apply to all OpenAI Codex / Codex CLI sessions on this repository.

---

## BEFORE WRITING ANY CODE — read in this order

1. `.ai/architecture.md` — system topology, all models, all API routes
2. `.ai/current_task.md` — what is in progress, what is done, what is pending
3. `.ai/next_steps.md` — ordered engineering backlog
4. `.ai/failure_patterns.md` — confirmed bugs with exact fixes

Do not generate code until these four files have been read.

---

## Stack facts (do not assume defaults)

| Layer | Tech | Notes |
|-------|------|-------|
| Backend | FastAPI 0.115, Python 3.11, SQLAlchemy 2.0 async, asyncpg | All DB ops are `async` with `AsyncSession` |
| ORM | Mapped[] + mapped_column() (SQLAlchemy 2.0 style) | NOT Column() legacy style |
| Auth | python-jose (JWT), bcrypt (direct) | NOT passlib |
| Frontend | Next.js 16, TypeScript, Tailwind, shadcn/ui v5 (base-ui) | No `asChild` prop on Button |
| DB | Postgres 16, JSONB for evolving schemas | No active Alembic migrations |
| LLM | anthropic SDK, claude-haiku-4-5, async | Optional — fallback required |

---

## Inviolable constraints

### 1. Never add passlib
```python
# WRONG
from passlib.context import CryptContext

# CORRECT
import bcrypt
bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
```

### 2. Never use asChild on Button
```tsx
// WRONG — TypeScript error in shadcn v5
<Button asChild><Link href="/x">text</Link></Button>

// CORRECT
import { buttonVariants } from "@/components/ui/button"
<Link href="/x" className={cn(buttonVariants({ variant: "default" }))}>text</Link>
```

### 3. Ingest payload format
```python
# WRONG
POST /ingest/metrics  body: [{metric_name: ..., value: ...}]

# CORRECT
POST /ingest/metrics  body: {"metrics": [{metric_name: ..., value: ...}]}
```

### 4. All LLM calls have non-LLM fallback
```python
if not settings.anthropic_api_key:
    return fallback_value  # system works without API key
```

### 5. New DB columns require ALTER TABLE
`create_all` does not add columns to existing tables. For any new model field:
```sql
ALTER TABLE tablename ADD COLUMN IF NOT EXISTS colname TYPE DEFAULT value;
```

---

## API route reference

All routes prefixed `/api/v1`. See `.ai/architecture.md` for full table.

Key routes for most tasks:
```
POST /auth/login           → JWT token
POST /incidents/{id}/analyze      → runs 7 rules + optional LLM
POST /incidents/{id}/replay-bundle → generates ZIP
POST /ingest/metrics       → {metrics:[...]}
POST /seed/demo            → creates demo@watchpoint.ai + sample data
```

---

## Model conventions

All models extend `UUIDMixin` (uuid4 PK) and `TimestampMixin` (created_at, updated_at):
```python
from app.models.base import Base, UUIDMixin, TimestampMixin

class MyModel(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "my_models"
    # fields...
```

All datetimes are timezone-aware (`DateTime(timezone=True)` via type_annotation_map in Base).

---

## Service pattern

Analysis and replay bundle are in `apps/api/app/services/`. New business logic goes here, not in routers. Routers call services; services use `AsyncSession`.

```python
async def my_service(id: uuid.UUID, db: AsyncSession) -> dict:
    result = await db.execute(select(Model).where(Model.id == id))
    obj = result.scalar_one_or_none()
    ...
    return {...}
```

---

## Do not touch

- `apps/api/app/config.py:normalize_postgres_url()` — do not modify URL normalization logic
- `apps/api/app/security.py` — auth logic is stable; do not add passlib
- `apps/web/src/lib/auth.ts` — token storage keys must remain `watchpoint_token` / `watchpoint_user`
- `deploy/docker-compose/docker-compose.yml` — do not change port mappings or service names
- `apps/api/render.yaml` — do not remove or rename env var keys
