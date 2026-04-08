from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://tracemind:tracemind@localhost:5432/tracemind"
    cors_origins: str = "http://localhost:3000"
    storage_path: str = "./storage"
    api_version: str = "0.1.0"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
