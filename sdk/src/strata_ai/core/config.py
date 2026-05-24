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

    service_name: str = Field(..., description="Unique service identifier")
    env: str = Field("dev", description="Runtime environment: dev, staging, prod")
    otlp_endpoint: Optional[str] = Field(None, description="OTLP collector URL")
    database_url: Optional[str] = Field(None, description="Async SQLAlchemy URL")
    redis_url: Optional[str] = Field(None, description="Redis connection URL")
    task_backend: str = Field("redis", description="Task queue backend")
    task_result_ttl_seconds: int = Field(3600)

    # Agent defaults (overridable per-agent)
    default_model: str = Field("openai:gpt-4o")
    max_iterations: int = Field(10)
    temperature: float = Field(0.0)

    @classmethod
    def from_env(cls) -> "StrataBaseConfig":
        """Factory that reads STRATA_AI_ prefixed env vars."""
        return cls()
