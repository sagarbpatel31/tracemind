"""Tests for AI failure rules AI-001 and AI-002.

Uses AsyncMock DB sessions — no live database required.
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.rca.ai_rules.rule_ai001 import RuleAI001
from app.rca.ai_rules.rule_ai002 import RuleAI002

INCIDENT_ID = uuid.uuid4()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_inference(confidence: float | None, timestamp_ns: int = 0) -> MagicMock:
    inf = MagicMock()
    inf.id = uuid.uuid4()
    inf.incident_id = INCIDENT_ID
    inf.confidence = confidence
    inf.timestamp_ns = timestamp_ns
    return inf


def _make_ood_signal(is_ood: bool, signal_type: str = "softmax_entropy") -> MagicMock:
    sig = MagicMock()
    sig.id = uuid.uuid4()
    sig.inference_id = uuid.uuid4()
    sig.signal_type = signal_type
    sig.score = 0.85 if is_ood else 0.3
    sig.threshold = 0.5
    sig.is_ood = is_ood
    return sig


def _db_with_inferences(inferences: list, ood_signals: list | None = None) -> AsyncMock:
    """Mock DB that returns inferences on first execute, ood_signals on second."""
    db = AsyncMock()
    calls = []

    inf_result = MagicMock()
    inf_result.scalars.return_value.all.return_value = inferences

    ood_result = MagicMock()
    ood_result.scalars.return_value.all.return_value = ood_signals or []

    calls.extend([inf_result, ood_result])
    db.execute = AsyncMock(side_effect=calls)
    return db


# ---------------------------------------------------------------------------
# AI-001: Perception confidence collapse
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ai001_fires_on_confidence_drop():
    """30%+ drop in median confidence → rule fires."""
    # First half: high confidence ~0.90, second half: ~0.55 (39% drop)
    inferences = [
        _make_inference(0.92, i * 1_000_000)
        for i in range(6)
    ] + [
        _make_inference(0.55, (i + 6) * 1_000_000)
        for i in range(6)
    ]
    db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = inferences
    db.execute = AsyncMock(return_value=result)

    finding = await RuleAI001().evaluate(INCIDENT_ID, db)

    assert finding is not None
    assert finding["rule_id"] == "AI-001"
    assert finding["confidence"] == pytest.approx(0.78)
    assert "collapse" in finding["cause"].lower()
    assert len(finding["evidence"]) == 1
    assert finding["evidence"][0]["drop_pct"] > 30


@pytest.mark.asyncio
async def test_ai001_does_not_fire_on_stable_confidence():
    """Stable confidence → rule does not fire."""
    inferences = [_make_inference(0.88, i * 1_000_000) for i in range(12)]
    db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = inferences
    db.execute = AsyncMock(return_value=result)

    finding = await RuleAI001().evaluate(INCIDENT_ID, db)
    assert finding is None


@pytest.mark.asyncio
async def test_ai001_does_not_fire_on_too_few_inferences():
    """< 6 inferences with confidence → rule skips to avoid noise."""
    inferences = [_make_inference(0.9, i) for i in range(4)]
    db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = inferences
    db.execute = AsyncMock(return_value=result)

    finding = await RuleAI001().evaluate(INCIDENT_ID, db)
    assert finding is None


@pytest.mark.asyncio
async def test_ai001_ignores_none_confidence():
    """Inferences with confidence=None are skipped; rule fires on those with values."""
    # 6 inferences with None, then 6 with a 40% drop
    inferences = (
        [_make_inference(None, i) for i in range(6)]
        + [_make_inference(0.9, i + 6) for i in range(6)]
        + [_make_inference(0.5, i + 12) for i in range(6)]
    )
    db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = inferences
    db.execute = AsyncMock(return_value=result)

    finding = await RuleAI001().evaluate(INCIDENT_ID, db)
    assert finding is not None
    assert finding["evidence"][0]["drop_pct"] > 30


# ---------------------------------------------------------------------------
# AI-002: OOD signal
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ai002_fires_on_ood_signal():
    """Any is_ood=True signal → rule fires."""
    signals = [_make_ood_signal(True), _make_ood_signal(False)]
    db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = signals
    db.execute = AsyncMock(return_value=result)

    finding = await RuleAI002().evaluate(INCIDENT_ID, db)

    assert finding is not None
    assert finding["rule_id"] == "AI-002"
    assert "out-of-distribution" in finding["cause"].lower()
    assert finding["evidence"][0]["ood_count"] == 1
    assert finding["evidence"][0]["total_signals"] == 2


@pytest.mark.asyncio
async def test_ai002_does_not_fire_when_no_ood():
    """All is_ood=False → rule does not fire."""
    signals = [_make_ood_signal(False) for _ in range(5)]
    db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = signals
    db.execute = AsyncMock(return_value=result)

    finding = await RuleAI002().evaluate(INCIDENT_ID, db)
    assert finding is None


@pytest.mark.asyncio
async def test_ai002_does_not_fire_on_empty_signals():
    """No OOD signals at all → rule does not fire."""
    db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = []
    db.execute = AsyncMock(return_value=result)

    finding = await RuleAI002().evaluate(INCIDENT_ID, db)
    assert finding is None


@pytest.mark.asyncio
async def test_ai002_confidence_scales_with_signal_count():
    """More OOD signals → higher rule confidence (caps at 0.90)."""
    signals_1 = [_make_ood_signal(True)]
    signals_5 = [_make_ood_signal(True) for _ in range(5)]

    for signals, expected_min in [(signals_1, 0.65), (signals_5, 0.80)]:
        db = AsyncMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = signals
        db.execute = AsyncMock(return_value=result)
        finding = await RuleAI002().evaluate(INCIDENT_ID, db)
        assert finding is not None
        assert finding["confidence"] >= expected_min
        assert finding["confidence"] <= 0.90
