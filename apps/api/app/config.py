from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://tracemind:tracemind@localhost:5432/tracemind"
    cors_origins: str = "http://localhost:3000"
    storage_path: str = "./storage"
    api_version: str = "0.1.0"
    jwt_secret_key: str = "tracemind-dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
