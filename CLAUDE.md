# Watchpoint — Engineering Spec & Claude Code Bootstrap

> **One-liner:** *AI failure forensics for physical AI. When your robot fails in the field, we tell you why — at the AI layer, not just the logs.*
>
> **Repo:** https://github.com/sagarbpatel31/watchpoint (public)

---

## ⚠️ READ BEFORE CODING

Read these files before writing any production code:

```
1. .ai/architecture.md      — system topology, all models, all routes
2. .ai/current_task.md      — what's in progress, what's done, what's blocked
3. .ai/next_steps.md        — ordered engineering backlog
4. .ai/failure_patterns.md  — confirmed bugs with exact fixes (read before debugging)
```

Additional context:
```
.ai/decisions.md      — why key technical choices were made
.ai/principles.md     — engineering rules for this repo
.ai/debugging.md      — per-error-class debugging workflow
.ai/handoff.md        — concise state summary for resuming after context break
agents/CLAUDE.md      — Claude-specific usage rules (hard constraints, tool paths, commit style)
```

---

## Session rules

- Always run `make test` and `make lint` before saying a task is done.
- When adding a new file, mirror the style and structure of the closest existing
  file in the same module.
- If you're uncertain about a design choice, ask before implementing —
  do not pick silently.
- Update `CHANGELOG.md` as part of the same commit.

---

## Non-negotiable rules (memorize these)

| Rule | Detail |
|------|--------|
| No passlib | Use `import bcrypt` directly — passlib breaks on bcrypt 4.x / Python 3.11 |
| No `asChild` on Button | shadcn v5 doesn't have it — use `buttonVariants()` spread on Link |
| Ingest format | `{metrics:[...]}` not `[...]` — all agents depend on this |
| LLM fallback required | Every LLM call returns rules text / default if `ANTHROPIC_API_KEY` is empty |
| No hardcoded secrets | JWT key and Anthropic key via env vars only |
| URL normalization | `config.py` handles `postgres://` → `postgresql+asyncpg://` automatically |
| Alembic before schema changes | `alembic/versions/` must have migrations before any new column on live DB |

---

## Repository layout

```
apps/api/                   FastAPI backend (Python 3.11, SQLAlchemy 2.0 async, asyncpg)
apps/web/                   Next.js 16 frontend (TypeScript, Tailwind, shadcn/ui v5)
agents/edge-agent/          Go — system metrics collector (CPU/disk/net stubs)
agents/ros2-collector/      Python — ROS2 topic/node monitor (simulation mode)
agents/model-collector/     Python — PyTorch/ONNX/TensorRT hook capture (NEW — Week 1)
packages/sample-data/       Seed script + JSON fixtures (3 system + 3 AI layer demos)
deploy/docker-compose/      Local dev stack (postgres + api + web)
.ai/                        AI engineering context — READ BEFORE CODING
```

---

## Local dev

