"""
Configuration settings for SkillForge AI Audit Service
"""

import secrets
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Basic App Configuration
    PROJECT_NAME: str = "SkillForge AI Audit Service"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # API Gateway Integration
    API_GATEWAY_URL: Optional[str] = Field(default=None, env="API_GATEWAY_URL")
    
    # Security
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="SECRET_KEY")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="BACKEND_CORS_ORIGINS"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1"], 
        env="ALLOWED_HOSTS"
    )
    
    # Database
    DATABASE_URL: Optional[str] = Field(default=None, env="DATABASE_URL")
    POSTGRES_USER: str = Field(default="skillforge_user", env="POSTGRES_USER")
    POSTGRES_PASSWORD: Optional[str] = Field(default=None, env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(default="skillforge_audit", env="POSTGRES_DB")
    POSTGRES_HOST: str = Field(default="localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, env="POSTGRES_PORT")
    
    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379/11", env="REDIS_URL")
    CACHE_TTL: int = Field(default=300, env="CACHE_TTL")
    
    # External Services
    USER_SERVICE_URL: Optional[str] = Field(default="http://user-service:8000", env="USER_SERVICE_URL")\n    
    # Service-specific Configuration
    AUDIT_RETENTION_DAYS: Optional[str] = Field(default=None, env="AUDIT_RETENTION_DAYS")\n    LOG_ENCRYPTION_KEY: Optional[str] = Field(default=None, env="LOG_ENCRYPTION_KEY")\n    
    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    
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
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"
    
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