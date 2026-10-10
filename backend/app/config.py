"""Application configuration via pydantic-settings (env-driven)."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # database
    database_url: str = "postgresql+asyncpg://relay:relay@db:5432/relay"

    # hold / turnaround policy (minutes)
    turnaround_minutes: int = 15
    hold_pending_ttl_minutes: int = 10
    no_show_grace_minutes: int = 15

    # scheduler
    sweep_interval_seconds: int = 60

    # app
    app_name: str = "College Event Kit Relay"
    debug: bool = False


settings = Settings()