```bash
cd deploy/docker-compose
/Applications/Docker.app/Contents/Resources/bin/docker compose up -d
curl -X POST http://localhost:8000/api/v1/seed/demo
# open http://localhost:3000  →  demo@watchpoint.ai / demo123
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

After modifying code: `graphify update .`

---

## 1. The product

A self-hosted (and eventually SaaS) observability and incident-analysis platform for robots and edge AI systems. Captures system-level telemetry **and** model-level introspection (inputs, outputs, attention, decisions), then lets users replay incidents deterministically through the model to find root cause at the AI layer.

**Primary users:** small-to-midsize robotics startups (10–200 engineers) running ROS 2 or custom edge stacks.

The wedge — what existing tools miss:
1. **What the model saw** (synced sensor frames + lidar + depth)
2. **What the model predicted** (outputs, confidence, attention/saliency maps)
3. **What the policy decided** (action, alternatives, confidence)
4. **Whether the input was OOD** (out-of-distribution from training data)

---

## 2. Current state

**Working today:**
- Edge agent: CPU, memory, disk, thermal, log tails
- ROS 2 collector: topic publish rates, node health, message lag
- 7-rule RCA engine + optional Claude Haiku 2-sentence summary
- Replay bundles: ZIP exports
- 3 demo scenarios: CPU contention, thermal throttling, version regression

**What's missing (this spec):**
- `agents/model-collector/` — PyTorch/ONNX/TensorRT hooks (Week 1)
- Sensor sync in ros2-collector (image/lidar/depth ring buffer) (Week 2)
- Backend AI tables: `ModelRun`, `Inference`, `Decision`, `OODSignal` (Week 2)
- AI failure rules AI-001 through AI-008 (Week 4)
- Replay sandbox `apps/replay-runner/` (Week 5)
- Frontend: `/inferences/[id]`, `<AttentionOverlay />`, `<DecisionTree />`, `<OODHeatmap />` (Week 3+)
- Demo scenarios 4, 5, 6 (Week 4–5)

---

## 3. New modules — specs

### 3.1 `agents/model-collector/` (NEW — Python)

**Design constraints:**
- < 1% runtime overhead at p99
- Zero-copy where possible (numpy views, not pickling)
- Ring-buffered locally, only flushed on incident trigger
- Pluggable adapters: PyTorch first, ONNX Runtime second, TensorRT third

**File layout:**
```
agents/model-collector/
├── pyproject.toml
├── model_collector/
│   ├── __init__.py
│   ├── ring_buffer.py           # thread-safe fixed-size deque
│   ├── writer.py                # flush to {incident_id}/run_{ts}.msgpack
│   ├── config.py                # CollectorConfig
│   ├── sender.py                # HTTP flush to backend
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── pytorch_adapter.py   # register_forward_hook
│   │   ├── onnx_adapter.py      # ONNX Runtime profiler
│   │   └── tensorrt_adapter.py  # IExecutionContext
│   └── introspection/
│       ├── gradcam.py           # Grad-CAM for CNNs (Week 3)
│       ├── attention.py         # Attention rollout for ViT (Week 3)
│       └── embeddings.py        # Penultimate-layer extraction (Week 3)
└── tests/
```

**Public API:**
```python
from model_collector import Collector
from model_collector.adapters.pytorch_adapter import attach_hooks

