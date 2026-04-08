"""TraceMind ROS2 Collector entry point.

Monitors ROS2 topics and nodes, sending telemetry to the TraceMind API.
Falls back to simulation mode when rclpy is not available.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import signal
import sys
import time

from .sender import TraceMindSender
from .topic_monitor import TopicMonitor
from .node_inspector import NodeInspector

try:
    import rclpy
    from rclpy.node import Node

    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False

logger = logging.getLogger("ros2_collector")

COLLECTION_INTERVAL_SEC = 5.0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="TraceMind ROS2 Collector",
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="TraceMind API base URL (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--device-id",
        required=True,
        help="UUID of the device this collector runs on",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=COLLECTION_INTERVAL_SEC,
        help=f"Collection interval in seconds (default: {COLLECTION_INTERVAL_SEC})",
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        default=False,
        help="Force simulation mode even if rclpy is available",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )
    return parser.parse_args(argv)


async def collect_and_send(
    topic_monitor: TopicMonitor,
    node_inspector: NodeInspector,
    sender: TraceMindSender,
    device_id: str,
) -> None:
    """Run a single collection cycle: gather data and send to API."""
    timestamp = time.time()

    topics = topic_monitor.list_topics()
    topic_rates = topic_monitor.measure_rates()
    nodes = node_inspector.list_nodes()

    metric_points = []
    for topic_name, rate_hz in topic_rates.items():
        metric_points.append(
            {
                "device_id": device_id,
                "metric_name": "topic_rate_hz",
                "value": rate_hz,
                "timestamp": timestamp,
                "labels": {"topic": topic_name},
            }
        )

    metric_points.append(
        {
            "device_id": device_id,
            "metric_name": "ros2_node_count",
            "value": len(nodes),
            "timestamp": timestamp,
            "labels": {},
        }
    )

    metric_points.append(
        {
            "device_id": device_id,
            "metric_name": "ros2_topic_count",
            "value": len(topics),
            "timestamp": timestamp,
            "labels": {},
        }
    )

    await sender.send_metrics(metric_points)

    event = {
        "device_id": device_id,
        "timestamp": timestamp,
        "level": "info",
        "source": "ros2_collector",
        "message": f"Collected {len(topics)} topics, {len(nodes)} nodes",
        "metadata": {
            "topics": topics,
            "nodes": nodes,
            "rates": topic_rates,
        },
    }
    await sender.send_logs([event])


async def run_loop(args: argparse.Namespace) -> None:
    """Main collection loop."""
    use_simulation = args.simulate or not ROS2_AVAILABLE

    if use_simulation:
        logger.info("Running in SIMULATION mode (rclpy not available or --simulate set)")
    else:
        logger.info("Running with live ROS2 connection")
        rclpy.init()

    topic_monitor = TopicMonitor(use_simulation=use_simulation)
    node_inspector = NodeInspector(use_simulation=use_simulation)
    sender = TraceMindSender(api_url=args.api_url)

    shutdown = asyncio.Event()

    def _handle_signal() -> None:
        logger.info("Shutdown signal received")
        shutdown.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _handle_signal)

    logger.info(
        "Starting collection loop (device=%s, interval=%.1fs)",
        args.device_id,
        args.interval,
    )

    try:
        while not shutdown.is_set():
            try:
                await collect_and_send(
                    topic_monitor, node_inspector, sender, args.device_id
                )
                logger.debug("Collection cycle complete")
            except Exception:
                logger.exception("Error during collection cycle")

            try:
                await asyncio.wait_for(shutdown.wait(), timeout=args.interval)
            except asyncio.TimeoutError:
                pass
    finally:
        await sender.close()
        if not use_simulation:
            rclpy.shutdown()
        logger.info("Collector stopped")


def main() -> None:
    args = parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    asyncio.run(run_loop(args))


if __name__ == "__main__":
    main()
