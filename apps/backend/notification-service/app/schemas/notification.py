"""
Pydantic schemas for notification service
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    """Types of notifications"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationStatus(str, Enum):
    """Status of notifications"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"


class NotificationPriority(str, Enum):
    """Priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationBase(BaseModel):
    """Base notification schema"""
    title: str = Field(..., max_length=255)
    content: str
    html_content: Optional[str] = None
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.NORMAL
    recipient_email: Optional[EmailStr] = None
    recipient_phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-\(\)]+$')
    category: Optional[str] = Field(None, max_length=100)
    action_url: Optional[str] = Field(None, max_length=500)
    expires_at: Optional[datetime] = None


class NotificationCreate(NotificationBase):
    """Schema for creating notifications"""
    user_id: int


class NotificationUpdate(BaseModel):
    """Schema for updating notifications"""
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    html_content: Optional[str] = None
    status: Optional[NotificationStatus] = None
    priority: Optional[NotificationPriority] = None
    action_url: Optional[str] = Field(None, max_length=500)
    expires_at: Optional[datetime] = None


class NotificationResponse(NotificationBase):
    """Schema for notification responses"""
    id: int
    user_id: int
    status: NotificationStatus
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema for paginated notification list"""
    notifications: List[NotificationResponse]
    total: int
    page: int
    size: int
    total_pages: int


class SendNotificationRequest(BaseModel):
    """Schema for sending notifications"""
    user_id: int
    template_key: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    html_content: Optional[str] = None
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.NORMAL
    recipient_email: Optional[EmailStr] = None
    recipient_phone: Optional[str] = None
    category: Optional[str] = None
    action_url: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = {}

    @validator('template_data', pre=True)
    def validate_template_data(cls, v):
        return v or {}


class BulkNotificationRequest(BaseModel):
    """Schema for bulk notifications"""
    user_ids: List[int]
    template_key: str
    template_data: Dict[str, Any] = {}
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.NORMAL
    category: Optional[str] = None


class NotificationTemplateBase(BaseModel):
    """Base template schema"""
    template_name: str = Field(..., max_length=100)
    template_key: str = Field(..., max_length=100)
    subject_template: str = Field(..., max_length=255)
    content_template: str
    html_template: Optional[str] = None
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.NORMAL
    category: Optional[str] = Field(None, max_length=100)
    is_active: bool = True


class NotificationTemplateCreate(NotificationTemplateBase):
    """Schema for creating templates"""
    pass


class NotificationTemplateUpdate(BaseModel):
    """Schema for updating templates"""
    template_name: Optional[str] = Field(None, max_length=100)
    subject_template: Optional[str] = Field(None, max_length=255)
    content_template: Optional[str] = None
    html_template: Optional[str] = None
    priority: Optional[NotificationPriority] = None
    category: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class NotificationTemplateResponse(NotificationTemplateBase):
    """Schema for template responses"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationPreferenceBase(BaseModel):
    """Base preference schema"""
    email_notifications: bool = True
    email_marketing: bool = True
    email_updates: bool = True
    sms_notifications: bool = False
    sms_urgent_only: bool = True
    push_notifications: bool = True
    push_sound: bool = True
    push_vibration: bool = True
    in_app_notifications: bool = True
    quiet_hours_start: str = Field("22:00", pattern=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    quiet_hours_end: str = Field("08:00", pattern=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    timezone: str = "UTC"


class NotificationPreferenceUpdate(NotificationPreferenceBase):
    """Schema for updating preferences"""
    pass


class NotificationPreferenceResponse(NotificationPreferenceBase):
    """Schema for preference responses"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationStatsResponse(BaseModel):
    """Schema for notification statistics"""
    total_sent: int
    total_delivered: int
    total_failed: int
    total_read: int
    delivery_rate: float
    read_rate: float
    stats_by_type: Dict[str, Dict[str, int]]


class MarkAsReadRequest(BaseModel):
    """Schema for marking notifications as read"""
    notification_ids: List[int]