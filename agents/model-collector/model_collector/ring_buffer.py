"""Thread-safe fixed-size ring buffer for inference frames.

Design goals:
- O(1) append and snapshot
- No locks on the hot read path; only append acquires a lock
- Oldest frames dropped silently when full (ring semantics)
- Zero external dependencies
"""
from __future__ import annotations

import threading
from collections import deque
from typing import Any


class RingBuffer:
    """Fixed-capacity deque with thread-safe append and snapshot.

    Args:
        maxsize: Maximum number of frames to retain.
                 When full, the oldest frame is discarded on each append.
    """

    def __init__(self, maxsize: int = 512) -> None:
        if maxsize < 1:
            raise ValueError(f"maxsize must be >= 1, got {maxsize}")
        self._maxsize = maxsize
        self._buf: deque[dict[str, Any]] = deque(maxlen=maxsize)
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Write path (called from hook — must be fast)
    # ------------------------------------------------------------------

    def append(self, frame: dict[str, Any]) -> None:
        """Append a frame.  Drops the oldest when full (silent, by design)."""
        with self._lock:
            self._buf.append(frame)

    # ------------------------------------------------------------------
    # Read path
    # ------------------------------------------------------------------

    def snapshot(self) -> list[dict[str, Any]]:
        """Return a shallow copy of all buffered frames, oldest first."""
        with self._lock:
            return list(self._buf)

    def clear(self) -> None:
        """Discard all buffered frames (called after successful flush)."""
        with self._lock:
            self._buf.clear()

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        with self._lock:
            return len(self._buf)

    @property
    def maxsize(self) -> int:
        return self._maxsize

    def is_full(self) -> bool:
        with self._lock:
            return len(self._buf) == self._maxsize
