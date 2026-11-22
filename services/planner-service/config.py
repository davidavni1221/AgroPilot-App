from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Service settings. Real environment variables win over the .env file.

    Every field is required: a missing one stops the service at startup.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    registry_url: str
    weather_url: str
    registry_timeout_seconds: float = Field(gt=0)
    weather_timeout_seconds: float = Field(gt=0)


def get_settings() -> Settings:
    return Settings()
