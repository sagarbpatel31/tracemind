#!/usr/bin/env python3
"""Demo script: attach hooks to a ResNet-18 and print per-layer captures.

Usage:
    uv run python scripts/demo_hook.py

Requires torch + torchvision:
    uv pip install torch torchvision

Output example:
    Layer: __top__  | output_shape: [1, 1000] | confidence: 0.0823 | latency: 0.12ms
    Layer: layer4   | output_shape: [1, 512, 1, 1] | mean: 0.031 | std: 0.289
"""
from __future__ import annotations

import sys
import time


def main() -> None:
    try:
        import torch
        import torchvision.models as models
    except ImportError:
        print("ERROR: torch and torchvision are required.")
        print("Install: uv pip install torch torchvision")
        sys.exit(1)

    from model_collector import Collector
    from model_collector.adapters.pytorch_adapter import attach_hooks

    print("Watchpoint model-collector — PyTorch hook demo")
    print("=" * 52)

    # Load pretrained ResNet-18 (downloads ~44MB on first run)
    print("Loading ResNet-18...")
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model.eval()

    # Set up collector
    collector = Collector(
        device_id="demo-robot",
        ring_buffer_size=64,
        flush_path="/tmp/watchpoint/demo",
    )

    # Attach hooks: top-level + two intermediate layers
    handles = attach_hooks(
        model,
        collector,
        layer_names=["layer4", "avgpool", "fc"],
    )
    print(f"Attached {len(handles)} hooks\n")

    # Run 5 inference passes with random inputs (simulates a video stream)
    for i in range(5):
        x = torch.randn(1, 3, 224, 224)
        t0 = time.perf_counter()
        with torch.no_grad():
            _ = model(x)
        total_ms = (time.perf_counter() - t0) * 1000
        print(f"Forward pass {i + 1}: {total_ms:.1f}ms  |  buffer size: {collector.buffer_len}")

    print(f"\nCaptured {collector.buffer_len} frames in ring buffer")
    print("\nFrame details (last 4):")
    frames = collector._buf.snapshot()[-4:]
    for f in frames:
        shape = f.get("output_shape", "?")
        mean = f.get("output_mean")
        conf = f.get("confidence")
        layer = f.get("layer_name", "?")
        parts = [f"  layer={layer:<12}", f"shape={str(shape):<20}"]
        if mean is not None:
            parts.append(f"mean={mean:+.4f}")
        if conf is not None:
            parts.append(f"confidence={conf:.4f}")
        print("  ".join(parts))

    # Flush to disk
    print("\nFlushing ring buffer to disk...")
    path = collector.flush(incident_id="demo-incident-001")
    print(f"Saved: {path}")
    print("Buffer after flush:", collector.buffer_len)

    for h in handles:
        h.remove()
    print("\nDone. Hooks removed.")


if __name__ == "__main__":
    main()
