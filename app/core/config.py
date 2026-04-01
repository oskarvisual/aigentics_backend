from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    app_base_url: str = "http://localhost:8000"
    api_v1_prefix: str = "/api/v1"

    mysql_url: str = Field(default="mysql+pymysql://root:root@localhost:3306/aigentics")
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None

    s3_endpoint: str = "http://localhost:9000"
    s3_bucket: str = "aigentics"
    s3_region: str | None = None
    s3_key_prefix: str = ""
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"

    google_api_key: str | None = None
    openai_api_key: str | None = None

    jwt_secret: str = "change-me-with-at-least-32-characters"
    jwt_refresh_secret: str = "change-me-refresh-with-at-least-32-chars"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30

    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )
    socket_io_path: str = "/socket.io"

    default_agent_model_openai: str = "openai:gpt-4o-mini"
    default_agent_model_gemini: str = "google-gla:gemini-2.0-flash"
    default_embedding_model: str = "models/gemini-embedding-001"
    default_manager_check_interval_minutes: int = 10

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str) and not value.startswith("["):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def is_local(self) -> bool:
        return self.app_env in {"local", "development", "dev"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
