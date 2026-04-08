import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Annotation(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "annotations"

    incident_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("incidents.id"))
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    content: Mapped[str] = mapped_column(Text)
    annotation_type: Mapped[str] = mapped_column(String(50), default="note")

    incident: Mapped["Incident"] = relationship(back_populates="annotations")  # noqa: F821
    user: Mapped[Optional["User"]] = relationship(back_populates="annotations")  # noqa: F821
