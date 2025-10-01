"""
Reports API schemas for request/response models
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, EmailStr
from app.models.report import ReportType, ReportStatus, ReportFormat


class ReportParametersSchema(BaseModel):
    """Schema for report parameters."""
    time_range: Optional[str] = Field(default="30d", description="Time range for report data")
    start_date: Optional[datetime] = Field(default=None, description="Custom start date")
    end_date: Optional[datetime] = Field(default=None, description="Custom end date")
    company_id: Optional[str] = Field(default=None, description="Company filter")
    user_segment: Optional[str] = Field(default=None, description="User segment filter")
    include_charts: bool = Field(default=True, description="Include charts in report")
    include_insights: bool = Field(default=True, description="Include AI insights")
    include_recommendations: bool = Field(default=False, description="Include recommendations")
    custom_parameters: Dict[str, Any] = Field(default_factory=dict, description="Custom parameters")


class ReportScheduleConfigSchema(BaseModel):
    """Schema for report schedule configuration."""
    frequency: str = Field(..., regex="^(daily|weekly|monthly|quarterly|yearly)$", description="Schedule frequency")
    day: Optional[int] = Field(default=None, ge=1, le=31, description="Day of month (for monthly/quarterly/yearly)")
    weekday: Optional[str] = Field(default=None, regex="^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$", description="Day of week (for weekly)")
    time: str = Field(..., regex="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$", description="Time in HH:MM format")
    timezone: str = Field(default="UTC", description="Timezone for scheduling")
    enabled: bool = Field(default=True, description="Whether schedule is enabled")


class ReportSectionConfigSchema(BaseModel):
    """Schema for report section configuration."""
    title: str = Field(..., description="Section title")
    type: str = Field(..., description="Section type (summary, chart, table, etc.)")
    metrics: List[str] = Field(default_factory=list, description="Metrics to include")
    chart_type: Optional[str] = Field(default=None, description="Chart type for chart sections")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Section-specific parameters")
    order: int = Field(default=0, description="Section order")
    enabled: bool = Field(default=True, description="Whether section is enabled")


class ReportTemplateConfigSchema(BaseModel):
    """Schema for report template configuration."""
    template_name: str = Field(default="default", description="Template name")
    page_size: str = Field(default="A4", description="Page size")
    orientation: str = Field(default="portrait", regex="^(portrait|landscape)$", description="Page orientation")
    header: Dict[str, Any] = Field(default_factory=dict, description="Header configuration")
    footer: Dict[str, Any] = Field(default_factory=dict, description="Footer configuration")
    sections: List[ReportSectionConfigSchema] = Field(default_factory=list, description="Report sections")
    styles: Dict[str, Any] = Field(default_factory=dict, description="Custom styles")


class ReportCreateSchema(BaseModel):
    """Schema for creating a report."""
    name: str = Field(..., min_length=1, max_length=200, description="Report name")
    description: Optional[str] = Field(default=None, max_length=1000, description="Report description")
    report_type: ReportType = Field(..., description="Type of report")
    format: ReportFormat = Field(default=ReportFormat.PDF, description="Output format")
    recipients: List[EmailStr] = Field(default_factory=list, description="Email recipients")
    parameters: ReportParametersSchema = Field(default_factory=ReportParametersSchema, description="Report parameters")
    template_config: ReportTemplateConfigSchema = Field(default_factory=ReportTemplateConfigSchema, description="Template configuration")
    schedule_config: Optional[ReportScheduleConfigSchema] = Field(default=None, description="Schedule configuration")
    is_scheduled: bool = Field(default=False, description="Whether report is scheduled")


class ReportUpdateSchema(BaseModel):
    """Schema for updating a report."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=200, description="Report name")
    description: Optional[str] = Field(default=None, max_length=1000, description="Report description")
    format: Optional[ReportFormat] = Field(default=None, description="Output format")
    recipients: Optional[List[EmailStr]] = Field(default=None, description="Email recipients")
    parameters: Optional[ReportParametersSchema] = Field(default=None, description="Report parameters")
    template_config: Optional[ReportTemplateConfigSchema] = Field(default=None, description="Template configuration")
    schedule_config: Optional[ReportScheduleConfigSchema] = Field(default=None, description="Schedule configuration")
    is_scheduled: Optional[bool] = Field(default=None, description="Whether report is scheduled")
    is_active: Optional[bool] = Field(default=None, description="Whether report is active")


class ReportResponseSchema(BaseModel):
    """Schema for report response."""
    id: str = Field(..., description="Report ID")
    name: str = Field(..., description="Report name")
    description: Optional[str] = Field(default=None, description="Report description")
    report_type: ReportType = Field(..., description="Report type")
    format: ReportFormat = Field(..., description="Output format")
    recipients: List[str] = Field(..., description="Email recipients")
    parameters: Dict[str, Any] = Field(..., description="Report parameters")
    template_config: Dict[str, Any] = Field(..., description="Template configuration")
    schedule_config: Optional[Dict[str, Any]] = Field(default=None, description="Schedule configuration")
    is_scheduled: bool = Field(..., description="Whether report is scheduled")
    is_active: bool = Field(..., description="Whether report is active")
    created_by: Optional[str] = Field(default=None, description="Created by user")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    last_generated: Optional[datetime] = Field(default=None, description="Last generation timestamp")
    next_scheduled: Optional[datetime] = Field(default=None, description="Next scheduled generation")

    class Config:
        from_attributes = True


