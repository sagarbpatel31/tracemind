"""AI-001 — Perception confidence collapse.

Trigger: median confidence in the second half of the incident window
drops >30% compared to the first half.

Severity: high
Min inferences: 6 (3 per half — avoids noise on sparse data)
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.rca.ai_rules.base import AIBaseRule

# Minimum relative drop (30%) to fire
_DROP_THRESHOLD = 0.30
# Minimum inference count (whole incident) to run the rule
_MIN_INFERENCES = 6


class RuleAI001(AIBaseRule):
    rule_id = "AI-001"
    name = "Perception confidence collapse"

    async def evaluate(self, incident_id: uuid.UUID, db: AsyncSession) -> dict[str, Any] | None:
        inferences = await self._get_inferences(incident_id, db)

        # Filter to those that have a confidence value
        with_conf = [i for i in inferences if i.confidence is not None]
        if len(with_conf) < _MIN_INFERENCES:
            return None

        # Split into first and second half
        mid = len(with_conf) // 2
        first_half = [i.confidence for i in with_conf[:mid]]  # type: ignore[misc]
        second_half = [i.confidence for i in with_conf[mid:]]  # type: ignore[misc]

        median_start = self._median(first_half)
        median_end = self._median(second_half)

        if median_start == 0:
            return None

        drop_fraction = (median_start - median_end) / median_start
        if drop_fraction < _DROP_THRESHOLD:
            return None

        drop_pct = drop_fraction * 100
        return {
            "rule_id": self.rule_id,
            "cause": "Perception confidence collapse",
            "confidence": 0.78,
            "description": (
                f"Model detection confidence dropped {drop_pct:.0f}% "
                f"(from {median_start:.2f} → {median_end:.2f} median) "
                "over the incident window. This indicates the model began "
                "processing inputs significantly different from its training distribution."
            ),
            "evidence": [
                {
                    "signal": "inference_confidence",
                    "rule_id": self.rule_id,
                    "median_start": round(median_start, 4),
                    "median_end": round(median_end, 4),
                    "drop_pct": round(drop_pct, 1),
                    "inference_count": len(with_conf),
                    "description": (
                        f"Inference confidence: p50 {median_start:.2f} → {median_end:.2f} "
                        f"({drop_pct:.0f}% drop, {len(with_conf)} frames)"
                    ),
                }
            ],
            "suggested_steps": [
                "Inspect sensor inputs at the confidence drop point for quality degradation",
                "Compare input distributions between high- and low-confidence windows",
                "Review Grad-CAM saliency maps if available (Week 3 feature)",
                "Collect new training data from the failure conditions",
            ],
        }
