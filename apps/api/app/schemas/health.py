from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "tracemind-api"
    version: str = "0.1.0"