class ReportListResponseSchema(BaseModel):
    """Schema for report list response."""
    reports: List[ReportResponseSchema] = Field(..., description="List of reports")
    total: int = Field(..., ge=0, description="Total number of reports")
    page: int = Field(..., ge=1, description="Current page number")
    size: int = Field(..., ge=1, description="Page size")


class ReportExecutionResponseSchema(BaseModel):
    """Schema for report execution response."""
    id: str = Field(..., description="Execution ID")
    report_id: str = Field(..., description="Report ID")
    status: ReportStatus = Field(..., description="Execution status")
    started_at: datetime = Field(..., description="Start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Completion timestamp")
    duration_seconds: Optional[float] = Field(default=None, description="Execution duration")
    file_path: Optional[str] = Field(default=None, description="Generated file path")
    file_size_bytes: Optional[int] = Field(default=None, description="File size in bytes")
    download_url: Optional[str] = Field(default=None, description="Download URL")
    error_message: Optional[str] = Field(default=None, description="Error message")
    parameters_used: Dict[str, Any] = Field(..., description="Parameters used")
    metadata: Dict[str, Any] = Field(..., description="Execution metadata")

    class Config:
        from_attributes = True


class ReportGenerationRequestSchema(BaseModel):
    """Schema for report generation request."""
    report_id: str = Field(..., description="Report ID to generate")
    parameters_override: Optional[ReportParametersSchema] = Field(default=None, description="Override report parameters")
    priority: str = Field(default="normal", regex="^(low|normal|high|urgent)$", description="Generation priority")
    notify_on_completion: bool = Field(default=True, description="Send notification when complete")


class ReportPreviewRequestSchema(BaseModel):
    """Schema for report preview request."""
    report_config: ReportTemplateConfigSchema = Field(..., description="Report configuration")
    parameters: ReportParametersSchema = Field(default_factory=ReportParametersSchema, description="Preview parameters")
    sample_data_only: bool = Field(default=True, description="Use sample data for faster preview")


class ReportPreviewResponseSchema(BaseModel):
    """Schema for report preview response."""
    preview_url: str = Field(..., description="Preview URL")
    expires_at: datetime = Field(..., description="Preview expiration time")
    sections: List[Dict[str, Any]] = Field(..., description="Preview sections data")


class ReportTemplateSchema(BaseModel):
    """Schema for report template."""
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    report_type: ReportType = Field(..., description="Applicable report type")
    config: ReportTemplateConfigSchema = Field(..., description="Template configuration")
    preview_image: Optional[str] = Field(default=None, description="Preview image URL")
    tags: List[str] = Field(default_factory=list, description="Template tags")
    is_public: bool = Field(default=False, description="Whether template is publicly available")


class ReportAnalyticsSchema(BaseModel):
    """Schema for report analytics."""
    report_id: str = Field(..., description="Report ID")
    total_generations: int = Field(..., description="Total number of generations")
    successful_generations: int = Field(..., description="Successful generations")
    failed_generations: int = Field(..., description="Failed generations")
    average_generation_time: float = Field(..., description="Average generation time in seconds")
    last_30_days_generations: int = Field(..., description="Generations in last 30 days")
    most_recent_generation: Optional[datetime] = Field(default=None, description="Most recent generation")
    download_stats: Dict[str, int] = Field(default_factory=dict, description="Download statistics")
    error_stats: Dict[str, int] = Field(default_factory=dict, description="Error statistics")


class BulkReportOperationSchema(BaseModel):
    """Schema for bulk report operations."""
    report_ids: List[str] = Field(..., min_items=1, description="List of report IDs")
    operation: str = Field(..., regex="^(generate|activate|deactivate|delete|export)$", description="Operation to perform")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Operation parameters")


class BulkReportOperationResponseSchema(BaseModel):
    """Schema for bulk report operation response."""
    operation_id: str = Field(..., description="Operation ID")
    operation: str = Field(..., description="Operation type")
    total_reports: int = Field(..., description="Total reports to process")
    processed_reports: int = Field(default=0, description="Reports processed")
    successful_operations: int = Field(default=0, description="Successful operations")
    failed_operations: int = Field(default=0, description="Failed operations")
    status: str = Field(default="pending", description="Operation status")
    started_at: datetime = Field(..., description="Operation start time")
    completed_at: Optional[datetime] = Field(default=None, description="Operation completion time")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Operation errors")


class ReportSubscriptionSchema(BaseModel):
    """Schema for report subscription."""
    report_id: str = Field(..., description="Report ID")
    user_email: EmailStr = Field(..., description="Subscriber email")
    delivery_preferences: Dict[str, Any] = Field(default_factory=dict, description="Delivery preferences")
    is_active: bool = Field(default=True, description="Whether subscription is active")
    subscribed_at: datetime = Field(default_factory=datetime.utcnow, description="Subscription timestamp")


class ReportDeliveryLogSchema(BaseModel):
    """Schema for report delivery log."""
    id: str = Field(..., description="Delivery log ID")
    report_execution_id: str = Field(..., description="Report execution ID")
    recipient: str = Field(..., description="Recipient email")
    delivery_method: str = Field(..., description="Delivery method (email, download, etc.)")
    status: str = Field(..., description="Delivery status")
    delivered_at: Optional[datetime] = Field(default=None, description="Delivery timestamp")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Delivery metadata")