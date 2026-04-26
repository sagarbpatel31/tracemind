# Engineering Principles

Rules for this codebase. Follow these before adding anything.

---

## 1. Incident case file, not dashboard

TraceMind's core artifact is the **incident case file** — a full investigative record with timeline, telemetry, root cause, and replay bundle. Not charts. Not dashboards.

Every feature should answer: *does this help an engineer understand what happened and why?*

## 2. Rules first, LLM second

Deterministic rules run before any LLM call. The LLM only synthesizes structured rule output into prose — it does not reason, infer, or replace logic.

Benefits: rules are free, instant, testable, and work offline. LLM layer is opt-in via `ANTHROPIC_API_KEY`.

## 3. Token budget discipline

Every LLM call has explicit token limits:
- Input: cap evidence to 4 signals (~120 tokens)
- Output: `max_tokens=80` hard ceiling
- Model: Haiku unless task requires reasoning

Use caveman-style terse prompts: *"Write 2 sentences: what failed and what to do. Terse. No preamble."*

## 4. Graceful degradation

Every external dependency has a fallback:
- No `ANTHROPIC_API_KEY` → return rules-based summary text
- No agent data → incident still creatable manually
- Supabase paused → app shows connection error, not data corruption

## 5. Do not build outside the wedge

Do NOT add: fleet orchestration, teleoperation, OTA updates, digital twin, simulation, real-time video, general DevOps tooling.

TraceMind's wedge: **incident intelligence and reproducibility for ROS2 + Jetson/Linux teams.**

## 6. Keep the schema flexible with JSONB

Use JSONB columns (`analysis_json`, `metadata_json`, `labels_json`) for evolving data structures. Don't add columns for every new field — serialize into JSONB until the shape is stable.

## 7. No migrations until real data exists

`Base.metadata.create_all()` on startup is fine for MVP. Add Alembic before the first real customer's data is in production.

## 8. Security defaults

- JWT secret must come from env var (`JWT_SECRET_KEY`) — never hardcode
- `ANTHROPIC_API_KEY` is optional and never logged
- Demo password `demo123` is acceptable for seeded demo data only
- All secrets injected via Render env vars, never in source

## 9. Monorepo discipline

Each `apps/` service is independently buildable and deployable. Don't import across `apps/` boundaries. Agents in `agents/` talk to the API via HTTP only — no direct DB access.

## 10. Agent protocol

Edge agents communicate with the API via:
- `POST /api/v1/devices/register` — on startup
- `POST /api/v1/ingest/metrics` — batch: `{metrics: [{...}]}`
- `POST /api/v1/ingest/logs` — batch: `{logs: [{...}]}`
- `POST /api/v1/devices/heartbeat/{device_id}` — keep-alive

No other API surface is accessible to agents. Auth for agents: device_id (no JWT for agents in MVP).
