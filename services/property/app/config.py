from pydantic_settings import BaseSettings
from pathlib import Path

ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    REDIS_HOST: str
    REDIS_PORT: int

    MINIO_HOST: str
    MINIO_PORT: int
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_BUCKET: str

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = str(ROOT_ENV)
        extra = "ignore"


settings = Settings()
