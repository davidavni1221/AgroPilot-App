from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

SUPPORTED_SCHEMES = ("postgresql", "postgres")


class Settings(BaseSettings):
    """Service settings. Real environment variables win over the .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Unset or blank means the local SQLite file registry.db.
    database_url: str | None = None

    @field_validator("database_url")
    @classmethod
    def check_database_url(cls, value: str | None) -> str | None:
        value = (value or "").strip()
        if not value:
            return None
        scheme = value.split("://", 1)[0].lower() if "://" in value else ""
        if scheme not in SUPPORTED_SCHEMES:
            raise ValueError(f"Unsupported DATABASE_URL scheme: {scheme!r}. Use postgresql://... or leave it unset for SQLite.")
        return value


def get_settings() -> Settings:
    # Read on every call, so tests that change DATABASE_URL take effect immediately.
    return Settings()
