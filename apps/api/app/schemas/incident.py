import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.incident import ArtifactType, IncidentStatus, Severity


class IncidentCreate(BaseModel):
    project_id: uuid.UUID
    device_id: uuid.UUID
    deployment_id: Optional[uuid.UUID] = None
    title: str
    severity: Severity = Severity.medium
    trigger_type: Optional[str] = None
    started_at: Optional[datetime] = None


class IncidentResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    device_id: uuid.UUID
    deployment_id: Optional[uuid.UUID]
    title: str
    severity: Severity
    status: IncidentStatus
    trigger_type: Optional[str]
    root_cause_summary: Optional[str]
    analysis_json: Optional[dict]
    started_at: datetime
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IncidentListResponse(BaseModel):
    incidents: list[IncidentResponse]
    total: int


class IncidentDetailResponse(IncidentResponse):
    device_name: Optional[str] = None
    deployment_version: Optional[str] = None
    event_count: int = 0
    metric_count: int = 0


class AnalysisResult(BaseModel):
    probable_causes: list[dict]
    evidence: list[dict]
    suggested_steps: list[str]
    similar_incidents: list[uuid.UUID] = []


class ArtifactResponse(BaseModel):
    id: uuid.UUID
    incident_id: uuid.UUID
    artifact_type: ArtifactType
    file_path: str
    size_bytes: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}
