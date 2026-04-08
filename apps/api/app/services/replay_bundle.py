import json
import os
import uuid
import zipfile
from datetime import datetime, timezone
from io import BytesIO

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.device import Device, Deployment
from app.models.incident import Incident, IncidentArtifact, ArtifactType
from app.models.telemetry import EventLog, MetricPoint


async def generate_replay_bundle(incident_id: uuid.UUID, db: AsyncSession) -> str:
    """Generate a .zip replay bundle for an incident."""
    # Fetch incident
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one()

    # Fetch device
    device_result = await db.execute(select(Device).where(Device.id == incident.device_id))
    device = device_result.scalar_one()

    # Fetch deployment if exists
    deployment = None
    if incident.deployment_id:
        dep_result = await db.execute(
            select(Deployment).where(Deployment.id == incident.deployment_id)
        )
        deployment = dep_result.scalar_one_or_none()

    # Fetch events
    events_result = await db.execute(
        select(EventLog)
        .where(EventLog.incident_id == incident_id)
        .order_by(EventLog.timestamp)
    )
    events = events_result.scalars().all()

    # Fetch metrics
    metrics_result = await db.execute(
        select(MetricPoint)
        .where(MetricPoint.incident_id == incident_id)
        .order_by(MetricPoint.timestamp)
    )
    metrics = metrics_result.scalars().all()

    # Build bundle contents
    metadata = {
        "incident_id": str(incident.id),
        "title": incident.title,
        "severity": incident.severity.value,
        "status": incident.status.value,
        "trigger_type": incident.trigger_type,
        "started_at": incident.started_at.isoformat(),
        "resolved_at": incident.resolved_at.isoformat() if incident.resolved_at else None,
        "device": {
            "id": str(device.id),
            "name": device.device_name,
            "hardware_model": device.hardware_model,
            "os_version": device.os_version,
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    deployment_data = None
    if deployment:
        deployment_data = {
            "id": str(deployment.id),
            "version": deployment.version,
            "deployed_at": deployment.deployed_at.isoformat(),
            "metadata": deployment.metadata_json,
        }

    events_data = [
        {
            "timestamp": e.timestamp.isoformat(),
            "level": e.level.value,
            "source": e.source,
            "message": e.message,
            "metadata": e.metadata_json,
        }
        for e in events
    ]

    metrics_data = [
        {
            "timestamp": m.timestamp.isoformat(),
            "metric_name": m.metric_name,
            "value": m.value,
            "unit": m.unit,
            "labels": m.labels_json,
        }
        for m in metrics
    ]

    analysis_summary = incident.root_cause_summary or "No analysis performed yet."

    # Create zip bundle
    storage_dir = os.path.join(settings.storage_path, "bundles")
    os.makedirs(storage_dir, exist_ok=True)
    bundle_filename = f"tracemind-replay-{incident_id}.zip"
    bundle_path = os.path.join(storage_dir, bundle_filename)

    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("metadata.json", json.dumps(metadata, indent=2))
        zf.writestr("events.json", json.dumps(events_data, indent=2))
        zf.writestr("metrics.json", json.dumps(metrics_data, indent=2))
        if deployment_data:
            zf.writestr("deployment.json", json.dumps(deployment_data, indent=2))
        zf.writestr("analysis_summary.txt", analysis_summary)
        zf.writestr(
            "ros2_snapshot.json",
            json.dumps({"note": "ROS2 metadata snapshot placeholder"}, indent=2),
        )

    # Record artifact
    file_size = os.path.getsize(bundle_path)
    artifact = IncidentArtifact(
        incident_id=incident_id,
        artifact_type=ArtifactType.replay_bundle,
        file_path=bundle_path,
        size_bytes=file_size,
        created_at=datetime.now(timezone.utc),
    )
    db.add(artifact)
    await db.commit()

    return bundle_path
