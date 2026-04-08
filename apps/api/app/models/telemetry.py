import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin


class LogLevel(str, enum.Enum):
    debug = "debug"
    info = "info"
    warn = "warn"
    error = "error"
    fatal = "fatal"


class EventLog(UUIDMixin, Base):
    __tablename__ = "event_logs"

    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id"), index=True)
    incident_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("incidents.id"), nullable=True, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(index=True)
    level: Mapped[LogLevel] = mapped_column(Enum(LogLevel), default=LogLevel.info)
    source: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    device: Mapped["Device"] = relationship(back_populates="event_logs")  # noqa: F821
    incident: Mapped[Optional["Incident"]] = relationship(back_populates="event_logs")  # noqa: F821


class MetricPoint(UUIDMixin, Base):
    __tablename__ = "metric_points"

    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id"), index=True)
    incident_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("incidents.id"), nullable=True, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(index=True)
    metric_name: Mapped[str] = mapped_column(String(255), index=True)
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    labels_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    device: Mapped["Device"] = relationship(back_populates="metric_points")  # noqa: F821
    incident: Mapped[Optional["Incident"]] = relationship(back_populates="metric_points")  # noqa: F821
