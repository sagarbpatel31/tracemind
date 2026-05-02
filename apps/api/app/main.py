from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.config import settings
from app.database import engine
from app.models import Base
from app.routers import auth, devices, health, incidents, ingest, projects, seed
from app.routers import ai_ingest


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (use alembic in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Watchpoint API",
    description="AI failure forensics for physical AI systems",
    version=settings.api_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")
app.include_router(devices.router, prefix="/api/v1")
app.include_router(incidents.router, prefix="/api/v1")
app.include_router(ingest.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(seed.router, prefix="/api/v1")
app.include_router(ai_ingest.router, prefix="/api/v1")


@app.get("/api/v1/bundles/{incident_id}")
async def download_bundle(incident_id: str):
    import os
    bundle_path = os.path.join(settings.storage_path, "bundles", f"watchpoint-replay-{incident_id}.zip")
    if not os.path.exists(bundle_path):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Bundle not found")
    return FileResponse(
        bundle_path,
        media_type="application/zip",
        filename=f"watchpoint-replay-{incident_id}.zip",
    )
