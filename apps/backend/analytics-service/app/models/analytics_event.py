"""
Analytics Event model for tracking user interactions and system events
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlmodel import SQLModel, Field, JSON, Column
from uuid import uuid4
import json


class AnalyticsEventBase(SQLModel):
    """Base analytics event model."""
    event_type: str = Field(..., description="Type of event (login, page_view, action, etc.)")
    user_id: Optional[str] = Field(default=None, description="User ID if authenticated")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, sa_column=Column(JSON), description="Event metadata")
    user_agent: Optional[str] = Field(default=None, description="User agent string")
    ip_address: Optional[str] = Field(default=None, description="IP address")
    referrer: Optional[str] = Field(default=None, description="HTTP referrer")
    page_url: Optional[str] = Field(default=None, description="Page URL where event occurred")


class AnalyticsEvent(AnalyticsEventBase, table=True):
    """Analytics event database model."""
    __tablename__ = "analytics_events"

    id: Optional[str] = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        description="Unique event identifier"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Event timestamp"
    )
    processed: bool = Field(default=False, description="Whether event has been processed for aggregation")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Record update timestamp")

    def to_bigquery_row(self) -> Dict[str, Any]:
        """Convert to BigQuery row format."""
        return {
            "event_id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "event_type": self.event_type,
            "event_data": self.metadata,
            "timestamp": self.timestamp,
            "user_agent": self.user_agent,
            "ip_address": self.ip_address,
        }


class AnalyticsEventCreate(AnalyticsEventBase):
    """Analytics event creation model."""
    pass


class AnalyticsEventRead(AnalyticsEventBase):
    """Analytics event read model."""
    id: str
    timestamp: datetime
    processed: bool
    created_at: datetime
    updated_at: Optional[datetime]


class AnalyticsEventUpdate(SQLModel):
    """Analytics event update model."""
    processed: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Event type constants
class EventTypes:
    """Common event types for analytics tracking."""

    # Authentication events
    LOGIN = "login"
    LOGOUT = "logout"
    SIGNUP = "signup"
    PASSWORD_RESET = "password_reset"

    # Navigation events
    PAGE_VIEW = "page_view"
    LANDING_PAGE_VIEW = "landing_page_view"
    SIGNUP_PAGE_VIEW = "signup_page_view"

    # User actions
    BUTTON_CLICK = "button_click"
    FORM_SUBMIT = "form_submit"
    FILE_UPLOAD = "file_upload"
    FILE_DOWNLOAD = "file_download"

    # Project events
    PROJECT_CREATED = "project_created"
    PROJECT_SUBMITTED = "project_submitted"
    PROJECT_COMPLETED = "project_completed"
    PROJECT_VIEWED = "project_viewed"

    # Matching events
    MATCH_REQUESTED = "match_requested"
    MATCH_SUCCESSFUL = "match_successful"
    MATCH_FAILED = "match_failed"

    # Learning events
    COURSE_STARTED = "course_started"
    COURSE_COMPLETED = "course_completed"
    SKILL_ASSESSED = "skill_assessed"

    # Company events
    JOB_POSTED = "job_posted"
    CANDIDATE_VIEWED = "candidate_viewed"
    INTERVIEW_SCHEDULED = "interview_scheduled"

    # System events
    API_CALL = "api_call"
    ERROR_OCCURRED = "error_occurred"
    PERFORMANCE_METRIC = "performance_metric"