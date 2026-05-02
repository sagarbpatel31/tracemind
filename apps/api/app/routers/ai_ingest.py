"""AI layer ingest endpoints.

Unauthenticated (same policy as /ingest/* routes) — Priority 3 to add auth.

Routes:
  POST /ingest/model-runs       Register a model run from the model-collector agent
  POST /ingest/inferences       Batch ingest inference frames
  POST /ingest/decisions        Batch ingest policy decisions
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.ai_layer import Decision, Inference, ModelRun
from app.schemas.ai_layer import (
    DecisionBatchCreate,
    InferenceBatchCreate,
    IngestResponse,
    ModelRunCreate,
    ModelRunResponse,
)

router = APIRouter(prefix="/ingest", tags=["ai-ingest"])


# ---------------------------------------------------------------------------
# Model runs
# ---------------------------------------------------------------------------


@router.post(
    "/model-runs",
    status_code=status.HTTP_201_CREATED,
    response_model=ModelRunResponse,
    summary="Register a model run",
    description=(
        "Called by the model-collector agent when a model starts running on a device. "
        "Returns the persisted model run with its assigned ID."
    ),
)
async def create_model_run(
    payload: ModelRunCreate,
    db: AsyncSession = Depends(get_db),
) -> ModelRunResponse:
    run = ModelRun(
        id=payload.id or uuid.uuid4(),
        device_id=payload.device_id,
        framework=payload.framework,  # type: ignore[arg-type]
        model_name=payload.model_name,
        weights_hash=payload.weights_hash,
        started_at=payload.started_at or datetime.now(timezone.utc),
        metadata_json=payload.metadata,
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return ModelRunResponse.model_validate(run)


# ---------------------------------------------------------------------------
# Inferences
# ---------------------------------------------------------------------------


@router.post(
    "/inferences",
    status_code=status.HTTP_201_CREATED,
    response_model=IngestResponse,
    summary="Batch ingest inference frames",
    description=(
        "Accept a batch of inference frames captured by the model-collector hook adapter. "
        "Each frame records one forward pass through the model."
    ),
)
async def ingest_inferences(
    payload: InferenceBatchCreate,
    db: AsyncSession = Depends(get_db),
) -> IngestResponse:
    rows: list[Inference] = []
    for item in payload.inferences:
        rows.append(
            Inference(
                id=item.inference_id or uuid.uuid4(),
                model_run_id=item.model_run_id,
                device_id=item.device_id,
                incident_id=item.incident_id,
                timestamp_ns=item.timestamp_ns,
                input_hash=item.input_hash,
                input_ref=item.input_ref,
                outputs=item.outputs,
                confidence=item.confidence,
                latency_ms=item.latency_ms,
                gpu_mem_mb=item.gpu_mem_mb,
                layer_name=item.layer_name,
                output_mean=item.output_mean,
                output_std=item.output_std,
            )
        )
    db.add_all(rows)
    await db.commit()
    return IngestResponse(created=len(rows))


# ---------------------------------------------------------------------------
# Decisions
# ---------------------------------------------------------------------------


@router.post(
    "/decisions",
    status_code=status.HTTP_201_CREATED,
    response_model=IngestResponse,
    summary="Batch ingest policy decisions",
    description=(
        "Accept a batch of policy decision records. "
        "Each decision references an inference and records what action was chosen."
    ),
)
async def ingest_decisions(
    payload: DecisionBatchCreate,
    db: AsyncSession = Depends(get_db),
) -> IngestResponse:
    now = datetime.now(timezone.utc)
    rows: list[Decision] = []
    for item in payload.decisions:
        rows.append(
            Decision(
                inference_id=item.inference_id,
                policy_name=item.policy_name,
                action=item.action,
                alternatives={"items": item.alternatives} if item.alternatives else None,
                confidence=item.confidence,
                timestamp_ns=item.timestamp_ns,
                created_at=now,
            )
        )
    db.add_all(rows)
    await db.commit()
    return IngestResponse(created=len(rows))
