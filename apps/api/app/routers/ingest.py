from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.telemetry import EventLog, MetricPoint
from app.schemas.telemetry import EventBatchIngest, LogBatchIngest, MetricBatchIngest

router = APIRouter(prefix="/ingest", tags=["ingestion"])


@router.post("/logs")
async def ingest_logs(body: LogBatchIngest, db: AsyncSession = Depends(get_db)):
    entries = []
    for log in body.logs:
        entry = EventLog(
            device_id=log.device_id,
            incident_id=log.incident_id,
            timestamp=log.timestamp,
            level=log.level,
            source=log.source,
            message=log.message,
            metadata_json=log.metadata_json,
        )
        entries.append(entry)
    db.add_all(entries)
    await db.commit()
    return {"ingested": len(entries)}


@router.post("/metrics")
async def ingest_metrics(body: MetricBatchIngest, db: AsyncSession = Depends(get_db)):
    entries = []
    for metric in body.metrics:
        entry = MetricPoint(
            device_id=metric.device_id,
            incident_id=metric.incident_id,
            timestamp=metric.timestamp,
            metric_name=metric.metric_name,
            value=metric.value,
            unit=metric.unit,
            labels_json=metric.labels_json,
        )
        entries.append(entry)
    db.add_all(entries)
    await db.commit()
    return {"ingested": len(entries)}


@router.post("/events")
async def ingest_events(body: EventBatchIngest, db: AsyncSession = Depends(get_db)):
    entries = []
    for event in body.events:
        entry = EventLog(
            device_id=event.device_id,
            incident_id=event.incident_id,
            timestamp=event.timestamp,
            level=event.level,
            source=event.source,
            message=event.message,
            metadata_json=event.metadata_json,
        )
        entries.append(entry)
    db.add_all(entries)
    await db.commit()
    return {"ingested": len(entries)}
