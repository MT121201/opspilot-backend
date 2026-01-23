# app/core/config.py
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="OPSPILOT_",
        extra="ignore",
    )

    SECRET_KEY: str = "secret"
    APP_NAME: str = "OpsPilot Backend"
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/opspilot"

    JWT_SECRET_KEY: str = "dev_jwt_secret_change_me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_MINUTES: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
