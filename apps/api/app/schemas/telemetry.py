import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.telemetry import LogLevel


class LogEntry(BaseModel):
    device_id: uuid.UUID
    incident_id: Optional[uuid.UUID] = None
    timestamp: datetime
    level: LogLevel = LogLevel.info
    source: str
    message: str
    metadata_json: Optional[dict] = None


class LogBatchIngest(BaseModel):
    logs: list[LogEntry]


class MetricEntry(BaseModel):
    device_id: uuid.UUID
    incident_id: Optional[uuid.UUID] = None
    timestamp: datetime
    metric_name: str
    value: float
    unit: Optional[str] = None
    labels_json: Optional[dict] = None


class MetricBatchIngest(BaseModel):
    metrics: list[MetricEntry]


class EventEntry(BaseModel):
    device_id: uuid.UUID
    incident_id: Optional[uuid.UUID] = None
    timestamp: datetime
    source: str
    message: str
    level: LogLevel = LogLevel.info
    metadata_json: Optional[dict] = None


class EventBatchIngest(BaseModel):
    events: list[EventEntry]


class LogResponse(BaseModel):
    id: uuid.UUID
    device_id: uuid.UUID
    incident_id: Optional[uuid.UUID]
    timestamp: datetime
    level: LogLevel
    source: str
    message: str
    metadata_json: Optional[dict]

    model_config = {"from_attributes": True}


class MetricResponse(BaseModel):
    id: uuid.UUID
    device_id: uuid.UUID
    incident_id: Optional[uuid.UUID]
    timestamp: datetime
    metric_name: str
    value: float
    unit: Optional[str]
    labels_json: Optional[dict]

    model_config = {"from_attributes": True}
