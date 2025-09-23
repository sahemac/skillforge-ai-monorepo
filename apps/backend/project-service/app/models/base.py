"""
Base model classes for SkillForge AI Project Service
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
import uuid


class TimestampMixin:
    """Mixin for models with timestamp fields."""
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: Optional[datetime] = Field(default=None, nullable=True)


class UUIDMixin:
    """Mixin for models with UUID primary key."""
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )


class BaseModel(SQLModel, UUIDMixin, TimestampMixin):
    """Base model with common fields."""
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            uuid.UUID: str
        }
        
    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()


class SoftDeleteMixin:
    """Mixin for models with soft delete functionality."""
    is_active: bool = Field(default=True, nullable=False)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)
    
    def soft_delete(self):
        """Soft delete the record."""
        self.is_active = False
        self.deleted_at = datetime.utcnow()
        self.update_timestamp()
    
    def restore(self):
        """Restore a soft deleted record."""
        self.is_active = True
        self.deleted_at = None
        self.update_timestamp()