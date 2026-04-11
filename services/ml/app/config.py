from pydantic_settings import BaseSettings
from pathlib import Path

ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True

    class Config:
        env_file = str(ROOT_ENV)
        extra = "ignore"


settings = Settings()
