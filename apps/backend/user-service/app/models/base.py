"""
Base model classes for SkillForge AI User Service
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
import uuid


class TimestampMixin:
    """Mixin for models with timestamp fields."""
    created_at: datetime
    updated_at: Optional[datetime]


class UUIDMixin:
    """Mixin for models with UUID primary key."""
    id: uuid.UUID