"""
Notification models for SkillForge AI platform
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from enum import Enum as PyEnum

Base = declarative_base()


class NotificationType(PyEnum):
    """Types of notifications"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationStatus(PyEnum):
    """Status of notifications"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"


class NotificationPriority(PyEnum):
    """Priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Base):
    """Main notification model"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)

    # Notification content
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    html_content = Column(Text, nullable=True)

    # Notification metadata
    notification_type = Column(Enum(NotificationType), nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.NORMAL)

    # Delivery information
    recipient_email = Column(String(255), nullable=True)
    recipient_phone = Column(String(20), nullable=True)

    # Tracking
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    failure_reason = Column(Text, nullable=True)

    # Metadata
    category = Column(String(100), nullable=True)
    action_url = Column(String(500), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class NotificationTemplate(Base):
    """Template for reusable notifications"""
    __tablename__ = "notification_templates"

    id = Column(Integer, primary_key=True, index=True)

    # Template identification
    template_name = Column(String(100), unique=True, nullable=False)
    template_key = Column(String(100), unique=True, nullable=False)

    # Template content
    subject_template = Column(String(255), nullable=False)
    content_template = Column(Text, nullable=False)
    html_template = Column(Text, nullable=True)

    # Configuration
    notification_type = Column(Enum(NotificationType), nullable=False)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.NORMAL)
    category = Column(String(100), nullable=True)

    # Settings
    is_active = Column(Boolean, default=True)

    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class NotificationPreference(Base):
    """User notification preferences"""
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)

    # Email preferences
    email_notifications = Column(Boolean, default=True)
    email_marketing = Column(Boolean, default=True)
    email_updates = Column(Boolean, default=True)

    # SMS preferences
    sms_notifications = Column(Boolean, default=False)
    sms_urgent_only = Column(Boolean, default=True)

    # Push preferences
    push_notifications = Column(Boolean, default=True)
    push_sound = Column(Boolean, default=True)
    push_vibration = Column(Boolean, default=True)

    # In-app preferences
    in_app_notifications = Column(Boolean, default=True)

    # Time preferences
    quiet_hours_start = Column(String(5), default="22:00")  # HH:MM format
    quiet_hours_end = Column(String(5), default="08:00")    # HH:MM format
    timezone = Column(String(50), default="UTC")

    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())