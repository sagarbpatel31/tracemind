"""HTTP client for sending telemetry data to the TraceMind API."""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger("ros2_collector.sender")

DEFAULT_TIMEOUT = 10.0
MAX_RETRIES = 3


class TraceMindSender:
    """Sends collected ROS2 data to the TraceMind API via HTTP."""

    def __init__(
        self,
        api_url: str = "http://localhost:8000",
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._api_url = api_url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self._api_url,
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )
        logger.info("Initialized sender targeting %s", self._api_url)

    async def send_metrics(self, metric_points: list[dict[str, Any]]) -> bool:
        """Send metric data points to the ingest endpoint.

        Returns True on success, False on failure.
        """
        if not metric_points:
            return True

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = await self._client.post(
                    "/api/v1/ingest/metrics",
                    json={"metrics": metric_points},
                )
                response.raise_for_status()
                logger.debug(
                    "Sent %d metric points (status=%d)",
                    len(metric_points),
                    response.status_code,
                )
                return True
            except httpx.HTTPStatusError as exc:
                logger.warning(
                    "API returned %d on metrics send (attempt %d/%d): %s",
                    exc.response.status_code,
                    attempt,
                    MAX_RETRIES,
                    exc.response.text[:200],
                )
            except httpx.RequestError as exc:
                logger.warning(
                    "Network error sending metrics (attempt %d/%d): %s",
                    attempt,
                    MAX_RETRIES,
                    exc,
                )

        logger.error("Failed to send metrics after %d attempts", MAX_RETRIES)
        return False

    async def send_logs(self, events: list[dict[str, Any]]) -> bool:
        """Send event log entries to the ingest endpoint.

        Returns True on success, False on failure.
        """
        if not events:
            return True

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = await self._client.post(
                    "/api/v1/ingest/logs",
                    json={"events": events},
                )
                response.raise_for_status()
                logger.debug(
                    "Sent %d log events (status=%d)",
                    len(events),
                    response.status_code,
                )
                return True
            except httpx.HTTPStatusError as exc:
                logger.warning(
                    "API returned %d on log send (attempt %d/%d): %s",
                    exc.response.status_code,
                    attempt,
                    MAX_RETRIES,
                    exc.response.text[:200],
                )
            except httpx.RequestError as exc:
                logger.warning(
                    "Network error sending logs (attempt %d/%d): %s",
                    attempt,
                    MAX_RETRIES,
                    exc,
                )

        logger.error("Failed to send logs after %d attempts", MAX_RETRIES)
        return False

    async def register_device(self, device_info: dict[str, Any]) -> bool:
        """Register or update this device with the API.

        Returns True on success, False on failure.
        """
        try:
            response = await self._client.post(
                "/api/v1/devices/register",
                json=device_info,
            )
            response.raise_for_status()
            logger.info("Device registered successfully")
            return True
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            logger.error("Failed to register device: %s", exc)
            return False

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
        logger.info("Sender closed")
