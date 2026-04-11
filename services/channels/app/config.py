from pydantic_settings import BaseSettings
from pathlib import Path

ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True

    REDIS_HOST: str
    REDIS_PORT: int

    AT_USERNAME: str
    AT_API_KEY: str
    AT_SHORTCODE: str = "AFRIPROP"

    PROPERTY_SERVICE_URL: str = "http://localhost:8001"
    ML_SERVICE_URL: str = "http://localhost:8004"
    GATEWAY_SERVICE_URL: str = "http://localhost:8000"

    class Config:
        env_file = str(ROOT_ENV)
        extra = "ignore"


settings = Settings()
