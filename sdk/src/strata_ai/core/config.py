from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class StrataBaseConfig(BaseSettings):
    """Environment-driven, zero-hardcoded-secret configuration contract."""

    model_config = SettingsConfigDict(
        env_prefix="STRATA_AI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Required
    service_name: str = Field(..., description="Unique service identifier")

    # Optional with defaults
    env: str = Field(default="dev", description="Runtime environment")
    otlp_endpoint: Optional[str] = Field(default=None, description="OTLP collector URL")
    database_url: Optional[str] = Field(
        default=None, description="Async SQLAlchemy URL"
    )
    redis_url: Optional[str] = Field(default=None, description="Redis connection URL")
    task_backend: str = Field(default="redis", description="Task queue backend")
    task_result_ttl_seconds: int = Field(default=3600)

    # Agent defaults (overridable per-agent)
    default_model: str = Field(default="openai:gpt-4o")
    max_iterations: int = Field(default=10)
    temperature: float = Field(default=0.0)

    @classmethod
    def from_env(cls) -> "StrataBaseConfig":
        """Factory that reads STRATA_AI_ prefixed env vars."""
        return cls()  # type: ignore[call-arg]
