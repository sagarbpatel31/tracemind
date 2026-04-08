"""Seed endpoint for populating demo data directly into the database."""

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.device import Deployment, Device, DeviceStatus
from app.models.incident import Incident, IncidentStatus, Severity
from app.models.telemetry import EventLog, LogLevel, MetricPoint
from app.models.user import User
from app.models.workspace import Project, Workspace
from app.security import hash_password

router = APIRouter(prefix="/seed", tags=["seed"])

# Fixed IDs for demo consistency
WORKSPACE_ID = uuid.UUID("00000000-0000-0000-0000-000000000000")
PROJECT_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
USER_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")
DEVICE_IDS = [
    uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
    uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
    uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
]
DEPLOYMENT_IDS = [
    uuid.UUID("dddddddd-dddd-dddd-dddd-dddddddddd01"),
    uuid.UUID("dddddddd-dddd-dddd-dddd-dddddddddd02"),
    uuid.UUID("dddddddd-dddd-dddd-dddd-dddddddddd03"),
]
INCIDENT_IDS = [
    uuid.UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeee01"),
    uuid.UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeee02"),
    uuid.UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeee03"),
]


@router.post("/demo")
async def seed_demo_data(db: AsyncSession = Depends(get_db)):
    """Seed the database with demo data for 3 devices and 3 incidents."""
    now = datetime.now(timezone.utc)
    base_time = now - timedelta(hours=1)

    # User
    user = User(
        id=USER_ID,
        email="demo@tracemind.ai",
        name="Demo User",
        password_hash=hash_password("demo123"),
    )
    db.add(user)

    # Workspace
    workspace = Workspace(
        id=WORKSPACE_ID, name="TraceMind Demo", slug="tracemind-demo", owner_id=USER_ID
    )
    db.add(workspace)

    # Project
    project = Project(
        id=PROJECT_ID,
        workspace_id=WORKSPACE_ID,
        name="Warehouse Robotics Fleet",
        slug="warehouse-fleet",
    )
    db.add(project)

    # Devices
    devices_data = [
        {
            "id": DEVICE_IDS[0],
            "name": "jetson-orin-nav-01",
            "hardware": "NVIDIA Jetson Orin NX",
            "os": "Ubuntu 22.04 L4T",
            "agent": "0.1.0",
            "status": DeviceStatus.online,
        },
        {
            "id": DEVICE_IDS[1],
            "name": "rpi4-patrol-02",
            "hardware": "Raspberry Pi 4 Model B",
            "os": "Debian 12",
            "agent": "0.1.0",
            "status": DeviceStatus.online,
        },
        {
            "id": DEVICE_IDS[2],
            "name": "x86-warehouse-03",
            "hardware": "Intel NUC i7-1260P",
            "os": "Ubuntu 22.04",
            "agent": "0.1.0",
            "status": DeviceStatus.offline,
        },
    ]

    for d in devices_data:
        device = Device(
            id=d["id"],
            project_id=PROJECT_ID,
            device_name=d["name"],
            hardware_model=d["hardware"],
            os_version=d["os"],
            agent_version=d["agent"],
            status=d["status"],
            last_seen_at=now - timedelta(minutes=5) if d["status"] == DeviceStatus.online else now - timedelta(hours=3),
            registered_at=now - timedelta(days=7),
        )
        db.add(device)

    # Deployments
    deployments_data = [
        {"id": DEPLOYMENT_IDS[0], "device_id": DEVICE_IDS[0], "version": "nav-stack-v2.3.1"},
        {"id": DEPLOYMENT_IDS[1], "device_id": DEVICE_IDS[1], "version": "patrol-v1.8.0"},
        {"id": DEPLOYMENT_IDS[2], "device_id": DEVICE_IDS[2], "version": "warehouse-v2.4.0"},
    ]

    for dep in deployments_data:
        deployment = Deployment(
            id=dep["id"],
            device_id=dep["device_id"],
            version=dep["version"],
            deployed_at=now - timedelta(days=2),
            created_at=now - timedelta(days=2),
        )
        db.add(deployment)

    await db.flush()

    # --- INCIDENT 1: CPU contention causing topic degradation ---
    incident1 = Incident(
        id=INCIDENT_IDS[0],
        project_id=PROJECT_ID,
        device_id=DEVICE_IDS[0],
        deployment_id=DEPLOYMENT_IDS[0],
        title="CPU contention causing /cmd_vel topic degradation",
        severity=Severity.high,
        status=IncidentStatus.open,
        trigger_type="topic_rate_drop",
        started_at=base_time,
    )
    db.add(incident1)

    # Metrics for incident 1 - 90 seconds of data
    import math
    import random
    random.seed(42)

    for sec in range(90):
        ts = base_time + timedelta(seconds=sec)
        # CPU rises from 45% to 98%
        cpu = 45 + (53 * (sec / 90) ** 1.5) + random.uniform(-2, 2)
        cpu = min(cpu, 99)
        # Topic rate drops from 10Hz to 2Hz
        topic_rate = 10 - (8 * max(0, (sec - 20) / 70) ** 1.3) + random.uniform(-0.3, 0.3)
        topic_rate = max(topic_rate, 1)
        # Inference latency spikes from 15ms to 200ms
        latency = 15 + (185 * max(0, (sec - 30) / 60) ** 2) + random.uniform(-3, 3)
        # Memory stays relatively stable
        memory = 62 + (sec / 90) * 15 + random.uniform(-1, 1)
        # GPU temp rises
        gpu_temp = 55 + (sec / 90) * 25 + random.uniform(-1, 1)

        for name, value, unit in [
            ("cpu_percent", cpu, "%"),
            ("topic_rate_hz", topic_rate, "Hz"),
            ("inference_latency_ms", latency, "ms"),
            ("memory_percent", memory, "%"),
            ("gpu_temp_c", gpu_temp, "C"),
        ]:
            db.add(MetricPoint(
                device_id=DEVICE_IDS[0],
                incident_id=INCIDENT_IDS[0],
                timestamp=ts,
                metric_name=name,
                value=round(value, 2),
                unit=unit,
            ))

    # Events for incident 1
    events_1 = [
        (0, LogLevel.info, "system", "Agent started monitoring"),
        (5, LogLevel.info, "ros2_monitor", "Topic /cmd_vel publishing at 10.2 Hz"),
        (15, LogLevel.warn, "system", "CPU usage rising: 58%"),
        (22, LogLevel.warn, "ros2_monitor", "Topic /cmd_vel rate dropped to 8.1 Hz"),
        (30, LogLevel.error, "ros2_monitor", "Topic /cmd_vel rate below threshold: 6.3 Hz"),
        (35, LogLevel.warn, "inference", "Inference latency increased: 45ms (baseline: 15ms)"),
        (40, LogLevel.error, "system", "CPU usage critical: 89%"),
        (45, LogLevel.error, "ros2_monitor", "Topic /cmd_vel rate critically low: 3.8 Hz"),
        (50, LogLevel.warn, "navigation", "Motion planner receiving degraded inputs"),
        (55, LogLevel.error, "inference", "Inference latency spike: 120ms"),
        (60, LogLevel.fatal, "watchdog", "Navigation watchdog timeout - no valid /cmd_vel for 5s"),
        (65, LogLevel.error, "system", "CPU sustained above 95% for 30s"),
        (70, LogLevel.warn, "ros2_monitor", "Topic /scan subscriber backlog: 12 messages"),
        (75, LogLevel.error, "navigation", "Emergency stop triggered - topic starvation"),
        (80, LogLevel.info, "system", "Incident captured - uploading context window"),
    ]
    for offset, level, source, message in events_1:
        db.add(EventLog(
            device_id=DEVICE_IDS[0],
            incident_id=INCIDENT_IDS[0],
            timestamp=base_time + timedelta(seconds=offset),
            level=level,
            source=source,
            message=message,
        ))

    # --- INCIDENT 2: Thermal throttling ---
    incident2 = Incident(
        id=INCIDENT_IDS[1],
        project_id=PROJECT_ID,
        device_id=DEVICE_IDS[0],
        deployment_id=DEPLOYMENT_IDS[0],
        title="GPU thermal throttling during outdoor operation",
        severity=Severity.critical,
        status=IncidentStatus.investigating,
        trigger_type="thermal_threshold",
        started_at=base_time + timedelta(minutes=15),
    )
    db.add(incident2)

    t2_base = base_time + timedelta(minutes=15)
    for sec in range(120):
        ts = t2_base + timedelta(seconds=sec)
        gpu_temp = 65 + (27 * (sec / 120) ** 1.2) + random.uniform(-1, 1)
        inference_lat = 18 + (180 * max(0, (sec - 40) / 80) ** 2) + random.uniform(-2, 2)
        cpu = 55 + random.uniform(-5, 5)
        topic_rate = max(2, 10 - (8 * max(0, (sec - 60) / 60)) + random.uniform(-0.5, 0.5))

        for name, value, unit in [
            ("gpu_temp_c", gpu_temp, "C"),
            ("inference_latency_ms", inference_lat, "ms"),
            ("cpu_percent", cpu, "%"),
            ("topic_rate_hz", topic_rate, "Hz"),
        ]:
            db.add(MetricPoint(
                device_id=DEVICE_IDS[0],
                incident_id=INCIDENT_IDS[1],
                timestamp=ts,
                metric_name=name,
                value=round(value, 2),
                unit=unit,
            ))

    events_2 = [
        (0, LogLevel.info, "thermal", "GPU temperature: 65°C - normal range"),
        (20, LogLevel.warn, "thermal", "GPU temperature rising: 72°C"),
        (40, LogLevel.warn, "thermal", "GPU temperature: 78°C - approaching throttle threshold"),
        (50, LogLevel.error, "thermal", "GPU thermal throttling activated at 82°C"),
        (55, LogLevel.warn, "inference", "Inference latency increased: 65ms"),
        (70, LogLevel.error, "thermal", "GPU temperature critical: 88°C"),
        (80, LogLevel.error, "inference", "Inference latency spike: 150ms"),
        (90, LogLevel.fatal, "watchdog", "Inference watchdog timeout"),
        (95, LogLevel.error, "thermal", "GPU temperature: 91°C - emergency"),
        (100, LogLevel.info, "system", "Emergency thermal shutdown initiated"),
    ]
    for offset, level, source, message in events_2:
        db.add(EventLog(
            device_id=DEVICE_IDS[0],
            incident_id=INCIDENT_IDS[1],
            timestamp=t2_base + timedelta(seconds=offset),
            level=level,
            source=source,
            message=message,
        ))

    # --- INCIDENT 3: Version regression ---
    incident3 = Incident(
        id=INCIDENT_IDS[2],
        project_id=PROJECT_ID,
        device_id=DEVICE_IDS[2],
        deployment_id=DEPLOYMENT_IDS[2],
        title="Navigation regression after warehouse-v2.4.0 deployment",
        severity=Severity.medium,
        status=IncidentStatus.resolved,
        trigger_type="mission_abort",
        started_at=base_time + timedelta(minutes=30),
        resolved_at=base_time + timedelta(minutes=45),
    )
    db.add(incident3)

    t3_base = base_time + timedelta(minutes=30)
    for sec in range(60):
        ts = t3_base + timedelta(seconds=sec)
        cpu = 40 + random.uniform(-5, 10)
        latency = 25 + (sec / 60) * 40 + random.uniform(-3, 3)
        topic_rate = max(4, 10 - (sec / 60) * 4 + random.uniform(-0.5, 0.5))

        for name, value, unit in [
            ("cpu_percent", cpu, "%"),
            ("inference_latency_ms", latency, "ms"),
            ("topic_rate_hz", topic_rate, "Hz"),
        ]:
            db.add(MetricPoint(
                device_id=DEVICE_IDS[2],
                incident_id=INCIDENT_IDS[2],
                timestamp=ts,
                metric_name=name,
                value=round(value, 2),
                unit=unit,
            ))

    events_3 = [
        (0, LogLevel.info, "deployment", "New deployment warehouse-v2.4.0 active"),
        (5, LogLevel.info, "navigation", "Navigation stack initialized"),
        (10, LogLevel.warn, "navigation", "Path planner latency higher than v2.3.x baseline"),
        (20, LogLevel.warn, "navigation", "Missed 2 waypoints in sequence"),
        (30, LogLevel.error, "navigation", "Mission abort - could not reach waypoint within timeout"),
        (35, LogLevel.info, "system", "Config diff detected: planner_hz changed from 20 to 10 in v2.4.0"),
        (40, LogLevel.warn, "navigation", "v2.4.0 planner frequency is half of v2.3.x"),
        (50, LogLevel.info, "system", "Incident captured and correlated with deployment version change"),
    ]
    for offset, level, source, message in events_3:
        db.add(EventLog(
            device_id=DEVICE_IDS[2],
            incident_id=INCIDENT_IDS[2],
            timestamp=t3_base + timedelta(seconds=offset),
            level=level,
            source=source,
            message=message,
        ))

    await db.commit()

    return {
        "status": "ok",
        "seeded": {
            "users": 1,
            "workspaces": 1,
            "projects": 1,
            "devices": 3,
            "deployments": 3,
            "incidents": 3,
            "event_logs": len(events_1) + len(events_2) + len(events_3),
            "metric_points": 90 * 5 + 120 * 4 + 60 * 3,
        },
    }
