"""AI-002 — Out-of-distribution (OOD) input detected.

Trigger: any OODSignal linked to this incident has is_ood=True.

Severity: medium
The rule aggregates all OOD signals; higher score / more signals = higher confidence.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.rca.ai_rules.base import AIBaseRule


class RuleAI002(AIBaseRule):
    rule_id = "AI-002"
    name = "OOD input detected"

    async def evaluate(self, incident_id: uuid.UUID, db: AsyncSession) -> dict[str, Any] | None:
        signals = await self._get_ood_signals(incident_id, db)
        ood_signals = [s for s in signals if s.is_ood]

        if not ood_signals:
            return None

        # Scale confidence with number of OOD signals (caps at 0.90)
        base_confidence = 0.65
        per_signal_bonus = 0.05
        rule_confidence = min(base_confidence + (len(ood_signals) - 1) * per_signal_bonus, 0.90)

        # Summarise signal types seen
        types_seen = sorted({s.signal_type for s in ood_signals})
        max_score = max(s.score for s in ood_signals)
        avg_threshold = sum(s.threshold for s in ood_signals) / len(ood_signals)

        return {
            "rule_id": self.rule_id,
            "cause": "Out-of-distribution input detected",
            "confidence": round(rule_confidence, 2),
            "description": (
                f"{len(ood_signals)} OOD signal(s) fired during this incident "
                f"(types: {', '.join(types_seen)}, max score: {max_score:.3f}). "
                "The model received inputs outside its training distribution, "
                "which can cause unpredictable outputs regardless of apparent confidence."
            ),
            "evidence": [
                {
                    "signal": "ood_signals",
                    "rule_id": self.rule_id,
                    "ood_count": len(ood_signals),
                    "total_signals": len(signals),
                    "signal_types": types_seen,
                    "max_score": round(max_score, 4),
                    "avg_threshold": round(avg_threshold, 4),
                    "description": (
                        f"{len(ood_signals)}/{len(signals)} OOD signals fired "
                        f"(max score {max_score:.3f} vs threshold {avg_threshold:.3f})"
                    ),
                }
            ],
            "suggested_steps": [
                "Inspect raw sensor inputs at OOD signal timestamps",
                "Check for environmental conditions at failure time "
                "(lighting, weather, obstacles not in training data)",
                "Add OOD examples to the training set or use ensembling to improve robustness",
                "Lower the OOD threshold to catch earlier warnings in production",
            ],
        }
