"""Watchpoint model-collector — transparent AI inference capture.

Quick start (PyTorch):

    from model_collector import Collector
    from model_collector.adapters.pytorch_adapter import attach_hooks

    collector = Collector(device_id="robot-01", backend_url="http://localhost:8000")
    attach_hooks(model, collector, layer_names=["backbone.layer4", "head"])
    output = model(input_tensor)   # capture is transparent
    collector.flush(incident_id="some-uuid")
"""

from __future__ import annotations

import uuid
from typing import Any

from model_collector.config import CollectorConfig
from model_collector.ring_buffer import RingBuffer
from model_collector.writer import flush_to_disk

__all__ = ["Collector"]


class Collector:
    """Central coordinator: holds the ring buffer, exposes flush interface.

    One Collector instance per model process.  Multiple adapters can write
    to the same Collector (e.g. a PyTorch adapter + an OOD detector).
    """

    def __init__(
        self,
        device_id: str | None = None,
        backend_url: str | None = None,
        capture_layers: list[str] | None = None,
        ring_buffer_size: int | None = None,
        flush_path: str | None = None,
    ) -> None:
        cfg = CollectorConfig()
        self.device_id = device_id or cfg.device_id
        self.backend_url = backend_url or cfg.backend_url
        self.capture_layers = capture_layers or cfg.capture_layers
        self.flush_path = flush_path or cfg.flush_path
        self._buf = RingBuffer(maxsize=ring_buffer_size or cfg.ring_buffer_size)
        self._model_run_id: str = str(uuid.uuid4())

    # ------------------------------------------------------------------
    # Write path (called by adapters from forward hooks)
    # ------------------------------------------------------------------

    def record(self, frame: dict[str, Any]) -> None:
        """Store one inference frame in the ring buffer.

        Called by adapters; must be fast — runs on the inference thread.
        """
        frame.setdefault("model_run_id", self._model_run_id)
        frame.setdefault("device_id", self.device_id)
        self._buf.append(frame)

    # ------------------------------------------------------------------
    # Flush path (called on incident trigger)
    # ------------------------------------------------------------------

    def flush(self, incident_id: str | None = None) -> str:
        """Snapshot the ring buffer, write to disk, clear buffer.

        Args:
            incident_id: UUID for the incident.  Auto-generated if not given.

        Returns:
            Path to the written msgpack file.
        """
        incident_id = incident_id or str(uuid.uuid4())
        frames = self._buf.snapshot()
        if not frames:
            raise RuntimeError("Ring buffer is empty — nothing to flush")
        path = flush_to_disk(frames, self.flush_path, incident_id)
        self._buf.clear()
        return path

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def buffer_len(self) -> int:
        return len(self._buf)

    def reset_model_run(self) -> str:
        """Start a new model run (new weights loaded, etc.)."""
        self._model_run_id = str(uuid.uuid4())
        return self._model_run_id
