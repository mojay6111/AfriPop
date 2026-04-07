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

    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_DB: str
    MONGO_USER: str
    MONGO_PASSWORD: str

    REDIS_HOST: str
    REDIS_PORT: int

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    AT_USERNAME: str
    AT_API_KEY: str

    class Config:
        env_file = str(ROOT_ENV)
        extra = "ignore"


settings = Settings()
