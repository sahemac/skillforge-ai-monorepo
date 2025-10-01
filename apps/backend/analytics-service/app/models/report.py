"""
Report model for generated analytics reports
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlmodel import SQLModel, Field, JSON, Column
from uuid import uuid4
from enum import Enum


class ReportType(str, Enum):
    """Report types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"
    AD_HOC = "ad_hoc"


class ReportStatus(str, Enum):
    """Report generation status."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class ReportFormat(str, Enum):
    """Report output formats."""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    HTML = "html"


class ReportBase(SQLModel):
    """Base report model."""
    name: str = Field(..., description="Report name")
    description: Optional[str] = Field(default=None, description="Report description")
    report_type: ReportType = Field(..., description="Type of report")
    format: ReportFormat = Field(default=ReportFormat.PDF, description="Output format")
    recipients: List[str] = Field(default_factory=list, sa_column=Column(JSON), description="Email recipients")
    schedule_config: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON), description="Schedule configuration")
    parameters: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON), description="Report parameters")
    template_config: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON), description="Report template configuration")
    is_scheduled: bool = Field(default=False, description="Whether report is scheduled")
    is_active: bool = Field(default=True, description="Whether report is active")


class Report(ReportBase, table=True):
    """Report database model."""
    __tablename__ = "reports"

    id: Optional[str] = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        description="Report ID"
    )
    created_by: Optional[str] = Field(default=None, description="User who created the report")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    last_generated: Optional[datetime] = Field(default=None, description="Last generation timestamp")
    next_scheduled: Optional[datetime] = Field(default=None, description="Next scheduled generation")


class ReportCreate(ReportBase):
    """Report creation model."""
    pass


class ReportRead(ReportBase):
    """Report read model."""
    id: str
    created_by: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    last_generated: Optional[datetime]
    next_scheduled: Optional[datetime]


class ReportUpdate(SQLModel):
    """Report update model."""
    name: Optional[str] = None
    description: Optional[str] = None
    format: Optional[ReportFormat] = None
    recipients: Optional[List[str]] = None
    schedule_config: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    template_config: Optional[Dict[str, Any]] = None
    is_scheduled: Optional[bool] = None
    is_active: Optional[bool] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ReportExecution(SQLModel, table=True):
    """Report execution history."""
    __tablename__ = "report_executions"

    id: Optional[str] = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        description="Execution ID"
    )
    report_id: str = Field(..., description="Report ID", foreign_key="reports.id")
    status: ReportStatus = Field(default=ReportStatus.PENDING, description="Execution status")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Execution start time")
    completed_at: Optional[datetime] = Field(default=None, description="Execution completion time")
    duration_seconds: Optional[float] = Field(default=None, description="Execution duration in seconds")
    file_path: Optional[str] = Field(default=None, description="Generated file path")
    file_size_bytes: Optional[int] = Field(default=None, description="Generated file size")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    parameters_used: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON), description="Parameters used for this execution")
    metadata: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON), description="Execution metadata")

    def mark_as_completed(self, file_path: str, file_size: int):
        """Mark execution as completed."""
        self.status = ReportStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.file_path = file_path
        self.file_size_bytes = file_size
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()

    def mark_as_failed(self, error_message: str):
        """Mark execution as failed."""
        self.status = ReportStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()


class ReportExecutionCreate(SQLModel):
    """Report execution creation model."""
    report_id: str
    parameters_used: Optional[Dict[str, Any]] = None


class ReportExecutionRead(SQLModel):
    """Report execution read model."""
    id: str
    report_id: str
    status: ReportStatus
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    file_path: Optional[str]
    file_size_bytes: Optional[int]
    error_message: Optional[str]
    parameters_used: Dict[str, Any]
    metadata: Dict[str, Any]


# Pre-defined report templates
PREDEFINED_REPORTS = [
    {
        "name": "Daily Platform Summary",
        "description": "Daily summary of platform metrics and user activity",
        "report_type": ReportType.DAILY,
        "format": ReportFormat.PDF,
        "recipients": ["admin@skillforge.ai"],
        "schedule_config": {
            "frequency": "daily",
            "time": "08:00",
            "timezone": "UTC"
        },
        "parameters": {
            "include_charts": True,
            "include_insights": True,
            "time_range": "1d"
        },
        "template_config": {
            "sections": [
                {
                    "title": "Executive Summary",
                    "type": "summary",
                    "metrics": ["daily_active_users", "new_signups", "projects_submitted"]
                },
                {
                    "title": "User Engagement",
                    "type": "chart",
                    "chart_type": "line",
                    "metrics": ["page_views", "session_duration"]
                },
                {
                    "title": "System Performance",
                    "type": "table",
                    "metrics": ["response_time", "error_rate", "uptime"]
                }
            ]
        },
        "is_scheduled": True
    },
    {
        "name": "Weekly Business Report",
        "description": "Weekly business analytics and insights",
        "report_type": ReportType.WEEKLY,
        "format": ReportFormat.EXCEL,
        "recipients": ["business@skillforge.ai", "ceo@skillforge.ai"],
        "schedule_config": {
            "frequency": "weekly",
            "day": "monday",
            "time": "09:00",
            "timezone": "UTC"
        },
        "parameters": {
            "include_financial": True,
            "include_user_cohorts": True,
            "include_predictions": True,
            "time_range": "7d"
        },
        "template_config": {
            "sections": [
                {
                    "title": "Key Performance Indicators",
                    "type": "kpi_cards",
                    "metrics": ["weekly_active_users", "conversion_rate", "revenue"]
                },
                {
                    "title": "User Growth Analysis",
                    "type": "cohort_table",
                    "parameters": {"cohort_type": "registration"}
                },
                {
                    "title": "Feature Usage",
                    "type": "heatmap",
                    "metrics": ["feature_usage"]
                },
                {
                    "title": "Projections",
                    "type": "forecast",
                    "metrics": ["user_growth", "revenue_forecast"]
                }
            ]
        },
        "is_scheduled": True
    },
    {
        "name": "Monthly Executive Dashboard",
        "description": "Monthly executive summary with strategic insights",
        "report_type": ReportType.MONTHLY,
        "format": ReportFormat.PDF,
        "recipients": ["executives@skillforge.ai"],
        "schedule_config": {
            "frequency": "monthly",
            "day": 1,
            "time": "10:00",
            "timezone": "UTC"
        },
        "parameters": {
            "include_strategic_insights": True,
            "include_competitive_analysis": True,
            "include_recommendations": True,
            "time_range": "30d"
        },
        "template_config": {
            "sections": [
                {
                    "title": "Executive Summary",
                    "type": "executive_summary"
                },
                {
                    "title": "Growth Metrics",
                    "type": "growth_analysis",
                    "metrics": ["monthly_active_users", "revenue_growth", "market_expansion"]
                },
                {
                    "title": "Strategic Recommendations",
                    "type": "recommendations"
                }
            ]
        },
        "is_scheduled": True
    },
    {
        "name": "Company Performance Report",
        "description": "Performance metrics for company clients",
        "report_type": ReportType.CUSTOM,
        "format": ReportFormat.PDF,
        "parameters": {
            "company_specific": True,
            "include_talent_pipeline": True,
            "include_hiring_metrics": True,
            "customizable": True
        },
        "template_config": {
            "sections": [
                {
                    "title": "Talent Acquisition Overview",
                    "type": "summary",
                    "metrics": ["active_positions", "candidate_applications", "hiring_success_rate"]
                },
                {
                    "title": "Candidate Pipeline",
                    "type": "funnel",
                    "metrics": ["pipeline_conversion"]
                },
                {
                    "title": "Skills Analysis",
                    "type": "skills_breakdown",
                    "metrics": ["skills_demand", "skills_availability"]
                }
            ]
        },
        "is_scheduled": False
    },
    {
        "name": "System Health Report",
        "description": "Technical performance and system health metrics",
        "report_type": ReportType.WEEKLY,
        "format": ReportFormat.HTML,
        "recipients": ["devops@skillforge.ai", "engineering@skillforge.ai"],
        "schedule_config": {
            "frequency": "weekly",
            "day": "sunday",
            "time": "23:00",
            "timezone": "UTC"
        },
        "parameters": {
            "include_performance_metrics": True,
            "include_error_analysis": True,
            "include_capacity_planning": True,
            "time_range": "7d"
        },
        "template_config": {
            "sections": [
                {
                    "title": "Service Availability",
                    "type": "uptime_summary",
                    "metrics": ["service_uptime", "response_times"]
                },
                {
                    "title": "Error Analysis",
                    "type": "error_breakdown",
                    "metrics": ["error_rate", "error_types"]
                },
                {
                    "title": "Performance Trends",
                    "type": "performance_charts",
                    "metrics": ["cpu_usage", "memory_usage", "database_performance"]
                }
            ]
        },
        "is_scheduled": True
    }
]