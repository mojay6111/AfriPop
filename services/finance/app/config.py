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

    MPESA_CONSUMER_KEY: str = "sandbox"
    MPESA_CONSUMER_SECRET: str = "sandbox"
    MPESA_SHORTCODE: str = "174379"
    MPESA_PASSKEY: str = "sandbox"
    MPESA_CALLBACK_URL: str = "https://localhost/api/v1/finance/payments/mpesa/callback"

    AT_USERNAME: str = "sandbox"
    AT_API_KEY: str = "sandbox"

    PROPERTY_SERVICE_URL: str = "http://localhost:8001"
    CHANNELS_SERVICE_URL: str = "http://localhost:8006"

    class Config:
        env_file = str(ROOT_ENV)
        extra = "ignore"


settings = Settings()
