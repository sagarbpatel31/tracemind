import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.device import Deployment, Device, DeviceStatus
from app.schemas.device import (
    DeploymentCreate,
    DeploymentResponse,
    DeviceRegister,
    DeviceResponse,
)

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/register", response_model=DeviceResponse)
async def register_device(body: DeviceRegister, db: AsyncSession = Depends(get_db)):
    device = Device(
        project_id=body.project_id,
        device_name=body.device_name,
        hardware_model=body.hardware_model,
        os_version=body.os_version,
        agent_version=body.agent_version,
        status=DeviceStatus.online,
        last_seen_at=datetime.now(timezone.utc),
        registered_at=datetime.now(timezone.utc),
    )
    db.add(device)
    await db.commit()
    await db.refresh(device)
    return device


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.get("/", response_model=list[DeviceResponse])
async def list_devices(project_id: uuid.UUID | None = None, db: AsyncSession = Depends(get_db)):
    query = select(Device)
    if project_id:
        query = query.where(Device.project_id == project_id)
    query = query.order_by(Device.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/heartbeat/{device_id}")
async def device_heartbeat(device_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    device.last_seen_at = datetime.now(timezone.utc)
    device.status = DeviceStatus.online
    await db.commit()
    return {"status": "ok"}


@router.post("/deployments", response_model=DeploymentResponse)
async def create_deployment(body: DeploymentCreate, db: AsyncSession = Depends(get_db)):
    deployment = Deployment(
        device_id=body.device_id,
        version=body.version,
        metadata_json=body.metadata_json,
        deployed_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )
    db.add(deployment)
    await db.commit()
    await db.refresh(deployment)
    return deployment
