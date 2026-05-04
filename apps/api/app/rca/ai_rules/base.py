"""Base class for AI-layer RCA rules."""

from __future__ import annotations

import statistics
import uuid
from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_layer import Inference, OODSignal


class AIBaseRule(ABC):
    """Interface for AI-layer root-cause rules.

    Each subclass inspects AI-layer data (Inference, OODSignal, Decision)
    for a single incident and returns a finding dict or None.

    Finding dict format (compatible with analysis.py probable_causes):
    {
        "rule_id":        str          # e.g. "AI-001"
        "cause":          str          # short label shown in UI
        "confidence":     float        # 0.0–1.0
        "description":    str          # 1–2 sentence explanation
        "evidence":       list[dict]   # appended to global evidence list
        "suggested_steps": list[str]   # appended to global suggestions
    }
    """

    rule_id: str = ""
    name: str = ""

    @abstractmethod
    async def evaluate(self, incident_id: uuid.UUID, db: AsyncSession) -> dict[str, Any] | None:
        """Evaluate the rule for `incident_id`. Return finding or None."""

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    async def _get_inferences(self, incident_id: uuid.UUID, db: AsyncSession) -> list[Inference]:
        """Fetch all inferences for incident ordered by timestamp_ns."""
        result = await db.execute(
            select(Inference)
            .where(Inference.incident_id == incident_id)
            .order_by(Inference.timestamp_ns)
        )
        return list(result.scalars().all())

    async def _get_ood_signals(self, incident_id: uuid.UUID, db: AsyncSession) -> list[OODSignal]:
        """Fetch OOD signals for all inferences in the incident."""
        # Join via Inference.incident_id
        result = await db.execute(
            select(OODSignal)
            .join(Inference, OODSignal.inference_id == Inference.id)
            .where(Inference.incident_id == incident_id)
        )
        return list(result.scalars().all())

    @staticmethod
    def _median(values: list[float]) -> float:
        """Median of a non-empty list."""
        return statistics.median(values)
