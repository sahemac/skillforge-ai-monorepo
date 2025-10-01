"""
Configuration settings for SkillForge AI Payment Service
"""

import secrets
from decimal import Decimal
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Basic App Configuration
    PROJECT_NAME: str = "SkillForge AI Payment Service"
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
    POSTGRES_DB: str = Field(default="skillforge_payment", env="POSTGRES_DB")
    POSTGRES_HOST: str = Field(default="localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, env="POSTGRES_PORT")
    
    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379/4", env="REDIS_URL")
    CACHE_TTL: int = Field(default=300, env="CACHE_TTL")
    
    # External Services
    SUBSCRIPTION_SERVICE_URL: Optional[str] = Field(default="http://subscription-service:8000", env="SUBSCRIPTION_SERVICE_URL")
    USER_SERVICE_URL: Optional[str] = Field(default="http://user-service:8000", env="USER_SERVICE_URL")
    NOTIFICATION_SERVICE_URL: Optional[str] = Field(default="http://notification-service:8000", env="NOTIFICATION_SERVICE_URL")

    # Payment Provider Configuration
    STRIPE_SECRET_KEY: Optional[str] = Field(default=None, env="STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY: Optional[str] = Field(default=None, env="STRIPE_PUBLISHABLE_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(default=None, env="STRIPE_WEBHOOK_SECRET")

    PAYPAL_CLIENT_ID: Optional[str] = Field(default=None, env="PAYPAL_CLIENT_ID")
    PAYPAL_CLIENT_SECRET: Optional[str] = Field(default=None, env="PAYPAL_CLIENT_SECRET")
    PAYPAL_ENVIRONMENT: str = Field(default="sandbox", env="PAYPAL_ENVIRONMENT")  # sandbox or live
    PAYPAL_WEBHOOK_ID: Optional[str] = Field(default=None, env="PAYPAL_WEBHOOK_ID")

    # PCI Compliance & Security
    ENCRYPTION_KEY: Optional[str] = Field(default=None, env="ENCRYPTION_KEY")
    DATABASE_ENCRYPTION: bool = Field(default=True, env="DATABASE_ENCRYPTION")

    # Invoice & PDF Configuration
    INVOICE_TEMPLATE_PATH: str = Field(default="templates/invoices", env="INVOICE_TEMPLATE_PATH")
    PDF_STORAGE_PATH: str = Field(default="/tmp/invoices", env="PDF_STORAGE_PATH")

    # Celery Configuration
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/5", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/6", env="CELERY_RESULT_BACKEND")

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    PAYMENT_RATE_LIMIT: str = Field(default="10/minute", env="PAYMENT_RATE_LIMIT")

    # Business Configuration
    DEFAULT_CURRENCY: str = Field(default="EUR", env="DEFAULT_CURRENCY")
    SUPPORTED_CURRENCIES: List[str] = Field(default=["EUR", "USD", "GBP"], env="SUPPORTED_CURRENCIES")

    # Tax Configuration
    DEFAULT_TAX_RATE: Decimal = Field(default=Decimal('0.20'), env="DEFAULT_TAX_RATE")  # 20% VAT
    TAX_ENABLED: bool = Field(default=True, env="TAX_ENABLED")

    # Invoice Configuration
    INVOICE_PREFIX: str = Field(default="SF", env="INVOICE_PREFIX")
    INVOICE_NUMBER_LENGTH: int = Field(default=8, env="INVOICE_NUMBER_LENGTH")

    # Webhook Configuration
    WEBHOOK_TIMEOUT: int = Field(default=30, env="WEBHOOK_TIMEOUT")
    MAX_WEBHOOK_RETRIES: int = Field(default=3, env="MAX_WEBHOOK_RETRIES")

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