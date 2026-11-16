from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Service settings. Real environment variables win over the .env file.

    Every field except provider_api_key is required: a missing one stops the service at startup.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    provider_base_url: str
    provider_api_key: str = ""  # empty on the free tier
    provider_timeout_seconds: float = Field(gt=0)
    provider_retries: int = Field(ge=0)
    forecast_fresh_seconds: int = Field(gt=0)
    forecast_max_stale_seconds: int = Field(gt=0)
    retry_after_seconds: int = Field(gt=0)


def get_settings() -> Settings:
    return Settings()
