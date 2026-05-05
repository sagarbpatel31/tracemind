"""Flush captured frames to local disk as msgpack bundles.

Each flush produces one file:
    {flush_path}/{incident_id}/run_{timestamp_ns}.msgpack

The file contains a msgpack-serialized list of frame dicts.
Numpy arrays are serialized as {__ndarray__: true, data: bytes, dtype: str, shape: list}.
"""

from __future__ import annotations

import os
import time
from typing import Any

import msgpack
import numpy as np


def _encode_numpy(obj: Any) -> Any:
    """msgpack default encoder — handles numpy arrays."""
    if isinstance(obj, np.ndarray):
        return {
            "__ndarray__": True,
            "data": obj.tobytes(),
            "dtype": str(obj.dtype),
            "shape": list(obj.shape),
        }
    raise TypeError(f"Unknown type: {type(obj)}")


def flush_to_disk(
    frames: list[dict[str, Any]],
    flush_path: str,
    incident_id: str,
) -> str:
    """Write frames to a msgpack file and return the file path.

    Args:
        frames:      List of frame dicts from the ring buffer snapshot.
        flush_path:  Base directory for captures (from CollectorConfig).
        incident_id: Incident UUID string — used as sub-directory name.

    Returns:
        Absolute path to the written file.
    """
    if not frames:
        raise ValueError("No frames to flush")

    ts_ns = time.monotonic_ns()
    out_dir = os.path.join(flush_path, incident_id)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"run_{ts_ns}.msgpack")

    packed = msgpack.packb(frames, default=_encode_numpy, use_bin_type=True)
    with open(out_path, "wb") as f:
        f.write(packed)

    return out_path


def load_from_disk(file_path: str) -> list[dict[str, Any]]:
    """Decode a msgpack bundle written by flush_to_disk.

    Numpy arrays are reconstructed from their encoded representation.
    """

    def _decode_numpy(obj: Any) -> Any:
        # With raw=False, msgpack decodes keys as str — use str keys here.
        if isinstance(obj, dict) and obj.get("__ndarray__"):
            return np.frombuffer(obj["data"], dtype=obj["dtype"]).reshape(obj["shape"])
        return obj

    with open(file_path, "rb") as f:
        raw = f.read()

    return msgpack.unpackb(raw, object_hook=_decode_numpy, raw=False)
