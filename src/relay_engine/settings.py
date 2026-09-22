"""Operational settings for the Relay service.

Project engineering state is intentionally not loaded from ``.relay/`` here.
That repository contract belongs to a later authorized slice.
"""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["local", "test", "production"]
LogFormat = Literal["console", "json"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class RelaySettings(BaseSettings):
    """Minimal operational configuration for the Relay runtime."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="RELAY_",
        extra="ignore",
        case_sensitive=False,
    )

    environment: Environment = "local"
    service_name: str = Field(default="relay-engine", min_length=1)
    log_level: LogLevel = "INFO"
    log_format: LogFormat = "console"
