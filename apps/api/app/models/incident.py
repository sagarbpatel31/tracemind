import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Severity(str, enum.Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class IncidentStatus(str, enum.Enum):
    open = "open"
    investigating = "investigating"
    resolved = "resolved"


class ArtifactType(str, enum.Enum):
    log_bundle = "log_bundle"
    metrics_bundle = "metrics_bundle"
    replay_bundle = "replay_bundle"
    ros2_snapshot = "ros2_snapshot"


class Incident(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "incidents"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"))
    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id"))
    deployment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("deployments.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(500))
    severity: Mapped[Severity] = mapped_column(Enum(Severity), default=Severity.medium)
    status: Mapped[IncidentStatus] = mapped_column(
        Enum(IncidentStatus), default=IncidentStatus.open
    )
    trigger_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    root_cause_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    analysis_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime] = mapped_column()
    resolved_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    project: Mapped["Project"] = relationship(back_populates="incidents")  # noqa: F821
    device: Mapped["Device"] = relationship(back_populates="incidents")  # noqa: F821
    deployment: Mapped[Optional["Deployment"]] = relationship(back_populates="incidents")  # noqa: F821
    artifacts: Mapped[list["IncidentArtifact"]] = relationship(back_populates="incident")
    event_logs: Mapped[list["EventLog"]] = relationship(back_populates="incident")  # noqa: F821
    metric_points: Mapped[list["MetricPoint"]] = relationship(back_populates="incident")  # noqa: F821
    annotations: Mapped[list["Annotation"]] = relationship(back_populates="incident")  # noqa: F821


class IncidentArtifact(UUIDMixin, Base):
    __tablename__ = "incident_artifacts"

    incident_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("incidents.id"))
    artifact_type: Mapped[ArtifactType] = mapped_column(Enum(ArtifactType))
    file_path: Mapped[str] = mapped_column(String(1000))
    size_bytes: Mapped[Optional[int]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column()

    incident: Mapped[Incident] = relationship(back_populates="artifacts")
