"""AI-003 — Inference latency spike.

Trigger: p99 latency in the second half of the incident window
is more than 2× the p99 of the first half.

Severity: medium
Min inferences with latency data: 6 (3 per half)
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.rca.ai_rules.base import AIBaseRule

_RATIO_THRESHOLD = 2.0  # second-half p99 must be ≥ 2× first-half p99 to fire
_MIN_INFERENCES = 6


def _p99(values: list[float]) -> float:
    """Return 99th-percentile (or max when n < 100) of a non-empty list."""
    sorted_vals = sorted(values)
    idx = max(0, int(len(sorted_vals) * 0.99) - 1)
    return sorted_vals[idx]


class RuleAI003(AIBaseRule):
    rule_id = "AI-003"
    name = "Inference latency spike"

    async def evaluate(self, incident_id: uuid.UUID, db: AsyncSession) -> dict[str, Any] | None:
        inferences = await self._get_inferences(incident_id, db)

        with_lat = [i for i in inferences if i.latency_ms is not None]
        if len(with_lat) < _MIN_INFERENCES:
            return None

        mid = len(with_lat) // 2
        first_lats = [i.latency_ms for i in with_lat[:mid]]  # type: ignore[misc]
        second_lats = [i.latency_ms for i in with_lat[mid:]]  # type: ignore[misc]

        p99_start = _p99(first_lats)
        p99_end = _p99(second_lats)

        if p99_start == 0:
            return None

        ratio = p99_end / p99_start
        if ratio < _RATIO_THRESHOLD:
            return None

        return {
            "rule_id": self.rule_id,
            "cause": "Inference latency spike",
            "confidence": min(0.60 + (ratio - 2.0) * 0.05, 0.88),
            "description": (
                f"Inference p99 latency increased {ratio:.1f}× "
                f"({p99_start:.0f}ms → {p99_end:.0f}ms) over the incident window. "
                "This points to GPU throttling, CPU contention, or memory pressure "
                "degrading model execution time."
            ),
            "evidence": [
                {
                    "signal": "inference_latency",
                    "rule_id": self.rule_id,
                    "p99_start_ms": round(p99_start, 1),
                    "p99_end_ms": round(p99_end, 1),
                    "ratio": round(ratio, 2),
                    "inference_count": len(with_lat),
                    "description": (
                        f"Inference latency p99: {p99_start:.0f}ms → {p99_end:.0f}ms "
                        f"({ratio:.1f}× increase, {len(with_lat)} frames)"
                    ),
                }
            ],
            "suggested_steps": [
                "Check GPU utilisation and thermal throttling state at latency spike point",
                "Correlate with CPU contention metrics (cpu_percent)",
                "Profile the model with torch.profiler to find the slow layer",
                "Consider TensorRT compilation or input resolution reduction to cut baseline latency",
            ],
        }
