"""
Two-Factor Authentication model for Auth Service
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import JSON, Text
import uuid

from .base import TimestampMixin, UUIDMixin


class UserTwoFactor(SQLModel, UUIDMixin, TimestampMixin, table=True):
    """Two-Factor Authentication settings for users."""

    __tablename__ = "user_two_factor"

    # Primary key (from UUIDMixin)
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False
    )

    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, unique=True, index=True)

    # TOTP Secret (encrypted in production)
    secret: str = Field(sa_column=Column(Text, nullable=False))

    # Backup codes (hashed in production)
    backup_codes: Optional[List[str]] = Field(default_factory=list, sa_column=Column(JSON))

    # 2FA Status
    is_enabled: bool = Field(default=False, nullable=False)
    enabled_at: Optional[datetime] = Field(default=None)

    # Last verified
    last_verified_at: Optional[datetime] = Field(default=None)

    # Recovery
    recovery_email: Optional[str] = Field(default=None, max_length=255)