collector = Collector(device_id="robot-01", backend_url="http://...:8000")
attach_hooks(model, collector, layer_names=["backbone.layer4", "head"])
output = model(input_tensor)   # capture is transparent
collector.flush(incident_id="...")
```

**Captured per inference:** `inference_id`, `device_id`, `model_run_id`, `timestamp_ns`, `input_hash`, `input_ref`, `outputs`, `intermediate_activations`, `latency_per_layer_ms`, `gpu_mem_used_mb`, `confidence`, `attention_map_ref`

### 3.2 Sensor collector extension (Week 2)

Extend `agents/ros2-collector/` with:
- 30s rolling buffer per image/lidar/depth topic
- Approximate-time sync with model-collector inference IDs (tolerance: 50ms)
- Keyframe + diff compression (OpenCV), voxel downsampling (5cm) for point clouds

### 3.3 Backend extensions — `apps/api/`

**New tables** (Alembic migration `0002_ai_layer.py`):
- `ModelRun` — framework, model_name, weights_hash, started_at, metadata_json
- `Inference` — model_run_id, device_id, timestamp_ns, input_hash, input_ref, outputs(JSONB), confidence, latency_ms, incident_id
- `Decision` — inference_id, policy_name, action, alternatives(JSONB), confidence
- `OODSignal` — inference_id, signal_type, score, threshold, is_ood

**New endpoints:**
```
POST /api/v1/ingest/model-runs
POST /api/v1/ingest/inferences
POST /api/v1/ingest/decisions
GET  /api/v1/incidents/{id}/inferences
GET  /api/v1/inferences/{id}
GET  /api/v1/inferences/{id}/attention
POST /api/v1/incidents/{id}/replay
GET  /api/v1/replay/{job_id}
```

### 3.4 Replay sandbox — `apps/replay-runner/` (Week 5)

Phase 1: Docker subprocess. Receives `incident_id` + `inference_id_range`, pulls framework container + weights + captured inputs, runs inference, diffs against original outputs.

### 3.5 Frontend additions (Week 3+)

New routes: `/devices/[id]/models`, `/incidents/[id]/inferences`, `/inferences/[id]`, `/incidents/[id]/replay`

New components: `<InferenceTimeline />`, `<AttentionOverlay />`, `<DecisionTree />`, `<OODHeatmap />`, `<ReplayDiff />`

---

## 4. AI failure taxonomy

| Rule ID | Name | Trigger | Severity |
|---------|------|---------|---------|
| AI-001 | Perception confidence collapse | Detection conf p50 over 60s drops > 30% from baseline | high |
| AI-002 | OOD input detected | Embedding distance > 3σ from training-set centroid | medium |
| AI-003 | Inference latency spike | p99 latency over 60s > 2x baseline | medium |
| AI-004 | Per-layer latency anomaly | Single layer latency > 5x baseline (TensorRT only) | low |
| AI-005 | Decision-perception mismatch | Policy chose action incompatible with high-conf detection | high |
| AI-006 | Attention drift | Attention center-of-mass shifted > 50% of frame from baseline | low |
| AI-007 | Output saturation | Softmax entropy < 0.1 nats on diverse inputs | medium |
| AI-008 | Sensor degradation upstream of model | Image sharpness / lidar density dropped > 40% from baseline | medium |

Rules live in `apps/api/app/rca/ai_rules/` inheriting from `BaseRule`.

---

## 5. Demo scenarios

**Demo 4 — Shadow misclassification** (attention overlay): YOLO robot stops mid-mission; Grad-CAM shows model fixated on shadow; OOD signal fires (2.7σ). Replay with new weights = no obstacle detected.

**Demo 5 — Sensor degradation cascade** (confidence drift + AI-008): Camera lens fogs over 20 min; detection p50 drifts 0.93→0.62; AI-001 + AI-008 fire together; system metrics look fine throughout.

**Demo 6 — Policy-perception mismatch** (decision trace): Pedestrian detected at 0.96 conf; policy chose "continue" over "reroute" due to misweighted config; AI-005 fires.

Seeds in `packages/sample-data/seed_ai_layer.py`.

---

## 6. Phased build order

| Week | Deliverable |
|------|------------|
| **1** | `agents/model-collector/` PyTorch adapter + ring buffer. Script: YOLO on test video → dump tensors to disk. |
| **2** | Alembic migration for AI tables. Ingest endpoints. ros2-collector image buffer + sync. |
| **3** | Grad-CAM API endpoint. `/inferences/[id]/attention` page. `<AttentionOverlay />`. |
| **4** | AI rules AI-001, AI-002. Demo 4 seed. Rules engine tags incidents. |
| **5** | Replay sandbox Phase 1. Demos 5, 6. Decision trace viz. |
| **6** | Polish, demo video, YC application, blog: "8 ways your robot's AI fails silently". |

---

## 7. Coding conventions

**Python:** Python 3.11+, `from __future__ import annotations`, ruff, mypy --strict on `apps/api/app/` and `agents/model-collector/`. pytest-asyncio, ≥70% coverage on new modules.

**TypeScript:** strict mode, no `any`. Server Components by default. shadcn/ui only. Recharts for charts, d3 only when Recharts can't.

**Go:** stdlib only. Cross-compile: `linux/amd64`, `linux/arm64`, `linux/arm/v7`.

**Commits:** conventional commits (`feat:`, `fix:`, `docs:`, `chore:`). PRs over direct main even solo.

---

## 8. What we're NOT building (resist scope creep)

❌ Teleoperation · Fleet orchestration / OTA · Digital twin · Mobile app · Multi-tenant billing · Custom auth · Foundation model fine-tuning UI · Anomaly detection ML models · Kubernetes-native deployment · Mac/Windows edge agent

---

*Last updated: 2026-05-01. Owner: Sagar Patel.*
