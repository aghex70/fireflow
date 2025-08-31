"""Application configuration management using Pydantic Settings and dotenv."""

from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="DB_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    url: str = Field(
        default="sqlite:///data/fireflow.db", description="Database connection URL"
    )
    echo: bool = Field(default=False, description="Enable SQL query logging")
    pool_size: int = Field(default=5, description="Database connection pool size")
    max_overflow: int = Field(
        default=10, description="Maximum database connection overflow"
    )


class RedisSettings(BaseSettings):
    """Redis configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="REDIS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    url: str = Field(
        default="redis://redis:6379/0",
        description="Redis connection URL for Celery broker",
    )
    cache_url: str = Field(
        default="redis://redis:6379/1",
        description="Redis connection URL for caching",
    )
    password: str | None = Field(default=None, description="Redis password (optional)")
    max_connections: int = Field(default=20, description="Maximum Redis connections")


class CelerySettings(BaseSettings):
    """Celery configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="CELERY_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    broker_url: str = Field(
        default="redis://redis:6379/0", description="Celery broker URL"
    )
    result_backend: str = Field(
        default="redis://redis:6379/0", description="Celery result backend URL"
    )
    task_serializer: str = Field(
        default="json", description="Task serialization format"
    )
    result_serializer: str = Field(
        default="json", description="Result serialization format"
    )
    timezone: str = Field(default="UTC", description="Celery timezone")
    worker_concurrency: int = Field(default=4, description="Number of worker processes")


class JWTSettings(BaseSettings):
    """JWT authentication settings."""

    model_config = SettingsConfigDict(
        env_prefix="JWT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    secret_key: str = Field(
        default="",
        description="JWT signing secret key (must be set via environment)",
    )
    algorithm: str = Field(default="HS256", description="JWT signing algorithm")
    access_token_expire_minutes: int = Field(
        default=120, description="Access token expiration time in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7, description="Refresh token expiration time in days"
    )

    @field_validator("secret_key")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Validate JWT secret key strength."""
        if not v or v == "":
            raise ValueError(
                "JWT secret key is required. Set JWT_SECRET_KEY environment variable."
            )
        if len(v) < 32:
            raise ValueError("JWT secret key must be at least 32 characters long")
        if v in [
            "fireflow-dev-secret-key-change-in-production",
            "dev-secret-key-for-testing",
        ]:
            raise ValueError("Default JWT secret keys are not allowed in production")
        return v


class SecuritySettings(BaseSettings):
    """Security configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="SECURITY_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bcrypt_rounds: int = Field(default=12, description="Bcrypt hashing rounds")
    max_login_attempts: int = Field(
        default=5, description="Maximum failed login attempts before lockout"
    )
    lockout_duration_minutes: int = Field(
        default=30, description="Account lockout duration in minutes"
    )
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="CORS allowed origins (avoid '*' in production)",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="LOG_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format",
    )
    file_path: str | None = Field(
        default=None, description="Log file path (if None, logs to console only)"
    )
    max_file_size_mb: int = Field(default=10, description="Maximum log file size in MB")
    backup_count: int = Field(
        default=5, description="Number of log file backups to keep"
    )


class MonitoringSettings(BaseSettings):
    """Monitoring and observability settings."""

    model_config = SettingsConfigDict(
        env_prefix="MONITORING_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    sentry_dsn: str | None = Field(
        default=None,
        description="Sentry DSN for error tracking (HTTPS URL required if provided)",
    )
    sentry_environment: str = Field(
        default="development", description="Sentry environment name"
    )
    metrics_enabled: bool = Field(
        default=False, description="Enable metrics collection"
    )
    health_check_timeout: int = Field(
        default=5, description="Health check timeout in seconds"
    )


class AppSettings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Application settings
    app_name: str = Field(default="FireFlow", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Enable debug mode")
    environment: Literal["development", "testing", "staging", "production"] = Field(
        default="development", description="Application environment"
    )

    # Flask settings
    flask_secret_key: str = Field(
        default="",
        description="Flask secret key (must be set via environment)",
    )
    flask_host: str = Field(default="0.0.0.0", description="Flask host")  # noqa: S104
    flask_port: int = Field(default=12345, description="Flask port")

    # Component settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    celery: CelerySettings = Field(default_factory=CelerySettings)
    jwt: JWTSettings = Field(default_factory=JWTSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment == "testing"

    @field_validator("flask_secret_key")
    @classmethod
    def validate_flask_secret(cls, v: str) -> str:
        """Validate Flask secret key strength."""
        if not v or v == "":
            raise ValueError(
                "Flask secret key is required. Set FLASK_SECRET_KEY environment variable."
            )
        if len(v) < 32:
            raise ValueError("Flask secret key must be at least 32 characters long")
        if v in [
            "fireflow-flask-secret-change-in-production",
            "dev-flask-secret-for-testing",
        ]:
            raise ValueError("Default Flask secret keys are not allowed in production")
        return v


# Global settings instance
settings = AppSettings()


def get_settings() -> AppSettings:
    """Get application settings instance."""
    return settings


def reload_settings() -> AppSettings:
    """Reload settings from environment/dotenv files."""
    global settings  # noqa: PLW0603
    settings = AppSettings()
    return settings
