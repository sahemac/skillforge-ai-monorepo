"""
Configuration settings for SkillForge AI Analytics Service
"""

import secrets
from typing import List, Optional, Union, Dict, Any
from pydantic import AnyHttpUrl, EmailStr, Field, field_validator
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """Application settings."""

    # Basic App Configuration
    PROJECT_NAME: str = "SkillForge AI Analytics Service"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")

    # API Gateway Integration
    API_GATEWAY_URL: Optional[str] = Field(default=None, env="API_GATEWAY_URL")

    # Security
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="BACKEND_CORS_ORIGINS"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        env="ALLOWED_HOSTS"
    )

    # Database - NO DEFAULTS FOR PRODUCTION SECRETS
    DATABASE_URL: Optional[str] = Field(default=None, env="DATABASE_URL")
    POSTGRES_USER: str = Field(default="skillforge_user", env="POSTGRES_USER")
    POSTGRES_PASSWORD: Optional[str] = Field(default=None, env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(default="skillforge_analytics", env="POSTGRES_DB")
    POSTGRES_HOST: str = Field(default="localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, env="POSTGRES_PORT")

    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379/6", env="REDIS_URL")
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_DB: int = Field(default=6, env="REDIS_DB")
    CACHE_TTL: int = Field(default=300, env="CACHE_TTL")  # 5 minutes

    # BigQuery Configuration
    GOOGLE_CLOUD_PROJECT: Optional[str] = Field(default=None, env="GOOGLE_CLOUD_PROJECT")
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = Field(default=None, env="GOOGLE_APPLICATION_CREDENTIALS")
    BIGQUERY_DATASET: str = Field(default="skillforge_analytics", env="BIGQUERY_DATASET")
    BIGQUERY_LOCATION: str = Field(default="US", env="BIGQUERY_LOCATION")

    # Prometheus Configuration
    PROMETHEUS_URL: str = Field(default="http://prometheus:9090", env="PROMETHEUS_URL")
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")

    # External Services
    USER_SERVICE_URL: str = Field(default="http://user-service:8000", env="USER_SERVICE_URL")
    PROJECT_SERVICE_URL: str = Field(default="http://project-service:8003", env="PROJECT_SERVICE_URL")
    MATCHING_SERVICE_URL: str = Field(default="http://matching-service:8000", env="MATCHING_SERVICE_URL")
    COMPANY_SERVICE_URL: str = Field(default="http://company-service:8000", env="COMPANY_SERVICE_URL")
    NOTIFICATION_SERVICE_URL: str = Field(default="http://notification-service:8000", env="NOTIFICATION_SERVICE_URL")

    # Analytics Configuration
    ANALYTICS_API_KEY: Optional[str] = Field(default=None, env="ANALYTICS_API_KEY")
    GOOGLE_ANALYTICS_ID: Optional[str] = Field(default=None, env="GOOGLE_ANALYTICS_ID")
    DASHBOARD_REFRESH_INTERVAL: int = Field(default=300, env="DASHBOARD_REFRESH_INTERVAL")  # 5 minutes
    REALTIME_UPDATE_INTERVAL: int = Field(default=30, env="REALTIME_UPDATE_INTERVAL")  # 30 seconds

    # Celery Configuration for Background Jobs
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/7", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/8", env="CELERY_RESULT_BACKEND")

    # WebSocket Configuration
    WEBSOCKET_ENABLED: bool = Field(default=True, env="WEBSOCKET_ENABLED")
    MAX_WEBSOCKET_CONNECTIONS: int = Field(default=1000, env="MAX_WEBSOCKET_CONNECTIONS")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=120, env="RATE_LIMIT_PER_MINUTE")  # Higher for analytics

    # File Upload
    MAX_FILE_SIZE_MB: int = Field(default=50, env="MAX_FILE_SIZE_MB")  # Larger for reports
    UPLOAD_PATH: str = Field(default="/tmp/analytics_uploads", env="UPLOAD_PATH")

    # Report Generation
    REPORTS_OUTPUT_PATH: str = Field(default="/tmp/analytics_reports", env="REPORTS_OUTPUT_PATH")
    MAX_REPORT_RETENTION_DAYS: int = Field(default=30, env="MAX_REPORT_RETENTION_DAYS")

    # Testing
    TEST_DATABASE_URL: Optional[str] = Field(default=None, env="TEST_DATABASE_URL")

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @field_validator("ALLOWED_HOSTS", mode="before")
    def assemble_allowed_hosts(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> Any:
        if isinstance(v, str) and v:
            return v
        # Build from individual components if not provided
        user = values.get("POSTGRES_USER")
        password = values.get("POSTGRES_PASSWORD")
        host = values.get("POSTGRES_HOST", "localhost")
        port = values.get("POSTGRES_PORT", 5432)
        db = values.get("POSTGRES_DB", "skillforge_analytics")

        # For development only - fallback to SQLite if no password provided
        if not password or not user:
            return "sqlite+aiosqlite:///./skillforge_analytics_dev.db"

        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.ENVIRONMENT.lower() == "testing"

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Application settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings


# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
        }
    },
    "handlers": {
        "default": {
            "formatter": settings.LOG_FORMAT,
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "level": settings.LOG_LEVEL,
        "handlers": ["default"],
    },
    "loggers": {
        "uvicorn": {
            "level": settings.LOG_LEVEL,
            "handlers": ["default"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": settings.LOG_LEVEL,
            "handlers": ["default"],
            "propagate": False,
        },
        "sqlalchemy": {
            "level": "WARNING" if settings.is_production else "INFO",
            "handlers": ["default"],
            "propagate": False,
        },
        "alembic": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": False,
        },
        "celery": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": False,
        },
        "analytics": {
            "level": settings.LOG_LEVEL,
            "handlers": ["default"],
            "propagate": False,
        },
    },
}