"""
Base model classes for SkillForge AI User Service
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy.orm import declarative_base
import uuid

# Create declarative base for all models
Base = declarative_base()


class TimestampMixin:
    """Mixin for models with timestamp fields."""
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: Optional[datetime] = Field(default=None, nullable=True)


class UUIDMixin:
    """Mixin for models with UUID primary key."""
    id: uuid.UUID